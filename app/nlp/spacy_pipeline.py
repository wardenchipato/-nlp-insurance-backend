"""spaCy + EntityRuler loaded from gazette CSV; singleton NLP object."""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.nlp.gazette_loader import load_gazette_rows
from app.nlp.gazette_mapping import (
    empty_buckets,
    empty_legacy,
    merge_buckets,
    merge_legacy,
    normalize_phrase,
    score_gazette_match,
    score_supplementary_text,
)
from app.nlp.negation import apply_denial_phrase_overrides, entity_is_negated

_nlp = None
_GAZETTE_META: Dict[str, Dict[str, str]] = {}


def _build_patterns_and_meta() -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, str]]]:
    rows = load_gazette_rows()
    patterns: List[Dict[str, Any]] = []
    meta: Dict[str, Dict[str, str]] = {}
    seen_norm: set[str] = set()

    for row in rows:
        phrase = row["phrase"]
        norm = normalize_phrase(phrase)
        if not norm:
            continue
        meta[norm] = {
            "label": row["label"],
            "category": row["category"],
            "phrase": phrase,
        }
        if norm in seen_norm:
            continue
        seen_norm.add(norm)
        tokens = norm.split()
        if not tokens:
            continue
        pat = [{"LOWER": t} for t in tokens]
        patterns.append({"label": row["label"], "pattern": pat})

    return patterns, meta


def get_nlp():
    """Lazy-load spaCy model and attach gazette EntityRuler."""
    global _nlp, _GAZETTE_META
    if _nlp is not None:
        return _nlp

    import spacy

    _nlp = spacy.load("en_core_web_sm")
    if "ner" in _nlp.pipe_names:
        _nlp.remove_pipe("ner")

    patterns, _GAZETTE_META = _build_patterns_and_meta()
    ruler = _nlp.add_pipe("entity_ruler", last=True)
    ruler.add_patterns(patterns)
    return _nlp


def analyze_with_spacy(cleaned_text: str) -> Dict[str, Any]:
    """Full narrative analysis: gazette entities + supplementary cues."""
    legacy = empty_legacy()
    buckets = empty_buckets()
    matched_keywords: List[str] = []
    gazette_matches: List[Dict[str, str]] = []
    extreme_risk = False

    nlp = get_nlp()
    doc = nlp(cleaned_text)

    lower_full = cleaned_text.lower()

    for ent in doc.ents:
        if entity_is_negated(doc, ent):
            continue
        raw = ent.text.strip()
        norm_ent = normalize_phrase(raw)
        info = _GAZETTE_META.get(norm_ent)
        label = ent.label_
        category = ""
        phrase_display = raw
        if info:
            label = info["label"]
            category = info["category"]
            phrase_display = info["phrase"]
        leg_delta, bucket_delta, ex = score_gazette_match(
            norm_ent or normalize_phrase(raw),
            label,
            category,
            phrase_display,
        )
        merge_legacy(legacy, leg_delta)
        merge_buckets(buckets, bucket_delta)
        extreme_risk = extreme_risk or ex
        matched_keywords.append(phrase_display.lower())
        gazette_matches.append(
            {
                "phrase": phrase_display,
                "label": label,
                "category": category,
            }
        )

    sup_legacy, sup_buckets, sup_kw, sup_ex = score_supplementary_text(cleaned_text)
    merge_legacy(legacy, sup_legacy)
    merge_buckets(buckets, sup_buckets)
    extreme_risk = extreme_risk or sup_ex
    matched_keywords.extend(sup_kw)

    apply_denial_phrase_overrides(lower_full, legacy, buckets)

    if any(w >= 0.9 for w in buckets.values()):
        extreme_risk = True

    return {
        "buckets": buckets,
        "legacy_features": legacy,
        "matched_keywords": list(dict.fromkeys(matched_keywords)),
        "extreme_risk": extreme_risk,
        "gazette_matches": gazette_matches,
    }


def spacy_available() -> bool:
    try:
        import spacy  # noqa: F401

        spacy.load("en_core_web_sm")
        return True
    except Exception:
        return False
