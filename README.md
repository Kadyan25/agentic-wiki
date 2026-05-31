# Agentic Wiki

A multi-agent AI system that answers queries, builds a local Markdown knowledge base, and links notes automatically — all through a clean web UI. Supports text queries, PDF uploads, and URL scraping as input.

---

## Business Use Case: Research Intelligence System

Analysts and founders use this to process documents, URLs, and ad-hoc text queries into a connected, searchable knowledge base — without manual note-taking.

**Example workflows:**
- Upload a competitor's whitepaper (PDF) → agents extract, summarize, and file it
- Paste an article URL → agents scrape, distill, and link it to related notes
- Ask a question → agents search existing knowledge, fill gaps, and update the base

Over time the knowledge base becomes a living, cross-linked wiki that reflects everything you've fed it.

---

## Architecture

```
User Input
  │
  ├── Text Query  ─────────────────────────────────────────────┐
  │                                                            │
  ├── PDF Upload  ── PyMuPDF (open source) ──► text ───────────┤
  │                                                            │
  └── URL Scrape ── requests + BeautifulSoup (OSS) ──► text ───┤
                                                               │
                                                               ▼
                                               ┌──────────────────────┐
                                               │   0. Intake Agent    │
                                               │   (rule-based, OSS)  │
                                               │ detect type, clean,  │
                                               │ extract topics/intent│
                                               └──────────┬───────────┘
                                                          │
                                               ┌──────────▼───────────┐
                                               │ 1. RAG/Knowledge Agent│
                                               │   (open source)      │
                                               │  keyword search in   │
                                               │    /knowledge/       │
                                               └──────────┬───────────┘
                                                          │
                                               ┌──────────▼───────────┐
                                               │  2. Reasoning Agent  │
                                               │   (OpenAI API)       │
                                               │ structured summary   │
                                               └──────────┬───────────┘
                                                          │
                                               ┌──────────▼───────────┐
                                               │   3. Action Agent    │
                                               │   (OpenAI API)       │
                                               │ create/update .md    │
                                               └──────────┬───────────┘
                                                          │
                                    ┌─────────────────────┴─────────────────────┐
                                    │                                           │
                         ┌──────────▼───────────┐               ┌──────────────▼──────────┐
                         │   4. Linker Agent    │               │   5. Validator Agent    │
                         │   (open source)      │               │     (OpenAI API)        │
                         │ [[wiki-links]] +     │               │  score 1–10 + issues    │
                         │  _index.md regen     │               └─────────────────────────┘
                         └──────────────────────┘
                                    │
                         ┌──────────▼───────────┐
                         │     Git Sync         │
                         │   (open source)      │
                         │   commit + push      │
                         └──────────────────────┘
```

---

## Open Source vs API Split

| Component | Technology | Type | Cost |
|-----------|-----------|------|------|
| PDF text extraction | PyMuPDF (`fitz`) | Open source | Free |
| Web scraping | `requests` + `BeautifulSoup4` | Open source | Free |
| Intake (detect, clean, classify) | Python (regex) | Open source | Free |
| Knowledge base search | Python (keyword match) | Open source | Free |
| Wiki-link injection | Python (regex) | Open source | Free |
| Git sync | subprocess / git CLI | Open source | Free |
| Answer generation | OpenAI `gpt-4o-mini` | API | Per token |
| Note metadata extraction | OpenAI `gpt-4o-mini` | API | Per token |
| Note merge on update | OpenAI `gpt-4o-mini` | API | Per token |
| Quality validation | OpenAI `gpt-4o-mini` | API | Per token |

---

## Efficiency Strategy

- **Open source for all extraction** — PDF parsing, URL scraping, intake classification, and wiki-linking run locally with zero token cost.
- **Structured JSON output on all LLM calls** — every agent's system prompt instructs the model to respond in structured format, reducing verbose prose and cutting token usage.
- **Smaller model for all tasks** — `gpt-4o-mini` handles summarization, writing, and validation; no GPT-4o or GPT-4 calls unless the task warrants it.
- **Validator catches errors before output reaches user** — the validator agent scores every response 1–10 and surfaces issues; if score is below 5, the UI flags it visually so the user knows the output may be low quality.
- **4000-character input cap** — PDF and URL content is truncated before entering the pipeline to prevent runaway token usage.

---

## How It Works

Each query triggers a pipeline of 6 specialized agents running in sequence:

