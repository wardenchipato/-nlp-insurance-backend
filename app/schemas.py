from pydantic import BaseModel

class AccidentReport(BaseModel):
    """
    Input schema for accident report submission.
    """
    description: str

class ComponentScores(BaseModel):
    """
    Schema for individual risk component scores.
    """
    behavioural: float
    environmental: float
    time: float
    vehicle: float
    location: float

class RiskResponse(BaseModel):
    """
    Output schema for risk assessment response.
    """
    risk_class: str
    color: str
    recommendation: str
    final_score: float
    components: ComponentScores
    flags: list