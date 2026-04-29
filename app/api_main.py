from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas import AccidentReport, RiskResponse
from nlp.text_cleaner import clean_text
from nlp.tokenizer import tokenize
from nlp.feature_extractor import extract_features
from scoring.risk_engine import calculate_risk_score
from scoring.classifier import classify_risk

# Initialize FastAPI app
app = FastAPI(
    title="Motor Insurance Risk Assessment API",
    description="NLP-powered risk prediction system",
    version="1.0.0"
)

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Motor Insurance Risk API Running",
        "status": "online"
    }

@app.post("/predict")
def predict_risk(report: AccidentReport):
    """
    Main endpoint - takes accident description
    and returns risk assessment.
    """

    # Step 1 - Clean the text
    cleaned = clean_text(report.description)

    # Step 2 - Tokenize
    tokens = tokenize(cleaned)

    # Step 3 - Extract features
    features = extract_features(tokens)

    # Step 4 - Calculate risk score
    scores = calculate_risk_score(features)

    # Step 5 - Classify risk
    result = classify_risk(scores["final_score"])

    # Get detected risk flags
    flags = [
        key for key, value
        in features.items()
        if value == 1
    ]

    return {
        "risk_class": result["risk_class"],
        "color": result["color"],
        "recommendation": result["recommendation"],
        "final_score": scores["final_score"],
        "components": {
            "behavioural": scores["behavioural"],
            "environmental": scores["environmental"],
            "time": scores["time"],
            "vehicle": scores["vehicle"],
            "location": scores["location"],
        },
        "flags": flags
    }