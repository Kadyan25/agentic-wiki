# Research Intelligence System

A multimodal, multi-agent AI pipeline that turns any input — text, PDF, image, URL, or CSV — into structured knowledge. Seven specialised agents handle intake, extraction, semantic search, reasoning, writing, linking, and validation in sequence. The result is a growing, cross-linked markdown knowledge base with a clean dark-theme web UI.

**Live demo:** _deploy to Render and add URL here_
**GitHub:** https://github.com/Kadyan25/agentic-wiki

---

## Business Use Case

Built for analysts, founders, and researchers who need to process documents and sources into a connected knowledge base without manual note-taking.

**Example workflows:**
- Upload a competitor's whitepaper (PDF) → agents extract, summarise, and file it as a linked note
- Paste an article URL → agents scrape, distil key facts, and connect it to related existing notes
- Drop in a CSV market dataset → agents summarise structure, extract key figures, build a note
- Upload a screenshot or diagram (image) → Claude vision reads it, pipeline writes a note
- Ask a research question → agents search existing knowledge via semantic RAG, fill gaps, update the base

Over time the knowledge base becomes a living, cross-linked wiki that reflects everything you've fed it.

---

## Architecture

See the interactive diagram: [architecture.html](/architecture.html)

```
Multimodal Input
  │
  ├── Text Query     ──────────────────────────────────────────────┐
  ├── PDF Upload     ── PyMuPDF (OSS) ──► text ────────────────────┤
  ├── URL Scrape     ── requests + BeautifulSoup (OSS) ──► text ───┤
  ├── Image Upload   ── Claude Vision API ──► text ────────────────┤
  └── CSV / JSON     ── Python stdlib (OSS) ──► structured text ───┤
                                                                   ▼
                                               ┌───────────────────────────┐
                                               │   1. Intake Agent  [OSS]  │
                                               │  detect type · clean text │
                                               │  extract topics · intent  │
                                               └──────────────┬────────────┘
                                                              │
                                               ┌──────────────▼────────────┐
                                               │ 2. Extraction Agent [OSS] │
                                               │  named entities · numbers │
                                               │  key terms (regex-based)  │
                                               └──────────────┬────────────┘
                                                              │
                                               ┌──────────────▼────────────┐
                                               │  3. RAG/Knowledge Agent   │
                                               │  [Google Embeddings OSS]  │
                                               │  semantic search · top-5  │
                                               │  cosine similarity ≥ 0.35 │
                                               └──────────────┬────────────┘
                                                              │
                                               ┌──────────────▼────────────┐
                                               │  4. Reasoning Agent [LLM] │
                                               │  claude-sonnet-4-6        │
                                               │  grounded markdown summary│
                                               │  streamed token by token  │
                                               └──────────────┬────────────┘
                                                              │
                                               ┌──────────────▼────────────┐
                                               │   5. Action Agent  [LLM]  │
                                               │   claude-haiku-4-5        │
                                               │   create / merge .md note │
                                               └──────────────┬────────────┘
                                                              │
                                               ┌──────────────▼────────────┐
                                               │   6. Linker Agent  [OSS]  │
                                               │   [[wiki-links]] inject   │
                                               │   _index.md regenerated   │
                                               └──────────────┬────────────┘
                                                              │
                                               ┌──────────────▼────────────┐
                                               │  7. Validator Agent [LLM] │
                                               │   claude-haiku-4-5        │
                                               │   score 1–10 · issues     │
                                               │   retry if score < 6      │
                                               └───────────────────────────┘
```

---

## Code vs LLM Calls

| Agent | Type | Why |
|---|---|---|
| Intake Agent | Pure code (regex) | Type detection and text cleaning are deterministic rules — no reasoning needed |
| Extraction Agent | Pure code (regex) | Entity and number extraction via pattern matching — zero token cost |
| RAG/Knowledge Agent | OSS API (Google Embeddings) | Semantic similarity requires embeddings; Google `gemini-embedding-001` is free-tier |
| Reasoning Agent | LLM — `claude-sonnet-4-6` | Structured reasoning and coherent prose require the strongest available model |
| Action Agent | LLM — `claude-haiku-4-5` | Metadata extraction and note merging need language understanding, not heavy reasoning |
| Linker Agent | Pure code (regex + file I/O) | Wiki-link injection and index regeneration are fully deterministic |
| Validator Agent | LLM — `claude-haiku-4-5` | Scoring coherence and catching subtle quality issues needs LLM judgment |

