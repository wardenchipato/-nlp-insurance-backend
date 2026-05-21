#!/usr/bin/env python3
"""
Scrape news listings into knowledge/*.txt (same storage as manual KB uploads).

Usage (from repo root):
  py scripts/run_scraper.py
  py scripts/run_scraper.py --source newsday_accidents
  py scripts/run_scraper.py -v

Config: scrape_sources.yaml at repo root.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from app.kb.paths import KNOWLEDGE_DIR
from app.scrape.runner import run_scraper


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scrape configured news sources into knowledge/ .txt files",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to scrape_sources.yaml (default: repo root scrape_sources.yaml)",
    )
    parser.add_argument(
        "--source",
        action="append",
        dest="sources",
        metavar="ID",
        help="Only run these source ids from scrape_sources.yaml (repeatable)",
    )
    parser.add_argument(
        "--no-sync",
        action="store_true",
        help="Skip knowledge folder DB sync after scrape",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    print(f"Knowledge directory: {KNOWLEDGE_DIR}")
    print(f"Config: {args.config or os.path.join(_REPO_ROOT, 'scrape_sources.yaml')}")

    result = run_scraper(
        args.config,
        sync_after=not args.no_sync,
        source_ids=args.sources,
    )

    print(json.dumps(result["summary"], indent=2))

    for src in result.get("sources") or []:
        print(
            f"  {src.get('id')}: discovered={src.get('discovered', 0)}, "
            f"saved={src.get('saved', 0)}, not_relevant={src.get('skipped_not_relevant', 0)}"
        )

    skipped_rel = result.get("skipped_not_relevant") or []
    if skipped_rel:
        print(f"\nSkipped (not accident-related): {len(skipped_rel)}")

    if result["saved"]:
        print("\nSaved files:")
        for item in result["saved"]:
            title = (item.get("title") or "")[:70]
            print(f"  - {item['filename']}  ({title})")

    summary = result["summary"]
    if summary.get("saved_count", 0) == 0 and not skipped_rel and not any(
        (s.get("discovered") or 0) > 0 for s in (result.get("sources") or [])
    ):
        print("\nNo article URLs found on listing pages. Check scrape_sources.yaml.")
    elif summary.get("saved_count", 0) == 0 and skipped_rel:
        print(
            "\nArticles were fetched but none matched accident criteria. "
            "Adjust accident_filter in scrape_sources.yaml if needed."
        )

    if summary.get("failed_count", 0) and not result["saved"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
