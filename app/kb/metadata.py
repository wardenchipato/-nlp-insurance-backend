"""Parse report header metadata from knowledge-base .txt files and compute recency weights."""
from __future__ import annotations

import math
import re
from datetime import date, datetime, timezone
from typing import Any, Dict, Optional, Tuple

# Canonical header keys (case-insensitive match on line prefix)
_META_KEYS = {
    "source": "source",
    "period covered": "period_covered",
    "date of report": "date_of_report",
    "source url": "source_url",
}

# Month name patterns for date parsing
_MONTH = (
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
)
_DATE_PATTERNS = [
    # December 27, 2022
    re.compile(
        rf"\b({_MONTH})\s+(\d{{1,2}}),?\s+(\d{{4}})\b",
        re.IGNORECASE,
    ),
    # 27 December 2022 / 22nd APRIL 2025
    re.compile(
        rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+({_MONTH})\s+(\d{{4}})\b",
        re.IGNORECASE,
    ),
    # 2022-12-27 / 27/12/2022
    re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b"),
    re.compile(r"\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})\b"),
]

_MONTH_TO_NUM = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def _month_num(name: str) -> Optional[int]:
    return _MONTH_TO_NUM.get(name.strip().lower()[:12])


def parse_date_from_text(text: str) -> Optional[date]:
    """Best-effort parse of the first recognizable calendar date in *text*."""
    if not text or not str(text).strip():
        return None
    s = str(text).strip()

    m = _DATE_PATTERNS[0].search(s)
    if m:
        mo = _month_num(m.group(1))
        if mo:
            try:
                return date(int(m.group(3)), mo, int(m.group(2)))
            except ValueError:
                pass

    m = _DATE_PATTERNS[1].search(s)
    if m:
        mo = _month_num(m.group(2))
        if mo:
            try:
                return date(int(m.group(3)), mo, int(m.group(1)))
            except ValueError:
                pass

    m = _DATE_PATTERNS[2].search(s)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

    m = _DATE_PATTERNS[3].search(s)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return date(y, mo, d)
        except ValueError:
            try:
                return date(y, d, mo)
            except ValueError:
                pass

    # Year-only fallback when no day/month found (mid-year anchor)
    if not re.search(r"\b\d{1,2}\b", s):
        ym = re.search(r"\b(20\d{2})\b", s)
        if ym:
            try:
                return date(int(ym.group(1)), 7, 1)
            except ValueError:
                pass
    return None


def _line_is_metadata(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if ":" not in stripped:
        return False
    key = stripped.split(":", 1)[0].strip().lower()
    return key in _META_KEYS


def parse_kb_metadata(raw: str) -> Tuple[Dict[str, Any], str]:
    """
    Split optional header block from narrative body.

    Returns (metadata dict, body text). Metadata keys: source, period_covered,
    date_of_report, source_url, report_date (ISO), recency_reference_date.
    """
    meta: Dict[str, Any] = {
        "source": None,
        "period_covered": None,
        "date_of_report": None,
        "source_url": None,
    }
    if not raw:
        return meta, ""

    lines = raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    header_lines: list[str] = []
    body_start = 0
    in_header = True
    saw_meta = False

    for i, line in enumerate(lines):
        if in_header and _line_is_metadata(line):
            header_lines.append(line)
            if line.strip() and ":" in line:
                saw_meta = True
            body_start = i + 1
            continue
        if in_header and not line.strip():
            header_lines.append(line)
            body_start = i + 1
            continue
        if in_header and saw_meta:
            in_header = False
            body_start = i
            break
        if in_header and not saw_meta:
            body_start = i
            break
        break

    for line in header_lines:
        stripped = line.strip()
        if not stripped or ":" not in stripped:
            continue
        key_part, _, val_part = stripped.partition(":")
        key = key_part.strip().lower()
        val = val_part.strip()
        field = _META_KEYS.get(key)
        if field and val:
            meta[field] = val

    body = "\n".join(lines[body_start:]).strip()
    if not body and not saw_meta:
        body = raw.strip()

    if not saw_meta:
        for line in lines[:4]:
            if line.strip():
                inferred = parse_date_from_text(line)
                if inferred is not None:
                    meta["report_date"] = inferred.isoformat()
                    if not meta.get("date_of_report"):
                        meta["date_of_report"] = line.strip()[:120]
                    break

    report_date = parse_date_from_text(meta.get("date_of_report") or "")
    if report_date is None and meta.get("period_covered"):
        # Use end of period (last date-like token in range text)
        period = meta["period_covered"]
        dates_found: list[date] = []
        for chunk in re.split(r"[-–—to]+", period, flags=re.IGNORECASE):
            d = parse_date_from_text(chunk)
            if d:
                dates_found.append(d)
        if dates_found:
            report_date = max(dates_found)
        else:
            report_date = parse_date_from_text(period)

    if report_date is not None:
        meta["report_date"] = report_date.isoformat()

    return meta, body


def recency_weight(
    report_date: Optional[date],
    *,
    reference: Optional[date] = None,
    half_life_days: float = 548.0,
    min_weight: float = 0.12,
) -> float:
    """
    Exponential decay by age: weight = exp(-ln(2) * age_days / half_life_days).
    Unknown dates receive a neutral 0.5 weight.
    """
    if report_date is None:
        return 0.5
    ref = reference or datetime.now(timezone.utc).date()
    age_days = max(0, (ref - report_date).days)
    w = math.exp(-0.6931471805599453 * age_days / half_life_days)
    return round(max(min_weight, min(1.0, w)), 4)


def metadata_with_recency(
    meta: Dict[str, Any],
    *,
    reference: Optional[date] = None,
    half_life_days: float = 548.0,
) -> Dict[str, Any]:
    """Attach recency_weight to a metadata dict (mutates copy)."""
    out = dict(meta)
    rd: Optional[date] = None
    if out.get("report_date"):
        try:
            rd = date.fromisoformat(str(out["report_date"]))
        except ValueError:
            rd = None
    out["recency_weight"] = recency_weight(rd, reference=reference, half_life_days=half_life_days)
    out["recency_half_life_days"] = half_life_days
    return out


def empty_metadata() -> Dict[str, Any]:
    return {
        "source": None,
        "period_covered": None,
        "date_of_report": None,
        "source_url": None,
        "report_date": None,
        "recency_weight": 0.5,
    }
