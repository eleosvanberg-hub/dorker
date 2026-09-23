"""
Async page fetcher with concurrency control, UA rotation,
and response size limits.
"""

import asyncio
import random
from dataclasses import dataclass
from typing import Optional
import aiohttp
from config import USER_AGENTS, FETCH_TIMEOUT, FETCH_CONCURRENCY, MAX_RESPONSE_SIZE
from logger_setup import setup_logger

logger = setup_logger("cern.fetcher")


@dataclass
class FetchResult:
    html: str
    headers: dict
    status_code: int
    final_url: str


class PageFetcher:

    def __init__(self, timeout: int = FETCH_TIMEOUT,
                 concurrency: int = FETCH_CONCURRENCY):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.semaphore = asyncio.Semaphore(concurrency)

    async def fetch_many(self, urls: list[str]) -> dict[str, Optional[FetchResult]]:
        """Fetch multiple URLs concurrently.
        Returns {original_url: FetchResult or None}."""
        connector = aiohttp.TCPConnector(limit=FETCH_CONCURRENCY, ssl=False)
        async with aiohttp.ClientSession(
            timeout=self.timeout,
            connector=connector,
        ) as session:
            tasks = [self._fetch_one(session, url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            output = {}
            for url, result in zip(urls, results):
                if isinstance(result, Exception):
                    logger.debug(f"Fetch failed {url}: {result}")
                    output[url] = None
                else:
                    output[url] = result
            return output

    async def _fetch_one(self, session: aiohttp.ClientSession,
                          url: str) -> Optional[FetchResult]:
        """Fetch a single URL with retries."""
        async with self.semaphore:
            ua = random.choice(USER_AGENTS)
            headers = {
                "User-Agent": ua,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate",
            }

            for attempt in range(2):
                try:
                    async with session.get(
                        url,
                        headers=headers,
                        allow_redirects=True,
                        max_redirects=5,
                    ) as resp:
                        # Check content type
                        content_type = resp.headers.get("Content-Type", "")
                        if "text/html" not in content_type and "application/xhtml" not in content_type:
                            return None

                        # Read with size limit
                        body = await resp.content.read(MAX_RESPONSE_SIZE)
                        html = body.decode("utf-8", errors="replace")

                        # Convert headers to dict
                        resp_headers = {k: v for k, v in resp.headers.items()}

                        return FetchResult(
                            html=html,
                            headers=resp_headers,
                            status_code=resp.status,
                            final_url=str(resp.url),
                        )

                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    if attempt == 0:
                        await asyncio.sleep(1)
                    else:
                        return None
                except Exception:
                    return None

        return None
