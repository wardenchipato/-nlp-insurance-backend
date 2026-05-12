"""SQLite persistence for knowledge-base files and NLP outputs."""
from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional, Tuple

from app.kb.paths import LOCAL_DB_PATH, KNOWLEDGE_DIR, ensure_kb_dirs, knowledge_scan_roots

_schema_ready = False


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    ensure_kb_dirs()
    conn = sqlite3.connect(LOCAL_DB_PATH, check_same_thread=False, timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=8000")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    init_db()
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create schema (uses a dedicated connection to avoid re-entrancy with get_conn)."""
    global _schema_ready
    if _schema_ready:
        return
    ensure_kb_dirs()
    conn = _connect()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS knowledge_file (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL UNIQUE,
                file_size INTEGER NOT NULL DEFAULT 0,
                char_count INTEGER NOT NULL DEFAULT 0,
                mtime REAL NOT NULL DEFAULT 0,
                first_seen_utc TEXT NOT NULL,
                last_seen_utc TEXT NOT NULL,
                is_present INTEGER NOT NULL DEFAULT 1,
                last_nlp_at_utc TEXT
            );

            CREATE TABLE IF NOT EXISTS nlp_aggregate_run (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_at_utc TEXT NOT NULL,
                document_filenames_json TEXT NOT NULL,
                stats_json TEXT NOT NULL,
                document_count INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS nlp_document_output (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aggregate_run_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                analyzed_at_utc TEXT NOT NULL,
                output_json TEXT NOT NULL,
                FOREIGN KEY (aggregate_run_id) REFERENCES nlp_aggregate_run(id)
            );

            CREATE INDEX IF NOT EXISTS idx_nlp_doc_run ON nlp_document_output(aggregate_run_id);
            CREATE INDEX IF NOT EXISTS idx_nlp_doc_file ON nlp_document_output(filename);
            """
        )
        cols = {r[1] for r in conn.execute("PRAGMA table_info(knowledge_file)").fetchall()}
        if "char_count" not in cols:
            conn.execute(
                "ALTER TABLE knowledge_file ADD COLUMN char_count INTEGER NOT NULL DEFAULT 0"
            )
        conn.commit()
        _schema_ready = True
    finally:
        conn.close()


def _txt_paths_on_disk() -> List[str]:
    """All *.txt files under configured knowledge folders (flat; no subfolders)."""
    out: List[str] = []
    for root in knowledge_scan_roots():
        if not os.path.isdir(root):
            continue
        try:
            names = sorted(os.listdir(root))
        except OSError:
            continue
        for name in names:
            if not name.lower().endswith(".txt"):
                continue
            path = os.path.join(root, name)
            if os.path.isfile(path):
                out.append(path)
    return out


def sync_knowledge_folder() -> int:
    """Scan knowledge dirs for *.txt, upsert DB rows, mark missing files not present. Returns count on disk."""
    now = _utc_now()
    # First matching path wins per basename (same order as knowledge_scan_roots).
    on_disk: Dict[str, str] = {}
    for p in _txt_paths_on_disk():
        bn = os.path.basename(p)
        if bn not in on_disk:
            on_disk[bn] = p
    with get_conn() as conn:
        for basename, path in on_disk.items():
            st = os.stat(path)
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as fh:
                    char_count = len(fh.read())
            except OSError:
                char_count = 0
            row = conn.execute(
                "SELECT id FROM knowledge_file WHERE filename = ?", (basename,)
            ).fetchone()
            if row:
                conn.execute(
                    """
                    UPDATE knowledge_file
                    SET file_size = ?, char_count = ?, mtime = ?, last_seen_utc = ?, is_present = 1
                    WHERE filename = ?
                    """,
                    (st.st_size, char_count, st.st_mtime, now, basename),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO knowledge_file
                    (filename, file_size, char_count, mtime, first_seen_utc, last_seen_utc, is_present)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                    """,
                    (basename, st.st_size, char_count, st.st_mtime, now, now),
                )
        if on_disk:
            placeholders = ",".join("?" for _ in on_disk)
            conn.execute(
                f"""
                UPDATE knowledge_file
                SET is_present = 0
                WHERE is_present = 1 AND filename NOT IN ({placeholders})
                """,
                tuple(on_disk.keys()),
            )
        else:
            conn.execute(
                "UPDATE knowledge_file SET is_present = 0 WHERE is_present = 1"
            )
    return len(on_disk)


def list_knowledge_files() -> List[Dict[str, Any]]:
    sync_knowledge_folder()
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT k.id, k.filename, k.file_size, k.char_count, k.mtime, k.first_seen_utc,
                   k.last_seen_utc, k.last_nlp_at_utc
            FROM knowledge_file k
            WHERE k.is_present = 1
            ORDER BY k.last_seen_utc DESC
            """
        ).fetchall()
    result: List[Dict[str, Any]] = []
    for r in rows:
        result.append(
            {
                "id": str(r["id"]),
                "filename": r["filename"],
                "original_name": r["filename"],
                "char_count": int(r["char_count"] or 0),
                "mtime": r["mtime"],
                "uploaded_at": r["first_seen_utc"],
                "last_seen_at": r["last_seen_utc"],
                "last_nlp_at": r["last_nlp_at_utc"],
            }
        )
    return result


