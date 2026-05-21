"""
Motor insurance narrative risk scoring.

Composite narrative score (before KB calibration):
    R = 0.35*B + 0.10*E + 0.10*T + 0.15*V + 0.10*L + 0.20*C

B–L,C are 0–100 subscores built from cumulative keyword-style points (policy tables),
with interaction bonuses (e.g. DUI + speeding +20; rain + night +10).
"""


def _active(features: dict, key: str) -> bool:
    return float(features.get(key, 0) or 0) >= 0.5


def _clamp_component(raw: float) -> float:
    return round(min(100.0, max(0.0, raw)), 2)


def calculate_risk_score(features: dict) -> dict:
    """
    Map gazette-driven legacy flags to six dimensions (0–100 each), then weighted sum.

    Behavioural (cumulative points; cap 100):
      speeding +25, drunk_driving +40, reckless +30, distracted +20, fatigue +15
      — drunk + speeding: +20 — night_driving + drunk: +15

    Environmental: rain/fog/poor_visibility +10, wet_roads +10, wind +6, darkness +8
      — rain + night_driving: +10

    Time: night_driving +12, peak_hours +8 — off_peak + speeding: +10

    Vehicle: brake_failure +20, tyre_problem +18, commercial_vehicle_context +12

    Location: highway +12, junction +10, traffic_congestion +8, rural_road +6, urban +8

    Claims/Severity (separate from behaviour): fatal +50, injury +20, multi_vehicle +15
    """
    # --- Behavioural ---
    b_pts = 0.0
    if _active(features, "speeding"):
        b_pts += 25
    if _active(features, "drunk_driving"):
        b_pts += 40
    if _active(features, "reckless"):
        b_pts += 30
    if _active(features, "distracted"):
        b_pts += 20
    if _active(features, "fatigue"):
        b_pts += 15
    if _active(features, "drunk_driving") and _active(features, "speeding"):
        b_pts += 20
    if _active(features, "drunk_driving") and _active(features, "night_driving"):
        b_pts += 15

    behavioural = _clamp_component(b_pts)

    # --- Environmental ---
    e_pts = 0.0
    if _active(features, "rain"):
        e_pts += 10
    if _active(features, "fog"):
        e_pts += 10
    if _active(features, "poor_visibility"):
        e_pts += 10
    if _active(features, "wet_roads"):
        e_pts += 10
    if _active(features, "wind"):
        e_pts += 6
    if _active(features, "darkness"):
        e_pts += 8
    if _active(features, "rain") and _active(features, "night_driving"):
        e_pts += 10

    environmental = _clamp_component(e_pts)

    # --- Time ---
    t_pts = 0.0
    if _active(features, "night_driving"):
        t_pts += 12
    if _active(features, "peak_hours"):
        t_pts += 8
    if _active(features, "off_peak") and _active(features, "speeding"):
        t_pts += 10

    time = _clamp_component(t_pts)

    # --- Vehicle ---
    v_pts = 0.0
    if _active(features, "brake_failure"):
        v_pts += 20
    if _active(features, "tyre_problem"):
        v_pts += 18
    if _active(features, "commercial_vehicle_context"):
        v_pts += 12

    vehicle = _clamp_component(v_pts)

    # --- Location ---
    l_pts = 0.0
    if _active(features, "highway"):
        l_pts += 12
    if _active(features, "junction"):
        l_pts += 10
    if _active(features, "traffic_congestion"):
        l_pts += 8
    if _active(features, "rural_road"):
        l_pts += 6
    if _active(features, "urban"):
        l_pts += 8

    location = _clamp_component(l_pts)

    # --- Claims / severity (not folded into behavioural) ---
    c_pts = 0.0
    if _active(features, "severity_fatal"):
        c_pts += 50
    if _active(features, "severity_injury"):
        c_pts += 20
    if _active(features, "severity_multi_vehicle"):
        c_pts += 15

    claims_severity = _clamp_component(c_pts)

    weights = {
        "behavioural": 0.35,
        "environmental": 0.10,
        "time": 0.10,
        "vehicle": 0.15,
        "location": 0.10,
        "claims_severity": 0.20,
    }

    final_score = round(
        weights["behavioural"] * behavioural
        + weights["environmental"] * environmental
        + weights["time"] * time
        + weights["vehicle"] * vehicle
        + weights["location"] * location
        + weights["claims_severity"] * claims_severity,
        2,
    )

    return {
        "behavioural": behavioural,
        "environmental": environmental,
        "time": time,
        "vehicle": vehicle,
        "location": location,
        "claims_severity": claims_severity,
        "final_score": final_score,
    }


