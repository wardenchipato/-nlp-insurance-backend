def calculate_risk_score(features: dict) -> dict:
    """
    Applies weighted risk formula:
    R = w1*B + w2*E + w3*T + w4*V + w5*L
    """

    # Weights for each component.
    # Behavioural remains primary, while other components stay meaningful.
    weights = {
        "behavioural": 0.35,
        "environmental": 0.20,
        "time": 0.15,
        "vehicle": 0.20,
        "location": 0.10,
    }

    # Per-feature points: each detected feature adds its full points.
    # Component totals are capped at 100 to prevent runaway inflation.
    behavioural_map = {
        "speeding": 35,
        "drunk_driving": 40,
        "fatigue": 18,
        "distracted": 15,
        "reckless": 22,
    }
    environmental_map = {
        "rain": 22,
        "fog": 28,
        "darkness": 18,
    }
    time_map = {
        "peak_hours": 20,
        "night_driving": 28,
    }
    vehicle_map = {
        "brake_failure": 45,
        "tyre_problem": 30,
    }
    location_map = {
        "junction": 25,
        "highway": 22,
        "urban": 18,
    }

    def component_score(points_map: dict) -> float:
        detected_points = sum(
            features.get(feature, 0) * points
            for feature, points in points_map.items()
        )
        return float(min(100, detected_points))

    behavioural = component_score(behavioural_map)
    environmental = component_score(environmental_map)
    time = component_score(time_map)
    vehicle = component_score(vehicle_map)
    location = component_score(location_map)

    # Apply weighted formula
    base_score = (
        weights["behavioural"] * behavioural +
        weights["environmental"] * environmental +
        weights["time"] * time +
        weights["vehicle"] * vehicle +
        weights["location"] * location
    )

    # Combined-risk boosts to reflect severe interacting factors.
    combo_bonus = 0.0
    if features.get("speeding", 0) and features.get("drunk_driving", 0):
        combo_bonus += 10.0
    if (
        features.get("speeding", 0)
        and features.get("drunk_driving", 0)
        and features.get("brake_failure", 0)
    ):
        combo_bonus += 22.0
    if features.get("fatigue", 0) and features.get("distracted", 0):
        combo_bonus += 6.0
    if features.get("reckless", 0) and features.get("highway", 0):
        combo_bonus += 5.0

    # Business cap: keep maximum score below absolute ceiling.
    final_score = round(min(95.0, base_score + combo_bonus), 2)

    # Return all component scores
    return {
        "behavioural": round(behavioural, 2),
        "environmental": round(environmental, 2),
        "time": round(time, 2),
        "vehicle": round(vehicle, 2),
        "location": round(location, 2),
        "final_score": final_score,
    }