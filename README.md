# Agentic Wiki

A multi-agent AI system that answers queries, builds a local Markdown knowledge base, and links notes automatically — all through a clean web UI.

---

## How It Works

Each query triggers a pipeline of 5 specialized agents running in sequence:

| Agent | What it does |
|-------|-------------|
| **Research** | Scans existing notes for relevant content |
| **Summarizer** | Generates a structured answer via OpenAI |
| **Writer** | Creates or updates a `.md` note in `/knowledge/` |
| **Linker** | Adds `[[wiki-links]]` between related notes, updates index |
| **Validator** | Scores the output quality (1–10) and flags issues |

Results are returned as structured JSON and rendered in the UI with a collapsible agent trace.

---

## Setup

**Requirements:** Python 3.11+, an OpenAI API key.

```bash
# 1. Clone the repo
git clone https://github.com/Kadyan25/agentic-wiki.git
cd agentic-wiki

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your API key
cp .env.example .env
# Open .env and add: OPENAI_API_KEY=your_key_here

# 4. Run
uvicorn main:app --reload
```

Open `http://localhost:8000` in your browser.

---

## Usage

1. Type any question in the input field and press **Ask** or hit Enter
2. The agents process your query (~5–15 seconds)
3. You'll see:
   - **Answer card** — structured markdown response
   - **Quality score** — 1–10 badge from the validator
   - **Agent trace** — collapsible log of what each agent did
   - **Notes panel** — all knowledge base files, clickable to view raw markdown

New `.md` files are created in `/knowledge/` automatically and persist between sessions.

---

## Project Structure

```
├── main.py                  # FastAPI app, 3 API endpoints
├── agents/
│   ├── orchestrator.py      # Runs all agents in sequence
│   ├── research_agent.py    # Scans /knowledge/ for relevant notes
│   ├── summarizer_agent.py  # Structured summary via OpenAI
│   ├── writer_agent.py      # Creates/updates .md files
│   ├── linker_agent.py      # Injects [[links]], updates _index.md
│   ├── validator_agent.py   # Scores output quality
│   └── utils.py             # Shared OpenAI client
├── knowledge/               # All notes live here (git-tracked)
│   └── _index.md            # Auto-maintained index
├── static/
│   └── index.html           # Full frontend (single file, no framework)
├── requirements.txt
└── render.yaml              # Render deployment config
```

---

## API

```
POST /api/query
  Body:    { "query": "string" }
  Returns: { "answer", "notes_created", "notes_updated", "agent_trace", "validation" }

GET  /api/notes
  Returns: list of all notes with title and last_updated date

GET  /api/notes/{filename}
  Returns: raw markdown content of a single note
```

---

## Deploy to Render

1. Push to GitHub
2. Create a new **Web Service** on [render.com](https://render.com), connect the repo
3. Set environment variable: `OPENAI_API_KEY=your_key_here`
4. Render uses `render.yaml` automatically — no extra config needed

---

## Tech Stack

- **Backend:** Python 3.11, FastAPI, Uvicorn
- **AI:** OpenAI `gpt-4o` via the OpenAI SDK
- **Storage:** Local Markdown files (no database)
- **Frontend:** Vanilla HTML/CSS/JS, dark theme, no frameworks
