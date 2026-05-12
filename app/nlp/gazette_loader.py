"""Load gazette CSV from backend/gazette/."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List


def gazette_csv_path() -> Path:
    # app/nlp/gazette_loader.py -> parents[2] == backend/
    return Path(__file__).resolve().parents[2] / "gazette" / "large_spacy_gazetteer_insurance_nlp.csv"


def load_gazette_rows() -> List[Dict[str, Any]]:
    path = gazette_csv_path()
    if not path.is_file():
        return []
    rows: List[Dict[str, Any]] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            phrase = (row.get("phrase") or "").strip()
            if not phrase:
                continue
            rows.append(
                {
                    "phrase": phrase,
                    "label": (row.get("label") or "").strip(),
                    "category": (row.get("category") or "").strip(),
                }
            )
    return rows
