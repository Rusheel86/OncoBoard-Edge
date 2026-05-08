from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from core.graph import build_onco_graph
from core.state import ArtifactIndex, OncoState, PatientIntake


APP_DIR = Path(".oncoedge")
UPLOAD_DIR = APP_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_UPLOAD_BYTES = int(os.getenv("ONCO_MAX_UPLOAD_MB", "25")) * 1024 * 1024
ALLOWED_EXTENSIONS = {
    "images": {".png", ".jpg", ".jpeg", ".webp"},
    "pdfs": {".pdf"},
    "audios": {".wav", ".mp3", ".m4a", ".flac"},
}


def _sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


async def _save_upload(upload: UploadFile, *, subdir: str) -> str:
    data = await upload.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty upload.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Upload exceeds {MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit.",
        )

    digest = _sha256_bytes(data)[:16]
    ext = Path(upload.filename or "file").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS[subdir]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type for {subdir}: {ext or 'none'}",
        )
    safe_ext = ext if ext and len(ext) <= 10 else ""

    out_dir = UPLOAD_DIR / subdir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{digest}{safe_ext}"
    out_path.write_bytes(data)
    return str(out_path)


class AnalyzeRequest(BaseModel):
    intake: PatientIntake
    artifacts: ArtifactIndex = Field(default_factory=ArtifactIndex)


app = FastAPI(
    title="OncoBoard-Edge API",
    version="0.1.0",
    description="Offline-first multimodal oncology intelligence (Phase 1 foundation).",
)


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "offline_default": os.getenv("ONCO_LLM_PROVIDER", "auto") in {"auto", "offline"},
    }


@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...)) -> dict[str, Any]:
    path = await _save_upload(file, subdir="images")
    return {"path": path}


@app.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...)) -> dict[str, Any]:
    path = await _save_upload(file, subdir="pdfs")
    return {"path": path}


@app.post("/upload/audio")
async def upload_audio(file: UploadFile = File(...)) -> dict[str, Any]:
    path = await _save_upload(file, subdir="audios")
    return {"path": path}


@app.post("/analyze")
async def analyze(req: AnalyzeRequest) -> dict[str, Any]:
    try:
        run = build_onco_graph()
        state = OncoState(case=req.intake, artifacts=req.artifacts)
        out = run(state)
        final_state = OncoState.model_validate(out)
        if not final_state.report:
            raise RuntimeError("No report generated.")
        return {
            "report": final_state.report.model_dump(),
            "retrieval": final_state.retrieval.model_dump() if final_state.retrieval else None,
            "extractions": final_state.extractions.model_dump(),
            "telemetry": final_state.telemetry,
        }
    except Exception as e:
        detail = (
            str(e)
            if os.getenv("ONCO_DEBUG_ERRORS", "0").lower() in {"1", "true", "yes"}
            else "Analysis failed. Check server logs and configuration."
        )
        raise HTTPException(status_code=500, detail=detail) from e
