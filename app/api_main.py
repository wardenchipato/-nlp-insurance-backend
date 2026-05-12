import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.schemas import PolicyholderAssessRequest, PolicyholderAssessResponse
from app.nlp.analysis import analyze_text
from app.nlp.gazette_mapping import empty_buckets, empty_legacy
from app.nlp.text_cleaner import clean_text
from app.scoring.risk_engine import calculate_policyholder_risk_score, legacy_features_from_policy_form
from app.scoring.classifier import classify_policyholder_risk
from app.scoring.explanation import build_policyholder_explanation
from app.kb.router import router as kb_router
from app.kb import service as kb_service
from app.kb.paths import ensure_kb_dirs
from app.db.store import init_db

_BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
KB_ADMIN_DIST = os.path.join(_BACKEND_ROOT, "kb-admin", "dist")


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_kb_dirs()
    init_db()
    yield


app = FastAPI(
    title="Motor Insurance Risk Assessment API",
    description="Standardized form underwriting index with optional placename keywords for knowledge-base calibration "
    "(corpus phrase prevalence). Accident texts in knowledge/ drive NLP statistics; gazette matches on form fields "
    "lift scores when terms are frequent in your corpus (e.g. Mutare).",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(kb_router)


def _empty_nlp_ctx() -> dict:
    return {
        "buckets": empty_buckets(),
        "legacy_features": empty_legacy(),
        "matched_keywords": [],
        "extreme_risk": False,
        "gazette_matches": [],
    }


def _form_text_for_kb(report: PolicyholderAssessRequest) -> str:
    parts = [report.primary_city_or_region, report.additional_place_keywords]
    return " ".join(p.strip() for p in parts if (p or "").strip())


@app.get("/")
def home():
    return {
        "message": "Motor Insurance Risk API",
        "status": "online",
        "endpoints": {
            "assess": "POST /api/assess",
            "knowledge_base": "/api/kb/*",
            "kb_websocket": "WS /ws/kb",
        },
        "kb_admin": "/admin/" if os.path.isdir(KB_ADMIN_DIST) else None,
    }


@app.post("/api/assess", response_model=PolicyholderAssessResponse)
def assess_policyholder_risk(report: PolicyholderAssessRequest):
    form_kb = _form_text_for_kb(report)
    if form_kb.strip():
        nlp_ctx = analyze_text(clean_text(form_kb))
    else:
        nlp_ctx = _empty_nlp_ctx()

    kb_stats = kb_service.load_stats()
    scores = calculate_policyholder_risk_score(
        report,
        kb_stats,
        gazette_matches=nlp_ctx.get("gazette_matches"),
    )
    classification = classify_policyholder_risk(scores["predicted_claim_risk_score"])

    leg = legacy_features_from_policy_form(report)
    indicators = [
        key.replace("_", " ").title() for key, value in leg.items() if float(value or 0) >= 0.5
    ]
    if report.prior_claims >= 3:
        indicators.append("Prior claims (3+)")
    elif report.prior_claims >= 1:
        indicators.append("Prior claims")

    kb_doc_n = int(kb_stats.get("document_count") or 0)
    kb_lifts = scores.get("_kb_lifts") or {}
    kb_corpus_cat = scores.get("_kb_category_lifts") or {}
    kb_term_prev = scores.get("_kb_term_prevalence_lifts") or {}

    explanation = build_policyholder_explanation(
        matched_keywords=nlp_ctx.get("matched_keywords") or [],
        gazette_match_count=len(nlp_ctx.get("gazette_matches") or []),
        nlp_unadjusted_components=scores.get("_nlp_unadjusted_components"),
        kb_stats=kb_stats if kb_doc_n > 0 else None,
        kb_lifts=kb_lifts,
        kb_corpus_category_lifts=kb_corpus_cat,
        kb_term_prevalence_lifts=kb_term_prev,
        narrative_buckets=nlp_ctx.get("buckets") or {},
        structured_score=float(scores.get("_structured_score", 0)),
        nlp_score_raw=float(scores.get("_nlp_raw_final", 0)),
        nlp_score_adjusted=float(scores.get("_nlp_adjusted_final", 0)),
        predicted_claim_risk_score=float(scores["predicted_claim_risk_score"]),
        component_scores={
            "behavioural": scores["behavioural"],
            "environmental": scores["environmental"],
            "time": scores["time"],
            "vehicle": scores["vehicle"],
            "location": scores["location"],
            "claims_severity": scores["claims_severity"],
        },
        form_kb_text_preview=_form_text_for_kb(report)[:240],
    )

    return PolicyholderAssessResponse(
        policyholder_risk_class=classification["policyholder_risk_class"],
        predicted_claim_risk_score=scores["predicted_claim_risk_score"],
        component_breakdown={
            "behavioural": scores["behavioural"],
            "environmental": scores["environmental"],
            "time": scores["time"],
            "vehicle": scores["vehicle"],
            "location": scores["location"],
            "claims_severity": scores["claims_severity"],
        },
        risk_indicators=indicators,
        underwriting_recommendation=classification["underwriting_recommendation"],
        matched_nlp_keywords=nlp_ctx.get("matched_keywords") or [],
        gazette_matches=nlp_ctx.get("gazette_matches") or [],
        narrative_bucket_profile=nlp_ctx.get("buckets") or {},
        kb_document_count=kb_doc_n,
        kb_category_lifts=kb_lifts,
        kb_corpus_category_lifts=kb_corpus_cat,
        kb_term_prevalence_lifts=kb_term_prev,
        risk_decision_explanation=explanation,
    )


@app.websocket("/ws/kb")
async def kb_analyze_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        msg = await websocket.receive_json()
        if msg.get("action") != "analyze_all":
            await websocket.send_json({"type": "error", "message": "Use action=analyze_all"})
            return

        async def broadcast(payload: dict) -> None:
            await websocket.send_json(payload)

        await kb_service.analyze_all_files_async(broadcast)
    except WebSocketDisconnect:
        pass
    except Exception as exc:  # noqa: BLE001
        try:
            await websocket.send_json({"type": "error", "message": str(exc)})
        except Exception:
            pass


if os.path.isdir(KB_ADMIN_DIST):
    app.mount(
        "/admin",
        StaticFiles(directory=KB_ADMIN_DIST, html=True),
        name="kb_admin",
    )
