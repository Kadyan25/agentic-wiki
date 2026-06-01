"""
Endpoint tests for all FastAPI routes.
run_pipeline() is mocked — no live API calls made.
Run with: pytest tests/test_endpoints.py -v
"""
import io
import os
import sys
import json
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["DISABLE_GIT_SYNC"] = "1"

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"), override=True)

from fastapi.testclient import TestClient

# ── Shared mock pipeline response ─────────────────────────────────────────────

MOCK_RESULT = {
    "answer": "This is a mocked answer.",
    "input_type": "text_query",
    "notes_created": ["mocked-note.md"],
    "notes_updated": [],
    "agent_trace": [
        {"agent": "Intake Agent", "action": "Intake complete.", "files_read": [], "files_written": []},
        {"agent": "Extraction Agent", "action": "Extracted 0 entities.", "files_read": [], "files_written": []},
        {"agent": "RAG/Knowledge Agent", "action": "Found 0 notes.", "files_read": [], "files_written": []},
        {"agent": "Reasoning Agent", "action": "Summary generated.", "files_read": [], "files_written": []},
        {"agent": "Action Agent", "action": "Note created.", "files_read": [], "files_written": ["mocked-note.md"]},
        {"agent": "Linker Agent", "action": "Links added.", "files_read": [], "files_written": []},
        {"agent": "Validator Agent", "action": "Score: 8/10", "files_read": [], "files_written": []},
    ],
    "validation": {"score": 8, "issues": [], "suggestions": []},
}


@pytest.fixture
def client(monkeypatch):
    """TestClient with run_pipeline mocked out."""
    import main
    monkeypatch.setattr(main, "run_pipeline", lambda q: MOCK_RESULT)
    return TestClient(main.app)


# ── POST /api/query ────────────────────────────────────────────────────────────

class TestQueryEndpoint:
    def test_returns_200(self, client):
        res = client.post("/api/query", json={"query": "What is AI?"})
        assert res.status_code == 200

    def test_response_shape(self, client):
        res = client.post("/api/query", json={"query": "What is AI?"})
        data = res.json()
        assert "answer" in data
        assert "input_type" in data
        assert "notes_created" in data
        assert "notes_updated" in data
        assert "agent_trace" in data
        assert "validation" in data

    def test_validation_shape(self, client):
        res = client.post("/api/query", json={"query": "test"})
        v = res.json()["validation"]
        assert "score" in v
        assert "issues" in v
        assert "suggestions" in v

    def test_agent_trace_is_list(self, client):
        res = client.post("/api/query", json={"query": "test"})
        assert isinstance(res.json()["agent_trace"], list)

    def test_missing_query_field_returns_422(self, client):
        res = client.post("/api/query", json={})
        assert res.status_code == 422

    def test_empty_query_still_processes(self, client):
        res = client.post("/api/query", json={"query": ""})
        # Empty string is valid JSON — pipeline handles it
        assert res.status_code == 200


# ── POST /api/ingest/pdf ───────────────────────────────────────────────────────