---

## Open Source vs API Split

| Component | Technology | Type | Cost |
|---|---|---|---|
| PDF text extraction | PyMuPDF (`fitz`) | Open source | Free |
| Web scraping | `requests` + `BeautifulSoup4` | Open source | Free |
| CSV / JSON parsing | Python stdlib | Open source | Free |
| Intake classification | Python regex | Open source | Free |
| Entity / number extraction | Python regex | Open source | Free |
| Semantic embeddings | Google `gemini-embedding-001` | OSS API (free tier) | Free |
| Cosine similarity ranking | numpy | Open source | Free |
| Wiki-link injection | Python regex | Open source | Free |
| Markdown rendering (UI) | marked.js (CDN) | Open source | Free |
| Git sync / persistence | subprocess / git CLI | Open source | Free |
| Image understanding | Claude Vision (`claude-haiku-4-5`) | API | Per token |
| Answer generation | `claude-sonnet-4-6` | API | Per token |
| Note writing / merging | `claude-haiku-4-5` | API | Per token |
| Quality validation | `claude-haiku-4-5` | API | Per token |

**Why this split:** extraction, classification, linking, and ranking are deterministic tasks — using an LLM here adds latency and cost with no quality benefit. LLM calls are reserved for tasks that genuinely require language understanding: reasoning, writing, and judgment.

---

## Efficiency Strategy

| Strategy | Where Applied | Effect |
|---|---|---|
| Rule-based agents for extraction | Intake + Extraction + Linker | Zero token cost on 3 of 7 agents |
| Google embeddings (free tier) | RAG agent | Semantic search at zero LLM cost |
| `claude-haiku-4-5` for write/validate | Action + Validator agents | ~5× cheaper than Sonnet for non-reasoning tasks |
| `claude-sonnet-4-6` only for reasoning | Reasoning agent | Quality where it matters, cost contained |
| In-memory response cache | `utils.call_ai()` | Identical prompts hit cache — zero API calls on repeat |
| Embedding cache | `research_agent._embed()` | Repeated queries skip Google API call entirely |
| Parallel Extraction + RAG | Orchestrator | Both run concurrently after Intake — ~30-40% faster pipeline |
| Intake topics as note title | Writer Agent (text queries) | Skips one Haiku metadata call on text queries |
| Anthropic prompt caching | All LLM agents | System prompts cached server-side — reduces input tokens on repeated calls |
| 2-attempt retry with 1s backoff | `utils.call_ai()`, `call_vision()`, `stream_ai()` | Handles transient API failures without crashing the pipeline |
| Validator retry loop | Orchestrator | If score < 6, re-runs Reasoning Agent with issues as feedback — one retry max |
| Grounding instruction | Reasoning Agent system prompt | Prevents hallucination — model told to only use facts from provided notes |
| 4000-character input cap | All ingest endpoints | Prevents runaway token usage on large PDFs and URLs |
| Response streaming | `/api/stream` SSE endpoint | Answer visible in ~1s; no 20s blank wait |
| Git sync only on Render | `git_sync.sync()` | Local runs never trigger GitHub auth or push |

---

## Setup

**Requirements:** Python 3.11+, Anthropic API key, Google API key.

```bash
# 1. Clone
git clone https://github.com/Kadyan25/agentic-wiki.git
cd agentic-wiki

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
```

Add to `.env`:
```
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Optional — for Render git sync persistence
GITHUB_TOKEN=your_github_token
GITHUB_REPO=username/repo-name
```

```bash
# 4. Run
uvicorn main:app --reload
```

Open `http://localhost:8000`.

---

## Usage

The interface uses a tab strip to switch between input modes:

| Tab | Input | What happens |
|---|---|---|
| ✎ Text | Type a question | Pipeline researches and answers directly |
| 🔗 URL | Paste a URL | Page is scraped, text extracted, pipeline runs |
| 📄 PDF | Upload a .pdf | Text extracted via PyMuPDF, pipeline runs |
| 🖼 Image | Upload jpg/png/webp | Claude Vision reads it, pipeline runs |
| 📊 CSV/JSON | Upload data file | Column/row summary generated, pipeline runs |

All inputs produce the same output:
- **Streamed answer** — markdown rendered live, word by word
- **Quality score** — 1–10 badge (green ≥ 8, yellow ≥ 5, red < 5)
- **Input type badge** — Text Query / Document / URL Content
- **Agent trace** — collapsible log of all 7 agents with files read/written
- **Notes panel** — knowledge base sidebar, clickable to view raw markdown
- **New Research button** — resets all inputs and returns to the start state

---

## API

```
POST /api/stream
  Body:    { "query": "string" }
  Returns: SSE stream — token events then a final done event with full result

POST /api/query
  Body:    { "query": "string" }
  Returns: { "answer", "input_type", "notes_created", "notes_updated", "agent_trace", "validation" }

POST /api/ingest/pdf
  Body:    multipart/form-data, field "file" (.pdf only)
  Returns: same shape as /api/query

POST /api/ingest/url
  Body:    { "url": "https://..." }
  Returns: same shape as /api/query

POST /api/ingest/image
  Body:    multipart/form-data, field "file" (jpg/jpeg/png/webp)
  Returns: same shape as /api/query

POST /api/ingest/csv
  Body:    multipart/form-data, field "file" (.csv or .json)
  Returns: same shape as /api/query

GET  /api/provider
  Returns: { "provider": "Claude (Haiku)" }

GET  /api/notes
  Returns: list of all notes with filename, title, last_updated

GET  /api/notes/{filename}
  Returns: { "filename", "content" } — raw markdown
```

---

## Token / Cost Tradeoffs

| Decision | Tradeoff |
|---|---|
| Sonnet only for reasoning | Higher quality answer at ~5× cost vs Haiku — justified because reasoning is the user-facing output |
| Haiku for write + validate | Lower quality acceptable for metadata extraction and scoring — saves ~80% on those calls |
| 3 LLM calls per query (reason + write + validate) | Predictable cost; collapsing to 1 call loses agent separation and validator catch |
| Validator as separate LLM call | Adds ~150 tokens per query; catches quality issues before output reaches user |
| Validator retry (score < 6) | Adds up to 2 extra calls on bad runs; prevents low-quality answers from being accepted silently |
| In-memory cache | Free repeat queries within a process lifetime; lost on restart |
| 4000-char input cap | Prevents runaway costs; may truncate tail content of long documents |
| Google embeddings (free tier) | Full semantic search at zero cost; 3072-dim vectors via `gemini-embedding-001` |
| Streaming via SSE | No cost change — same tokens, better perceived latency |

**Typical query cost:**
- Haiku calls (write + validate): ~800–1200 tokens → ~$0.001
- Sonnet call (reasoning): ~1000–1500 tokens → ~$0.015
- Google embeddings: free tier
- **Total per query: ~$0.015–0.020**

---

## Known Limitations

- **JS-rendered pages not supported** — URL scraping uses `requests` + BeautifulSoup; pages built with React, Next.js, or other SPAs return an empty shell or Cloudflare challenge page
- **Hosting IP blocked by Cloudflare** — Render, Railway, and AWS outbound IPs are flagged by Cloudflare and most major bot-detection systems; URL ingestion may fail on popular sites when deployed
- **Embeddings lost on restart** — the vector index is in-memory; every server restart requires re-embedding all knowledge files from scratch before RAG is effective
- **No concurrent write safety** — simultaneous requests can corrupt a knowledge file; designed for single-user / demo use
- **Text-only PDFs** — scanned or image-based PDFs have no extractable text and return an error
- **4000-char input cap** — long documents lose tail content; only the first ~4000 characters enter the pipeline
- **Slug collisions** — two notes whose titles reduce to the same filename slug overwrite each other
- **No rate limiting** — any client can spam the API endpoints
- **Git sync failure is silent** — sync errors are logged server-side only, not surfaced in the UI

