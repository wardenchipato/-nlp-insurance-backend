from __future__ import annotations

from typing import Any, Dict, List, Optional


def _sec(title: str, detail: str, group: str) -> Dict[str, str]:
    return {"title": title, "detail": detail, "group": group}


def build_policyholder_explanation(
    *,
    matched_keywords: List[str],
    gazette_match_count: int = 0,
    nlp_unadjusted_components: Optional[Dict[str, float]] = None,
    kb_stats: Optional[Dict[str, Any]],
    kb_lifts: Dict[str, float],
    kb_corpus_category_lifts: Optional[Dict[str, float]] = None,
    kb_term_prevalence_lifts: Optional[Dict[str, float]] = None,
    narrative_buckets: Dict[str, float],
    structured_score: float,
    nlp_score_raw: float,
    nlp_score_adjusted: float,
    predicted_claim_risk_score: float,
    component_scores: Dict[str, float],
    form_kb_text_preview: str = "",
) -> Dict[str, Any]:
    """
    Human-readable trace: structured form index is the base; short location/placename text
    is matched for gazette + KB prevalence (e.g. 'Mutare' often in your accident corpus).
    """
    sections: List[Dict[str, str]] = []
    nlp_unadjusted_components = nlp_unadjusted_components or {}
    form_preview = (form_kb_text_preview or "").strip()

    comp_line = ", ".join(
        f"{k}={round(float(nlp_unadjusted_components.get(k, 0)), 1)}"
        for k in [
            "behavioural",
            "environmental",
            "time",
            "vehicle",
            "location",
            "claims_severity",
        ]
    )
    if comp_line.strip(", "):
        comp_line = " Per-dimension baselines (blend of underwriting index + declared exposure factors): " + comp_line + "."
    else:
        comp_line = ""

    kb_applied = bool(kb_stats and kb_stats.get("document_count", 0) > 0)
    calib_note = (
        f" Knowledge-base calibration adjusted that composite from {nlp_score_raw:.1f} to {nlp_score_adjusted:.1f}: "
        f"(a) how often each risk dimension appears across your real-accident files, and "
        f"(b) how often each matched phrase appears in those files—terms that dominate your corpus "
        f"(for example the place name Mutare if it appears in many uploads) add upward lift on the matching dimension "
        f"when the applicant typed similar wording in city/placename fields."
        if kb_applied
        else (
            f" No knowledge-base calibration was applied (no corpus snapshot), so the score stays at the "
            f"structured index before KB ({nlp_score_adjusted:.1f})."
        )
    )

    sections.append(
        _sec(
            "What drives your score (this submission)",
            (
                "**Primary inputs:** (1) Core underwriting fields produce one index (0–100). (2) Declared exposure "
                "checkboxes (behaviour, weather, roads, time, past severity—aligned with your accident-report feature lists) "
                "map into rule dimensions. Each calibrated dimension blends roughly 38% underwriting index + 62% factor score "
                "before knowledge-base lifts. "
                "**Optional placename text** (city or route keywords you entered) is **not** scored as a long accident "
                "story; it is only used to find gazette spans so we can look up how common those terms are in "
                "**your** stored accident texts. "
                "Example: if Mutare appears in a large share of files under backend/knowledge/, "
                "typing Mutare in city/placename fields raises the location lift when the corpus backs it."
            ),
            "submission",
        )
    )

    sections.append(
        _sec(
            "Step-by-step: how the number is built",
            (
                f"1. Structured form → underwriting index {structured_score:.1f} / 100. "
                f"2. Declared exposure factors → rule-based dimension scores; each dimension blends with that index "
                f"(see raw components below).{comp_line} "
                f"3. Optional city/place field text → {gazette_match_count} gazette span(s) for KB lookup only. "
                f"{(' Text used: “' + form_preview + '”.') if form_preview else ' No place text was entered, so only category-level KB lifts (if any) apply—no term-specific prevalence.'} "
                f"4. After calibration → {nlp_score_adjusted:.1f} / 100.{calib_note} "
                f"5. **Final score** = {predicted_claim_risk_score:.1f} / 100 (the calibrated composite; "
                f"no separate 70/30 blend with a free-text narrative)."
            ),
            "submission",
        )
    )

    sections.append(
        _sec(
            "Structured profile",
            (
                f"The core underwriting index from demographics, vehicle, usage, and distance is {structured_score:.1f} / 100. "
                "Declared exposure checkboxes are blended into each dimension before knowledge-base calibration."
            ),
            "submission",
        )
    )

    sections.append(
        _sec(
            "Place keywords (knowledge lookup only)",
            (
                "If you entered city or route keywords, they are scanned with the same gazette as your corpus pipeline "
                "— purely to attach corpus prevalence statistics, not to infer behaviour from a long narrative."
            ),
            "submission",
        )
    )

    if matched_keywords:
        sections.append(
            _sec(
                "Matched terms from your place fields",
                "Terms detected in **your** city/placename input: "
                + ", ".join(sorted(set(matched_keywords)))
                + ".",
                "submission",
            )
        )
    elif form_preview:
        sections.append(
            _sec(
                "Matched terms from your place fields",
                "No gazette phrases matched that short text—try wording from your lexicon (e.g. exact town names).",
                "submission",
            )
        )

    bucket_bits = ", ".join(
        f"{k}={narrative_buckets.get(k, 0):.2f}"
        for k in ["behavioural", "environmental", "time", "vehicle", "location"]
    )
    sections.append(
        _sec(
            "Keyword-match strength from place text (0–1)",
            "If place text matched the gazette, strength by bucket: " + bucket_bits + ".",
            "submission",
        )
    )

    if kb_stats and kb_stats.get("document_count", 0) > 0:
        doc_n = kb_stats["document_count"]
        src = kb_stats.get("source_documents") or []
        src_txt = ", ".join(src[:12]) + (" …" if len(src) > 12 else "") if src else "not recorded"
        cat_txt = ", ".join(f"{k}×{v}" for k, v in sorted((kb_corpus_category_lifts or {}).items()))
        term_txt = ", ".join(f"{k}×{v}" for k, v in sorted((kb_term_prevalence_lifts or {}).items()))
        lift_txt_eff = ", ".join(f"{k}×{v}" for k, v in sorted(kb_lifts.items()))
        sections.append(
            _sec(
                "Accident knowledge base influence",
                (
                    f"Statistics come from your knowledge/ corpus ({doc_n} non-empty document(s) "
                    f"in the last run: {src_txt}). "
                    f"(1) Dimension prevalence across files (category lifts: {cat_txt or 'n/a'}). "
                    f"(2) Phrase prevalence—when a term like Mutare appears in many accident files, "
                    f"and the applicant also typed it in city/placename fields, that dimension gets extra lift "
                    f"(term lifts: {term_txt or 'n/a'}). "
                    f"Combined effective multiplier per dimension: {lift_txt_eff}."
                ),
                "knowledge_base",
            )
        )
        top_kw = list((kb_stats.get("keyword_counts") or {}).items())[:8]
        if top_kw:
            pretty = ", ".join(f"{w} ({c}×)" for w, c in top_kw)
            sections.append(
                _sec(
                    "Frequent themes in your knowledge base",
                    f"Most common extracted terms across all stored files: {pretty}.",
                    "knowledge_base",
                )
            )
    else:
        sections.append(
            _sec(
                "Accident knowledge base influence",
                (
                    "No corpus snapshot is stored yet. Add .txt files under backend/knowledge/, "
                    "then run Analyse all in the admin UI so phrase prevalence (e.g. Mutare) can lift scores "
                    "when applicants mention the same places."
                ),
                "knowledge_base",
            )
        )

    sections.append(
        _sec(
            "Outcome",
            (
                f"Final predicted claim risk score: {predicted_claim_risk_score:.1f} / 100 "
                f"(calibrated form-based composite), then mapped to Low / Medium / High / Very High / Critical."
            ),
            "outcome",
        )
    )

    return {
        "sections": sections,
        "metrics": {
            "structured_score": round(structured_score, 2),
            "nlp_raw": round(nlp_score_raw, 2),
            "nlp_adjusted": round(nlp_score_adjusted, 2),
            "form_index_before_kb": round(structured_score, 2),
            "final_after_kb_calibration": round(predicted_claim_risk_score, 2),
            "gazette_match_count": gazette_match_count,
            "kb_document_count": (kb_stats or {}).get("document_count", 0),
            "kb_source_documents": (kb_stats or {}).get("source_documents") or [],
            "kb_aggregate_run_id": (kb_stats or {}).get("aggregate_run_id"),
            "kb_lifts": kb_lifts,
            "kb_corpus_category_lifts": kb_corpus_category_lifts or {},
            "kb_term_prevalence_lifts": kb_term_prevalence_lifts or {},
            "components_calibrated": {k: round(component_scores.get(k, 0), 2) for k in component_scores},
            "components_raw_nlp": {
                k: round(float(nlp_unadjusted_components.get(k, 0)), 2)
                for k in [
                    "behavioural",
                    "environmental",
                    "time",
                    "vehicle",
                    "location",
                    "claims_severity",
                ]
            },
            "form_kb_text_preview": form_preview[:240],
        },
    }
