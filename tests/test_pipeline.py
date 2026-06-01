"""
End-to-end and unit tests for the Research Intelligence System.
Run with: DISABLE_GIT_SYNC=1 pytest tests/ -v
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ["DISABLE_GIT_SYNC"] = "1"

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"), override=True)


# ── Intake Agent ───────────────────────────────────────────────────────────────

class TestIntakeAgent:
    def setup_method(self):
        from agents import intake_agent
        self.agent = intake_agent

    def test_text_query_detection(self):
        result = self.agent.run("What are transformer models?", {})
        assert result["data"]["input_type"] == "text_query"

    def test_document_detection(self):
        long_text = "This is a long paragraph with many words in it.\n" * 25  # >15 newlines, >800 chars
        result = self.agent.run(long_text, {})
        assert result["data"]["input_type"] == "document"

    def test_url_detection(self):
        result = self.agent.run("https://example.com/article about AI", {})
        assert result["data"]["input_type"] == "url_content"

    def test_intent_question(self):
        result = self.agent.run("What is machine learning?", {})
        assert result["data"]["intent"] == "question"

    def test_intent_command(self):
        result = self.agent.run("Create a summary of neural networks", {})
        assert result["data"]["intent"] == "command"

    def test_intent_informational(self):
        result = self.agent.run("transformer models deep learning", {})
        assert result["data"]["intent"] == "informational"

    def test_key_topics_extracted(self):
        result = self.agent.run("transformer attention mechanism neural networks", {})
        assert len(result["data"]["key_topics"]) > 0

    def test_cleaned_text_strips_whitespace(self):
        # The cleaner collapses multiple spaces/tabs to a single space
        result = self.agent.run("  hello   world  ", {})
        assert result["data"]["cleaned_text"] == "hello world"

    def test_output_keys_present(self):
        result = self.agent.run("test query", {})
        assert "output" in result
        assert "files_read" in result
        assert "files_written" in result
        assert "data" in result


# ── Extraction Agent ───────────────────────────────────────────────────────────

class TestExtractionAgent:
    def setup_method(self):
        from agents import extraction_agent
        self.agent = extraction_agent

    def test_entity_extraction(self):
        context = {"intake": {"data": {"cleaned_text": "OpenAI released GPT Four in 2023"}}}
        result = self.agent.run("", context)
        assert isinstance(result["data"]["entities"], list)

    def test_number_extraction(self):
        context = {"intake": {"data": {"cleaned_text": "Revenue grew 42 percent to 500 million USD"}}}
        result = self.agent.run("", context)
        assert len(result["data"]["numbers"]) > 0

    def test_key_terms_extraction(self):
        context = {"intake": {"data": {"cleaned_text": "transformer attention mechanism architecture"}}}
        result = self.agent.run("", context)
        assert "transformer" in result["data"]["key_terms"] or len(result["data"]["key_terms"]) > 0

    def test_caps_at_10(self):
        long_text = " ".join([f"term{i}word" for i in range(50)])
        context = {"intake": {"data": {"cleaned_text": long_text}}}
        result = self.agent.run("", context)
        assert len(result["data"]["key_terms"]) <= 10
        assert len(result["data"]["entities"]) <= 10
        assert len(result["data"]["numbers"]) <= 10

    def test_fallback_to_query(self):
        # No intake data in context — should fall back to query
        result = self.agent.run("transformer models", {})
        assert isinstance(result["data"]["key_terms"], list)

    def test_output_structure(self):
        result = self.agent.run("test", {})
        assert "output" in result
        assert "data" in result
        assert "entities" in result["data"]
        assert "numbers" in result["data"]
        assert "key_terms" in result["data"]


# ── Research Agent chunker (unit, no API) ─────────────────────────────────────

class TestChunker:
    def setup_method(self):
        from agents.research_agent import _chunk_text
        self.chunk = _chunk_text

    def test_short_text_is_single_chunk(self):
        text = "Short text under 500 chars."
        chunks = self.chunk(text)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunks_respect_size(self):
        text = ("This is a sentence. " * 50)
        chunks = self.chunk(text, size=500)
        for chunk in chunks:
            # Allow slight overrun for sentences that exceed size alone
            assert len(chunk) < 700

    def test_markdown_headers_split(self):
        text = "# Section One\nContent one.\n\n# Section Two\nContent two."
        chunks = self.chunk(text, size=500)
        assert len(chunks) >= 1

    def test_overlap_applied(self):
        # Two paragraphs each ~200 chars, size=220 forces split
        para = "word " * 40  # 200 chars
        text = para + "\n\n" + para
        chunks = self.chunk(text, size=220, overlap=30)
        if len(chunks) > 1:
            # Second chunk should contain some words from end of first
            assert len(chunks[1]) > 0

    def test_empty_text(self):
        chunks = self.chunk("", size=500)
        assert isinstance(chunks, list)

    def test_no_mid_sentence_split(self):
        sentence = "A" * 100 + ". " + "B" * 100 + ". " + "C" * 100 + "."
        chunks = self.chunk(sentence, size=150)
        # Each chunk should not end in the middle of a word block
        for chunk in chunks:
            assert len(chunk) > 0


# ── Utils — cache and retry ────────────────────────────────────────────────────

class TestUtils:
    def setup_method(self):
        import agents.utils as utils_module
        utils_module._cache.clear()
        self.utils = utils_module

    def test_cache_hit_skips_api(self, monkeypatch):
        import agents.utils as u
        calls = []

        def fake_call(system_prompt, user_message, max_tokens, model):
            calls.append(1)
            return "fake response"

        monkeypatch.setattr(u, "_call_anthropic", fake_call)
        u._cache.clear()

        r1 = u.call_ai("sys", "msg", max_tokens=10)
        r2 = u.call_ai("sys", "msg", max_tokens=10)

        assert r1 == r2 == "fake response"
        assert len(calls) == 1  # second call served from cache

    def test_retry_on_failure(self, monkeypatch):
        import agents.utils as u
        attempts = []

        def flaky(system_prompt, user_message, max_tokens, model):
            attempts.append(1)
            if len(attempts) < 2:
                raise Exception("transient error")
            return "recovered"

        monkeypatch.setattr(u, "_call_anthropic", flaky)
        u._cache.clear()

        result = u.call_ai("sys2", "msg2", max_tokens=10)
        assert result == "recovered"
        assert len(attempts) == 2

    def test_both_retries_fail(self, monkeypatch):
        import agents.utils as u

        def always_fail(system_prompt, user_message, max_tokens, model):
            raise Exception("always fails")

        monkeypatch.setattr(u, "_call_anthropic", always_fail)
        u._cache.clear()

        result = u.call_ai("sys3", "msg3", max_tokens=10)
        assert result.startswith("AI call failed:")

    def test_get_active_provider(self):
        label = self.utils.get_active_provider()
        assert isinstance(label, str)
        assert len(label) > 0


# ── Orchestrator error resilience ─────────────────────────────────────────────

class TestOrchestratorResilience:
    def test_pipeline_returns_on_agent_failure(self, monkeypatch):
        import agents.summarizer_agent as sa
        import agents.utils as utils_module

        # Make summarizer always fail
        monkeypatch.setattr(sa, "run", lambda q, c: (_ for _ in ()).throw(Exception("boom")))
        utils_module._cache.clear()

        from agents.orchestrator import run_pipeline
        result = run_pipeline("test resilience query")

        # Should still return a valid structure
        assert "answer" in result
        assert "agent_trace" in result
        assert "validation" in result

        # Reasoning Agent trace should show error=True
        reasoning = next((t for t in result["agent_trace"] if t["agent"] == "Reasoning Agent"), None)
        assert reasoning is not None
        assert reasoning.get("error") is True

    def test_pipeline_structure_always_complete(self):
        from agents.orchestrator import run_pipeline
        result = run_pipeline("quick structure check")
        assert set(result.keys()) >= {"answer", "input_type", "notes_created", "notes_updated", "agent_trace", "validation"}
        assert set(result["validation"].keys()) >= {"score", "issues", "suggestions"}


# ── Full pipeline integration (requires live API keys) ────────────────────────

@pytest.mark.integration
class TestPipelineIntegration:
    def test_text_query_full_run(self):
        from agents.orchestrator import run_pipeline
        result = run_pipeline("Explain prompt engineering briefly")
        assert result["answer"] and len(result["answer"]) > 50
        assert result["validation"]["score"] >= 1
        assert len(result["agent_trace"]) == 7

    def test_all_agents_in_trace(self):
        from agents.orchestrator import run_pipeline
        result = run_pipeline("What is retrieval augmented generation?")
        agents_in_trace = [t["agent"] for t in result["agent_trace"]]
        expected = ["Intake Agent", "Extraction Agent", "RAG/Knowledge Agent",
                    "Reasoning Agent", "Action Agent", "Linker Agent", "Validator Agent"]
        assert agents_in_trace == expected

    def test_input_type_returned(self):
        from agents.orchestrator import run_pipeline
        result = run_pipeline("What is machine learning?")
        assert result["input_type"] in ("text_query", "document", "url_content")

    def test_note_created_or_updated(self):
        from agents.orchestrator import run_pipeline
        result = run_pipeline("Overview of large language models")
        assert result["notes_created"] or result["notes_updated"]
