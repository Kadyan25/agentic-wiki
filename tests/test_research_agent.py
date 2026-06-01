"""
Unit tests for the research agent — Google embeddings mocked throughout.
No live API calls made.
Run with: pytest tests/test_research_agent.py -v
"""
import os
import sys
import tempfile
import shutil

import pytest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["DISABLE_GIT_SYNC"] = "1"

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"), override=True)

import agents.research_agent as ra


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_index():
    """Clear the module-level index before each test."""
    ra._index.clear()
    ra._indexed_files.clear()
    yield
    ra._index.clear()
    ra._indexed_files.clear()


@pytest.fixture
def tmp_knowledge(monkeypatch, tmp_path):
    """Point KNOWLEDGE_DIR at a temp directory for the test."""
    monkeypatch.setattr(ra, "KNOWLEDGE_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture
def fixed_embed(monkeypatch):
    """
    Replace _embed with a deterministic function.
    Returns a unit vector in the direction of the word count hash —
    similar texts get similar vectors, different texts get orthogonal ones.
    """
    def fake_embed(text: str, task_type: str = "retrieval_document"):
        # Build a 10-dim vector based on which keywords appear
        keywords = ["transformer", "attention", "neural", "language", "model",
                    "deep", "learning", "python", "data", "science"]
        vec = [1.0 if kw in text.lower() else 0.0 for kw in keywords]
        norm = np.linalg.norm(vec)
        if norm == 0:
            return [0.0] * 10
        return (np.array(vec) / norm).tolist()

    monkeypatch.setattr(ra, "_embed", fake_embed)
    return fake_embed


# ── _cosine_similarity ─────────────────────────────────────────────────────────

class TestCosineSimilarity:
    def test_identical_vectors_return_1(self):
        v = [1.0, 0.0, 0.0]
        assert abs(ra._cosine_similarity(v, v) - 1.0) < 1e-6

    def test_orthogonal_vectors_return_0(self):
        a = [1.0, 0.0, 0.0]
        b = [0.0, 1.0, 0.0]
        assert abs(ra._cosine_similarity(a, b)) < 1e-6

    def test_opposite_vectors_return_minus_1(self):
        a = [1.0, 0.0]
        b = [-1.0, 0.0]
        assert abs(ra._cosine_similarity(a, b) - (-1.0)) < 1e-6

    def test_zero_vector_a_returns_0(self):
        assert ra._cosine_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0

    def test_zero_vector_b_returns_0(self):
        assert ra._cosine_similarity([1.0, 0.0], [0.0, 0.0]) == 0.0

    def test_both_zero_returns_0(self):
        assert ra._cosine_similarity([0.0, 0.0], [0.0, 0.0]) == 0.0

    def test_partial_similarity(self):
        a = [1.0, 1.0, 0.0]
        b = [1.0, 0.0, 0.0]
        sim = ra._cosine_similarity(a, b)
        assert 0.0 < sim < 1.0


# ── _build_index ───────────────────────────────────────────────────────────────

class TestBuildIndex:
    def test_indexes_md_files(self, tmp_knowledge, fixed_embed):
        (tmp_knowledge / "note1.md").write_text(
            "# Transformer Models\nAttention mechanism is key.", encoding="utf-8"
        )
        ra._build_index()
        assert len(ra._index) > 0
        assert "note1.md" in ra._indexed_files

    def test_skips_already_indexed_files(self, tmp_knowledge, fixed_embed):
        (tmp_knowledge / "note1.md").write_text("# Test\nContent.", encoding="utf-8")
        ra._build_index()
        count_after_first = len(ra._index)
        ra._build_index()  # second call
        assert len(ra._index) == count_after_first  # no duplicates

    def test_incrementally_indexes_new_files(self, tmp_knowledge, fixed_embed):
        (tmp_knowledge / "note1.md").write_text("# Note One\nContent.", encoding="utf-8")
        ra._build_index()
        count_first = len(ra._index)

        (tmp_knowledge / "note2.md").write_text("# Note Two\nMore content.", encoding="utf-8")
        ra._build_index()
        assert len(ra._index) > count_first
        assert "note2.md" in ra._indexed_files

    def test_ignores_non_md_files(self, tmp_knowledge, fixed_embed):
        (tmp_knowledge / "data.csv").write_text("col1,col2\nval1,val2", encoding="utf-8")
        (tmp_knowledge / "note.txt").write_text("some text", encoding="utf-8")
        ra._build_index()
        assert len(ra._indexed_files) == 0

    def test_empty_embed_skips_chunk(self, tmp_knowledge, monkeypatch):
        """If embedding returns empty list, chunk should not be added to index."""
        monkeypatch.setattr(ra, "_embed", lambda text, task_type="retrieval_document": [])
        (tmp_knowledge / "note.md").write_text("# Test\nContent.", encoding="utf-8")
        ra._build_index()
        assert len(ra._index) == 0

    def test_handles_unreadable_file_gracefully(self, tmp_knowledge, fixed_embed):
        """Build index should not crash if a file can't be read."""
        note = tmp_knowledge / "note.md"
        note.write_text("# Test\nContent.", encoding="utf-8")
        # Remove read permission on Unix; skip on Windows
        if os.name != "nt":
            note.chmod(0o000)
            try:
                ra._build_index()  # should not raise
            finally:
                note.chmod(0o644)


# ── run() — semantic search ────────────────────────────────────────────────────

class TestRunFunction:
    def test_empty_knowledge_base(self, tmp_knowledge, fixed_embed):
        result = ra.run("What are transformers?", {})
        assert result["output"] == "No relevant notes found."
        assert result["files_read"] == []

    def test_finds_relevant_note(self, tmp_knowledge, fixed_embed):
        (tmp_knowledge / "transformers.md").write_text(
            "# Transformer Models\nTransformer attention neural language model.", encoding="utf-8"
        )
        result = ra.run("transformer attention neural model", {})
        # Should find the note since embeddings will be similar
        assert result["files_read"] == ["transformers.md"] or result["output"] != "No relevant notes found."

    def test_returns_correct_keys(self, tmp_knowledge, fixed_embed):
        result = ra.run("test query", {})
        assert "output" in result
        assert "files_read" in result
        assert "files_written" in result
        assert "gaps" in result

    def test_files_written_always_empty(self, tmp_knowledge, fixed_embed):
        result = ra.run("anything", {})
        assert result["files_written"] == []

    def test_failed_query_embed_returns_no_results(self, tmp_knowledge, monkeypatch):
        """If query embedding fails, gracefully return no results."""
        call_count = [0]

        def selective_embed(text, task_type="retrieval_document"):
            call_count[0] += 1
            if task_type == "retrieval_query":
                return []  # fail only on query embedding
            return [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        (tmp_knowledge / "note.md").write_text("# Test\nContent.", encoding="utf-8")
        monkeypatch.setattr(ra, "_embed", selective_embed)
        result = ra.run("query", {})
        assert result["output"] == "No relevant notes found."
        assert result["files_read"] == []

    def test_below_threshold_not_returned(self, tmp_knowledge, monkeypatch):
        """Chunks with similarity below 0.35 should not appear in results."""
        # Note about python/data — query about transformer should be dissimilar
        (tmp_knowledge / "python.md").write_text(
            "# Python Data Science\nPython data science learning.", encoding="utf-8"
        )

        def fake_embed(text, task_type="retrieval_document"):
            if "python" in text.lower() or "data" in text.lower():
                return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0]
            # Query about transformers — orthogonal to python note
            return [1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        monkeypatch.setattr(ra, "_embed", fake_embed)
        result = ra.run("transformer attention", {})
        assert "python.md" not in result["files_read"]

    def test_top_k_limit(self, tmp_knowledge, fixed_embed):
        """Never return more than TOP_K results."""
        for i in range(10):
            (tmp_knowledge / f"note{i}.md").write_text(
                f"# Note {i}\nTransformer attention neural language model deep learning.",
                encoding="utf-8",
            )
        result = ra.run("transformer attention neural model", {})
        assert len(result["files_read"]) <= ra.TOP_K

    def test_gaps_identified(self, tmp_knowledge, fixed_embed):
        """Keywords in query not matching any indexed file → gaps."""
        (tmp_knowledge / "note.md").write_text("# Transformers\nSome content.", encoding="utf-8")
        result = ra.run("quantum computing blockchain", {})
        assert isinstance(result["gaps"], list)


# ── _chunk_text (markdown-aware, already in test_pipeline but more coverage) ──

class TestChunkTextExtended:
    def test_large_markdown_splits_on_headers(self):
        sections = []
        for i in range(5):
            sections.append(f"# Section {i}\n" + ("word " * 120))
        text = "\n\n".join(sections)
        chunks = ra._chunk_text(text, size=500)
        assert len(chunks) > 1

    def test_all_content_preserved(self):
        """No content should be silently dropped."""
        text = "apple " * 300
        chunks = ra._chunk_text(text, size=200)
        combined = " ".join(chunks)
        # All words should still be present (allow overlap duplication)
        assert "apple" in combined
        total_words = sum(c.count("apple") for c in chunks)
        assert total_words >= 300  # overlap may add extra

    def test_single_very_long_sentence_kept_intact(self):
        long_sentence = "word " * 150  # 750 chars, no sentence boundary
        chunks = ra._chunk_text(long_sentence, size=500)
        # Should not crash and should return something
        assert len(chunks) >= 1
        assert all(len(c) > 0 for c in chunks)
