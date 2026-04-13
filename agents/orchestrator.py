from . import research_agent, summarizer_agent, writer_agent, linker_agent, validator_agent


def run_pipeline(query: str) -> dict:
    context = {}
    agent_trace = []
    notes_created = []
    notes_updated = []

    # 1. Research
    research_out = research_agent.run(query, context)
    context["research"] = research_out
    agent_trace.append({
        "agent": "Research Agent",
        "action": f"Scanned knowledge base. Found {len(research_out['files_read'])} relevant note(s). "
                  f"Gaps identified: {research_out.get('gaps', [])}",
        "files_read": research_out["files_read"],
        "files_written": [],
    })

    # 2. Summarizer
    summarizer_out = summarizer_agent.run(query, context)
    context["summarizer"] = summarizer_out
    agent_trace.append({
        "agent": "Summarizer Agent",
        "action": "Generated structured summary via OpenAI API.",
        "files_read": [],
        "files_written": [],
    })

    # 3. Writer
    writer_out = writer_agent.run(query, context)
    context["writer"] = writer_out
    fname = writer_out.get("filename", "")
    agent_trace.append({
        "agent": "Writer Agent",
        "action": writer_out["output"],
        "files_read": [],
        "files_written": writer_out["files_written"],
    })
    if fname:
        # Determine if created or updated based on research findings
        if fname in research_out["files_read"]:
            notes_updated.append(fname)
        else:
            notes_created.append(fname)

    # 4. Linker
    linker_out = linker_agent.run(query, context)
    context["linker"] = linker_out
    agent_trace.append({
        "agent": "Linker Agent",
        "action": linker_out["output"],
        "files_read": [],
        "files_written": linker_out["files_written"],
    })

    # 5. Validator
    validator_out = validator_agent.run(query, context)
    context["validator"] = validator_out
    agent_trace.append({
        "agent": "Validator Agent",
        "action": validator_out["output"],
        "files_read": validator_out["files_read"],
        "files_written": [],
    })

    return {
        "answer": summarizer_out["output"],
        "notes_created": notes_created,
        "notes_updated": notes_updated,
        "agent_trace": agent_trace,
        "validation": {
            "score": validator_out["score"],
            "issues": validator_out["issues"],
            "suggestions": validator_out["suggestions"],
        },
    }
