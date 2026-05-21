from __future__ import annotations

import json
import os
from typing import Dict, Set

from app.kb.paths import LOCAL_DB_PATH

_STATE_DIR = os.path.dirname(LOCAL_DB_PATH)
_STATE_PATH = os.path.join(_STATE_DIR, "scraped_urls.json")


def load_url_mapping() -> Dict[str, str]:
    if not os.path.isfile(_STATE_PATH):
        return {}
    try:
        with open(_STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()}
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def load_scraped_urls() -> Set[str]:
    """URLs recorded on past runs (informational only; scraper does not skip by this)."""
    return set(load_url_mapping().keys())


def save_scraped_url(url: str, filename: str) -> None:
    os.makedirs(_STATE_DIR, exist_ok=True)
    mapping: Dict[str, str] = {}
    if os.path.isfile(_STATE_PATH):
        try:
            with open(_STATE_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, dict):
                mapping = {str(k): str(v) for k, v in raw.items()}
        except (json.JSONDecodeError, OSError):
            mapping = {}
    mapping[url] = filename
    with open(_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2)
