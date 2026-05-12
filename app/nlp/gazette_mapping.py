"""
Map gazette phrase + label + category to legacy risk flags and 0–1 bucket weights.
CLAIM_TERM / insurance_jargon: no numeric score impact (still listed as matched).
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

from app.nlp.negation import char_span_likely_negated

# Keys consumed by app.scoring.risk_engine.calculate_risk_score
LEGACY_KEYS: List[str] = [
    "speeding",
    "drunk_driving",
    "fatigue",
    "distracted",
    "reckless",
    "rain",
    "fog",
    "darkness",
    "wind",
    "poor_visibility",
    "wet_roads",
    "peak_hours",
    "night_driving",
    "daytime",
    "off_peak",
    "brake_failure",
    "tyre_problem",
    "commercial_vehicle_context",
    "junction",
    "highway",
    "urban",
    "rural_road",
    "traffic_congestion",
    "severity_fatal",
    "severity_injury",
    "severity_multi_vehicle",
]


BUCKET_KEYS = ("behavioural", "environmental", "time", "vehicle", "location")


def normalize_phrase(text: str) -> str:
    t = (text or "").lower().strip()
    t = re.sub(r"[^a-z\s]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def empty_legacy() -> Dict[str, float]:
    return {k: 0.0 for k in LEGACY_KEYS}


def empty_buckets() -> Dict[str, float]:
    return {k: 0.0 for k in BUCKET_KEYS}


def merge_legacy(base: Dict[str, float], delta: Dict[str, float]) -> None:
    for k, v in delta.items():
        if k in base:
            base[k] = max(base[k], float(v))


def merge_buckets(base: Dict[str, float], delta: Dict[str, float]) -> None:
    for k, v in delta.items():
        if k in base:
            base[k] = max(base[k], float(v))


_HEAVY_TRANSPORT = frozenset(
    {
        "kombi",
        "mushikashika",
        "cross-border bus",
        "haulage truck",
        "articulated truck",
        "tractor",
        "trailer",
        "lorry",
        "commuter omnibus",
        "fuel tanker",
        "delivery van",
        "school bus",
        "public transport",
        "minibus",
        "pickup truck",
    }
)

_TWO_WHEEL = frozenset({"motorbike", "bicycle"})


def score_gazette_match(
    norm_phrase: str,
    label: str,
    category: str,
    raw_phrase: str,
) -> Tuple[Dict[str, float], Dict[str, float], bool]:
    """
    Returns (legacy_delta, bucket_delta, extreme_risk).
    Empty deltas mean matched phrase did not move numeric risk (e.g. CLAIM_TERM).
    """
    legacy: Dict[str, float] = {}
    buckets: Dict[str, float] = {}
    extreme = False

    if label == "CLAIM_TERM" or category == "insurance_jargon":
        return legacy, buckets, False

    if label == "LOCATION" and category == "zimbabwe_place":
        legacy["urban"] = 1.0
        buckets["location"] = 0.45
        return legacy, buckets, False

    if label == "ROAD" and category == "road_name":
        np = norm_phrase
        if "highway" in np:
            legacy["highway"] = 1.0
            buckets["location"] = 0.85
            extreme = True
        else:
            legacy["junction"] = max(legacy.get("junction", 0), 0.4)
            buckets["location"] = 0.42
        legacy["urban"] = max(legacy.get("urban", 0), 0.5)
        return legacy, buckets, extreme

    if label == "TRANSPORT" and category == "vehicle_transport":
        rp = raw_phrase.strip().lower()
        if rp in _HEAVY_TRANSPORT:
            legacy["commercial_vehicle_context"] = 1.0
            buckets["vehicle"] = 0.78
            extreme = rp in {"fuel tanker", "haulage truck", "articulated truck"}
        elif rp in _TWO_WHEEL:
            buckets["vehicle"] = 0.55
        else:
            buckets["vehicle"] = 0.38
        return legacy, buckets, extreme

    if label == "BEHAVIOUR" and category == "risk_behaviour":
        return _score_behaviour(norm_phrase)

    if label == "WEATHER" and category == "environment_condition":
        return _score_weather(norm_phrase)

    if label == "ACCIDENT_TERM" and category == "accident_description":
        return _score_accident(norm_phrase)

    if label == "INJURY" and category == "injury_severity":
        return _score_injury(norm_phrase)

    if label == "TRAFFIC_TERM" and category == "traffic_context":
        return _score_traffic(norm_phrase)

    return legacy, buckets, False


def _score_behaviour(np: str) -> Tuple[Dict[str, float], Dict[str, float], bool]:
    legacy: Dict[str, float] = {}
    buckets: Dict[str, float] = {}
    extreme = False

    if np == "night driving":
        legacy["night_driving"] = 1.0
        buckets["time"] = 0.88
        extreme = True
        return legacy, buckets, extreme

    if np in {"speeding", "overspeeding"}:
        legacy["speeding"] = 1.0
        buckets["behavioural"] = 0.85
    elif "drunk" in np or np == "dui":
        legacy["drunk_driving"] = 1.0
        buckets["behavioural"] = 1.0
        extreme = True
    elif np in {"fatigue", "sleepy driving"}:
        legacy["fatigue"] = 1.0
        buckets["behavioural"] = 0.82
    elif "distract" in np or "texting" in np or "cellphone" in np:
        legacy["distracted"] = 1.0
        buckets["behavioural"] = 0.72
    elif (
        "reckless" in np
        or "tailgat" in np
        or "overtaking" in np
        or np == "lane switching"
        or np == "illegal u-turn"
        or np == "wrong overtaking"
        or np == "hit and run"
        or ("illegal" in np and "turn" in np)
    ):
        legacy["reckless"] = 1.0
        buckets["behavioural"] = 0.88
        extreme = np == "hit and run"
    elif np in {"brake failure", "brake malfunction"}:
        legacy["brake_failure"] = 1.0
        buckets["vehicle"] = 0.92
        extreme = True
    elif np == "failure to indicate":
        legacy["reckless"] = max(legacy.get("reckless", 0), 0.5)
        buckets["behavioural"] = 0.45
    elif np in {"driving without headlights", "using cellphone while driving"}:
        legacy["reckless"] = max(legacy.get("reckless", 0), 0.7)
        buckets["behavioural"] = 0.68
    else:
        buckets["behavioural"] = 0.55

    return legacy, buckets, extreme


def _score_weather(np: str) -> Tuple[Dict[str, float], Dict[str, float], bool]:
    legacy: Dict[str, float] = {}
    buckets: Dict[str, float] = {}
    extreme = False

    if np in {"heavy rain", "light rain", "drizzle", "flooded road"}:
        legacy["rain"] = 1.0
        buckets["environmental"] = 0.78
    elif "fog" in np or np == "misty weather":
        legacy["fog"] = 1.0
        buckets["environmental"] = 0.82
    elif np in {"poor visibility", "sun glare"}:
        legacy["poor_visibility"] = 1.0
        buckets["environmental"] = 0.8
    elif np in {"wet road", "slippery road", "muddy road", "oil spill on road"}:
        legacy["wet_roads"] = 1.0
        buckets["environmental"] = 0.74
    elif np == "strong winds":
        legacy["wind"] = 1.0
        buckets["environmental"] = 0.85
        extreme = True
    elif np in {"dust storm", "hailstorm", "storm"}:
        legacy["rain"] = max(legacy.get("rain", 0), 0.8)
        legacy["poor_visibility"] = max(legacy.get("poor_visibility", 0), 0.7)
        buckets["environmental"] = 0.82
    elif np in {
        "potholes",
        "loose gravel",
        "sharp curve",
        "damaged road surface",
    }:
        legacy["junction"] = max(legacy.get("junction", 0), 0.35)
        buckets["location"] = 0.55
        buckets["environmental"] = 0.68
    else:
        buckets["environmental"] = 0.55

    return legacy, buckets, extreme


def _score_accident(np: str) -> Tuple[Dict[str, float], Dict[str, float], bool]:
    legacy: Dict[str, float] = {}
    buckets: Dict[str, float] = {}
    extreme = False

    if "fatal" in np:
        legacy["severity_fatal"] = 1.0
        buckets["behavioural"] = 0.95
        extreme = True
    elif "intersection" in np or "junction" in np:
        legacy["junction"] = 1.0
        buckets["location"] = 0.78
    elif np == "multiple vehicle collision" or np == "chain collision":
        legacy["severity_multi_vehicle"] = 1.0
        buckets["location"] = 0.72
        extreme = np == "chain collision"
    elif np == "tyre burst":
        legacy["tyre_problem"] = 1.0
        buckets["vehicle"] = 0.82
    elif np in {"brake malfunction", "loss of control", "vehicle skidded"}:
        legacy["brake_failure"] = max(legacy.get("brake_failure", 0), 0.85)
        buckets["vehicle"] = 0.8
    elif np in {"rollover accident", "vehicle overturned"}:
        legacy["severity_injury"] = max(legacy.get("severity_injury", 0), 0.9)
        buckets["vehicle"] = 0.9
        extreme = True
    elif np == "major impact":
        legacy["severity_injury"] = max(legacy.get("severity_injury", 0), 0.75)
        buckets["behavioural"] = 0.7
    elif np == "minor impact":
        buckets["behavioural"] = 0.35
    elif np in {"head-on collision", "rear-end collision", "side collision"}:
        buckets["location"] = 0.62
        buckets["behavioural"] = 0.68

    if not buckets:
        buckets["behavioural"] = 0.5

    return legacy, buckets, extreme


def _score_injury(np: str) -> Tuple[Dict[str, float], Dict[str, float], bool]:
    legacy: Dict[str, float] = {}
    buckets: Dict[str, float] = {}
    extreme = False

    if np in {"fatal injuries", "deceased at scene"}:
        legacy["severity_fatal"] = 1.0
        buckets["behavioural"] = 0.98
        extreme = True
    elif np == "no injuries reported":
        return {}, {}, False
    elif "fatal" in np or np == "critical condition":
        legacy["severity_fatal"] = 1.0
        buckets["behavioural"] = 0.95
        extreme = True
    else:
        legacy["severity_injury"] = 1.0
        buckets["behavioural"] = 0.75

    return legacy, buckets, extreme


def _score_traffic(np: str) -> Tuple[Dict[str, float], Dict[str, float], bool]:
    legacy: Dict[str, float] = {}
    buckets: Dict[str, float] = {}
    extreme = False

    if np in {"traffic congestion"}:
        legacy["traffic_congestion"] = 1.0
        buckets["location"] = 0.62
    elif np in {"driving under influence", "dui"}:
        legacy["drunk_driving"] = 1.0
        buckets["behavioural"] = 1.0
        extreme = True
    elif np in {"traffic violation", "traffic offense", "speed limit"}:
        legacy["speeding"] = max(legacy.get("speeding", 0), 0.65)
        buckets["behavioural"] = 0.58
    elif np == "unroadworthy vehicle":
        legacy["tyre_problem"] = max(legacy.get("tyre_problem", 0), 0.7)
        buckets["vehicle"] = 0.72
    elif np in {"zebra crossing", "stop sign", "traffic lights"}:
        legacy["junction"] = max(legacy.get("junction", 0), 0.55)
        buckets["location"] = 0.5
    else:
        buckets["location"] = 0.35

    return legacy, buckets, extreme


def _supplementary_regex_hits(ct: str, pattern: re.Pattern[str]) -> bool:
    """True if pattern matches at least once and the match is not negated (e.g. not during rush hour)."""
    for m in pattern.finditer(ct):
        if not char_span_likely_negated(ct, m.start()):
            return True
    return False


def score_supplementary_text(cleaned_text: str) -> Tuple[Dict[str, float], Dict[str, float], List[str], bool]:
    """
    Non-gazette phrases and coarse cues (daytime, rural road, darkness).
    Returns deltas to merge, bucket deltas, extra matched keywords, extreme.
    """
    ct = cleaned_text.lower()
    legacy = empty_legacy()
    buckets = empty_buckets()
    matched: List[str] = []
    extreme = False

    if _supplementary_regex_hits(ct, re.compile(r"\b(daytime|during the day|in daylight)\b")):
        legacy["daytime"] = 1.0
        buckets["time"] = max(buckets["time"], 0.35)
        matched.append("daytime")

    if _supplementary_regex_hits(ct, re.compile(r"\b(off[\s-]?peak)\b")):
        legacy["off_peak"] = 1.0
        buckets["time"] = max(buckets["time"], 0.32)
        matched.append("off_peak")

    if _supplementary_regex_hits(ct, re.compile(r"\b(rush hour|peak hour)\b")):
        legacy["peak_hours"] = 1.0
        buckets["time"] = max(buckets["time"], 0.55)
        matched.append("peak_hours")

    if "rural road" in ct or re.search(r"\brural\b.*\broad\b", ct):
        legacy["rural_road"] = 1.0
        buckets["location"] = max(buckets["location"], 0.52)
        matched.append("rural road")

    if _supplementary_regex_hits(ct, re.compile(r"\b(midnight|1\s*am|2\s*am|11\s*pm)\b")):
        legacy["night_driving"] = max(legacy["night_driving"], 1.0)
        buckets["time"] = max(buckets["time"], 0.72)
        matched.append("late night")

    if _supplementary_regex_hits(ct, re.compile(r"\b(darkness|after dark|no street lights)\b")):
        legacy["darkness"] = 1.0
        buckets["environmental"] = max(buckets["environmental"], 0.55)
        matched.append("darkness")

    return legacy, buckets, matched, extreme
