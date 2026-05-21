import unittest
from datetime import date

from app.kb.metadata import (
    metadata_with_recency,
    parse_date_from_text,
    parse_kb_metadata,
    recency_weight,
)
from app.kb.service import aggregate_from_results


SAMPLE_TXT = """Source: Zimbabwe Republic Police (via Africa Press)

Period Covered: December 15-26, 2022

Date of Report: December 27, 2022

Source URL: https://www.africa-press.net/zimbabwe/all-news/zrp-releases-2022-festive-season-accident-statistics

During the festive season police recorded many road traffic accidents near Harare.
"""


class TestMetadataParse(unittest.TestCase):
    def test_parse_header_block(self) -> None:
        meta, body = parse_kb_metadata(SAMPLE_TXT)
        self.assertEqual(meta["source"], "Zimbabwe Republic Police (via Africa Press)")
        self.assertIn("December 15", meta["period_covered"])
        self.assertEqual(meta["date_of_report"], "December 27, 2022")
        self.assertTrue(meta["source_url"].startswith("https://"))
        self.assertEqual(meta.get("report_date"), "2022-12-27")
        self.assertIn("festive season", body.lower())
        self.assertNotIn("Source:", body)

    def test_parse_date_variants(self) -> None:
        self.assertEqual(parse_date_from_text("22nd APRIL 2025"), date(2025, 4, 22))
        self.assertEqual(parse_date_from_text("December 27, 2022"), date(2022, 12, 27))

    def test_recency_older_weighs_less(self) -> None:
        old = date(2020, 1, 1)
        recent = date(2025, 4, 1)
        ref = date(2025, 5, 1)
        w_old = recency_weight(old, reference=ref)
        w_new = recency_weight(recent, reference=ref)
        self.assertLess(w_old, w_new)
        self.assertGreater(w_new, 0.9)

    def test_metadata_with_recency_attached(self) -> None:
        meta, _ = parse_kb_metadata(SAMPLE_TXT)
        enriched = metadata_with_recency(meta, reference=date(2025, 5, 1))
        self.assertIn("recency_weight", enriched)
        self.assertLess(enriched["recency_weight"], 0.5)


class TestRecencyAggregate(unittest.TestCase):
    def test_weighted_aggregate_favours_recent(self) -> None:
        recent = {
            "filename": "recent.txt",
            "metadata": {"recency_weight": 1.0},
            "recency_weight": 1.0,
            "buckets": {"behavioural": 1.0},
            "matched_keywords": ["speeding"],
            "legacy_features": {"severity_fatal": 1},
        }
        old = {
            "filename": "old.txt",
            "metadata": {"recency_weight": 0.15},
            "recency_weight": 0.15,
            "buckets": {"behavioural": 0.0},
            "matched_keywords": [],
            "legacy_features": {},
        }
        stats = aggregate_from_results([recent, old])
        self.assertTrue(stats.get("recency_weighted"))
        self.assertGreater(stats["avg_bucket_scores"]["behavioural"], 0.7)
        self.assertEqual(len(stats.get("report_provenance") or []), 2)


if __name__ == "__main__":
    unittest.main()
