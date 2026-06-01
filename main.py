from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import threading
import time
import urllib.request

load_dotenv(override=True)


def _self_ping():
    url = os.getenv("RENDER_EXTERNAL_URL")
    if not url:
        return  # only runs on Render
    url = url.rstrip("/") + "/api/notes"
    while True:
        time.sleep(300)  # 5 minutes
        try:
            urllib.request.urlopen(url, timeout=10)
        except Exception:
            pass


threading.Thread(target=_self_ping, daemon=True).start()

from agents.orchestrator import run_pipeline, run_pipeline_streaming

app = FastAPI(title="Research Intelligence System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge")
os.makedirs(KNOWLEDGE_DIR, exist_ok=True)

# Upload size limits
MAX_PDF_BYTES   = 20 * 1024 * 1024   # 20 MB
MAX_IMAGE_BYTES = 5  * 1024 * 1024   # 5 MB
MAX_CSV_BYTES   = 5  * 1024 * 1024   # 5 MB
MAX_URL_BYTES   = 2  * 1024 * 1024   # 2 MB response body

# SSRF guard — block requests to private / loopback addresses
_BLOCKED_HOSTS = ("localhost", "127.", "0.0.0.0", "10.", "192.168.", "172.16.",
                  "172.17.", "172.18.", "172.19.", "172.20.", "172.21.", "172.22.",
                  "172.23.", "172.24.", "172.25.", "172.26.", "172.27.", "172.28.",
                  "172.29.", "172.30.", "172.31.", "169.254.", "::1", "metadata.google")

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


class QueryRequest(BaseModel):
    query: str
    max_depth: int = 1


class UrlRequest(BaseModel):
    url: str


# ── Text query ─────────────────────────────────────────────────────────────────

