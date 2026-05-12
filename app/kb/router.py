from __future__ import annotations

import logging
import os
from typing import Any, Dict

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.kb import service as kb_service
from app.kb.paths import KNOWLEDGE_DIR, knowledge_scan_roots

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/kb", tags=["knowledge_base"])


def _kb_call(fn_name: str, fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as exc:  # noqa: BLE001
        logger.exception("%s failed", fn_name)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/sync")
def kb_sync() -> Dict[str, Any]:
    """Rescan `knowledge/*.txt` and sync the local database."""
    return _kb_call("kb_sync", kb_service.sync_folder)


@router.get("/files")
def kb_list_files() -> Dict[str, Any]:
    return {"files": _kb_call("kb_list_files", kb_service.list_kb_files)}


@router.post("/upload")
async def kb_upload(file: UploadFile = File(...)) -> Dict[str, Any]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    try:
        raw = await file.read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("utf-8", errors="replace")
        row = _kb_call("kb_add_file", kb_service.add_kb_file, file.filename, text)
        return {"file": row}
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("kb_upload failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/files")
def kb_delete(filename: str = Query(..., description="Basename of the .txt file in knowledge/")) -> Dict[str, Any]:
    safe = os.path.basename(filename)
    if safe != filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not safe.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")
    ok = _kb_call("kb_delete", kb_service.delete_kb_file, safe)
    if not ok:
        raise HTTPException(status_code=404, detail="File not found or could not be removed")
    return {"deleted": safe}


@router.get("/stats")
def kb_stats() -> Dict[str, Any]:
    return _kb_call("kb_stats", kb_service.load_stats)


@router.post("/analyze-all")
def kb_analyze_all_sync() -> Dict[str, Any]:
    stats = _kb_call("kb_analyze_all", kb_service.analyze_all_files)
    return {"stats": stats}


@router.get("/health")
def kb_health() -> Dict[str, Any]:
    roots = knowledge_scan_roots()
    counts = []
    for r in roots:
        n = 0
        if os.path.isdir(r):
            try:
                n = sum(
                    1
                    for name in os.listdir(r)
                    if name.lower().endswith(".txt")
                    and os.path.isfile(os.path.join(r, name))
                )
            except OSError:
                n = -1
        counts.append({"path": r, "exists": os.path.isdir(r), "txt_files": n})
    return {
        "status": "ok",
        "module": "knowledge_base",
        "primary_upload_dir": KNOWLEDGE_DIR,
        "scan_roots": roots,
        "per_directory": counts,
        "hint": "Uploads save under primary_upload_dir. Both scan_roots are searched for .txt files.",
    }