def legacy_features_from_policy_form(data) -> dict:
    """
    Map standardized form + declared exposure checkboxes to LEGACY_KEYS (0/1 floats).
    Aligns with System Doc accident-report features and risk-rule dimensions.
    """
    from app.nlp.gazette_mapping import empty_legacy

    leg = empty_legacy()

    def _set(key: str, val: float) -> None:
        if key in leg:
            leg[key] = max(float(leg.get(key, 0)), float(val))

    if getattr(data, "typical_speeding", False):
        _set("speeding", 1.0)
    if getattr(data, "typical_drunk_driving_risk", False):
        _set("drunk_driving", 1.0)
    if getattr(data, "typical_phone_distraction", False):
        _set("distracted", 1.0)
    if getattr(data, "typical_reckless_or_overtake", False):
        _set("reckless", 1.0)
    if getattr(data, "typical_driver_fatigue", False):
        _set("fatigue", 1.0)

    if getattr(data, "typical_heavy_rain", False):
        _set("rain", 1.0)
    if getattr(data, "typical_fog", False):
        _set("fog", 1.0)
    if getattr(data, "typical_strong_wind", False):
        _set("wind", 1.0)
    if getattr(data, "typical_poor_visibility", False):
        _set("poor_visibility", 1.0)
    if getattr(data, "typical_darkness_low_light", False):
        _set("darkness", 1.0)
    if getattr(data, "typical_wet_slippery_roads", False):
        _set("wet_roads", 1.0)

    if getattr(data, "often_highway_driving", False):
        _set("highway", 1.0)
    if getattr(data, "often_intersections_junctions", False):
        _set("junction", 1.0)
    if getattr(data, "often_heavy_traffic_congestion", False):
        _set("traffic_congestion", 1.0)
    if getattr(data, "often_rural_roads", False):
        _set("rural_road", 1.0)

    if getattr(data, "often_drive_at_night", False):
        _set("night_driving", 1.0)
    if getattr(data, "often_peak_hour_travel", False):
        _set("peak_hours", 1.0)
    if getattr(data, "often_off_peak_travel", False):
        _set("off_peak", 1.0)
    if getattr(data, "mostly_daytime_driving", False):
        _set("daytime", 1.0)

    if getattr(data, "vehicle_brake_issues_known", False):
        _set("brake_failure", 1.0)

    tc = (getattr(data, "tyre_condition", "good") or "good").lower()
    if tc == "poor":
        _set("tyre_problem", 1.0)
    elif tc == "fair":
        _set("tyre_problem", 0.55)

    vt = getattr(data, "vehicle_type", "Car") or "Car"
    if vt.lower() == "truck":
        _set("commercial_vehicle_context", 1.0)
    ut = getattr(data, "usage_type", "Private") or "Private"
    if ut.lower() == "commercial":
        _set("commercial_vehicle_context", 1.0)

    at = getattr(data, "area_type", "") or ""
    if at.lower() == "urban":
        _set("urban", 1.0)
    elif at.lower() == "rural":
        _set("rural_road", 1.0)

    if getattr(data, "past_accident_injury", False):
        _set("severity_injury", 1.0)
    if getattr(data, "past_accident_fatality_involved", False):
        _set("severity_fatal", 1.0)
    if getattr(data, "past_multi_vehicle_accident", False):
        _set("severity_multi_vehicle", 1.0)

    return leg


def score_structured_data(data) -> float:
    """
    Structured underwriting index 0–100 from demographics, vehicle, usage, distance.
    """
    score = 0.0
    if data.driver_age < 25:
        score += 20
    elif data.driver_age > 65:
        score += 10
    score += data.prior_claims * 15
    if data.vehicle_type.lower() == "motorcycle":
        score += 20
    elif data.vehicle_type.lower() == "truck":
        score += 10
    if data.area_type.lower() == "urban":
        score += 10
    if data.usage_type.lower() == "commercial":
        score += 10

    va = int(getattr(data, "vehicle_age", 0) or 0)
    if va >= 15:
        score += 10
    elif va >= 10:
        score += 5

    ecc = int(getattr(data, "engine_capacity_cc", 0) or 0)
    if ecc >= 3000:
        score += 14
    elif ecc >= 2000:
        score += 8
    elif ecc >= 1600:
        score += 4

    val = float(getattr(data, "vehicle_value", 0) or 0)
    if val > 0:
        if val >= 50000:
            score += 10
        elif val >= 25000:
            score += 6
        elif val <= 4000:
            score += 5

    km = int(getattr(data, "annual_distance_km", 0) or 0)
    if km >= 40000:
        score += 18
    elif km >= 25000:
        score += 12
    elif km >= 15000:
        score += 6

    return min(score, 100)


