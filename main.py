from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

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


@app.post("/api/query")
async def query(req: QueryRequest):
    result = run_pipeline(req.query)
    return result


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
