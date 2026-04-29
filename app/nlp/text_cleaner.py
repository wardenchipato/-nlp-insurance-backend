import re

def clean_text(text: str) -> str:
    """
    Cleans raw accident report text for NLP processing.
    """
    if not text:
        return ""

    # Convert to lowercase
    text = text.lower()

    # Expand common abbreviations
    abbreviations = {
        "veh": "vehicle",
        "rd": "road",
        "ave": "avenue",
        "dr": "driver",
        "acc": "accident",
        "spd": "speed",
        "jnc": "junction",
    }

    for short, full in abbreviations.items():
        text = re.sub(r'\b' + short + r'\b', full, text)

    # Remove special characters but keep spaces
    text = re.sub(r'[^a-z\s]', '', text)

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text