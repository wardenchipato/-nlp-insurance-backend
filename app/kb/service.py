from __future__ import annotations

import os
import re
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from app.db import store as kb_store
from app.nlp.analysis import analyze_text
from app.scoring.risk_engine import claims_proxy_from_legacy
from app.nlp.gazette_mapping import normalize_phrase
from app.nlp.text_cleaner import clean_text


def _safe_filename(name: str) -> str:
    base = os.path.basename(name)
    base = re.sub(r"[^a-zA-Z0-9._-]+", "_", base).strip("._") or "document"
    if not base.lower().endswith(".txt"):
        base = f"{base}.txt"
    return base[:180]


def sync_folder() -> Dict[str, Any]:
    n = kb_store.sync_knowledge_folder()
    return {"txt_files_on_disk": n}


def list_kb_files() -> List[Dict[str, Any]]:
    return kb_store.list_knowledge_files()


def add_kb_file(original_name: str, content: str) -> Dict[str, Any]:
    safe = _safe_filename(original_name)
    written = kb_store.write_txt_file(safe, content)
    rows = [r for r in list_kb_files() if r["filename"] == written]
    return rows[0] if rows else {"filename": written, "id": "0", "char_count": len(content)}


def delete_kb_file(filename: str) -> bool:
    return kb_store.delete_txt_file(filename)


def read_kb_file_content(filename: str) -> str:
    return kb_store.read_txt_file(filename)


def analyze_document_text(raw: str) -> Dict[str, Any]:
    cleaned = clean_text(raw)
    nlp = analyze_text(cleaned)
    return {
        "cleaned_preview": cleaned[:400],
        "buckets": nlp["buckets"],
        "matched_keywords": nlp["matched_keywords"],
        "legacy_features": nlp["legacy_features"],
        "extreme_risk": nlp["extreme_risk"],
    }


def load_stats() -> Dict[str, Any]:
    return kb_store.load_latest_aggregate_stats()


def default_stats() -> Dict[str, Any]:
    return kb_store.default_stats()


def aggregate_from_results(per_file: List[Dict[str, Any]]) -> Dict[str, Any]:
    n = len(per_file)
    if n == 0:
        return default_stats()

    bucket_sums = {
        k: 0.0
        for k in [
            "behavioural",
            "environmental",
            "time",
            "vehicle",
            "location",
            "claims_severity",
        ]
    }
    cat_docs = {k: 0 for k in bucket_sums}
    kw_counter: Counter[str] = Counter()
    kw_doc_freq: Counter[str] = Counter()
    total_kw_hits = 0

    for item in per_file:
        b = item.get("buckets") or {}
        lf = item.get("legacy_features") or {}
        for k in ["behavioural", "environmental", "time", "vehicle", "location"]:
            v = float(b.get(k, 0) or 0)
            bucket_sums[k] += v
            if v > 0.01:
                cat_docs[k] += 1
        cs = claims_proxy_from_legacy(lf if isinstance(lf, dict) else {}) / 100.0
        bucket_sums["claims_severity"] += cs
        if cs > 0.05:
            cat_docs["claims_severity"] += 1
        matched = item.get("matched_keywords") or []
        for kw in matched:
            kn = normalize_phrase(str(kw))
            if kn:
                kw_counter[kn] += 1
                total_kw_hits += 1
        seen_terms = {normalize_phrase(str(kw)) for kw in matched}
        seen_terms.discard("")
        for kn in seen_terms:
            kw_doc_freq[kn] += 1

    now = datetime.now(timezone.utc).isoformat()
    avg_buckets = {k: round(bucket_sums[k] / n, 4) for k in bucket_sums}
    cat_share = {k: round(cat_docs[k] / n, 4) for k in cat_docs}
    keyword_doc_share = {k: round(v / n, 4) for k, v in kw_doc_freq.items()}

    return {
        "document_count": n,
        "analyzed_at": now,
        "avg_bucket_scores": avg_buckets,
        "category_doc_share": cat_share,
        "keyword_counts": dict(kw_counter.most_common(200)),
        "keyword_doc_frequency": dict(kw_doc_freq.most_common(500)),
        "keyword_doc_share": keyword_doc_share,
        "total_keyword_hits": total_kw_hits,
    }


async def analyze_all_files_async(
    broadcast: Callable[[Dict[str, Any]], Any],
) -> Dict[str, Any]:
    kb_store.sync_knowledge_folder()
    rows = list_kb_files()
    per_file: List[Dict[str, Any]] = []
    per_file_for_db: List[tuple[str, Dict[str, Any]]] = []
    total = len(rows)

    for i, row in enumerate(rows):
        fn = row["filename"]
        await broadcast(
            {
                "type": "progress",
                "index": i + 1,
                "total": total,
                "file_id": row.get("id"),
                "name": fn,
            }
        )
        raw = read_kb_file_content(fn)
        if not raw.strip():
            continue
        doc = analyze_document_text(raw)
        summary = {
            "filename": fn,
            "buckets": doc["buckets"],
            "matched_keywords": doc["matched_keywords"],
            "legacy_features": doc["legacy_features"],
        }
        per_file.append(summary)
        per_file_for_db.append((fn, doc))

    stats = aggregate_from_results(per_file)
    if per_file_for_db:
        kb_store.save_nlp_run(per_file_for_db, stats)
    stats = load_stats()
    await broadcast({"type": "stats", "stats": stats})
    await broadcast({"type": "complete", "stats": stats, "per_file": per_file})
    return stats


def analyze_all_files(
    progress: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    kb_store.sync_knowledge_folder()
    rows = list_kb_files()
    per_file: List[Dict[str, Any]] = []
    per_file_for_db: List[tuple[str, Dict[str, Any]]] = []
    total = len(rows)

    for i, row in enumerate(rows):
        fn = row["filename"]
        if progress:
            progress(
                {
                    "type": "progress",
                    "index": i + 1,
                    "total": total,
                    "file_id": row.get("id"),
                    "name": fn,
                }
            )
        raw = read_kb_file_content(fn)
        if not raw.strip():
            continue
        doc = analyze_document_text(raw)
        per_file.append(
            {
                "filename": fn,
                "buckets": doc["buckets"],
                "matched_keywords": doc["matched_keywords"],
                "legacy_features": doc["legacy_features"],
            }
        )
        per_file_for_db.append((fn, doc))

    stats = aggregate_from_results(per_file)
    if per_file_for_db:
        kb_store.save_nlp_run(per_file_for_db, stats)
    stats = load_stats()
    if progress:
        progress({"type": "complete", "stats": stats, "per_file": per_file})
    return stats
