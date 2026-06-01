from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

from agents.orchestrator import run_pipeline

app = FastAPI(title="Agentic Wiki")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge")


class QueryRequest(BaseModel):
    query: str
    max_depth: int = 1


class UrlRequest(BaseModel):
    url: str


@app.post("/api/query")
async def query(req: QueryRequest):
    result = run_pipeline(req.query)
    return result


@app.post("/api/ingest/pdf")
async def ingest_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise HTTPException(status_code=500, detail="PyMuPDF not installed")

    data = await file.read()
    try:
        doc = fitz.open(stream=data, filetype="pdf")
        text = "\n\n".join(page.get_text() for page in doc)
        doc.close()
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse PDF: {e}")

    text = text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="PDF contains no extractable text")

    query_text = text[:4000]  # cap to avoid excessive token usage
    result = run_pipeline(query_text)
    return result


@app.post("/api/ingest/url")
async def ingest_url(req: UrlRequest):
    url = req.url.strip()
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        raise HTTPException(status_code=500, detail="requests or beautifulsoup4 not installed")

    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "AgenticWiki/1.0"})
        resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not fetch URL: {e}")

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    text = "\n".join(line for line in text.splitlines() if line.strip())

    if not text:
        raise HTTPException(status_code=422, detail="Page contains no extractable text")

    query_text = text[:4000]  # cap to avoid excessive token usage
    result = run_pipeline(query_text)
    return result


ALLOWED_IMAGE_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
}


@app.post("/api/ingest/image")
async def ingest_image(file: UploadFile = File(...)):
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    media_type = ALLOWED_IMAGE_TYPES.get(ext)
    if not media_type:
        raise HTTPException(status_code=400, detail="Only jpg, jpeg, png, webp files are accepted")
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise HTTPException(status_code=400, detail="Image ingestion requires ANTHROPIC_API_KEY")

    image_bytes = await file.read()
    try:
        from agents.utils import call_vision
        extracted = call_vision(
            image_bytes,
            media_type,
            "Extract and describe all text, data, and key information visible in this image. "
            "Be thorough — include headings, body text, numbers, labels, and any notable visual content.",
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Image processing failed: {e}")

    if not extracted.strip():
        raise HTTPException(status_code=422, detail="No content could be extracted from the image")

    result = run_pipeline(extracted[:4000])
    return result


@app.post("/api/ingest/csv")
async def ingest_csv(file: UploadFile = File(...)):
    fname = file.filename.lower()
    if not (fname.endswith(".csv") or fname.endswith(".json")):
        raise HTTPException(status_code=400, detail="Only .csv and .json files are accepted")

    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")

    try:
        if fname.endswith(".json"):
            import json
            data = json.loads(text)
            summary = json.dumps(data, indent=2)
        else:
            import csv, io
            reader = csv.reader(io.StringIO(text))
            rows = list(reader)
            if not rows:
                raise HTTPException(status_code=422, detail="CSV file is empty")
            headers = rows[0]
            preview = rows[1:6]
            lines = [
                f"CSV file: {len(rows) - 1} rows, {len(headers)} columns.",
                f"Columns: {', '.join(headers)}",
                "First 5 rows:",
            ]
            for row in preview:
                lines.append("  " + " | ".join(row))
            summary = "\n".join(lines)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse file: {e}")

    result = run_pipeline(summary[:4000])
    return result


@app.get("/api/provider")
async def get_provider():
    from agents.utils import get_active_provider
    return {"provider": get_active_provider()}


@app.get("/api/notes")
async def list_notes():
    notes = []
    for fname in os.listdir(KNOWLEDGE_DIR):
        if fname.endswith(".md"):
            path = os.path.join(KNOWLEDGE_DIR, fname)
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            title = lines[0].lstrip("# ").strip() if lines else fname
            mtime = os.path.getmtime(path)
            import datetime
            last_updated = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
            notes.append({"filename": fname, "title": title, "last_updated": last_updated})
    return notes


@app.get("/api/notes/{filename}")
async def get_note(filename: str):
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    path = os.path.join(KNOWLEDGE_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Note not found")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return {"filename": filename, "content": content}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
