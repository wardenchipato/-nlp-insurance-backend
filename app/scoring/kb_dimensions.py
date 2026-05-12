"""Map gazette labels/phrases to NLP component dimensions for KB prevalence weighting."""
from __future__ import annotations

from typing import Optional


def gazette_match_to_dimension(label: str, norm_phrase: str) -> Optional[str]:
    """
    Route a corpus / submission gazette span to one of B,E,T,V,L,C.
    CLAIM_TERM is excluded (returns None).
    """
    np = norm_phrase or ""
    if label == "CLAIM_TERM":
        return None
    if label == "TRANSPORT":
        return "vehicle"
    if label == "WEATHER":
        return "environmental"
    if label == "BEHAVIOUR":
        if np == "night driving":
            return "time"
        return "behavioural"
    if label in ("LOCATION", "ROAD"):
        return "location"
    if label == "INJURY":
        return "claims_severity"
    if label == "ACCIDENT_TERM":
        if any(x in np for x in ("tyre", "brake", "rollover", "overturned")):
            return "vehicle"
        if any(x in np for x in ("intersection", "junction", "collision at intersection")):
            return "location"
        if any(
            x in np
            for x in (
                "fatal",
                "injury",
                "injuries",
                "deceased",
                "critical",
                "multiple vehicle",
                "chain collision",
            )
        ):
            return "claims_severity"
        return "location"
    if label == "TRAFFIC_TERM":
        if "congestion" in np:
            return "location"
        if np in ("dui", "driving under influence", "traffic violation", "traffic offense"):
            return "behavioural"
        return "location"
    return None


def bucket_weights_for_dimensions() -> dict[str, float]:
    """Same weights as risk_engine narrative composite."""
    return {
        "behavioural": 0.35,
        "environmental": 0.10,
        "time": 0.10,
        "vehicle": 0.15,
        "location": 0.10,
        "claims_severity": 0.20,
    }


__all__ = ["gazette_match_to_dimension", "bucket_weights_for_dimensions"]