class TestPdfEndpoint:
    def _make_pdf_bytes(self):
        """Minimal valid PDF bytes."""
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Test PDF content for ingestion.")
        buf = doc.tobytes()
        doc.close()
        return buf

    def test_valid_pdf_returns_200(self, client):
        pdf_bytes = self._make_pdf_bytes()
        res = client.post(
            "/api/ingest/pdf",
            files={"file": ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
        )
        assert res.status_code == 200

    def test_valid_pdf_response_shape(self, client):
        pdf_bytes = self._make_pdf_bytes()
        res = client.post(
            "/api/ingest/pdf",
            files={"file": ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
        )
        data = res.json()
        assert "answer" in data
        assert "agent_trace" in data

    def test_wrong_extension_returns_400(self, client):
        res = client.post(
            "/api/ingest/pdf",
            files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
        )
        assert res.status_code == 400
        assert "PDF" in res.json()["detail"]

    def test_empty_pdf_returns_422(self, client):
        """PDF with no text content."""
        import fitz
        doc = fitz.open()
        doc.new_page()  # blank page, no text
        buf = doc.tobytes()
        doc.close()
        res = client.post(
            "/api/ingest/pdf",
            files={"file": ("blank.pdf", io.BytesIO(buf), "application/pdf")},
        )
        assert res.status_code == 422
        assert "no extractable text" in res.json()["detail"]

    def test_corrupt_file_returns_422(self, client):
        res = client.post(
            "/api/ingest/pdf",
            files={"file": ("bad.pdf", io.BytesIO(b"not a pdf at all"), "application/pdf")},
        )
        assert res.status_code == 422


# ── POST /api/ingest/url ───────────────────────────────────────────────────────

class TestUrlEndpoint:
    def test_invalid_url_scheme_returns_400(self, client):
        res = client.post("/api/ingest/url", json={"url": "ftp://example.com"})
        assert res.status_code == 400
        assert "http" in res.json()["detail"]

    def test_no_scheme_returns_400(self, client):
        res = client.post("/api/ingest/url", json={"url": "example.com/page"})
        assert res.status_code == 400

    def test_missing_url_field_returns_422(self, client):
        res = client.post("/api/ingest/url", json={})
        assert res.status_code == 422

    def test_unreachable_url_returns_422(self, client):
        res = client.post(
            "/api/ingest/url",
            json={"url": "http://localhost:19999/nonexistent"},
        )
        assert res.status_code == 422

    def test_valid_url_returns_200(self, client, monkeypatch):
        """Mock requests.get to avoid real HTTP."""
        import main as m
        import requests

        class FakeResp:
            status_code = 200
            text = "<html><body><p>Hello world content here.</p></body></html>"
            def raise_for_status(self): pass

        monkeypatch.setattr(requests, "get", lambda *a, **kw: FakeResp())
        res = client.post("/api/ingest/url", json={"url": "https://example.com"})
        assert res.status_code == 200

    def test_empty_page_returns_422(self, client, monkeypatch):
        import requests

        class EmptyResp:
            status_code = 200
            text = "<html><body></body></html>"
            def raise_for_status(self): pass

        monkeypatch.setattr(requests, "get", lambda *a, **kw: EmptyResp())
        res = client.post("/api/ingest/url", json={"url": "https://example.com"})
        assert res.status_code == 422


# ── POST /api/ingest/image ─────────────────────────────────────────────────────

class TestImageEndpoint:
    def _png_bytes(self):
        """Minimal 1x1 white PNG."""
        return (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
            b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )

    def test_wrong_extension_returns_400(self, client):
        res = client.post(
            "/api/ingest/image",
            files={"file": ("doc.pdf", io.BytesIO(b"data"), "application/pdf")},
        )
        assert res.status_code == 400
        assert "jpg" in res.json()["detail"].lower() or "png" in res.json()["detail"].lower()

    def test_no_anthropic_key_returns_400(self, client, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        res = client.post(
            "/api/ingest/image",
            files={"file": ("photo.png", io.BytesIO(self._png_bytes()), "image/png")},
        )
        assert res.status_code == 400
        assert "ANTHROPIC_API_KEY" in res.json()["detail"]

    def test_valid_image_calls_pipeline(self, client, monkeypatch):
        """Mock call_vision so no real API call is made."""
        import agents.utils as u
        monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key-for-test")
        monkeypatch.setattr(u, "call_vision", lambda *a, **kw: "Extracted image text content.")
        res = client.post(
            "/api/ingest/image",
            files={"file": ("photo.png", io.BytesIO(self._png_bytes()), "image/png")},
        )
        assert res.status_code == 200
        assert "answer" in res.json()

    def test_vision_returning_empty_returns_422(self, client, monkeypatch):
        import agents.utils as u
        monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key-for-test")
        monkeypatch.setattr(u, "call_vision", lambda *a, **kw: "   ")
        res = client.post(
            "/api/ingest/image",
            files={"file": ("photo.png", io.BytesIO(self._png_bytes()), "image/png")},
        )
        assert res.status_code == 422

    def test_accepted_extensions(self, client, monkeypatch):
        import agents.utils as u
        monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key-for-test")
        monkeypatch.setattr(u, "call_vision", lambda *a, **kw: "some content")
        for ext in ("jpg", "jpeg", "png", "webp"):
            res = client.post(
                "/api/ingest/image",
                files={"file": (f"img.{ext}", io.BytesIO(self._png_bytes()), "image/png")},
            )
            assert res.status_code == 200, f"Failed for extension: {ext}"


# ── POST /api/ingest/csv ───────────────────────────────────────────────────────

class TestCsvEndpoint:
    def test_valid_csv_returns_200(self, client):
        csv_content = b"name,age,city\nAlice,30,London\nBob,25,Paris\n"
        res = client.post(
            "/api/ingest/csv",
            files={"file": ("data.csv", io.BytesIO(csv_content), "text/csv")},
        )
        assert res.status_code == 200

    def test_valid_json_returns_200(self, client):
        json_content = json.dumps([{"name": "Alice", "score": 95}]).encode()
        res = client.post(
            "/api/ingest/csv",
            files={"file": ("data.json", io.BytesIO(json_content), "application/json")},
        )
        assert res.status_code == 200

    def test_wrong_extension_returns_400(self, client):
        res = client.post(
            "/api/ingest/csv",
            files={"file": ("data.txt", io.BytesIO(b"hello"), "text/plain")},
        )
        assert res.status_code == 400
        assert "csv" in res.json()["detail"].lower()

    def test_invalid_json_returns_422(self, client):
        res = client.post(
            "/api/ingest/csv",
            files={"file": ("data.json", io.BytesIO(b"{not valid json}"), "application/json")},
        )
        assert res.status_code == 422

    def test_csv_response_shape(self, client):
        csv_content = b"col1,col2\nval1,val2\n"
        res = client.post(
            "/api/ingest/csv",
            files={"file": ("data.csv", io.BytesIO(csv_content), "text/csv")},
        )
        data = res.json()
        assert "answer" in data
        assert "validation" in data


# ── GET /api/notes ─────────────────────────────────────────────────────────────

class TestNotesEndpoint:
    def test_returns_200(self, client):
        res = client.get("/api/notes")
        assert res.status_code == 200

    def test_returns_list(self, client):
        res = client.get("/api/notes")
        assert isinstance(res.json(), list)

    def test_note_shape(self, client):
        res = client.get("/api/notes")
        notes = res.json()
        if notes:
            note = notes[0]
            assert "filename" in note
            assert "title" in note
            assert "last_updated" in note

    def test_only_md_files_returned(self, client):
        res = client.get("/api/notes")
        for note in res.json():
            assert note["filename"].endswith(".md")


# ── GET /api/notes/{filename} ─────────────────────────────────────────────────

class TestGetNoteEndpoint:
    def test_existing_note_returns_200(self, client):
        # Get any real note from the knowledge base
        notes = client.get("/api/notes").json()
        if not notes:
            pytest.skip("No notes in knowledge base")
        fname = notes[0]["filename"]
        res = client.get(f"/api/notes/{fname}")
        assert res.status_code == 200

    def test_existing_note_shape(self, client):
        notes = client.get("/api/notes").json()
        if not notes:
            pytest.skip("No notes in knowledge base")
        fname = notes[0]["filename"]
        res = client.get(f"/api/notes/{fname}")
        data = res.json()
        assert "filename" in data
        assert "content" in data

    def test_missing_note_returns_404(self, client):
        res = client.get("/api/notes/does-not-exist.md")
        assert res.status_code == 404

    def test_path_traversal_double_dot_not_served(self, client):
        # URL normalisation by the HTTP layer means this never hits our endpoint,
        # but the critical check is that no file content is returned.
        res = client.get("/api/notes/../../etc/passwd")
        assert res.status_code != 200

    def test_path_traversal_slash_not_served(self, client):
        # A slash in the filename maps to a different route entirely — 404, not 200.
        res = client.get("/api/notes/subdir/secret.md")
        assert res.status_code != 200

    def test_path_traversal_backslash_returns_400(self, client):
        # URL-encode backslash
        res = client.get("/api/notes/evil%5Cpath.md")
        assert res.status_code == 400


# ── GET /api/provider ─────────────────────────────────────────────────────────

class TestProviderEndpoint:
    def test_returns_200(self, client):
        res = client.get("/api/provider")
        assert res.status_code == 200

    def test_returns_provider_key(self, client):
        res = client.get("/api/provider")
        assert "provider" in res.json()

    def test_provider_is_string(self, client):
        res = client.get("/api/provider")
        assert isinstance(res.json()["provider"], str)
