from __future__ import annotations

import re
from typing import Optional, Tuple
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from app.scrape.writer import ScrapedArticle


def _clean_text(el) -> str:
    if el is None:
        return ""
    for tag in el.find_all(["script", "style", "nav", "footer", "aside", "form"]):
        tag.decompose()
    text = el.get_text("\n", strip=True)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n\n".join(lines)


# NewsDay-style: May. 9, 2026  (dot after abbreviated month — avoids "Marketing")
_NEWSDAY_DOTTED = re.compile(
    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.\s*(\d{1,2}),?\s*(\d{4})\b",
    re.I,
)

_MONTH_FULL = (
    r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:\.|ember)?)|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?"
)


def _parse_iso_date(text: str) -> Optional[str]:
    if not text:
        return None
    s = str(text).strip()

    m = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", s)
    if m:
        return m.group(1)

    m = _NEWSDAY_DOTTED.search(s)
    if m:
        return f"{m.group(1)}. {m.group(2)}, {m.group(3)}"

    m = re.search(
        rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+({_MONTH_FULL})\s+(\d{{4}})\b",
        s,
        re.I,
    )
    if m:
        return f"{m.group(2)} {m.group(1)}, {m.group(3)}"

    m = re.search(
        rf"\b({_MONTH_FULL})\s+(\d{{1,2}}),?\s+(\d{{4}})\b",
        s,
        re.I,
    )
    if m:
        return f"{m.group(1)} {m.group(2)}, {m.group(3)}"
    return None


def _meta_publish_date(soup: BeautifulSoup) -> Optional[str]:
    for prop in (
        "article:published_time",
        "og:published_time",
        "article:modified_time",
        "datePublished",
    ):
        meta = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        if meta and meta.get("content"):
            parsed = _parse_iso_date(meta["content"])
            if parsed:
                return parsed
    return None


def _text_from_regions(soup: BeautifulSoup, title_el) -> str:
    chunks: list[str] = []
    if title_el is not None:
        node = title_el
        for _ in range(4):
            if node is None:
                break
            chunks.append(node.get_text(" ", strip=True))
            node = getattr(node, "parent", None)
    for cls in ("contentholder", "section-phase", "contents", "content-body"):
        el = soup.find(class_=cls)
        if el:
            chunks.append(el.get_text(" ", strip=True)[:1200])
    return " ".join(chunks)


def extract_africa_press(html: str, url: str, source_label: str) -> Optional[ScrapedArticle]:
    soup = BeautifulSoup(html, "html.parser")
    title_el = soup.find("h1") or soup.find("h2")
    title = title_el.get_text(strip=True) if title_el else ""
    if not title:
        og = soup.find("meta", property="og:title")
        title = (og.get("content") if og else "") or ""

    date_str = _meta_publish_date(soup)
    if not date_str:
        time_el = soup.find("time")
        if time_el:
            date_str = time_el.get("datetime") or time_el.get_text(strip=True)
    if not date_str:
        date_str = _parse_iso_date(_text_from_regions(soup, title_el))

    body_el = (
        soup.find("article")
        or soup.find("div", class_=re.compile(r"entry|content|post", re.I))
        or soup.find("main")
    )
    body = _clean_text(body_el)
    if len(body) < 120:
        return None

    report_date = _parse_iso_date(date_str or "")
    if not report_date and date_str and "T" in date_str:
        report_date = _parse_iso_date(date_str[:10])
    display_date = report_date or (date_str[:80] if date_str else None)
    return ScrapedArticle(
        url=url,
        title=title or "Africa Press article",
        body=body,
        source_label=source_label,
        date_of_report=display_date,
    )


def extract_newsday(html: str, url: str, source_label: str) -> Optional[ScrapedArticle]:
    if "/sso" in url.lower() or "email-protection" in url.lower():
        return None

    soup = BeautifulSoup(html, "html.parser")
    title_el = soup.find("h1") or soup.find("h2", class_=re.compile(r"title|entry", re.I))
    title = title_el.get_text(strip=True) if title_el else ""
    if not title:
        og = soup.find("meta", property="og:title")
        title = (og.get("content") if og else "") or ""

    if re.search(r"\b(login|sign\s*in|subscribe)\b", title, re.I) and len(title) < 80:
        return None

    date_str = _meta_publish_date(soup)
    if not date_str:
        time_el = soup.find("time")
        if time_el:
            date_str = time_el.get("datetime") or time_el.get_text(strip=True)
    if not date_str:
        region_text = _text_from_regions(soup, title_el)
        date_str = _parse_iso_date(region_text)

    body_el = (
        soup.find(class_="content-body")
        or soup.find("div", class_=re.compile(r"content-body", re.I))
        or soup.find("article")
        or soup.find("div", class_=re.compile(r"entry-content|post-content", re.I))
        or soup.find("main")
    )
    body = _clean_text(body_el)
    if len(body) < 120:
        return None

    report_date = _parse_iso_date(date_str or "")
    display = report_date
    if not display and date_str:
        display = _parse_iso_date(date_str[:10]) or date_str[:80]
    return ScrapedArticle(
        url=url,
        title=title or "NewsDay article",
        body=body,
        source_label=source_label,
        date_of_report=display,
    )


def extract_generic(html: str, url: str, source_label: str) -> Optional[ScrapedArticle]:
    host = urlparse(url).netloc.lower()
    if "africa-press.net" in host:
        return extract_africa_press(html, url, source_label)
    if "newsday.co.zw" in host:
        return extract_newsday(html, url, source_label)

    soup = BeautifulSoup(html, "html.parser")
    title = ""
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)
    body_el = soup.find("article") or soup.find("main")
    body = _clean_text(body_el)
    if len(body) < 120:
        return None
    return ScrapedArticle(
        url=url,
        title=title or "Scraped article",
        body=body,
        source_label=source_label,
        date_of_report=_parse_iso_date(body[:500]),
    )


def extract_article(html: str, url: str, source_label: str) -> Optional[ScrapedArticle]:
    return extract_generic(html, url, source_label)
