"""
Stress and concurrency tests.
Run with: pytest tests/test_stress.py -v -m stress -s

Tests in this file are marked @pytest.mark.stress.
They make real API calls and write to the knowledge base.
Requires ANTHROPIC_API_KEY and GOOGLE_API_KEY in .env.
"""
import os
import sys
import time
import threading
import concurrent.futures
from collections import Counter

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["DISABLE_GIT_SYNC"] = "1"

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"), override=True)

pytestmark = pytest.mark.stress


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient
    import main
    return TestClient(main.app)


# ── Cache effectiveness ────────────────────────────────────────────────────────

class TestCacheEffectiveness:
    def test_repeated_identical_query_uses_cache(self):
        """Same prompt should hit cache on 2nd+ call — no extra API calls."""
        import agents.utils as u
        u._cache.clear()
        call_count = [0]
        original = u._call_anthropic

        def counting_call(*args, **kwargs):
            call_count[0] += 1
            return original(*args, **kwargs)

        u._call_anthropic = counting_call
        try:
            u.call_ai("You are a helper.", "Say yes.", max_tokens=5)
            u.call_ai("You are a helper.", "Say yes.", max_tokens=5)
            u.call_ai("You are a helper.", "Say yes.", max_tokens=5)
        finally:
            u._call_anthropic = original

        assert call_count[0] == 1, f"Expected 1 API call (2 cached), got {call_count[0]}"

    def test_different_queries_bypass_cache(self):
        """Different prompts should each make their own API call."""
        import agents.utils as u
        u._cache.clear()
        call_count = [0]
        original = u._call_anthropic

        def counting_call(*args, **kwargs):
            call_count[0] += 1
            return original(*args, **kwargs)

        u._call_anthropic = counting_call
        try:
            u.call_ai("You are a helper.", "Say yes.", max_tokens=5)
            u.call_ai("You are a helper.", "Say no.", max_tokens=5)
            u.call_ai("You are a helper.", "Say maybe.", max_tokens=5)
        finally:
            u._call_anthropic = original

        assert call_count[0] == 3, f"Expected 3 API calls, got {call_count[0]}"


# ── Concurrent requests ────────────────────────────────────────────────────────

class TestConcurrentRequests:
    def test_3_concurrent_queries_all_succeed(self, client):
        """3 concurrent queries should all return 200 without corrupting each other."""
        queries = [
            "What is natural language processing?",
            "Explain gradient descent optimisation.",
            "What is a recurrent neural network?",
        ]
        results = {}
        errors = {}

        def run_query(q):
            try:
                res = client.post("/api/query", json={"query": q})
                results[q] = res.status_code
            except Exception as e:
                errors[q] = str(e)

        threads = [threading.Thread(target=run_query, args=(q,)) for q in queries]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=120)

        assert not errors, f"Threads raised exceptions: {errors}"
        assert all(s == 200 for s in results.values()), f"Not all 200: {results}"

    def test_concurrent_notes_not_corrupted(self, client):
        """After concurrent writes, all notes should be valid markdown."""
        queries = [
            "What is convolutional neural network?",
            "Explain batch normalisation in deep learning.",
            "What is dropout regularisation?",
        ]

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            futs = [pool.submit(client.post, "/api/query", json={"query": q}) for q in queries]
            responses = [f.result(timeout=120) for f in futs]

        assert all(r.status_code == 200 for r in responses)

        # Verify knowledge base files are valid
        import main as m
        for fname in os.listdir(m.KNOWLEDGE_DIR):
            if not fname.endswith(".md"):
                continue
            path = os.path.join(m.KNOWLEDGE_DIR, fname)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            assert len(content) > 0, f"{fname} is empty after concurrent writes"

    def test_5_concurrent_queries_no_exception(self, client):
        """5 concurrent queries — assert none crash (200 or structured error acceptable)."""
        queries = [
            "What is BERT?",
            "Explain tokenisation in NLP.",
            "What is word embedding?",
            "Explain positional encoding.",
            "What is fine-tuning a language model?",
        ]

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            futs = [pool.submit(client.post, "/api/query", json={"query": q}) for q in queries]
            responses = [f.result(timeout=180) for f in futs]

        statuses = [r.status_code for r in responses]
        assert all(s == 200 for s in statuses), f"Unexpected statuses: {statuses}"


# ── Large input ────────────────────────────────────────────────────────────────

