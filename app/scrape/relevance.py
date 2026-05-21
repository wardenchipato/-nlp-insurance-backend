"""Filter scraped articles to motor-road accident / traffic crash reports only."""
from __future__ import annotations

import re
from typing import Iterable, List, Optional, Sequence, Tuple

# Strong signals: one match in title or body is enough (with exclusions applied).
_STRONG_PHRASES: Tuple[str, ...] = (
    "road traffic accident",
    "traffic accident",
    "road accident",
    "motor accident",
    "motor vehicle accident",
    "car crash",
    "fatal crash",
    "fatal accident",
    "fatal road",
    "killed in crash",
    "killed in accident",
    "died in crash",
    "died in accident",
    "injured in crash",
    "injured in accident",
    "head on collision",
    "head-on collision",
    "hit and run",
    "hit-and-run",
    "kombi accident",
    "bus accident",
    "truck accident",
    "accident statistics",
    "traffic statistics",
    "festive season accident",
    "road carnage",
    "traffic fatalities",
    "multi vehicle accident",
    "multiple vehicle",
    "pile up",
    "pile-up",
    "veered off the road",
    "overturned",
    "overturn",
    "collision",
    "road crash",
    "traffic crash",
    "zrp press",
    "police recorded",
    "people killed",
    "people injured",
    "fatalities",
    "road deaths",
    "road death",
    "rising road deaths",
    "bloody roads",
    "road safety",
    "motorists warned",
    "warn motorists",
    "accidents surge",
    "accidents claim",
    "claim 3 lives",
    "claim lives",
    "perish in",
    "festive season",
    "death statistics",
    "death toll",
    "vehicle collision",
    "vehicle accidents",
    "traffic deaths",
    "road toll",
    "zimbabwe roads",
    "zrp",
    "traffic management",
)

# Weaker signals: need several in body, or one in title plus one in body.
_WEAK_TERMS: Tuple[str, ...] = (
    "accident",
    "crash",
    "fatal",
    "fatality",
    "injury",
    "injured",
    "killed",
    "deaths",
    "death toll",
    "highway",
    "roadblock",
    "reckless driving",
    "drunk driving",
    "speeding",
    "traffic police",
    "zrp",
    "kombi",
    "minibus",
    "haulage",
    "traffic jam",
    "road safety",
    "pedestrian",
    "pedestrians",
    "motorist",
    "motorists",
    "perished",
    "perish",
    "casualties",
    "casualty",
    "carnage",
    "highways",
    "road toll",
    "minibus",
    "haulage truck",
    "overturned vehicle",
    "smash",
)

# Slug/title hints on dedicated accident listing pages (NewsDay topic/tag).
_LISTING_TOPIC_HINTS: Tuple[str, ...] = (
    "accident",
    "accidents",
    "road accident",
    "road-accident",
    "road carnage",
    "road death",
    "traffic accident",
    "crash",
    "collision",
    "bloody road",
    "motorist",
    "pedestrian",
    "perish",
    "fatal",
    "zrp",
)

# Drop obvious non–road-traffic uses of "accident" / "crash".
_EXCLUDE_PATTERNS: Tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.I)
    for p in (
        r"\bstock\s+market\s+crash\b",
        r"\bmarket\s+crash\b",
        r"\bcurrency\s+crash\b",
        r"\bplane\s+crash\b",
        r"\bair\s+crash\b",
        r"\baircraft\b",
        r"\bby\s+accident\b",
        r"\blabou?r\s+accident\b",
        r"\bindustrial\s+accident\b",
        r"\bnuclear\b",
        r"\bvaccine\b",
        r"\bebola\b",
        r"\bhantavirus\b",
        r"\bcattle\s+brand",
        r"\bfootball\b",
        r"\bvolleyball\b",
        r"\barsenal\b",
        r"\bcup\s+of\s+nations\b",
        r"\belection\b",
        r"\breferendum\b",
        r"\bembassy\b",
        r"\bvisa\b",
        r"\bfarm(s)?\s+return",
        r"\btraffic\s+camera",
        r"\bsmart\s+traffic",
        r"\bai\s+traffic",
        r"\btraffic\s+enforcement\s+camera",
    )
)


