from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.db import store as kb_store
from app.scrape.client import FetchClient
from app.scrape.config import ScrapeConfig, ScrapeSource, load_scrape_config
from app.scrape.discover import discover_article_urls
from app.scrape.extract import extract_article
from app.scrape.relevance import is_accident_relevant
from app.scrape.state import save_scraped_url
from app.scrape.writer import save_article_to_knowledge

logger = logging.getLogger(__name__)


def run_scraper(
    config_path: Optional[str] = None,
    *,
    sync_after: bool = True,
    source_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Fetch listing pages, download articles, write .txt files to knowledge/
    using kb_store.write_txt_file (same as manual upload).

    Re-fetches and overwrites matching .txt on every run (no URL skip cache).
    """
    cfg = load_scrape_config(config_path)
    seen_this_run: set[str] = set()
    results: Dict[str, Any] = {
        "config": cfg.config_path,
        "sources": [],
        "saved": [],
        "skipped_not_relevant": [],
        "failed": [],
    }

    af = cfg.accident_filter
    extra_strong = af.extra_strong_phrases if af.enabled else None
    extra_weak = af.extra_weak_terms if af.enabled else None

    client = FetchClient(cfg.defaults)
    try:
        for source in cfg.sources:
            if not source.enabled:
                continue
            if source_ids and source.id not in source_ids:
                continue
            if not source.listing_urls:
                continue

            limit = source.max_articles or cfg.defaults.max_articles_per_source
            src_result: Dict[str, Any] = {
                "id": source.id,
                "listing_urls": source.listing_urls,
                "discovered": 0,
                "saved": 0,
            }

            discover_cap = limit * max(3, cfg.defaults.discovery_multiplier)
            listing_filter = (
                af if (af.enabled and af.prefilter_listing_links) else None
            )
            urls = discover_article_urls(
                client,
                source,
                source.listing_urls,
                limit=discover_cap,
                accident_filter=listing_filter,
            )
            src_result["discovered"] = len(urls)
            if not urls:
                logger.warning(
                    "Source %s: no article URLs discovered from listing pages",
                    source.id,
                )

            saved_n = 0
            attempts = 0
            for url in urls:
                attempts += 1
                if saved_n >= limit:
                    break
                if url in seen_this_run:
                    continue
                seen_this_run.add(url)

                html = client.fetch_html(url)
                if not html:
                    results["failed"].append({"source": source.id, "url": url, "reason": "fetch_failed"})
                    continue

                article = extract_article(html, url, source.source_label)
                if not article:
                    results["failed"].append({"source": source.id, "url": url, "reason": "extract_failed"})
                    continue

                if af.enabled and not is_accident_relevant(
                    article.title,
                    article.body,
                    min_score=af.min_score,
                    extra_strong=extra_strong,
                    extra_weak=extra_weak,
                    url=url,
                    trust_accident_listing=source.trust_accident_listing,
                ):
                    results["skipped_not_relevant"].append(
                        {
                            "source": source.id,
                            "url": url,
                            "title": article.title,
                        }
                    )
                    logger.debug("Skipped non-accident article: %s", article.title)
                    continue

                try:
                    filename = save_article_to_knowledge(source.id, article)
                except OSError as exc:
                    results["failed"].append(
                        {"source": source.id, "url": url, "reason": f"write_failed: {exc}"}
                    )
                    continue

                save_scraped_url(url, filename)
                saved_n += 1
                entry = {
                    "source": source.id,
                    "url": url,
                    "filename": filename,
                    "title": article.title,
                }
                results["saved"].append(entry)
                src_result["saved"] = saved_n
                logger.info("Saved %s -> %s", url, filename)

            src_result["attempted"] = attempts
            src_result["skipped_not_relevant"] = sum(
                1 for x in results["skipped_not_relevant"] if x.get("source") == source.id
            )
            results["sources"].append(src_result)
    finally:
        client.close()

    if sync_after:
        kb_store.sync_knowledge_folder()

    results["summary"] = {
        "saved_count": len(results["saved"]),
        "skipped_not_relevant_count": len(results["skipped_not_relevant"]),
        "failed_count": len(results["failed"]),
        "accident_filter_enabled": af.enabled,
    }
    return results
