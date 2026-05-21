# NLP insurance backend

Knowledge-base accident reports live as `.txt` files under `knowledge/` (same folder for manual upload, scraper, and folder scan).

## Scrape news into `knowledge/`

1. Install deps: `pip install -r requirements.txt`
2. Edit `scrape_sources.yaml` to add listing URLs under `sources:`.
3. Run (from repo root):

```powershell
.\run_scraper.ps1
```

Or:

```powershell
py scripts/run_scraper.py
py scripts/run_scraper.py --source newsday_accidents
```

Or call `POST /api/kb/scrape` while the API is running.

Scraped files use the metadata header format (`Source`, `Date of Report`, `Source URL`, …) and are saved via the same `write_txt_file` path as admin uploads. Each run **re-downloads and overwrites** articles found on the listing pages (same URL → same filename, updated content).

NewsDay accident listings: [topic/accidents](https://www.newsday.co.zw/index.php/topic/accidents) and [tag/road-accidents](https://www.newsday.co.zw/tag/road-accidents) (configured in `scrape_sources.yaml`).

Only **road-traffic / accident** articles are kept (`accident_filter` in `scrape_sources.yaml`). Adjust `min_score` or add phrases under `extra_strong_phrases` / `extra_weak_terms` if you need broader coverage.

Then run **Scan folder** and **Run NLP** in the KB admin UI.