def _normalize(text: str) -> str:
    t = (text or "").lower()
    t = re.sub(r"[^a-z0-9\s-]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _has_exclusion(text: str, *, title: str = "") -> bool:
    """Exclude only when a blocklist hits and the title is not clearly road-safety."""
    if not any(p.search(text) for p in _EXCLUDE_PATTERNS):
        return False
    title_n = _normalize(title)
    if any(h in title_n for h in _LISTING_TOPIC_HINTS):
        return False
    return True


def _count_hits(haystack: str, phrases: Sequence[str]) -> int:
    n = 0
    for p in phrases:
        if p in haystack:
            n += 1
    return n


def accident_relevance_score(
    title: str,
    body: str = "",
    *,
    extra_strong: Optional[Iterable[str]] = None,
    extra_weak: Optional[Iterable[str]] = None,
) -> Tuple[int, List[str]]:
    """
    Return (score, matched_hints). Higher = more clearly a road-accident report.
    """
    title_n = _normalize(title)
    body_n = _normalize(body)
    combined = f"{title_n} {body_n}".strip()

    if not combined:
        return 0, []

    if _has_exclusion(combined, title=title):
        return 0, []

    strong = list(_STRONG_PHRASES)
    weak = list(_WEAK_TERMS)
    if extra_strong:
        strong.extend(_normalize(x) for x in extra_strong if x)
    if extra_weak:
        weak.extend(_normalize(x) for x in extra_weak if x)

    hints: List[str] = []
    score = 0

    for p in strong:
        in_title = p in title_n
        in_body = p in body_n
        if in_title or in_body:
            score += 3 if in_title else 2
            hints.append(p)

    weak_hits = 0
    for term in weak:
        if term in title_n:
            weak_hits += 2
            hints.append(term)
        elif term in body_n:
            weak_hits += 1
            if term not in hints:
                hints.append(term)

    score += min(weak_hits, 4)

    # Title-only weak "accident" in non-traffic context already excluded above.
    return score, hints[:12]


def _title_or_url_hints_accident(title: str, url: str = "") -> bool:
    from urllib.parse import urlparse

    slug = urlparse(url).path.replace("-", " ").replace("/", " ")
    blob = _normalize(f"{title} {slug}")
    return any(h in blob for h in _LISTING_TOPIC_HINTS)


# Obvious non–road-traffic stories (sports, health, etc.) — still allow normal scoring elsewhere.
_HARD_REJECT_TITLE = re.compile(
    r"\b(volleyball|arsenal|gunners|premier league|cup of nations|zamalek|football|"
    r"rugby|cricket|tennis|golf|ebola|hantavirus|vaccine|embassy|visa waiver)\b",
    re.I,
)


def _hard_reject_non_road(title: str, url: str = "") -> bool:
    low_url = (url or "").lower()
    if "/sport/article/" in low_url:
        return True
    return bool(_HARD_REJECT_TITLE.search(title or ""))


def is_accident_relevant(
    title: str,
    body: str = "",
    *,
    min_score: int = 1,
    extra_strong: Optional[Iterable[str]] = None,
    extra_weak: Optional[Iterable[str]] = None,
    url: str = "",
    trust_accident_listing: bool = False,
) -> bool:
    """
    When trust_accident_listing is True (NewsDay topic/tag accident pages), accept
    curated listing articles unless they are clearly sports/off-topic by title or URL.
    """
    if trust_accident_listing:
        if _hard_reject_non_road(title, url):
            return False
        return True

    if _hard_reject_non_road(title, url):
        return False

    score, _ = accident_relevance_score(
        title,
        body,
        extra_strong=extra_strong,
        extra_weak=extra_weak,
    )
    return score >= min_score


def is_link_likely_relevant(href: str, anchor_text: str = "") -> bool:
    """Fast pre-filter on listing pages before fetching full article HTML."""
    from urllib.parse import urlparse

    slug = urlparse(href).path.replace("-", " ").replace("/", " ")
    text = f"{anchor_text} {slug}"
    score, _ = accident_relevance_score(text, "")
    return score >= 2
