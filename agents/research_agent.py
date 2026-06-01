import os
import re
import textwrap

import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(override=True)
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", ""))

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge")
SIMILARITY_THRESHOLD = 0.35
TOP_K = 5

# Module-level in-memory vector index
_index: list = []          # list of {"file": str, "chunk": str, "embedding": list}
_indexed_files: set = set()


# ── Chunker ────────────────────────────────────────────────────────────────────

def _split_sentences(text: str) -> list[str]:
    """Split text on sentence boundaries (. ? !), keeping the delimiter."""
    parts = re.split(r'(?<=[.?!])\s+', text.strip())
    return [p for p in parts if p.strip()]


def _chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    """
    Markdown-aware recursive chunker. Splits in priority order:
      1. Markdown headers (lines starting with #)
      2. Double newlines (paragraphs)
      3. Single newlines
      4. Sentence boundaries (. ? !)
      5. Spaces (last resort via textwrap)
    Accumulates units until size is reached, then starts a new chunk.
    Adds overlap by prepending the last ~50 chars of the previous chunk.
    Never splits mid-sentence.
    """
    # Priority 1: split on markdown headers
    segments = re.split(r'(?=^#{1,6} )', text, flags=re.MULTILINE)

    units: list[str] = []
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        if len(seg) <= size:
            units.append(seg)
            continue
        # Priority 2: paragraph breaks
        paras = [p.strip() for p in re.split(r'\n{2,}', seg) if p.strip()]
        for para in paras:
            if len(para) <= size:
                units.append(para)
                continue
            # Priority 3: single newlines
            lines = [l.strip() for l in para.split('\n') if l.strip()]
            for line in lines:
                if len(line) <= size:
                    units.append(line)
                    continue
                # Priority 4: sentence boundaries
                sentences = _split_sentences(line)
                for sent in sentences:
                    if len(sent) <= size:
                        units.append(sent)
                    else:
                        # Priority 5: hard wrap on spaces
                        for part in textwrap.wrap(sent, width=size):
                            units.append(part)

    # Accumulate units into chunks of ~size chars
    chunks: list[str] = []
    current = ""
    last_unit = ""

    for unit in units:
        if not current:
            # Apply overlap from previous chunk
            prefix = last_unit[-overlap:] if last_unit else ""
            current = (prefix + " " + unit).strip() if prefix else unit
        elif len(current) + 1 + len(unit) <= size:
            current += "\n" + unit
        else:
            chunks.append(current)
            last_unit = current
            prefix = last_unit[-overlap:] if last_unit else ""
            current = (prefix + " " + unit).strip() if prefix else unit

    if current:
        chunks.append(current)

    return chunks if chunks else [text[:size]]


# ── Embedding ──────────────────────────────────────────────────────────────────

def _embed(text: str, task_type: str = "retrieval_document") -> list:
    try:
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=text,
            task_type=task_type,
        )
        return result["embedding"]
    except Exception:
        return []


def _cosine_similarity(a: list, b: list) -> float:
    va = np.array(a, dtype=float)
    vb = np.array(b, dtype=float)
    norm_a = np.linalg.norm(va)
    norm_b = np.linalg.norm(vb)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(va, vb) / (norm_a * norm_b))


# ── Index builder ──────────────────────────────────────────────────────────────

def _build_index() -> None:
    """Incrementally embed new .md files not yet in the index."""
    for fname in os.listdir(KNOWLEDGE_DIR):
        if not fname.endswith(".md") or fname in _indexed_files:
            continue
        path = os.path.join(KNOWLEDGE_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            continue

        for chunk in _chunk_text(content):
            embedding = _embed(chunk, task_type="retrieval_document")
            if embedding:
                _index.append({"file": fname, "chunk": chunk, "embedding": embedding})

        _indexed_files.add(fname)


# ── Public run ─────────────────────────────────────────────────────────────────

def run(query: str, context: dict) -> dict:
    _build_index()

    if not _index:
        return {
            "output": "No relevant notes found.",
            "files_read": [],
            "files_written": [],
            "gaps": [],
        }

    query_embedding = _embed(query, task_type="retrieval_query")
    if not query_embedding:
        return {
            "output": "No relevant notes found.",
            "files_read": [],
            "files_written": [],
            "gaps": [],
        }

    # Score all chunks
    scored = [
        (item, _cosine_similarity(query_embedding, item["embedding"]))
        for item in _index
    ]
    scored.sort(key=lambda x: x[1], reverse=True)

    top = [(item, score) for item, score in scored[:TOP_K] if score >= SIMILARITY_THRESHOLD]

    files_read = list(dict.fromkeys(item["file"] for item, _ in top))
    relevant_chunks = "\n\n---\n\n".join(
        f"### {item['file']} (score: {score:.2f})\n{item['chunk']}"
        for item, score in top
    )

    # Gaps: keywords from query not covered by any retrieved file
    keywords = [w for w in re.findall(r'\b[a-z]{4,}\b', query.lower()) if w not in {
        "with", "from", "that", "this", "have", "been", "will", "what", "when", "where",
    }]
    all_topics = " ".join(_indexed_files).lower()
    gaps = [kw for kw in keywords if kw not in all_topics]

    return {
        "output": relevant_chunks if relevant_chunks else "No relevant notes found.",
        "files_read": files_read,
        "files_written": [],
        "gaps": gaps,
    }
