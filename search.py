"""
Multi-provider search engine: Google CSE -> ValueSERP -> SerperDev -> SerpAPI.
Auto-fallback chain with per-provider quota tracking.
"""

import time
import requests
from typing import Optional
from config import (
    GOOGLE_API_KEY, GOOGLE_CSE_ID, SERPER_API_KEY,
    SERPAPI_KEY, VALUESERP_API_KEY, BING_API_KEY,
    DAILY_LIMITS,
)
from storage import Storage
from logger_setup import setup_logger

logger = setup_logger("cern.search")


class QuotaExhaustedError(Exception):
    """All search providers have exhausted their daily quota."""
    pass


class SearchClient:
    PROVIDERS = ["valueserp", "google", "serper", "serpapi", "bing"]

    def __init__(self, storage: Storage):
        self.storage = storage
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "CernBot/1.0"

    def search(self, query: str, num_results: int = 10) -> tuple[list[str], str]:
        """Search using the fallback chain. Returns (urls, provider_used).
        Raises QuotaExhaustedError if all providers exhausted."""
        for provider in self.PROVIDERS:
            if not self._provider_available(provider):
                continue
            if not self.storage.can_query(provider, DAILY_LIMITS.get(provider, 0)):
                logger.info(f"Quota exhausted for {provider}, trying next")
                continue
            try:
                urls = self._search_provider(provider, query, num_results)
                self.storage.increment_query_count(provider)
                return urls, provider
            except Exception as e:
                logger.warning(f"Search failed with {provider}: {e}")
                continue

        raise QuotaExhaustedError("All search providers exhausted for today")

    def _provider_available(self, provider: str) -> bool:
        """Check if provider has API key configured."""
        checks = {
            "google": bool(GOOGLE_API_KEY and GOOGLE_CSE_ID),
            "serper": bool(SERPER_API_KEY),
            "serpapi": bool(SERPAPI_KEY),
            "valueserp": bool(VALUESERP_API_KEY),
            "bing": bool(BING_API_KEY),
        }
        return checks.get(provider, False)

    def _search_provider(self, provider: str, query: str, num: int) -> list[str]:
        dispatch = {
            "google": self._google_search,
            "serper": self._serper_search,
            "serpapi": self._serpapi_search,
            "valueserp": self._valueserp_search,
            "bing": self._bing_search,
        }
        return dispatch[provider](query, num)

    def _google_search(self, query: str, num: int) -> list[str]:
        resp = self.session.get(
            "https://www.googleapis.com/customsearch/v1",
            params={"key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_ID, "q": query, "num": min(num, 10)},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return [item["link"] for item in data.get("items", [])]

    def _valueserp_search(self, query: str, num: int) -> list[str]:
        resp = self.session.get(
            "https://api.valueserp.com/search",
            params={
                "api_key": VALUESERP_API_KEY,
                "q": query,
                "num": min(num, 100),
                "output": "json",
            },
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        return [r["link"] for r in data.get("organic_results", []) if "link" in r]

    def _serper_search(self, query: str, num: int) -> list[str]:
        resp = self.session.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
            json={"q": query, "num": min(num, 100)},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return [r["link"] for r in data.get("organic", []) if "link" in r]

    def _serpapi_search(self, query: str, num: int) -> list[str]:
        resp = self.session.get(
            "https://serpapi.com/search",
            params={"api_key": SERPAPI_KEY, "q": query, "num": min(num, 100)},
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        return [r["link"] for r in data.get("organic_results", []) if "link" in r]

    def _bing_search(self, query: str, num: int) -> list[str]:
        resp = self.session.get(
            "https://api.bing.microsoft.com/v7.0/search",
            headers={"Ocp-Apim-Subscription-Key": BING_API_KEY},
            params={"q": query, "count": min(num, 50)},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return [r["url"] for r in data.get("webPages", {}).get("value", []) if "url" in r]

    def close(self):
        """Clean up session resources."""
        self.session.close()

    def search_custom(self, query: str, num_results: int = 10) -> tuple[list[str], str]:
        """Same as search() but for user-triggered one-off queries."""
        return self.search(query, num_results)
