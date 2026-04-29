def classify_risk(final_score: float) -> dict:
    """
    Classifies the final risk score into
    Low, Medium, or High risk category.
    """

    if final_score >= 67:
        risk_class = "High"
        color = "red"
        recommendation = (
            "High premium loading required. "
            "Consider coverage restrictions."
        )

    elif final_score >= 34:
        risk_class = "Medium"
        color = "yellow"
        recommendation = (
            "Moderate premium loading. "
            "Flag for underwriter review."
        )

    else:
        risk_class = "Low"
        color = "green"
        recommendation = (
            "Standard premium applies. "
            "No additional loading required."
        )

    return {
        "risk_class": risk_class,
        "color": color,
        "recommendation": recommendation,
        "final_score": round(final_score, 2),
    }