| Step | Agent | Role | LLM? |
|------|-------|------|------|
| 0 | **Intake Agent** | Detect input type, clean text, extract topics and intent | No |
| 1 | **RAG/Knowledge Agent** | Scan existing notes for relevant content | No |
| 2 | **Reasoning Agent** | Generate a structured answer | Yes |
| 3 | **Action Agent** | Create or update a `.md` note | Yes |
| 4 | **Linker Agent** | Add `[[wiki-links]]`, regenerate index | No |
| 5 | **Validator Agent** | Score output quality 1–10, flag issues | Yes |

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

1. **Text query** — type any question and press **Ask** or hit Enter
2. **URL ingest** — paste a URL and press **Ingest URL**; the page is scraped and fed into the pipeline
3. **PDF ingest** — choose a PDF file and press **Ingest PDF**; text is extracted and fed into the pipeline

All three inputs produce the same output:
- **Answer card** — structured markdown response with input-type badge
- **Quality score** — 1–10 badge (green ≥ 8, yellow ≥ 5, red < 5)
- **Agent trace** — collapsible log of all 6 agents
- **Notes panel** — all knowledge base files, clickable to view raw markdown

---

## API

```
POST /api/query
  Body:    { "query": "string" }
  Returns: { "answer", "input_type", "notes_created", "notes_updated", "agent_trace", "validation" }

POST /api/ingest/pdf
  Body:    multipart/form-data, field "file" (.pdf only)
  Returns: same shape as /api/query

POST /api/ingest/url
  Body:    { "url": "https://..." }
  Returns: same shape as /api/query

GET  /api/notes
  Returns: list of all notes with title and last_updated date

GET  /api/notes/{filename}
  Returns: raw markdown content of a single note
```

---

## Token / Cost Tradeoffs

| Decision | Tradeoff |
|----------|----------|
| `gpt-4o-mini` for all agents | Lower cost + lower latency vs. higher reasoning quality of GPT-4o |
| 4000-char input cap | Prevents runaway costs on large PDFs/pages; may truncate useful content |
| Structured JSON prompt instruction | Reduces token waste on prose; may occasionally conflict with specific format instructions (TITLE:, SCORE:) |
| 3 LLM calls per query (summarize + write + validate) | Predictable cost; could collapse to 1 call but loses agent separation |
| Validator as separate LLM call | Adds ~150 tokens per query but catches quality issues before they reach the user |

Typical query cost: ~1500–2500 tokens total across all three LLM calls (~$0.001 at gpt-4o-mini pricing).

---

## Known Limitations

- **No concurrent write safety** — simultaneous requests can corrupt a knowledge file; designed for single-user / demo use.
- **4000-char input cap** — PDF and URL content is truncated; long documents lose tail content.
- **Text-only PDFs** — scanned/image PDFs have no extractable text and return an error.
- **No rate limiting** — any client can spam the API; add a reverse proxy for production.
- **Git sync is silent** — sync failures are logged server-side but not surfaced in the UI.
- **Slug collisions** — two notes whose titles reduce to the same slug overwrite each other.
- **Structured JSON instruction conflicts** — agents that use line-prefix parsing (TITLE:, SCORE:) may occasionally produce malformed output if the model prioritises the JSON instruction over the format spec; defaults apply as fallback.

---

## Project Structure

```
├── main.py                  # FastAPI app — 5 API endpoints
├── agents/
│   ├── orchestrator.py      # Runs all 6 agents in sequence
│   ├── intake_agent.py      # Detect type, clean, classify (no LLM)
│   ├── research_agent.py    # RAG/Knowledge Agent — keyword search
│   ├── summarizer_agent.py  # Reasoning Agent — summary via OpenAI
│   ├── writer_agent.py      # Action Agent — creates/updates .md files
│   ├── linker_agent.py      # Injects [[links]], updates _index.md
│   ├── validator_agent.py   # Scores output quality
│   └── utils.py             # Shared OpenAI client (gpt-4o-mini)
├── knowledge/               # All notes live here
│   └── _index.md            # Auto-maintained index
├── static/
│   └── index.html           # Full frontend (single file, no framework)
├── requirements.txt
└── render.yaml              # Render deployment config
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
- **AI:** OpenAI `gpt-4o-mini` via the OpenAI SDK
- **PDF parsing:** PyMuPDF
- **Web scraping:** requests + BeautifulSoup4
- **Storage:** Local Markdown files (no database)
- **Frontend:** Vanilla HTML/CSS/JS, dark theme, no frameworks
