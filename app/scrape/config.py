from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, List, Optional

import yaml

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_CONFIG_PATH = os.path.join(_REPO_ROOT, "scrape_sources.yaml")


@dataclass
class AccidentFilterConfig:
    enabled: bool = True
    min_score: int = 1
    # If true, listing-page link text must look accident-related (often finds nothing).
    prefilter_listing_links: bool = False
    extra_strong_phrases: List[str] = field(default_factory=list)
    extra_weak_terms: List[str] = field(default_factory=list)


@dataclass
class ScrapeSource:
    id: str
    enabled: bool = True
    source_label: str = ""
    listing_urls: List[str] = field(default_factory=list)
    article_link_match: List[str] = field(default_factory=list)
    exclude_link_match: List[str] = field(default_factory=list)
    max_articles: Optional[int] = None
    trust_accident_listing: bool = False


@dataclass
class ScrapeDefaults:
    max_articles_per_source: int = 12
    delay_seconds: float = 1.5
    request_timeout_seconds: float = 25.0
    user_agent: str = "NLP-Insurance-KB-Scraper/1.0"
    discovery_multiplier: int = 8


@dataclass
class ScrapeConfig:
    defaults: ScrapeDefaults
    sources: List[ScrapeSource]
    config_path: str
    accident_filter: AccidentFilterConfig = field(default_factory=AccidentFilterConfig)


def load_scrape_config(path: Optional[str] = None) -> ScrapeConfig:
    cfg_path = os.path.abspath(path or DEFAULT_CONFIG_PATH)
    if not os.path.isfile(cfg_path):
        raise FileNotFoundError(f"Scrape config not found: {cfg_path}")

    with open(cfg_path, "r", encoding="utf-8") as f:
        raw: Any = yaml.safe_load(f) or {}

    d = raw.get("defaults") or {}
    defaults = ScrapeDefaults(
        max_articles_per_source=int(d.get("max_articles_per_source", 12)),
        delay_seconds=float(d.get("delay_seconds", 1.5)),
        request_timeout_seconds=float(d.get("request_timeout_seconds", 25)),
        user_agent=str(d.get("user_agent", ScrapeDefaults.user_agent)),
        discovery_multiplier=int(d.get("discovery_multiplier", 8)),
    )

    af_raw = raw.get("accident_filter") or {}
    accident_filter = AccidentFilterConfig(
        enabled=bool(af_raw.get("enabled", True)),
        min_score=int(af_raw.get("min_score", 1)),
        prefilter_listing_links=bool(af_raw.get("prefilter_listing_links", False)),
        extra_strong_phrases=[
            str(x) for x in (af_raw.get("extra_strong_phrases") or []) if str(x).strip()
        ],
        extra_weak_terms=[
            str(x) for x in (af_raw.get("extra_weak_terms") or []) if str(x).strip()
        ],
    )

    sources: List[ScrapeSource] = []
    for item in raw.get("sources") or []:
        if not isinstance(item, dict):
            continue
        sid = str(item.get("id") or "").strip()
        if not sid:
            continue
        sources.append(
            ScrapeSource(
                id=sid,
                enabled=bool(item.get("enabled", True)),
                source_label=str(item.get("source_label") or sid),
                listing_urls=[str(u).strip() for u in (item.get("listing_urls") or []) if str(u).strip()],
                article_link_match=[str(x) for x in (item.get("article_link_match") or [])],
                exclude_link_match=[str(x) for x in (item.get("exclude_link_match") or [])],
                max_articles=(
                    int(item["max_articles"]) if item.get("max_articles") is not None else None
                ),
                trust_accident_listing=_source_trusts_accident_listing(item),
            )
        )

    return ScrapeConfig(
        defaults=defaults,
        sources=sources,
        config_path=cfg_path,
        accident_filter=accident_filter,
    )


def _source_trusts_accident_listing(item: dict) -> bool:
    if bool(item.get("trust_accident_listing", False)):
        return True
    for u in item.get("listing_urls") or []:
        low = str(u).lower()
        if "accident" in low or "road-accident" in low or "road_accident" in low:
            return True
    return False
