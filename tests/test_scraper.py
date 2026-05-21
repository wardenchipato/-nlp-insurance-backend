import unittest

from app.scrape.discover import _looks_like_article
from app.scrape.relevance import is_accident_relevant, is_link_likely_relevant
from app.scrape.writer import ScrapedArticle, build_kb_txt, filename_for_article


class TestScraperWriter(unittest.TestCase):
    def test_build_kb_txt_metadata_header(self) -> None:
        art = ScrapedArticle(
            url="https://www.africa-press.net/zimbabwe/all-news/example/",
            title="Test headline",
            body="Accident statistics rose near Harare highway.",
            source_label="Africa Press English",
            date_of_report="2022-12-27",
        )
        txt = build_kb_txt(art)
        self.assertIn("Source: Africa Press English", txt)
        self.assertIn("Date of Report: 2022-12-27", txt)
        self.assertIn("Source URL: https://www.africa-press.net", txt)
        self.assertIn("Harare highway", txt)

    def test_filename_safe(self) -> None:
        art = ScrapedArticle(
            url="https://example.com/a",
            title="Hello World!",
            body="x" * 200,
            source_label="Test",
        )
        fn = filename_for_article("src1", art)
        self.assertTrue(fn.endswith(".txt"))
        self.assertIn("scraped_src1", fn)


class TestScraperDiscover(unittest.TestCase):
    def test_article_url_heuristics(self) -> None:
        self.assertTrue(
            _looks_like_article(
                "https://www.africa-press.net/zimbabwe/all-news/foo-bar/"
            )
        )
        self.assertFalse(_looks_like_article("https://www.africa-press.net/zimbabwe/all-news/"))
        self.assertTrue(
            _looks_like_article(
                "https://www.newsday.co.zw/local-news/article/200055715/swift-justice-as-zvitsva-receives-89-year-sentence"
            )
        )
        self.assertTrue(
            _looks_like_article(
                "https://www.newsday.co.zw/local/article/200053402/police-warn-motorists-as-road-accidents-surge"
            )
        )
        self.assertFalse(_looks_like_article("https://www.newsday.co.zw/tag/road-accidents"))
        self.assertFalse(_looks_like_article("https://www.newsday.co.zw/local-news"))


class TestExtractDates(unittest.TestCase):
    def test_parse_newsday_dotted_date(self) -> None:
        from app.scrape.extract import _parse_iso_date

        self.assertEqual(_parse_iso_date("By Nhau Mangirazi May. 9, 2026"), "May. 9, 2026")
        self.assertEqual(_parse_iso_date("Apr. 1, 2026"), "Apr. 1, 2026")

    def test_marketing_not_parsed_as_date(self) -> None:
        from app.scrape.extract import _parse_iso_date

        self.assertIsNone(_parse_iso_date("Marketing"))
        self.assertIsNone(_parse_iso_date("Digital Marketing Manager"))


class TestAccidentRelevance(unittest.TestCase):
    def test_accepts_traffic_accident_report(self) -> None:
        self.assertTrue(
            is_accident_relevant(
                "ZRP releases festive season road traffic accident statistics",
                "Police recorded 384 road traffic accidents and 24 people killed on highways.",
            )
        )

    def test_trusted_listing_accepts_curated_topic_stories(self) -> None:
        self.assertTrue(
            is_accident_relevant(
                "Zim bloody roads: A curse for pedestrians",
                "Pedestrians on highways without footpaths.",
                trust_accident_listing=True,
            )
        )
        self.assertTrue(
            is_accident_relevant(
                "Lets exercise extreme caution on the roads",
                "Editorial on holiday travel.",
                trust_accident_listing=True,
            )
        )

    def test_trusted_listing_rejects_sport_url(self) -> None:
        self.assertFalse(
            is_accident_relevant(
                "Arsenal league triumph",
                "Football fans celebrate.",
                url="https://www.newsday.co.zw/sport/article/1/arsenal",
                trust_accident_listing=True,
            )
        )

    def test_rejects_sports_article(self) -> None:
        self.assertFalse(
            is_accident_relevant(
                "Zamalek SC loses final to USM Alger",
                "Union won after penalty shootout following an injury substitution.",
            )
        )

    def test_link_prefilter(self) -> None:
        self.assertTrue(
            is_link_likely_relevant(
                "https://www.newsday.co.zw/local-news/article/1/serial-killer-jailed-89-years",
                "Guruve serial killer jailed after fatal crash",
            )
        )
        self.assertFalse(
            is_link_likely_relevant(
                "https://www.newsday.co.zw/local-news/article/1/homecoming-classical-tour",
                "Homecoming in harmony as Emma Price headlines tour",
            )
        )


if __name__ == "__main__":
    unittest.main()