def claims_proxy_from_legacy(legacy: dict | None) -> float:
    """0–100 severity proxy from narrative legacy flags (used in KB aggregate)."""
    if not legacy:
        return 0.0
    c_pts = 0.0
    if _active(legacy, "severity_fatal"):
        c_pts += 50
    if _active(legacy, "severity_injury"):
        c_pts += 20
    if _active(legacy, "severity_multi_vehicle"):
        c_pts += 15
    return min(100.0, c_pts)


def _kb_term_prevalence_lifts(
    kb_stats: dict | None,
    gazette_matches: list | None,
) -> dict[str, float]:
    """
    Terms that appear in a large share of real-accident KB files get stronger lift when
    they also appear in the current narrative (dimension-specific).
    """
    dims = [
        "behavioural",
        "environmental",
        "time",
        "vehicle",
        "location",
        "claims_severity",
    ]
    neutral = {k: 1.0 for k in dims}
    if not kb_stats or not gazette_matches:
        return dict(neutral)
    shares = kb_stats.get("keyword_doc_share") or {}
    if not shares:
        return dict(neutral)

    from app.nlp.gazette_mapping import normalize_phrase
    from app.scoring.kb_dimensions import gazette_match_to_dimension

    prev_by_dim: dict[str, list[float]] = {k: [] for k in dims}
    for gm in gazette_matches:
        if not isinstance(gm, dict):
            continue
        phrase = str(gm.get("phrase") or "")
        label = str(gm.get("label") or "")
        np = normalize_phrase(phrase)
        dim = gazette_match_to_dimension(label, np)
        if dim is None or not np:
            continue
        p = float(shares.get(np, 0.0))
        if p > 0:
            prev_by_dim[dim].append(p)

    gamma = 0.48
    cap = 1.28
    out: dict[str, float] = {}
    for d in dims:
        pts = prev_by_dim[d]
        if not pts:
            out[d] = 1.0
            continue
        mean_p = sum(pts) / len(pts)
        lift = 1.0 + gamma * mean_p
        out[d] = round(min(cap, max(1.0, lift)), 3)
    return out


def _corpus_recency_calibration_factor(kb_stats: dict | None) -> float:
    """
    When aggregate stats were built with report-date recency weights, scale KB lifts slightly
    so a corpus dominated by older press releases applies gentler calibration.
    """
    if not kb_stats or not kb_stats.get("recency_weighted"):
        return 1.0
    prov = kb_stats.get("report_provenance") or []
    if not prov:
        wdc = float(kb_stats.get("weighted_document_count") or 0)
        doc_n = float(kb_stats.get("document_count") or 0)
        if doc_n > 0 and wdc > 0:
            mean_w = wdc / doc_n
        else:
            return 1.0
    else:
        weights = [float(p.get("recency_weight") or 0.5) for p in prov if isinstance(p, dict)]
        mean_w = sum(weights) / len(weights) if weights else 0.5
    # mean_w in [0.12, 1.0] → factor in [0.88, 1.0]
    return round(0.88 + 0.12 * mean_w, 4)


