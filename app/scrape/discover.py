from __future__ import annotations

import re
from typing import List, Set
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from app.scrape.client import FetchClient
from app.scrape.config import AccidentFilterConfig, ScrapeSource
from app.scrape.relevance import is_link_likely_relevant


def _link_allowed(url: str, source: ScrapeSource) -> bool:
    low = url.lower()
    if source.exclude_link_match:
        for ex in source.exclude_link_match:
            if ex and ex.lower() in low:
                return False
    if source.article_link_match:
        return any(m.lower() in low for m in source.article_link_match if m)
    return True


_NEWS_DAY_HUB_PATHS = frozenset(
    {
        "local-news",
        "tag/road-accidents",
        "index.php/topic/accidents",
    }
)


def _is_listing_url(url: str, listing_urls: List[str]) -> bool:
    norm = url.rstrip("/")
    for lu in listing_urls:
        if norm == lu.rstrip("/"):
            return True
    parsed = urlparse(norm)
    path = parsed.path.strip("/").lower()
    if path in _NEWS_DAY_HUB_PATHS:
        return True
    return False


def _looks_like_article(url: str) -> bool:
    """Drop section indexes and shallow hub pages."""
    path = urlparse(url).path.strip("/")
    if not path:
        return False
    low_path = path.lower()
    hub_endings = (
        "local-news",
        "all-news",
        "policy",
        "economy",
        "sport",
        "articles",
    )
    if low_path in hub_endings:
        return False
    parts = [p for p in path.split("/") if p]
    if "newsday.co.zw" in url.lower():
        if low_path in _NEWS_DAY_HUB_PATHS:
            return False
        if "/article/" not in low_path:
            return False
        # e.g. local-news/article/200055102/slug
        return len(parts) >= 3 and any(p.isdigit() for p in parts)
    if "africa-press.net" in url.lower():
        return "all-news" in low_path and len(parts) >= 3
    return len(parts) >= 2


def discover_article_urls(
    client: FetchClient,
    source: ScrapeSource,
    listing_urls: List[str],
    limit: int,
    *,
    accident_filter: AccidentFilterConfig | None = None,
) -> List[str]:
    found: List[str] = []
    seen: Set[str] = set()

    for listing in listing_urls:
        html = client.fetch_html(listing)
        if not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        base = listing
        for a in soup.find_all("a", href=True):
            href = a.get("href")
            full = FetchClient.normalize_url(base, href)
            if not full or full in seen:
                continue
            if _is_listing_url(full, listing_urls):
                continue
            if not _link_allowed(full, source):
                continue
            # Skip obvious non-article paths
            path = urlparse(full).path.lower()
            if path in ("/", "") or path.endswith("/all-news") or path.endswith("/all-news/"):
                continue
            if not _looks_like_article(full):
                continue
            anchor = a.get_text(" ", strip=True)
            if accident_filter and accident_filter.enabled:
                if not is_link_likely_relevant(full, anchor):
                    continue
            seen.add(full)
            found.append(full)
            if len(found) >= limit:
                return found

    return found[:limit]
