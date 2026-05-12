"""
Detect negated risk phrases so "no drunk driving" does not score like "drunk driving".

Uses (1) explicit denial regexes, (2) token window before spaCy entity spans in the same sentence,
(3) character-window check for supplementary regex matches.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

# Lemmas/tokens that negate the following risk assertion (narrow list to reduce false positives).
_NEG_LEMMAS = frozenset(
    {
        "no",
        "not",
        "never",
        "neither",
        "nor",
        "nobody",
        "nothing",
        "without",
    }
)


def _token_is_negation(tok: Any) -> bool:
    t = tok.text.lower()
    if t in ("n't", "nt"):
        return True
    if tok.lemma_.lower() in _NEG_LEMMAS:
        return True
    if t in _NEG_LEMMAS:
        return True
    return False


def entity_is_negated(doc: Any, ent: Any) -> bool:
    """
    True if a negation cue appears shortly before this entity in the same sentence.
    """
    sent = ent.sent
    lo = max(sent.start, ent.start - 12)
    for i in range(lo, ent.start):
        if _token_is_negation(doc[i]):
            return True
    return False


# Explicit phrases that deny risk (normalized lowercase text).
_DENIAL_EXEMPT_LEGACY: List[Tuple[re.Pattern[str], List[str]]] = [
    (re.compile(r"\bno\s+drunk\s+driving\b"), ["drunk_driving"]),
    (re.compile(r"\bnot\s+drunk\b"), ["drunk_driving"]),
    (re.compile(r"\bno\s+history\s+of\s+(?:drunk|dui|alcohol)\b"), ["drunk_driving"]),
    (re.compile(r"\b(?:sober|not\s+intoxicated|not\s+under\s+the\s+influence)\b"), ["drunk_driving"]),
    (re.compile(r"\bno\s+speeding\b"), ["speeding"]),
    (re.compile(r"\bnot\s+speeding\b"), ["speeding"]),
    (re.compile(r"\bno\s+(?:injuries|injury|fatalities|fatal)\b"), ["severity_injury", "severity_fatal"]),
    (re.compile(r"\bno\s+(?:rain|fog)\b"), ["rain", "fog"]),
]


def apply_denial_phrase_overrides(
    lowercase_text: str,
    legacy: Dict[str, float],
    buckets: Optional[Dict[str, float]] = None,
) -> None:
    """Zero legacy flags when text explicitly denies that risk factor."""
    cleared_drunk = False
    cleared_injury_severity = False
    for pattern, keys in _DENIAL_EXEMPT_LEGACY:
        if pattern.search(lowercase_text):
            for k in keys:
                if k in legacy:
                    legacy[k] = 0.0
                    if k == "drunk_driving":
                        cleared_drunk = True
                    if k in ("severity_injury", "severity_fatal"):
                        cleared_injury_severity = True
    if buckets is not None:
        if cleared_drunk:
            buckets["behavioural"] = min(buckets["behavioural"], 0.42)
        if cleared_injury_severity:
            buckets["behavioural"] = min(buckets["behavioural"], 0.45)


def char_span_likely_negated(text_lower: str, span_start: int) -> bool:
    """Look at ~100 chars before match start for negation cue (supplementary regex matches)."""
    window_start = max(0, span_start - 100)
    before = text_lower[window_start:span_start]
    cut = max(
        before.rfind("."),
        before.rfind(";"),
        before.rfind("!"),
        before.rfind("?"),
    )
    if cut >= 0:
        before = before[cut + 1 :]
    neg_rx = re.compile(
        r"\b(?:no|not|never|neither|nor|without|lack\s+of|free\s+of|absence\s+of|"
        r"did\s+not|was\s+not|were\s+not|is\s+not|are\s+not|has\s+no|have\s+no|had\s+no)\b"
    )
    return bool(neg_rx.search(before))