def _adjust_nlp_with_kb(
    nlp_scores: dict,
    kb_stats: dict | None,
    gazette_matches: list | None = None,
) -> tuple[dict, dict, dict, dict, float, float]:
    """
    Apply (1) category prevalence lifts from the KB corpus and (2) term prevalence lifts:
    terms that appear in many real-accident files get extra weight when matched in this narrative.

    Corpus aggregates and keyword prevalence use recency weighting by report date when
    metadata headers are present in knowledge .txt files (older reports contribute less).

    Returns (
      adjusted_scores,
      combined_lifts (effective multiplier per dimension),
      category_lifts only,
      term_prevalence_lifts only,
      raw_final,
      adjusted_final,
    )
    """
    raw_final = float(nlp_scores["final_score"])
    dims = [
        "behavioural",
        "environmental",
        "time",
        "vehicle",
        "location",
        "claims_severity",
    ]
    if not kb_stats or kb_stats.get("document_count", 0) == 0:
        neutral = {k: 1.0 for k in dims}
        return dict(nlp_scores), dict(neutral), dict(neutral), dict(neutral), raw_final, raw_final

    weights = {
        "behavioural": 0.35,
        "environmental": 0.10,
        "time": 0.10,
        "vehicle": 0.15,
        "location": 0.10,
        "claims_severity": 0.20,
    }
    alpha = 0.65
    recency_factor = _corpus_recency_calibration_factor(kb_stats)
    combined_lifts: dict[str, float] = {}
    category_lifts: dict[str, float] = {}
    adjusted: dict[str, float] = {}
    shares = kb_stats.get("category_doc_share") or {}
    term_lifts = _kb_term_prevalence_lifts(kb_stats, gazette_matches)

    for key in dims:
        share = float(shares.get(key, 0.0) or 0.0)
        cat_lift = 1.0 + alpha * (share - 0.15)
        cat_lift = max(0.82, min(1.30, cat_lift))
        # Pull lifts toward neutral when the weighted corpus is mostly older reports
        cat_lift = 1.0 + (cat_lift - 1.0) * recency_factor
        category_lifts[key] = round(cat_lift, 3)
        tl = float(term_lifts.get(key, 1.0))
        tl = 1.0 + (tl - 1.0) * recency_factor
        combined = min(1.48, cat_lift * tl)
        combined_lifts[key] = round(combined, 3)
        adjusted[key] = round(min(100.0, float(nlp_scores[key]) * combined), 2)

    adjusted_final = round(
        sum(weights[k] * adjusted[k] for k in weights),
        2,
    )
    out = {
        "behavioural": adjusted["behavioural"],
        "environmental": adjusted["environmental"],
        "time": adjusted["time"],
        "vehicle": adjusted["vehicle"],
        "location": adjusted["location"],
        "claims_severity": adjusted["claims_severity"],
        "final_score": adjusted_final,
    }
    return out, combined_lifts, category_lifts, term_lifts, raw_final, adjusted_final


def calculate_policyholder_risk_score(
    data,
    kb_stats: dict | None = None,
    gazette_matches: list | None = None,
) -> dict:
    """
    Blends (1) structured underwriting index and (2) rule dimensions from declared exposure
    (System Doc features / risk tables), then applies knowledge-base calibration on placename gazette hits.

    Per dimension: baseline[k] = W_U * structured_score + W_F * factor_score[k]
    where factor_score comes from legacy_features_from_policy_form → calculate_risk_score.
    """
    structured_score = float(score_structured_data(data))
    legacy = legacy_features_from_policy_form(data)
    factor_scores = calculate_risk_score(legacy)

    dims = [
        "behavioural",
        "environmental",
        "time",
        "vehicle",
        "location",
        "claims_severity",
    ]
    w_u, w_f = 0.38, 0.62
    nlp_scores: dict = {}
    for k in dims:
        fk = float(factor_scores.get(k, 0.0))
        nlp_scores[k] = round(min(100.0, structured_score * w_u + fk * w_f), 2)

    weights = {
        "behavioural": 0.35,
        "environmental": 0.10,
        "time": 0.10,
        "vehicle": 0.15,
        "location": 0.10,
        "claims_severity": 0.20,
    }
    nlp_scores["final_score"] = round(sum(weights[k] * nlp_scores[k] for k in dims), 2)

    adjusted, kb_lifts, kb_cat_lifts, kb_term_lifts, nlp_raw_final, nlp_adj_final = _adjust_nlp_with_kb(
        nlp_scores,
        kb_stats,
        gazette_matches,
    )

    return {
        "behavioural": adjusted["behavioural"],
        "environmental": adjusted["environmental"],
        "time": adjusted["time"],
        "vehicle": adjusted["vehicle"],
        "location": adjusted["location"],
        "claims_severity": adjusted["claims_severity"],
        "predicted_claim_risk_score": nlp_adj_final,
        "_nlp_raw_final": nlp_raw_final,
        "_nlp_adjusted_final": nlp_adj_final,
        "_structured_score": structured_score,
        "_factor_scores_raw": {k: factor_scores[k] for k in dims},
        "_legacy_from_form": legacy,
        "_kb_lifts": kb_lifts,
        "_kb_category_lifts": kb_cat_lifts,
        "_kb_term_prevalence_lifts": kb_term_lifts,
        "_nlp_unadjusted_components": {k: nlp_scores[k] for k in dims},
    }
