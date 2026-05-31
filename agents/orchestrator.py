from . import intake_agent, research_agent, summarizer_agent, writer_agent, linker_agent, validator_agent
from . import git_sync


def run_pipeline(query: str) -> dict:
    context = {}
    agent_trace = []
    notes_created = []
    notes_updated = []

    # 0. Intake
    intake_out = intake_agent.run(query, context)
    context["intake"] = intake_out
    intake_data = intake_out["data"]
    agent_trace.append({
        "agent": "Intake Agent",
        "action": intake_out["output"],
        "files_read": [],
        "files_written": [],
    })

    # 1. RAG / Knowledge Agent
    research_out = research_agent.run(query, context)
    context["research"] = research_out
    agent_trace.append({
        "agent": "RAG/Knowledge Agent",
        "action": f"Scanned knowledge base. Found {len(research_out['files_read'])} relevant note(s). "
                  f"Gaps identified: {research_out.get('gaps', [])}",
        "files_read": research_out["files_read"],
        "files_written": [],
    })

    # 2. Reasoning Agent
    summarizer_out = summarizer_agent.run(query, context)
    context["summarizer"] = summarizer_out
    agent_trace.append({
        "agent": "Reasoning Agent",
        "action": "Generated structured summary via OpenAI API.",
        "files_read": [],
        "files_written": [],
    })

    # 3. Action Agent
    writer_out = writer_agent.run(query, context)
    context["writer"] = writer_out
    fname = writer_out.get("filename", "")
    agent_trace.append({
        "agent": "Action Agent",
        "action": writer_out["output"],
        "files_read": [],
        "files_written": writer_out["files_written"],
    })
    if fname:
        if fname in research_out["files_read"]:
            notes_updated.append(fname)
        else:
            notes_created.append(fname)

    # 4. Linker Agent
    linker_out = linker_agent.run(query, context)
    context["linker"] = linker_out
    agent_trace.append({
        "agent": "Linker Agent",
        "action": linker_out["output"],
        "files_read": [],
        "files_written": linker_out["files_written"],
    })

    # 5. Validator Agent
    validator_out = validator_agent.run(query, context)
    context["validator"] = validator_out
    agent_trace.append({
        "agent": "Validator Agent",
        "action": validator_out["output"],
        "files_read": validator_out["files_read"],
        "files_written": [],
    })

    git_sync.sync(query)

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