---

## Where the System Can Fail

| Failure point | Behaviour |
|---|---|
| Google API key invalid or suspended | RAG returns "No relevant notes found" silently; pipeline continues without semantic search |
| Anthropic API down | `call_ai()` retries once, then returns an error string; pipeline continues with degraded output |
| URL blocked (403/429/Cloudflare) | Returns a specific HTTP error to the UI with the status code and reason |
| PDF with no extractable text | Returns 422 with clear message |
| Validator scores < 6 | Reasoning Agent re-runs once with validator feedback; if still low, returns the better of the two |
| Any single agent raises an exception | `_safe_run()` catches it, marks that agent as errored in the trace, pipeline continues |

---

## What Would Be Improved for Production

- Persistent vector store (Qdrant) — survives restarts, supports concurrent users
- Playwright headless browser for JS-rendered pages — handles SPAs and dynamic content
- Residential proxy rotation — bypasses Cloudflare and hosting IP blocks
- Semantic cache — cosine similarity on query embeddings to hit cache for near-duplicate questions
- Async pipeline with parallel agent execution — Extraction and RAG run concurrently
- Rate limiting and auth middleware
- Observability — per-call token counts, latency, and cost logged to a database

---

## Project Structure

```
├── main.py                    # FastAPI app — 8 API endpoints
├── agents/
│   ├── orchestrator.py        # Sequential pipeline + streaming generator
│   ├── intake_agent.py        # Type detection, text cleaning (no LLM)
│   ├── extraction_agent.py    # Entities, numbers, key terms (no LLM)
│   ├── research_agent.py      # Semantic RAG — Google embeddings + cosine sim
│   ├── summarizer_agent.py    # Reasoning Agent — claude-sonnet-4-6, streaming
│   ├── writer_agent.py        # Action Agent — creates/merges .md notes
│   ├── linker_agent.py        # Wiki-link injection, _index.md (no LLM)
│   ├── validator_agent.py     # Quality scoring with retry logic
│   ├── git_sync.py            # Commits knowledge/ to GitHub (Render only)
│   └── utils.py               # Anthropic client, cache, retry, stream_ai
├── knowledge/                 # All notes live here
│   └── _index.md              # Auto-maintained cross-reference index
├── static/
│   ├── index.html             # Full frontend — tab strip, streaming UI
│   └── architecture.html      # Interactive SVG architecture diagram
├── tests/
│   ├── test_pipeline.py       # Unit tests — agents, chunker, utils
│   ├── test_endpoints.py      # Endpoint tests — all 8 routes via TestClient
│   ├── test_research_agent.py # RAG unit tests — cosine sim, index, chunker
│   ├── test_integration.py    # Live API tests — full pipeline, embeddings
│   └── test_stress.py         # Concurrency, cache, throughput, load tests
├── pytest.ini
├── requirements.txt
├── updates.md                 # Roadmap of planned improvements
└── render.yaml                # Render deployment config
```

---

## Deploy to Render

1. Push to GitHub
2. Create a new **Web Service** on [render.com](https://render.com), connect the repo
3. Set environment variables:
   ```
   ANTHROPIC_API_KEY=your_key
   GOOGLE_API_KEY=your_key
   GITHUB_TOKEN=your_token     # optional — enables knowledge base persistence
   GITHUB_REPO=username/repo
   ```
4. Render uses `render.yaml` automatically — no extra config needed

`RENDER=true` is set automatically by Render. Git sync only activates when this variable is present.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, Uvicorn |
| LLM | Anthropic Claude — `claude-sonnet-4-6` (reasoning), `claude-haiku-4-5` (write/validate/vision) |
| Embeddings | Google `gemini-embedding-001` via `google-generativeai` |
| Vector similarity | numpy cosine similarity |
| PDF parsing | PyMuPDF (`fitz`) |
| Web scraping | requests + BeautifulSoup4 |
| Storage | Local Markdown files — no database |
| Frontend | Vanilla HTML/CSS/JS, marked.js for markdown rendering, SSE for streaming |
| Tests | pytest, FastAPI TestClient, httpx |
