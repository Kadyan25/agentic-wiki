import json
from . import intake_agent, extraction_agent, research_agent, summarizer_agent, writer_agent, linker_agent, validator_agent
from . import git_sync


def _safe_run(agent_name: str, fn, *args, **kwargs):
    """Run an agent function and return (output, error). Never raises."""
    try:
        return fn(*args, **kwargs), None
    except Exception as e:
        return None, f"{agent_name} failed: {e}"


def _run_pre_summarizer(query: str) -> tuple[dict, list, dict]:
    """Run intake → extraction → RAG. Returns (context, agent_trace, intake_data)."""
    context = {}
    agent_trace = []

    # Intake
    intake_out, err = _safe_run("Intake Agent", intake_agent.run, query, context)
    if err or intake_out is None:
        intake_out = {
            "output": err or "Intake failed.",
            "files_read": [], "files_written": [],
            "data": {"input_type": "text_query", "cleaned_text": query, "key_topics": [], "intent": "informational"},
        }
        agent_trace.append({"agent": "Intake Agent", "action": intake_out["output"], "files_read": [], "files_written": [], "error": True})
    else:
        context["intake"] = intake_out
        agent_trace.append({"agent": "Intake Agent", "action": intake_out["output"], "files_read": [], "files_written": []})

    intake_data = intake_out["data"]

    # Extraction
    extraction_out, err = _safe_run("Extraction Agent", extraction_agent.run, query, context)
    if err or extraction_out is None:
        extraction_out = {"output": err or "Extraction failed.", "files_read": [], "files_written": [], "data": {}}
        agent_trace.append({"agent": "Extraction Agent", "action": extraction_out["output"], "files_read": [], "files_written": [], "error": True})
    else:
        context["extraction"] = extraction_out
        agent_trace.append({"agent": "Extraction Agent", "action": extraction_out["output"], "files_read": [], "files_written": []})

    # RAG
    research_out, err = _safe_run("RAG/Knowledge Agent", research_agent.run, query, context)
    if err or research_out is None:
        research_out = {"output": err or "Research failed.", "files_read": [], "gaps": []}
        agent_trace.append({"agent": "RAG/Knowledge Agent", "action": research_out["output"], "files_read": [], "files_written": [], "error": True})
    else:
        context["research"] = research_out
        agent_trace.append({
            "agent": "RAG/Knowledge Agent",
            "action": f"Scanned knowledge base. Found {len(research_out['files_read'])} relevant note(s). "
                      f"Gaps identified: {research_out.get('gaps', [])}",
            "files_read": research_out["files_read"],
            "files_written": [],
        })

    return context, agent_trace, intake_data


def _run_post_summarizer(query: str, context: dict, agent_trace: list, intake_data: dict) -> dict:
    """Run writer → linker → validator (with retry). Returns final result dict."""
    notes_created = []
    notes_updated = []
    summarizer_out = context.get("summarizer", {"output": "", "files_read": [], "files_written": []})
    research_out = context.get("research", {"files_read": [], "gaps": []})

    # Writer
    writer_out, err = _safe_run("Action Agent", writer_agent.run, query, context)
    if err or writer_out is None:
        writer_out = {"output": err or "Writer failed.", "files_read": [], "files_written": [], "filename": ""}
        agent_trace.append({"agent": "Action Agent", "action": writer_out["output"], "files_read": [], "files_written": [], "error": True})
    else:
        context["writer"] = writer_out
        fname = writer_out.get("filename", "")
        agent_trace.append({"agent": "Action Agent", "action": writer_out["output"], "files_read": [], "files_written": writer_out["files_written"]})
        if fname:
            if fname in research_out["files_read"]:
                notes_updated.append(fname)
            else:
                notes_created.append(fname)

    # Linker
    linker_out, err = _safe_run("Linker Agent", linker_agent.run, query, context)
    if err or linker_out is None:
        linker_out = {"output": err or "Linker failed.", "files_read": [], "files_written": []}
        agent_trace.append({"agent": "Linker Agent", "action": linker_out["output"], "files_read": [], "files_written": [], "error": True})
    else:
        context["linker"] = linker_out
        agent_trace.append({"agent": "Linker Agent", "action": linker_out["output"], "files_read": [], "files_written": linker_out["files_written"]})

    # Validator — with one retry if score < 6
    validator_out, err = _safe_run("Validator Agent", validator_agent.run, query, context)
    if err or validator_out is None:
        validator_out = {"output": err or "Validator failed.", "files_read": [], "score": 0, "issues": ["Validation failed"], "suggestions": []}
        agent_trace.append({"agent": "Validator Agent", "action": validator_out["output"], "files_read": [], "files_written": [], "error": True})
    else:
        context["validator"] = validator_out
        agent_trace.append({"agent": "Validator Agent", "action": validator_out["output"], "files_read": validator_out["files_read"], "files_written": []})

        # Retry: if score < 6, re-run summarizer with issues as feedback then re-validate
        if validator_out["score"] < 6 and validator_out["issues"]:
            issues_text = "; ".join(validator_out["issues"])
            feedback_context = dict(context)
            feedback_context["validator_feedback"] = issues_text

            # Inject feedback into research output so summarizer sees it
            original_research = context.get("research", {}).get("output", "")
            feedback_context["research"] = {
                **context.get("research", {}),
                "output": f"{original_research}\n\n[Validator feedback: {issues_text}]",
            }

            retry_out, retry_err = _safe_run("Reasoning Agent (retry)", summarizer_agent.run, query, feedback_context)
            if retry_out and not retry_err:
                # Only accept retry if it's not worse
                context["summarizer"] = retry_out
                summarizer_out = retry_out

                # Re-validate the retry
                retry_val, _ = _safe_run("Validator Agent (retry)", validator_agent.run, query, context)
                if retry_val and retry_val["score"] >= validator_out["score"]:
                    validator_out = retry_val
                    agent_trace.append({"agent": "Validator Agent (retry)", "action": f"Retry score: {retry_val['score']}/10", "files_read": [], "files_written": []})

    try:
        git_sync.sync(query)
    except Exception:
        pass

    return {
        "answer": summarizer_out["output"],
        "input_type": intake_data["input_type"],
        "notes_created": notes_created,
        "notes_updated": notes_updated,
        "agent_trace": agent_trace,
        "validation": {
            "score": validator_out["score"],
            "issues": validator_out["issues"],
            "suggestions": validator_out["suggestions"],
        },
    }


