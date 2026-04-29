def extract_features(tokens: list) -> dict:
    """
    Extracts risk features from tokens using
    rule-based keyword matching.
    """

    # Define risk keyword rules
    rules = {
        # Behavioural Risk (B)
        "speeding": [
            "speeding", "sped", "overspeed", "accelerating",
            "overspeeding", "high speed", "speed", "fast", "racing"
        ],
        "drunk_driving": [
            "drunk", "intoxicated", "drank", "alcohol",
            "dui", "under influence", "drinking"
        ],
        "fatigue": [
            "fatigue", "asleep", "sleeping", "tired", "drowsy",
            "fell asleep", "exhausted", "sleepy"
        ],
        "distracted": [
            "phone", "mobile", "texting", "not paying attention",
            "distracted", "inattentive"
        ],
        "reckless": [
            "reckless", "overtaking", "dangerous", "careless",
            "negligent"
        ],

        # Environmental Risk (E)
        "rain": [
            "rain", "raining", "rainy", "slippery",
            "wet road", "wet highway", "rainfall", "wet"
        ],
        "fog": [
            "fog", "foggy", "mist", "misty", "visibility"
        ],
        "darkness": [
            "dark", "night", "darkness", "no lights"
        ],

        # Time Risk (T)
        "peak_hours": [
            "morning", "evening", "rush", "peak", "busy"
        ],
        "night_driving": [
            "night", "midnight", "late", "after dark"
        ],

        # Vehicle Risk (V)
        "brake_failure": [
            "brakes", "brake", "failed brakes",
            "no brakes", "brake failure"
        ],
        "tyre_problem": [
            "tyre", "tire", "puncture", "blowout", "flat"
        ],

        # Location Risk (L)
        "junction": [
            "junction", "intersection", "crossroads", "turning"
        ],
        "highway": [
            "highway", "motorway", "freeway", "expressway"
        ],
        "urban": [
            "urban", "city", "town", "street", "suburb"
        ],
    }

    # Match tokens against rules
    features = {}
    for feature, keywords in rules.items():
        features[feature] = int(
            any(token in keywords for token in tokens)
        )

    return features