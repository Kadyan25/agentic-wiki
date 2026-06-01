from . import intake_agent, extraction_agent, research_agent, summarizer_agent, writer_agent, linker_agent, validator_agent
from . import git_sync


def _safe_run(agent_name: str, fn, *args, **kwargs):
    """Run an agent function and return (output, error). Never raises."""
    try:
        return fn(*args, **kwargs), None
    except Exception as e:
        return None, f"{agent_name} failed: {e}"


def run_pipeline(query: str) -> dict:
    context = {}
    agent_trace = []
    notes_created = []
    notes_updated = []

    # 0. Intake
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

    # 1. Extraction Agent
    extraction_out, err = _safe_run("Extraction Agent", extraction_agent.run, query, context)
    if err or extraction_out is None:
        extraction_out = {"output": err or "Extraction failed.", "files_read": [], "files_written": [], "data": {}}
        agent_trace.append({"agent": "Extraction Agent", "action": extraction_out["output"], "files_read": [], "files_written": [], "error": True})
    else:
        context["extraction"] = extraction_out
        agent_trace.append({"agent": "Extraction Agent", "action": extraction_out["output"], "files_read": [], "files_written": []})

    # 2. RAG / Knowledge Agent
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

    # 2. Reasoning Agent
    summarizer_out, err = _safe_run("Reasoning Agent", summarizer_agent.run, query, context)
    if err or summarizer_out is None:
        summarizer_out = {"output": "Could not generate a summary.", "files_read": [], "files_written": []}
        agent_trace.append({"agent": "Reasoning Agent", "action": err or "Summarizer failed.", "files_read": [], "files_written": [], "error": True})
    else:
        context["summarizer"] = summarizer_out
        agent_trace.append({"agent": "Reasoning Agent", "action": "Generated structured summary.", "files_read": [], "files_written": []})

    # 3. Action Agent
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

    # 4. Linker Agent
    linker_out, err = _safe_run("Linker Agent", linker_agent.run, query, context)
    if err or linker_out is None:
        linker_out = {"output": err or "Linker failed.", "files_read": [], "files_written": []}
        agent_trace.append({"agent": "Linker Agent", "action": linker_out["output"], "files_read": [], "files_written": [], "error": True})
    else:
        context["linker"] = linker_out
        agent_trace.append({"agent": "Linker Agent", "action": linker_out["output"], "files_read": [], "files_written": linker_out["files_written"]})

    # 5. Validator Agent
    validator_out, err = _safe_run("Validator Agent", validator_agent.run, query, context)
    if err or validator_out is None:
        validator_out = {"output": err or "Validator failed.", "files_read": [], "score": 0, "issues": ["Validation failed"], "suggestions": []}
        agent_trace.append({"agent": "Validator Agent", "action": validator_out["output"], "files_read": [], "files_written": [], "error": True})
    else:
        context["validator"] = validator_out
        agent_trace.append({"agent": "Validator Agent", "action": validator_out["output"], "files_read": validator_out["files_read"], "files_written": []})

    try:
        git_sync.sync(query)
    except Exception:
        pass  # sync failures are non-fatal

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
