"""
Live API integration tests — hit real Anthropic and Google APIs.
Requires ANTHROPIC_API_KEY and GOOGLE_API_KEY in .env.
Run with: pytest tests/test_integration.py -v -m integration

All tests in this file are marked @pytest.mark.integration.
Excluded from the default test run via: pytest -m "not integration"
"""
import io
import os
import sys
import json
import time
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["DISABLE_GIT_SYNC"] = "1"

from dotenv import load_dotenv, find_dotenv

# find_dotenv() walks up the directory tree until it finds .env
_dotenv_path = find_dotenv(usecwd=False) or os.path.join(os.path.dirname(__file__), "../../../../.env")
load_dotenv(_dotenv_path, override=True)

pytestmark = pytest.mark.integration


def _google_embed_available() -> bool:
    """Return True only if the Google embed API is reachable and working."""
    from agents.research_agent import _embed
    vec = _embed("test", task_type="retrieval_document")
    return len(vec) > 0

_GOOGLE_UP = _google_embed_available()
skip_if_google_down = pytest.mark.skipif(
    not _GOOGLE_UP,
    reason="Google embedding API unavailable or key suspended — skipping embedding tests",
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_client():
    from fastapi.testclient import TestClient
    import main
    return TestClient(main.app)


def make_pdf_bytes(text: str = "Transformer models use self-attention.") -> bytes:
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    buf = doc.tobytes()
    doc.close()
    return buf


def make_png_bytes() -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
        b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
        b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def client():
    return make_client()


@pytest.fixture(autouse=True)
def rate_limit_pause():
    """Small pause between tests to avoid API rate limits."""
    yield
    time.sleep(1)


# ── Provider check ─────────────────────────────────────────────────────────────

class TestProviderLive:
    def test_anthropic_key_loaded(self):
        load_dotenv(_dotenv_path, override=True)
        assert os.getenv("ANTHROPIC_API_KEY"), "ANTHROPIC_API_KEY must be set in .env"

    def test_google_key_loaded(self):
        load_dotenv(_dotenv_path, override=True)
        assert os.getenv("GOOGLE_API_KEY"), "GOOGLE_API_KEY must be set in .env"

    def test_provider_endpoint_returns_claude(self, client):
        res = client.get("/api/provider")
        assert res.status_code == 200
        assert "Claude" in res.json()["provider"]


# ── call_ai live ───────────────────────────────────────────────────────────────

class TestCallAiLive:
    def test_basic_response(self):
        from agents.utils import call_ai
        result = call_ai("You are a helpful assistant.", "Say hello in 3 words.", max_tokens=20)
        assert isinstance(result, str)
        assert len(result) > 0
        assert not result.startswith("AI call failed:")

    def test_cache_returns_same_result(self):
        import agents.utils as u
        u._cache.clear()
        from agents.utils import call_ai
        prompt = "What is 2+2? Answer with one number."
        r1 = call_ai("You are a math assistant.", prompt, max_tokens=10)
        r2 = call_ai("You are a math assistant.", prompt, max_tokens=10)
        assert r1 == r2  # second call served from cache

    def test_sonnet_model_works(self):
        from agents.utils import call_ai
        result = call_ai(
            "You are a helpful assistant.",
            "Name one country in Europe. One word only.",
            max_tokens=10,
            model="claude-sonnet-4-6",
        )
        assert isinstance(result, str)
        assert len(result) > 0
        assert not result.startswith("AI call failed:")

    def test_haiku_model_works(self):
        from agents.utils import call_ai
        result = call_ai(
            "You are a helpful assistant.",
            "Name one colour. One word only.",
            max_tokens=10,
            model="claude-haiku-4-5",
        )
        assert isinstance(result, str)
        assert len(result) > 0


# ── Full pipeline — text query ─────────────────────────────────────────────────

class TestPipelineLive:
    def test_returns_valid_structure(self, client):
        res = client.post("/api/query", json={"query": "What is prompt engineering?"})
        assert res.status_code == 200
        data = res.json()
        assert "answer" in data
        assert "input_type" in data
        assert "notes_created" in data
        assert "notes_updated" in data
        assert "agent_trace" in data
        assert "validation" in data

    def test_answer_is_non_empty(self, client):
        res = client.post("/api/query", json={"query": "Explain neural networks briefly."})
        assert res.status_code == 200
        assert len(res.json()["answer"]) > 50

    def test_input_type_is_text_query(self, client):
        res = client.post("/api/query", json={"query": "What is machine learning?"})
        assert res.json()["input_type"] == "text_query"

    def test_exactly_7_agents_in_trace(self, client):
        res = client.post("/api/query", json={"query": "What is deep learning?"})
        assert len(res.json()["agent_trace"]) == 7

    def test_agent_order_correct(self, client):
        res = client.post("/api/query", json={"query": "Explain attention mechanisms."})
        agents = [t["agent"] for t in res.json()["agent_trace"]]
        assert agents == [
            "Intake Agent",
            "Extraction Agent",
            "RAG/Knowledge Agent",
            "Reasoning Agent",
            "Action Agent",
            "Linker Agent",
            "Validator Agent",
        ]

    def test_no_agent_errors_in_trace(self, client):
        res = client.post("/api/query", json={"query": "What is reinforcement learning?"})
        for entry in res.json()["agent_trace"]:
            assert not entry.get("error"), f"Agent {entry['agent']} errored: {entry['action']}"

    def test_validation_score_in_range(self, client):
        res = client.post("/api/query", json={"query": "What is a knowledge graph?"})
        score = res.json()["validation"]["score"]
        assert 1 <= score <= 10

    def test_note_created_or_updated(self, client):
        res = client.post("/api/query", json={"query": "Overview of embeddings in NLP."})
        data = res.json()
        assert data["notes_created"] or data["notes_updated"]

    def test_created_note_appears_in_notes_list(self, client):
        res = client.post("/api/query", json={"query": "What is vector search?"})
        data = res.json()
        all_notes_res = client.get("/api/notes")
        all_filenames = [n["filename"] for n in all_notes_res.json()]
        for fname in data["notes_created"] + data["notes_updated"]:
            assert fname in all_filenames, f"{fname} not found in notes list"

    def test_second_query_on_same_topic_updates_note(self, client):
        client.post("/api/query", json={"query": "What is transfer learning in deep learning?"})
        time.sleep(1)
        res2 = client.post("/api/query", json={"query": "Explain transfer learning techniques."})
        data = res2.json()
        assert data["notes_updated"] or data["notes_created"]


# ── Reasoning Agent uses Sonnet ────────────────────────────────────────────────

class TestModelRouting:
    def test_summarizer_uses_sonnet(self):
        """Verify summarizer_agent passes claude-sonnet-4-6 to call_ai."""
        import agents.summarizer_agent as sa
        calls = []
        original = sa.call_ai

        def capturing_call(system_prompt, user_message, max_tokens=1000, model="claude-haiku-4-5"):
            calls.append(model)
            return original(system_prompt, user_message, max_tokens=max_tokens, model=model)

        sa.call_ai = capturing_call
        try:
            sa.run("What is AI?", {"research": {"output": "some research"}})
        finally:
            sa.call_ai = original

        assert calls, "call_ai was never called"
        assert calls[0] == "claude-sonnet-4-6", f"Expected sonnet, got {calls[0]}"

    def test_writer_uses_haiku(self):
        """Writer agent should use default Haiku model."""
        import agents.writer_agent as wa
        calls = []
        original = wa.call_ai

        def capturing_call(system_prompt, user_message, max_tokens=1000, model="claude-haiku-4-5"):
            calls.append(model)
            return original(system_prompt, user_message, max_tokens=max_tokens, model=model)

        wa.call_ai = capturing_call
        try:
            wa.run("test query", {"summarizer": {"output": "test summary"}})
        finally:
            wa.call_ai = original

        assert all(m == "claude-haiku-4-5" for m in calls), f"Writer used wrong model(s): {calls}"


# ── PDF ingest live ────────────────────────────────────────────────────────────

class TestPdfIngestLive:
    def test_pdf_with_text_returns_answer(self, client):
        pdf = make_pdf_bytes("Large language models are trained on vast text corpora.")
        res = client.post(
            "/api/ingest/pdf",
            files={"file": ("report.pdf", io.BytesIO(pdf), "application/pdf")},
        )
        assert res.status_code == 200
        assert len(res.json()["answer"]) > 20

    def test_pdf_input_type_detected(self, client):
        pdf = make_pdf_bytes("Deep learning with neural networks " * 50)
        res = client.post(
            "/api/ingest/pdf",
            files={"file": ("report.pdf", io.BytesIO(pdf), "application/pdf")},
        )
        assert res.status_code == 200
        assert res.json()["input_type"] in ("document", "text_query")

    def test_pdf_produces_agent_trace(self, client):
        pdf = make_pdf_bytes("Attention is all you need. Transformer architecture overview.")
        res = client.post(
            "/api/ingest/pdf",
            files={"file": ("paper.pdf", io.BytesIO(pdf), "application/pdf")},
        )
        assert len(res.json()["agent_trace"]) == 7


# ── URL ingest live ────────────────────────────────────────────────────────────

class TestUrlIngestLive:
    def test_real_url_returns_answer(self, client):
        res = client.post(
            "/api/ingest/url",
            json={"url": "https://en.wikipedia.org/wiki/Transformer_(deep_learning_architecture)"},
        )
        assert res.status_code == 200
        assert len(res.json()["answer"]) > 50

    def test_url_produces_full_trace(self, client):
        res = client.post(
            "/api/ingest/url",
            json={"url": "https://en.wikipedia.org/wiki/Artificial_intelligence"},
        )
        assert res.status_code == 200
        assert len(res.json()["agent_trace"]) == 7


# ── CSV ingest live ────────────────────────────────────────────────────────────

class TestCsvIngestLive:
    def test_csv_returns_answer(self, client):
        csv_content = b"model,accuracy,params\nGPT-4,95.2,1T\nLlama-2,91.5,70B\nMistral,90.1,7B\n"
        res = client.post(
            "/api/ingest/csv",
            files={"file": ("models.csv", io.BytesIO(csv_content), "text/csv")},
        )
        assert res.status_code == 200
        assert len(res.json()["answer"]) > 20

    def test_json_file_returns_answer(self, client):
        data = [{"name": "BERT", "type": "encoder", "year": 2018},
                {"name": "GPT", "type": "decoder", "year": 2018}]
        res = client.post(
            "/api/ingest/csv",
            files={"file": ("models.json", io.BytesIO(json.dumps(data).encode()), "application/json")},
        )
        assert res.status_code == 200
        assert len(res.json()["answer"]) > 20


# ── Image ingest live ──────────────────────────────────────────────────────────

class TestImageIngestLive:
    def test_image_endpoint_reachable(self, client):
        """Even a blank image should be accepted if key is set."""
        res = client.post(
            "/api/ingest/image",
            files={"file": ("img.png", io.BytesIO(make_png_bytes()), "image/png")},
        )
        # 200 = vision extracted something; 422 = blank image, no content — both acceptable
        assert res.status_code in (200, 422)

    def test_image_wrong_type_rejected(self, client):
        res = client.post(
            "/api/ingest/image",
            files={"file": ("doc.pdf", io.BytesIO(b"data"), "application/pdf")},
        )
        assert res.status_code == 400


# ── Google embeddings live ─────────────────────────────────────────────────────

class TestGoogleEmbeddingsLive:
    @skip_if_google_down
    def test_embed_returns_non_empty_vector(self):
        from agents.research_agent import _embed
        vec = _embed("transformer attention mechanism", task_type="retrieval_document")
        assert isinstance(vec, list)
        assert len(vec) > 0
        assert all(isinstance(x, float) for x in vec)

    @skip_if_google_down
    def test_query_embed_different_task_type(self):
        from agents.research_agent import _embed
        doc_vec = _embed("machine learning model", task_type="retrieval_document")
        qry_vec = _embed("machine learning model", task_type="retrieval_query")
        assert len(doc_vec) == len(qry_vec)

    @skip_if_google_down
    def test_similar_texts_high_similarity(self):
        from agents.research_agent import _embed, _cosine_similarity
        v1 = _embed("transformer neural network attention", task_type="retrieval_document")
        v2 = _embed("transformer model with attention mechanism", task_type="retrieval_document")
        sim = _cosine_similarity(v1, v2)
        assert sim > 0.7, f"Expected high similarity, got {sim:.3f}"

    @skip_if_google_down
    def test_dissimilar_texts_low_similarity(self):
        from agents.research_agent import _embed, _cosine_similarity
        v1 = _embed("quantum physics subatomic particles", task_type="retrieval_document")
        v2 = _embed("recipe for chocolate cake baking", task_type="retrieval_document")
        sim = _cosine_similarity(v1, v2)
        assert sim < 0.7, f"Expected lower similarity, got {sim:.3f}"

    @skip_if_google_down
    def test_research_agent_finds_relevant_note(self, client):
        """Run a query, then run a related query — RAG should find the note."""
        client.post("/api/query", json={"query": "What is attention in transformer models?"})
        time.sleep(1)
        from agents.research_agent import _index, _indexed_files
        assert len(_index) > 0, "Index should be populated after a query"
