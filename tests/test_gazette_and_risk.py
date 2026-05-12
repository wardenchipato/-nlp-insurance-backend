import unittest
from types import SimpleNamespace

from app.kb.service import aggregate_from_results
from app.nlp.gazette_mapping import (
    empty_buckets,
    empty_legacy,
    normalize_phrase,
    score_gazette_match,
    score_supplementary_text,
)
from app.nlp.negation import apply_denial_phrase_overrides
from app.scoring.risk_engine import calculate_risk_score, score_structured_data


class TestGazetteMapping(unittest.TestCase):
    def test_normalize_hyphen(self) -> None:
        self.assertEqual(normalize_phrase("Harare-Bulawayo Highway"), "hararebulawayo highway")

    def test_night_driving_routes_to_time(self) -> None:
        leg, buckets, _ = score_gazette_match(
            "night driving",
            "BEHAVIOUR",
            "risk_behaviour",
            "night driving",
        )
        self.assertEqual(leg.get("night_driving"), 1.0)
        self.assertGreater(buckets.get("time", 0), 0.5)

    def test_supplementary_peak_hours(self) -> None:
        leg, _, kw, _ = score_supplementary_text("crash during rush hour near harare")
        self.assertEqual(leg.get("peak_hours"), 1.0)
        self.assertIn("peak_hours", kw)

    def test_supplementary_peak_hours_negated(self) -> None:
        leg, _, kw, _ = score_supplementary_text("crash not during rush hour")
        self.assertEqual(leg.get("peak_hours"), 0.0)
        self.assertNotIn("peak_hours", kw)

    def test_supplementary_darkness_negated(self) -> None:
        leg, _, _, _ = score_supplementary_text("there was no darkness; daylight scene")
        self.assertEqual(leg.get("darkness"), 0.0)


class TestNegationPhraseOverrides(unittest.TestCase):
    def test_denial_clears_drunk_and_caps_behavioural_bucket(self) -> None:
        leg = empty_legacy()
        leg["drunk_driving"] = 1.0
        b = empty_buckets()
        b["behavioural"] = 0.95
        apply_denial_phrase_overrides("driver had no drunk driving history", leg, b)
        self.assertEqual(leg["drunk_driving"], 0.0)
        self.assertLessEqual(b["behavioural"], 0.42)


class TestSpacyIntegration(unittest.TestCase):
    def test_analyze_text_matches_gazette(self) -> None:
        try:
            import spacy  # noqa: F401

            spacy.load("en_core_web_sm")
        except Exception:
            self.skipTest("spaCy model en_core_web_sm not installed")

        from app.nlp.analysis import analyze_text

        out = analyze_text("drunk driving and heavy rain near harare")
        self.assertGreaterEqual(out["legacy_features"].get("drunk_driving", 0), 1.0)
        self.assertGreaterEqual(out["legacy_features"].get("rain", 0), 1.0)
        self.assertGreater(len(out.get("gazette_matches") or []), 0)

    def test_no_drunk_driving_not_scored_as_dui(self) -> None:
        try:
            import spacy  # noqa: F401

            spacy.load("en_core_web_sm")
        except Exception:
            self.skipTest("spaCy model en_core_web_sm not installed")

        from app.nlp.analysis import analyze_text

        out = analyze_text("Police confirmed no drunk driving; wet road only.")
        self.assertLess(out["legacy_features"].get("drunk_driving", 0), 0.5)


class TestKbAggregate(unittest.TestCase):
    def test_keyword_doc_share(self) -> None:
        per_file = [
            {"buckets": {}, "matched_keywords": ["heavy rain", "speeding"]},
            {"buckets": {}, "matched_keywords": ["heavy rain", "harare"]},
        ]
        stats = aggregate_from_results(per_file)
        self.assertEqual(stats["document_count"], 2)
        share = stats.get("keyword_doc_share") or {}
        self.assertAlmostEqual(share.get("heavy rain", 0), 1.0)
        self.assertAlmostEqual(share.get("speeding", 0), 0.5)


class TestRiskEngine(unittest.TestCase):
    def test_calculate_risk_score_extended_keys(self) -> None:
        features = {
            "speeding": 1,
            "drunk_driving": 0,
            "fatigue": 0,
            "distracted": 0,
            "reckless": 0,
            "rain": 0,
            "fog": 0,
            "darkness": 0,
            "wind": 0,
            "poor_visibility": 0,
            "wet_roads": 0,
            "peak_hours": 0,
            "night_driving": 0,
            "daytime": 0,
            "off_peak": 0,
            "brake_failure": 0,
            "tyre_problem": 0,
            "commercial_vehicle_context": 0,
            "junction": 0,
            "highway": 0,
            "urban": 0,
            "rural_road": 0,
            "traffic_congestion": 0,
            "severity_fatal": 0,
            "severity_injury": 0,
            "severity_multi_vehicle": 0,
        }
        out = calculate_risk_score(features)
        self.assertIn("final_score", out)
        self.assertIn("claims_severity", out)
        self.assertGreater(out["final_score"], 0)

    def test_claims_severity_separate_from_behavioural(self) -> None:
        """Severity flags score under claims_severity, not behavioural."""
        feats = {
            "speeding": 0,
            "drunk_driving": 0,
            "fatigue": 0,
            "distracted": 0,
            "reckless": 0,
            "rain": 0,
            "fog": 0,
            "darkness": 0,
            "wind": 0,
            "poor_visibility": 0,
            "wet_roads": 0,
            "peak_hours": 0,
            "night_driving": 0,
            "daytime": 0,
            "off_peak": 0,
            "brake_failure": 0,
            "tyre_problem": 0,
            "commercial_vehicle_context": 0,
            "junction": 0,
            "highway": 0,
            "urban": 0,
            "rural_road": 0,
            "traffic_congestion": 0,
            "severity_fatal": 1,
            "severity_injury": 0,
            "severity_multi_vehicle": 0,
        }
        out = calculate_risk_score(feats)
        self.assertGreaterEqual(out["claims_severity"], 50.0)
        self.assertEqual(out["behavioural"], 0.0)

    def test_structured_form_new_fields(self) -> None:
        data = SimpleNamespace(
            driver_age=40,
            gender="Male",
            years_licensed=15,
            vehicle_type="Car",
            vehicle_age=5,
            engine_capacity_cc=2800,
            vehicle_value=30000,
            annual_distance_km=30000,
            area_type="Urban",
            usage_type="Private",
            prior_claims=0,
        )
        s = score_structured_data(data)
        self.assertGreater(s, 20)


if __name__ == "__main__":
    unittest.main()
