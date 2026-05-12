from pydantic import BaseModel, Field


class ComponentScores(BaseModel):
    behavioural: float
    environmental: float
    time: float
    vehicle: float
    location: float
    claims_severity: float


class PolicyholderAssessRequest(BaseModel):
    """
    Standardized underwriting + declared exposure (maps to risk-engine legacy flags).
    Place fields feed gazette/KB only; booleans feed calculate_risk_score-style dimensions.
    """

    primary_city_or_region: str = ""
    additional_place_keywords: str = ""
    accident_history_narrative: str = ""

    driver_age: int
    gender: str
    years_licensed: int
    prior_claims: int

    vehicle_type: str
    vehicle_age: int
    engine_capacity_cc: int = 0
    vehicle_value: float = 0.0
    annual_distance_km: int = 0

    area_type: str
    usage_type: str

    tyre_condition: str = Field(
        default="good",
        description='Tyre condition: "good", "fair", or "poor"',
    )
    vehicle_brake_issues_known: bool = False

    typical_speeding: bool = False
    typical_drunk_driving_risk: bool = False
    typical_phone_distraction: bool = False
    typical_reckless_or_overtake: bool = False
    typical_driver_fatigue: bool = False

    typical_heavy_rain: bool = False
    typical_fog: bool = False
    typical_strong_wind: bool = False
    typical_poor_visibility: bool = False
    typical_darkness_low_light: bool = False
    typical_wet_slippery_roads: bool = False

    often_highway_driving: bool = False
    often_intersections_junctions: bool = False
    often_heavy_traffic_congestion: bool = False
    often_rural_roads: bool = False

    often_drive_at_night: bool = False
    often_peak_hour_travel: bool = False
    often_off_peak_travel: bool = False
    mostly_daytime_driving: bool = False

    past_accident_injury: bool = False
    past_accident_fatality_involved: bool = False
    past_multi_vehicle_accident: bool = False


class PolicyholderAssessResponse(BaseModel):
    policyholder_risk_class: str
    predicted_claim_risk_score: float
    component_breakdown: ComponentScores
    risk_indicators: list[str]
    underwriting_recommendation: str
    matched_nlp_keywords: list[str] = []
    gazette_matches: list[dict] = []
    narrative_bucket_profile: dict = {}
    kb_document_count: int = 0
    kb_category_lifts: dict = {}
    kb_corpus_category_lifts: dict = {}
    kb_term_prevalence_lifts: dict = {}
    risk_decision_explanation: dict = {}
