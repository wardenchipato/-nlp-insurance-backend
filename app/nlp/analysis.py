"""Single entrypoint: cleaned text → bucket scores, legacy flag dict, matched keywords."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from app.nlp.gazette_mapping import empty_buckets, empty_legacy
from app.nlp.negation import apply_denial_phrase_overrides

logger = logging.getLogger(__name__)

# Fallback substring extractor (optional if spaCy unavailable)
from app.nlp.feature_extractor import FeatureExtractor

# Old phrase → legacy keys for fallback path only
_KEYWORD_TO_LEGACY_FALLBACK: Dict[str, List[str]] = {
    "drunk": ["drunk_driving"],
    "drinking": ["drunk_driving"],
    "dwi": ["drunk_driving"],
    "dui": ["drunk_driving"],
    "racing": ["reckless", "speeding"],
    "street racing": ["reckless", "speeding"],
    "speeding": ["speeding"],
    "excessive speed": ["speeding"],
    "reckless": ["reckless"],
    "careless": ["reckless"],
    "distracted": ["distracted"],
    "phone": ["distracted"],
    "texting": ["distracted"],
    "rain": ["rain"],
    "heavy rain": ["rain"],
    "flood": ["rain"],
    "fog": ["fog"],
    "foggy": ["fog"],
    "dark": ["darkness", "night_driving"],
    "night": ["darkness", "night_driving"],
    "ice": ["rain"],
    "slippery": ["rain"],
    "late night": ["night_driving", "darkness"],
    "2am": ["night_driving", "darkness"],
    "3am": ["night_driving", "darkness"],
    "rush hour": ["peak_hours"],
    "peak hour": ["peak_hours"],
    "weekend night": ["night_driving"],
    "brake failure": ["brake_failure"],
    "brakes failed": ["brake_failure"],
    "tyre burst": ["tyre_problem"],
    "blowout": ["tyre_problem"],
    "overloaded": ["tyre_problem"],
    "mechanical fault": ["brake_failure"],
    "junction": ["junction"],
    "intersection": ["junction"],
    "highway": ["highway"],
    "rural": [],
    "blind corner": ["junction"],
    "mountain pass": ["highway"],
    "urban": ["urban"],
    "city": ["urban"],
}


def _legacy_from_fallback_keywords(matched: List[str]) -> Dict[str, float]:
    leg = empty_legacy()
    for phrase in matched:
        for flag in _KEYWORD_TO_LEGACY_FALLBACK.get(phrase, []):
            if flag in leg:
                leg[flag] = 1.0
    return leg


def _fallback_analyze(cleaned_text: str) -> Dict[str, Any]:
    fx = FeatureExtractor()
    buckets, extreme = fx.extract_features(cleaned_text)
    matched = fx.get_matched_keywords()
    legacy = _legacy_from_fallback_keywords(matched)
    apply_denial_phrase_overrides(cleaned_text.lower(), legacy, buckets)
    return {
        "buckets": buckets,
        "legacy_features": legacy,
        "matched_keywords": matched,
        "extreme_risk": extreme,
        "gazette_matches": [],
    }


def analyze_text(cleaned_text: str) -> Dict[str, Any]:
    """
    Returns:
      buckets: 5 category scores 0–1
      legacy_features: dict for calculate_risk_score (0/1 floats)
      matched_keywords: phrases hit
      extreme_risk: bool
      gazette_matches: list of {phrase, label, category} when spaCy path used
    """
    if not cleaned_text or not cleaned_text.strip():
        return {
            "buckets": empty_buckets(),
            "legacy_features": empty_legacy(),
            "matched_keywords": [],
            "extreme_risk": False,
            "gazette_matches": [],
        }

    try:
        from app.nlp.spacy_pipeline import analyze_with_spacy

        return analyze_with_spacy(cleaned_text)
    except Exception as exc:  # noqa: BLE001
        logger.warning("spaCy gazette analysis unavailable, using fallback: %s", exc)

    return _fallback_analyze(cleaned_text)


def analyze_tokens(tokens: List[str]) -> Dict[str, Any]:
    """Backward-compatible: join tokens and run full-text analysis."""
    text = " ".join(tokens) if tokens else ""
    return analyze_text(text)
