def classify_policyholder_risk(predicted_claim_risk_score: float) -> dict:
    """
    Map blended 0–100 score to underwriting bands:
    0–20 Low, 21–40 Medium, 41–60 High, 61–80 Very High, 81+ Critical.
    """
    s = float(predicted_claim_risk_score)

    if s >= 81:
        policyholder_risk_class = "Critical"
        recommendation = (
            "This policyholder presents CRITICAL future claim risk based on the assessed profile. "
            "Immediate underwriting review, strong premium loading, and strict coverage terms are indicated."
        )
    elif s >= 61:
        policyholder_risk_class = "Very High"
        recommendation = (
            "This policyholder presents VERY HIGH future claim risk. "
            "Apply substantial premium loading and detailed underwriting review."
        )
    elif s >= 41:
        policyholder_risk_class = "High"
        recommendation = (
            "This policyholder presents HIGH future claim risk based on assessed patterns. "
            "Apply premium loading and consider coverage restrictions."
        )
    elif s >= 21:
        policyholder_risk_class = "Medium"
        recommendation = (
            "This policyholder presents MODERATE future claim risk. "
            "Apply moderate premium loading and underwriter review."
        )
    else:
        policyholder_risk_class = "Low"
        recommendation = (
            "This policyholder presents LOW future claim risk. "
            "Standard premium terms are generally appropriate."
        )

    return {
        "policyholder_risk_class": policyholder_risk_class,
        "underwriting_recommendation": recommendation,
    }