def run_pipeline(query: str) -> dict:
    """Synchronous pipeline — used by ingest endpoints."""
    context, agent_trace, intake_data = _run_pre_summarizer(query)

    # Summarizer (synchronous)
    summarizer_out, err = _safe_run("Reasoning Agent", summarizer_agent.run, query, context)
    if err or summarizer_out is None:
        summarizer_out = {"output": "Could not generate a summary.", "files_read": [], "files_written": []}
        agent_trace.append({"agent": "Reasoning Agent", "action": err or "Summarizer failed.", "files_read": [], "files_written": [], "error": True})
    else:
        context["summarizer"] = summarizer_out
        agent_trace.append({"agent": "Reasoning Agent", "action": "Generated structured summary.", "files_read": [], "files_written": []})

    return _run_post_summarizer(query, context, agent_trace, intake_data)


def run_pipeline_streaming(query: str):
    """
    Generator for streaming responses.
    Yields JSON-encoded SSE data strings.

    Event types:
      {"type": "agent", "name": "..."}          — agent started
      {"type": "token", "text": "..."}           — summarizer token
      {"type": "done",  ...full result fields}   — pipeline complete
      {"type": "error", "message": "..."}        — unrecoverable error
    """
    def _event(payload: dict) -> str:
        return f"data: {json.dumps(payload)}\n\n"

    try:
        # Pre-summarizer agents
        for name in ["Intake Agent", "Extraction Agent", "RAG/Knowledge Agent"]:
            yield _event({"type": "agent", "name": name})

        context, agent_trace, intake_data = _run_pre_summarizer(query)

        # Stream summarizer tokens
        yield _event({"type": "agent", "name": "Reasoning Agent"})
        full_answer = ""
        try:
            for chunk in summarizer_agent.stream(query, context):
                full_answer += chunk
                yield _event({"type": "token", "text": chunk})
        except Exception as e:
            # Streaming failed — fall back to synchronous call
            summarizer_out = summarizer_agent.run(query, context)
            full_answer = summarizer_out["output"]
            for word in full_answer.split(" "):
                yield _event({"type": "token", "text": word + " "})

        context["summarizer"] = {"output": full_answer, "files_read": [], "files_written": []}
        agent_trace.append({"agent": "Reasoning Agent", "action": "Generated structured summary.", "files_read": [], "files_written": []})

        # Post-summarizer agents
        for name in ["Action Agent", "Linker Agent", "Validator Agent"]:
            yield _event({"type": "agent", "name": name})

        result = _run_post_summarizer(query, context, agent_trace, intake_data)
        # Override answer with the streamed version (already complete)
        result["answer"] = full_answer

        yield _event({"type": "done", **result})

    except Exception as e:
        yield _event({"type": "error", "message": str(e)})