@app.post("/api/query")
async def query(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    result = run_pipeline(req.query)
    return result


@app.post("/api/stream")
async def stream_query(req: QueryRequest):
    """SSE endpoint — streams summarizer tokens then sends final result."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    return StreamingResponse(
        run_pipeline_streaming(req.query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disables Nginx buffering on Render
        },
    )


# ── PDF ingest ─────────────────────────────────────────────────────────────────

@app.post("/api/ingest/pdf")
async def ingest_pdf(file: UploadFile = File(...)):
    # Extension check
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise HTTPException(status_code=500, detail="PyMuPDF not installed.")

    data = await file.read()

    # Empty file
    if not data:
        raise HTTPException(status_code=400, detail="The uploaded PDF is empty.")

    # Size limit
    if len(data) > MAX_PDF_BYTES:
        raise HTTPException(status_code=400, detail=f"PDF exceeds the 20 MB size limit.")

    # Parse
    try:
        doc = fitz.open(stream=data, filetype="pdf")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not open PDF — file may be corrupted or password-protected: {e}")

    try:
        text = "\n\n".join(page.get_text() for page in doc)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to extract text from PDF: {e}")
    finally:
        doc.close()

    text = text.strip()
    if not text:
        raise HTTPException(
            status_code=422,
            detail="PDF contains no extractable text. Scanned or image-only PDFs are not supported."
        )

    result = run_pipeline(text[:4000])
    return result


# ── URL ingest ─────────────────────────────────────────────────────────────────

@app.post("/api/ingest/url")
async def ingest_url(req: UrlRequest):
    url = req.url.strip()

    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty.")

    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

    # SSRF guard
    from urllib.parse import urlparse
    hostname = urlparse(url).hostname or ""
    if any(hostname.startswith(b) or hostname == b.rstrip(".") for b in _BLOCKED_HOSTS):
        raise HTTPException(status_code=400, detail="Requests to internal or private addresses are not allowed.")

    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        raise HTTPException(status_code=500, detail="requests or beautifulsoup4 not installed.")

    try:
        resp = requests.get(url, timeout=15, headers=BROWSER_HEADERS,
                            allow_redirects=True, stream=True)
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=422, detail="Could not connect to the URL. Check the address and try again.")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=422, detail="The page took too long to respond (15s timeout).")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Request failed: {e}")

    # Status code errors
    if resp.status_code == 401:
        raise HTTPException(status_code=422, detail="Authentication required (401) — this page requires a login.")
    if resp.status_code == 403:
        raise HTTPException(status_code=422, detail="Access denied (403) — this site blocks automated requests.")
    if resp.status_code == 404:
        raise HTTPException(status_code=422, detail="Page not found (404).")
    if resp.status_code == 429:
        raise HTTPException(status_code=422, detail="Rate limited (429) — try again later.")
    if resp.status_code == 451:
        raise HTTPException(status_code=422, detail="Content unavailable for legal reasons (451).")
    if resp.status_code >= 500:
        raise HTTPException(status_code=422, detail=f"The target server returned an error ({resp.status_code}). Try again later.")
    if resp.status_code >= 400:
        raise HTTPException(status_code=422, detail=f"Page returned HTTP {resp.status_code}.")

    # Content-type check — reject binary/non-HTML responses
    content_type = resp.headers.get("Content-Type", "").lower()
    if any(t in content_type for t in ("application/pdf", "application/octet-stream",
                                        "image/", "audio/", "video/", "application/zip")):
        raise HTTPException(
            status_code=422,
            detail=f"URL returned a binary file ({content_type.split(';')[0].strip()}), not a web page. "
                   "Use the PDF or Image upload instead."
        )

    # Response size limit — read up to MAX_URL_BYTES
    try:
        chunks = []
        total = 0
        for chunk in resp.iter_content(chunk_size=8192, decode_unicode=False):
            total += len(chunk)
            chunks.append(chunk)
            if total > MAX_URL_BYTES:
                break
        raw_bytes = b"".join(chunks)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to read page content: {e}")

    try:
        html = raw_bytes.decode("utf-8", errors="replace")
    except Exception:
        html = raw_bytes.decode("latin-1", errors="replace")

    # Parse and extract text
    try:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        text = "\n".join(line for line in text.splitlines() if line.strip())
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse page content: {e}")

    if not text or len(text) < 50:
        raise HTTPException(
            status_code=422,
            detail="Page contains no extractable text. The page may be JS-rendered, "
                   "behind a login wall, or blocked by bot detection."
        )

    result = run_pipeline(text[:4000])
    return result


# ── Image ingest ───────────────────────────────────────────────────────────────

ALLOWED_IMAGE_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
}


@app.post("/api/ingest/image")
async def ingest_image(file: UploadFile = File(...)):
    # Extension check
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    media_type = ALLOWED_IMAGE_TYPES.get(ext)
    if not media_type:
        raise HTTPException(status_code=400, detail="Only jpg, jpeg, png, and webp files are accepted.")

    if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
        raise HTTPException(status_code=500, detail="Image ingestion requires ANTHROPIC_API_KEY to be configured.")

    image_bytes = await file.read()

    # Empty file
    if not image_bytes:
        raise HTTPException(status_code=400, detail="The uploaded image is empty.")

    # Size limit
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail="Image exceeds the 5 MB size limit.")

    try:
        from agents.utils import call_vision
        extracted = call_vision(
            image_bytes,
            media_type,
            "Extract and describe all text, data, and key information visible in this image. "
            "Be thorough — include headings, body text, numbers, labels, and any notable visual content.",
        )
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=f"Image processing failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Unexpected error processing image: {e}")

    if not extracted or not extracted.strip():
        raise HTTPException(status_code=422, detail="No content could be extracted from the image.")

    result = run_pipeline(extracted[:4000])
    return result


# ── CSV / JSON ingest ──────────────────────────────────────────────────────────

@app.post("/api/ingest/csv")
async def ingest_csv(file: UploadFile = File(...)):
    fname = file.filename.lower()
    if not (fname.endswith(".csv") or fname.endswith(".json")):
        raise HTTPException(status_code=400, detail="Only .csv and .json files are accepted.")

    raw = await file.read()

    # Empty file
    if not raw:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    # Size limit
    if len(raw) > MAX_CSV_BYTES:
        raise HTTPException(status_code=400, detail="File exceeds the 5 MB size limit.")

    # Decode
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = raw.decode("latin-1")
        except Exception:
            raise HTTPException(status_code=422, detail="Could not decode file — unsupported encoding.")

    if not text.strip():
        raise HTTPException(status_code=400, detail="The file contains no content.")

    try:
        if fname.endswith(".json"):
            import json
            try:
                data = json.loads(text)
            except json.JSONDecodeError as e:
                raise HTTPException(status_code=422, detail=f"Invalid JSON: {e}")

            # Handle edge cases
            if data is None:
                raise HTTPException(status_code=422, detail="JSON file contains only null.")
            if isinstance(data, (int, float, bool, str)):
                raise HTTPException(status_code=422, detail="JSON must be an object or array, not a bare value.")
            if isinstance(data, (dict, list)) and not data:
                raise HTTPException(status_code=422, detail="JSON file is empty ({} or []).")

            summary = json.dumps(data, indent=2)

        else:
            import csv, io
            try:
                reader = csv.reader(io.StringIO(text))
                rows = list(reader)
            except csv.Error as e:
                raise HTTPException(status_code=422, detail=f"Could not parse CSV: {e}")

            if not rows:
                raise HTTPException(status_code=422, detail="CSV file is empty.")

            headers = rows[0]
            if not any(h.strip() for h in headers):
                raise HTTPException(status_code=422, detail="CSV has no valid headers in the first row.")

            data_rows = rows[1:]
            if not data_rows:
                raise HTTPException(status_code=422, detail="CSV has headers but no data rows.")

            preview = data_rows[:5]
            lines = [
                f"CSV file: {len(data_rows)} data rows, {len(headers)} columns.",
                f"Columns: {', '.join(h.strip() for h in headers)}",
                f"First {len(preview)} rows:",
            ]
            for row in preview:
                lines.append("  " + " | ".join(str(v).strip() for v in row))
            summary = "\n".join(lines)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not process file: {e}")

    result = run_pipeline(summary[:4000])
    return result


# ── Provider ───────────────────────────────────────────────────────────────────

@app.get("/api/provider")
async def get_provider():
    from agents.utils import get_active_provider
    return {"provider": get_active_provider()}


# ── Notes ──────────────────────────────────────────────────────────────────────

@app.get("/api/notes")
async def list_notes():
    import datetime
    notes = []
    try:
        filenames = os.listdir(KNOWLEDGE_DIR)
    except FileNotFoundError:
        return []  # knowledge dir not created yet

    for fname in filenames:
        if not fname.endswith(".md"):
            continue
        path = os.path.join(KNOWLEDGE_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            title = lines[0].lstrip("# ").strip() if lines else fname
            mtime = os.path.getmtime(path)
            last_updated = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
            notes.append({"filename": fname, "title": title, "last_updated": last_updated})
        except OSError:
            continue  # skip unreadable files silently

    return notes


@app.get("/api/notes/{filename}")
async def get_note(filename: str):
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    if not filename.endswith(".md"):
        raise HTTPException(status_code=400, detail="Only .md files can be retrieved.")
    path = os.path.join(KNOWLEDGE_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Note not found.")
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Could not read note: {e}")
    return {"filename": filename, "content": content}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
