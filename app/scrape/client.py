from __future__ import annotations

import time
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.scrape.config import ScrapeDefaults


class FetchClient:
    def __init__(self, defaults: ScrapeDefaults) -> None:
        self._defaults = defaults
        self._last_fetch = 0.0
        self._client = httpx.Client(
            timeout=defaults.request_timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": defaults.user_agent},
        )

    def close(self) -> None:
        self._client.close()

    def _throttle(self) -> None:
        delay = max(0.0, self._defaults.delay_seconds)
        elapsed = time.monotonic() - self._last_fetch
        if elapsed < delay:
            time.sleep(delay - elapsed)

    def fetch_html(self, url: str) -> Optional[str]:
        self._throttle()
        try:
            resp = self._client.get(url)
            self._last_fetch = time.monotonic()
            if resp.status_code >= 400:
                return None
            final = str(resp.url).lower()
            if "/sso" in final or "email-protection" in final:
                return None
            ctype = (resp.headers.get("content-type") or "").lower()
            if "html" not in ctype and "text" not in ctype:
                return None
            return resp.text
        except httpx.HTTPError:
            self._last_fetch = time.monotonic()
            return None

    @staticmethod
    def normalize_url(base: str, href: str) -> Optional[str]:
        if not href or not str(href).strip():
            return None
        href = str(href).strip()
        if href.startswith("#") or href.lower().startswith("javascript:"):
            return None
        full = urljoin(base, href)
        parsed = urlparse(full)
        if parsed.scheme not in ("http", "https"):
            return None
        # Drop fragments and query tracking noise where possible
        return parsed._replace(fragment="").geturl()