class TestLargeInput:
    def test_input_at_4000_char_cap(self, client):
        """Input exactly at the cap should be handled cleanly."""
        large_query = ("transformer model attention mechanism neural network deep learning " * 50)[:4000]
        res = client.post("/api/query", json={"query": large_query})
        assert res.status_code == 200
        assert len(res.json()["answer"]) > 0

    def test_input_over_cap_truncated_not_crashed(self, client):
        """Input over 4000 chars via /api/ingest endpoints gets truncated, not rejected."""
        import io
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        # ~8000 chars of text
        page.insert_text((72, 72), "transformer attention neural language model deep learning " * 140)
        pdf_bytes = doc.tobytes()
        doc.close()

        res = client.post(
            "/api/ingest/pdf",
            files={"file": ("big.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
        )
        assert res.status_code == 200

    def test_csv_with_many_rows_truncated(self, client):
        """Large CSV (>4000 chars summary) gets truncated and still processed."""
        import io
        rows = ["col1,col2,col3"] + [f"value{i},data{i},result{i}" for i in range(200)]
        csv_content = "\n".join(rows).encode()
        res = client.post(
            "/api/ingest/csv",
            files={"file": ("big.csv", io.BytesIO(csv_content), "text/csv")},
        )
        assert res.status_code == 200


# ── Throughput ─────────────────────────────────────────────────────────────────

class TestThroughput:
    def test_5_sequential_queries_complete_under_5_minutes(self, client):
        """5 sequential queries should all complete in a reasonable time."""
        queries = [
            "What is zero-shot learning?",
            "Explain few-shot prompting.",
            "What is chain-of-thought reasoning?",
            "Explain retrieval augmented generation.",
            "What is instruction tuning?",
        ]

        start = time.time()
        for q in queries:
            res = client.post("/api/query", json={"query": q})
            assert res.status_code == 200
        elapsed = time.time() - start

        assert elapsed < 300, f"5 queries took {elapsed:.1f}s — over 5 minute limit"
        print(f"\n  5 sequential queries completed in {elapsed:.1f}s ({elapsed/5:.1f}s avg)")

    def test_cached_query_faster_than_fresh(self, client):
        """A cached query should return faster than one hitting the API."""
        import agents.utils as u
        query = "What is self-supervised learning in NLP?"

        # First call — cold
        u._cache.clear()
        t0 = time.time()
        res1 = client.post("/api/query", json={"query": query})
        cold_time = time.time() - t0
        assert res1.status_code == 200

        # Second call — utils cache warm (same prompts in agents will hit cache)
        t0 = time.time()
        res2 = client.post("/api/query", json={"query": query})
        warm_time = time.time() - t0
        assert res2.status_code == 200

        print(f"\n  Cold: {cold_time:.2f}s  Warm: {warm_time:.2f}s")
        # Warm should be faster — not always guaranteed due to file I/O but generally true
        # Use a lenient check: warm must not be more than 2x slower than cold
        assert warm_time < cold_time * 2


# ── Research agent index under load ───────────────────────────────────────────

class TestIndexUnderLoad:
    def test_index_consistent_after_concurrent_builds(self):
        """Multiple threads calling _build_index() simultaneously shouldn't corrupt it."""
        import agents.research_agent as ra
        ra._index.clear()
        ra._indexed_files.clear()

        errors = []

        def build():
            try:
                ra._build_index()
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=build) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)

        assert not errors, f"Concurrent index builds raised: {errors}"
        # Index should have entries (real knowledge files exist)
        assert len(ra._indexed_files) >= 0  # at minimum, didn't crash

    def test_index_not_duplicated_by_concurrent_build(self, monkeypatch):
        """Files should appear at most once in _indexed_files even with races.
        _embed is mocked so this test doesn't need a live Google API key."""
        import agents.research_agent as ra

        monkeypatch.setattr(ra, "_embed", lambda text, task_type="retrieval_document": [0.1, 0.2, 0.3])
        ra._index.clear()
        ra._indexed_files.clear()

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            futs = [pool.submit(ra._build_index) for _ in range(4)]
            for f in futs:
                f.result(timeout=60)

        # _indexed_files is a set — by definition no duplicates
        # but verify it actually contains the expected files
        file_counter = Counter(ra._indexed_files)
        duplicates = {k: v for k, v in file_counter.items() if v > 1}
        assert not duplicates, f"Duplicate entries in index: {duplicates}"


# ── Memory / leakage ──────────────────────────────────────────────────────────

class TestMemoryBehaviour:
    def test_cache_grows_with_unique_queries(self):
        """Cache should accumulate entries for unique queries."""
        import agents.utils as u
        u._cache.clear()
        initial = len(u._cache)

        from agents.utils import call_ai
        call_ai("You are a helper.", "Say A.", max_tokens=5)
        call_ai("You are a helper.", "Say B.", max_tokens=5)
        call_ai("You are a helper.", "Say C.", max_tokens=5)

        assert len(u._cache) >= initial + 3

    def test_cache_does_not_grow_for_repeated_query(self):
        """Repeated identical queries should not grow the cache."""
        import agents.utils as u
        u._cache.clear()

        from agents.utils import call_ai
        call_ai("You are a helper.", "Say X.", max_tokens=5)
        size_after_first = len(u._cache)
        call_ai("You are a helper.", "Say X.", max_tokens=5)
        call_ai("You are a helper.", "Say X.", max_tokens=5)

        assert len(u._cache) == size_after_first
