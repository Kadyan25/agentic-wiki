# CLAUDE.md — Mini Agentic AI System (Karpathy-style Wiki)

## Project Goal
Build a working multi-agent AI system where a master orchestrator delegates to 3–5 specialized agents. Agents read/write local Markdown files as a compiled knowledge base. Simple UI for query input and structured output.

**Time budget: 3–4 hours. Ship working code. No over-engineering.**

---

## Architecture

```
User Query (via UI)
    ↓
Master Orchestrator
    ├── Research Agent     → reads existing .md files, identifies gaps
    ├── Summarizer Agent   → condenses & structures findings
    ├── Writer Agent       → creates or updates .md notes
    ├── Linker Agent       → adds [[wiki-links]] between related notes
    └── Validator Agent    → checks output quality & completeness
    ↓
Structured JSON response → rendered in UI
+ Markdown files created/updated in /knowledge/
```

---

## Tech Stack
- **Backend**: Python 3.11+ with FastAPI
- **AI**: Anthropic Claude API (`claude-sonnet-4-20250514`) via `anthropic` SDK
- **Storage**: Local `.md` files in `/knowledge/` folder (NO database, NO vector DB)
- **Frontend**: Single `index.html` — vanilla HTML/CSS/JS, no framework
- **Deploy**: Render (free tier) — include `render.yaml`

---

## Folder Structure to Create

```
project-root/
├── CLAUDE.md                  ← this file
├── main.py                    ← FastAPI app entry point
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py        ← master agent, calls all sub-agents in sequence
│   ├── research_agent.py      ← reads /knowledge/ files, finds relevant content
│   ├── summarizer_agent.py    ← summarizes & structures findings
│   ├── writer_agent.py        ← creates/updates .md files in /knowledge/
│   ├── linker_agent.py        ← adds [[Topic]] links between notes
│   └── validator_agent.py     ← validates output quality, flags gaps
├── knowledge/                 ← all .md files live here (git-tracked)
│   └── _index.md              ← auto-maintained index of all notes
├── static/
│   └── index.html             ← entire frontend (single file)
├── requirements.txt
├── render.yaml
└── .env.example
```

---

## Agent Contracts

Each agent is a Python function with this signature:
```python
def run(query: str, context: dict) -> dict:
    # context contains: existing_notes, previous_agent_outputs
    # returns: {"output": str, "files_read": [], "files_written": []}
```

### Agent Responsibilities

**1. Research Agent**
- Scans all `.md` files in `/knowledge/`
- Finds files relevant to the query (simple keyword/title match is fine)
- Returns: relevant file contents + list of gaps (topics not yet in knowledge base)

**2. Summarizer Agent**
- Takes research output
- Calls Claude API to produce a structured summary with key facts, subtopics
- Returns: structured summary as markdown text

**3. Writer Agent**
- Takes summarizer output
- Creates or updates a `.md` file in `/knowledge/` named after the topic
- File format (strict):
```markdown
# Topic Title

**Created**: YYYY-MM-DD  
**Updated**: YYYY-MM-DD  
**Tags**: tag1, tag2

## Summary
...

## Key Points
- ...

## Related Topics
[[Topic A]], [[Topic B]]
```

**4. Linker Agent**
- Scans all `.md` files for topic names
- Adds `[[TopicName]]` links where topics are mentioned but not yet linked
- Updates `_index.md` with the new/updated note

**5. Validator Agent**
- Checks: Does the written note actually answer the original query?
- Checks: Are there broken `[[links]]` pointing to non-existent notes?
- Returns: quality score (1–10), issues list, suggestions

---

## API Endpoints

```
POST /api/query
  Body: { "query": "string", "max_depth": 1 }
  Returns: {
    "answer": "string",
    "notes_created": ["filename.md"],
    "notes_updated": ["filename.md"],
    "agent_trace": [...],
    "validation": { "score": 8, "issues": [] }
  }

GET /api/notes
  Returns: list of all .md files with title + last_updated

GET /api/notes/{filename}
  Returns: raw markdown content of a single note
```

---

## Frontend (index.html) Requirements
- Single input field: "Ask anything..."
- Submit button → POST to `/api/query`
- Show: final answer in a readable card
- Show: agent trace (collapsible) — which agents ran, what they did
- Show: list of notes created/updated (clickable to view raw markdown)
- Show: validation score badge
- Style: clean, minimal, dark or light — **no frameworks, pure CSS**
- Must look polished — this is a UI skills demo too

---

## Sample Knowledge Files to Pre-populate
Create these 3 starter `.md` files in `/knowledge/` before first run so agents have something to work with:

1. `artificial-intelligence.md` — brief overview of AI
2. `large-language-models.md` — what LLMs are, how they work
3. `agentic-systems.md` — what agent-based AI systems are

---

## Claude API Usage Pattern
All agents use the same client. Keep it simple:

```python
import anthropic
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

def call_claude(system_prompt: str, user_message: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text
```

---

## Environment Variables
```
ANTHROPIC_API_KEY=your_key_here
```

`.env.example`:
```
ANTHROPIC_API_KEY=
```

---

## requirements.txt
```
fastapi==0.104.1
uvicorn==0.24.0
anthropic>=0.25.0
python-dotenv==1.0.0
```

---

## render.yaml
```yaml
services:
  - type: web
    name: agentic-wiki
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: ANTHROPIC_API_KEY
        sync: false
```

---

## Implementation Order (follow strictly)
1. `main.py` — FastAPI skeleton with 3 endpoints, CORS enabled
2. `agents/research_agent.py` — file reading logic first (no API needed)
3. `agents/writer_agent.py` — file writing logic (no API needed)
4. `agents/summarizer_agent.py` — first agent to call Claude API
5. `agents/linker_agent.py` — string matching on existing notes
6. `agents/validator_agent.py` — simple Claude call to score output
7. `agents/orchestrator.py` — wires all agents, builds agent_trace
8. `static/index.html` — full frontend last
9. Pre-populate `/knowledge/` with 3 sample `.md` files
10. Test end-to-end with query: "What are transformer models?"
11. `render.yaml` + push to GitHub + deploy

---

## Quality Bar
- [ ] Query returns a real answer (not placeholder text)
- [ ] At least one `.md` file is created in `/knowledge/` per new query
- [ ] `[[wiki-links]]` appear in written notes
- [ ] `_index.md` stays updated
- [ ] UI shows agent trace (proves it's actually agentic)
- [ ] Validation score displayed
- [ ] Works on Render without modification
- [ ] GitHub README has: description, setup steps, screenshot

---

## DO NOT
- Use LangChain, LlamaIndex, or any agent framework — build agents as plain Python functions
- Use a vector database — Markdown files only
- Over-engineer — if a feature takes >30 min, simplify it
- Leave placeholder/mock responses — everything must actually call the API and write real files