def read_txt_file(filename: str) -> str:
    safe = os.path.basename(filename)
    if not safe.lower().endswith(".txt"):
        return ""
    for root in knowledge_scan_roots():
        path = os.path.join(root, safe)
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
    return ""


def write_txt_file(filename: str, content: str) -> str:
    safe = os.path.basename(filename)
    if not safe.lower().endswith(".txt"):
        safe = f"{os.path.splitext(safe)[0] or 'document'}.txt"
    ensure_kb_dirs()
    path = os.path.join(KNOWLEDGE_DIR, safe)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    sync_knowledge_folder()
    return safe


def delete_txt_file(filename: str) -> bool:
    safe = os.path.basename(filename)
    path = os.path.join(KNOWLEDGE_DIR, safe)
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError:
            return False
    with get_conn() as conn:
        conn.execute(
            "UPDATE knowledge_file SET is_present = 0 WHERE filename = ?", (safe,)
        )
    return True


def load_latest_aggregate_stats() -> Dict[str, Any]:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, run_at_utc, document_filenames_json, stats_json, document_count
            FROM nlp_aggregate_run
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()
    if not row:
        return default_stats()
    try:
        stats = json.loads(row["stats_json"])
        docs = json.loads(row["document_filenames_json"])
    except (json.JSONDecodeError, TypeError):
        return default_stats()
    stats["aggregate_run_id"] = row["id"]
    stats["source_documents"] = docs if isinstance(docs, list) else []
    stats["document_count"] = row["document_count"]
    return stats


def save_nlp_run(
    per_file_outputs: List[Tuple[str, Dict[str, Any]]],
    stats: Dict[str, Any],
) -> int:
    """Persist one aggregate NLP run and per-document rows. Returns aggregate_run id."""
    now = _utc_now()
    filenames = [name for name, _ in per_file_outputs]
    stats_blob = {k: v for k, v in stats.items() if k not in ("source_documents", "aggregate_run_id")}
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO nlp_aggregate_run (run_at_utc, document_filenames_json, stats_json, document_count)
            VALUES (?, ?, ?, ?)
            """,
            (now, json.dumps(filenames), json.dumps(stats_blob), len(filenames)),
        )
        run_id = int(cur.lastrowid)
        for filename, output in per_file_outputs:
            conn.execute(
                """
                INSERT INTO nlp_document_output (aggregate_run_id, filename, analyzed_at_utc, output_json)
                VALUES (?, ?, ?, ?)
                """,
                (run_id, filename, now, json.dumps(output)),
            )
            conn.execute(
                """
                UPDATE knowledge_file SET last_nlp_at_utc = ? WHERE filename = ? AND is_present = 1
                """,
                (now, filename),
            )
    return run_id


def default_stats() -> Dict[str, Any]:
    return {
        "document_count": 0,
        "analyzed_at": None,
        "avg_bucket_scores": {
            "behavioural": 0.0,
            "environmental": 0.0,
            "time": 0.0,
            "vehicle": 0.0,
            "location": 0.0,
            "claims_severity": 0.0,
        },
        "category_doc_share": {
            "behavioural": 0.0,
            "environmental": 0.0,
            "time": 0.0,
            "vehicle": 0.0,
            "location": 0.0,
            "claims_severity": 0.0,
        },
        "keyword_counts": {},
        "keyword_doc_frequency": {},
        "keyword_doc_share": {},
        "total_keyword_hits": 0,
        "source_documents": [],
        "aggregate_run_id": None,
    }
