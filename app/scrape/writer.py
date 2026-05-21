from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Optional

from app.db import store as kb_store


@dataclass
class ScrapedArticle:
    url: str
    title: str
    body: str
    source_label: str
    date_of_report: Optional[str] = None
    period_covered: Optional[str] = None


def _slugify(text: str, max_len: int = 60) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", (text or "").strip().lower()).strip("-")
    return (s[:max_len] or "article").strip("-")


def build_kb_txt(article: ScrapedArticle) -> str:
    """Format .txt with the same metadata header block the KB parser expects."""
    lines = [
        f"Source: {article.source_label}",
        "",
    ]
    if article.period_covered:
        lines.extend([f"Period Covered: {article.period_covered}", ""])
    if article.date_of_report:
        lines.extend([f"Date of Report: {article.date_of_report}", ""])
    lines.extend([f"Source URL: {article.url}", "", (article.body or "").strip(), ""])
    return "\n".join(lines).strip() + "\n"


def filename_for_article(source_id: str, article: ScrapedArticle) -> str:
    """Stable, safe basename under knowledge/ (same rules as manual uploads)."""
    url_hash = hashlib.sha256(article.url.encode("utf-8")).hexdigest()[:10]
    slug = _slugify(article.title)
    base = f"scraped_{source_id}_{slug}_{url_hash}.txt"
    base = re.sub(r"[^a-zA-Z0-9._-]+", "_", base).strip("._")
    if not base.lower().endswith(".txt"):
        base = f"{base}.txt"
    return base[:180]


def save_article_to_knowledge(source_id: str, article: ScrapedArticle) -> str:
    """
    Persist via the same path as manual uploads: backend/knowledge/ + DB sync.
    """
    content = build_kb_txt(article)
    filename = filename_for_article(source_id, article)
    return kb_store.write_txt_file(filename, content)
