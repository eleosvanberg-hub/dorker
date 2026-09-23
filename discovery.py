"""
Alternative discovery sources: Certificate Transparency (crt.sh),
Common Crawl, and IRS nonprofit data. These find sites that
standard Google searches miss.
"""

import requests
import time
from typing import Optional
from logger_setup import setup_logger

logger = setup_logger("cern.discovery")


class AlternativeDiscovery:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "CernBot/1.0 (donation-research)"

    # ---- Certificate Transparency (crt.sh) ----

    def search_crtsh(self, patterns: list[str] = None) -> list[str]:
        """Search Certificate Transparency logs for domains with donation-related certs.
        FREE, unlimited, finds brand new domains as they register SSL certs."""
        if patterns is None:
            patterns = [
                "%donate%",
                "%giving%",
                "%donation%",
                "%foundation%",
                "%charity%",
                "%nonprofit%",
            ]

        domains = set()
        for pattern in patterns:
            try:
                resp = self.session.get(
                    "https://crt.sh/",
                    params={"q": pattern, "output": "json"},
                    timeout=30,
                )
                if resp.status_code != 200:
                    logger.warning(f"crt.sh returned {resp.status_code} for {pattern}")
                    continue

                data = resp.json()
                for entry in data[:200]:  # limit per pattern
                    name = entry.get("common_name", "").strip()
                    if name and not name.startswith("*") and "." in name:
                        # Build likely donation URLs
                        domains.add(f"https://{name}/donate")
                        domains.add(f"https://{name}/giving")
                        domains.add(f"https://{name}")

                logger.info(f"crt.sh '{pattern}': found {len(data)} certs")
                time.sleep(2)  # be nice to crt.sh

            except Exception as e:
                logger.warning(f"crt.sh error for '{pattern}': {e}")
                continue

        return list(domains)

    # ---- Common Crawl ----

    def search_commoncrawl(self, url_patterns: list[str] = None,
                            index: str = None) -> list[str]:
        """Search Common Crawl CDX index for donation URLs.
        FREE, massive dataset of crawled web pages."""
        if url_patterns is None:
            url_patterns = [
                "*.org/donate*",
                "*.org/giving*",
                "*.edu/donate*",
                "*.edu/giving*",
                "*.org/donation*",
                "*.org/ways-to-give*",
                "*.org/make-a-gift*",
                "*.org/support-us/donate*",
                "*.org/get-involved/donate*",
            ]

        if index is None:
            # Use latest available index
            index = self._get_latest_cc_index()
            if not index:
                logger.warning("Could not determine latest Common Crawl index")
                return []

        urls = set()
        for pattern in url_patterns:
            try:
                resp = self.session.get(
                    f"https://index.commoncrawl.org/{index}-index",
                    params={
                        "url": pattern,
                        "output": "json",
                        "limit": 100,
                        "fl": "url",
                        "filter": "mime:text/html",
                    },
                    timeout=30,
                )
                if resp.status_code != 200:
                    continue

                for line in resp.text.strip().split("\n"):
                    if line.strip():
                        try:
                            import json
                            entry = json.loads(line)
                            url = entry.get("url", "")
                            if url and url.startswith("http"):
                                urls.add(url)
                        except Exception:
                            continue

                logger.info(f"Common Crawl '{pattern}': found {len(urls)} URLs so far")
                time.sleep(1)

            except Exception as e:
                logger.warning(f"Common Crawl error for '{pattern}': {e}")
                continue

        return list(urls)

    def _get_latest_cc_index(self) -> Optional[str]:
        """Get the latest Common Crawl index name."""
        try:
            resp = self.session.get(
                "https://index.commoncrawl.org/collinfo.json",
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    # First entry is the latest
                    return data[0]["id"]
        except Exception as e:
            logger.warning(f"Failed to get CC index list: {e}")
        return None

    # ---- IRS Nonprofit / Exempt Org Discovery ----

    def search_nonprofit_sites(self) -> list[str]:
        """Search for nonprofit websites from public directories.
        Uses open charity/nonprofit listing APIs."""
        urls = set()

        # ProPublica Nonprofit Explorer API (free, no key needed)
        try:
            # Search for organizations with 'donate' in their name
            search_terms = ["foundation", "charity", "rescue", "shelter", "food bank"]
            for term in search_terms[:3]:  # limit to avoid too many requests
                resp = self.session.get(
                    "https://projects.propublica.org/nonprofits/api/v2/search.json",
                    params={"q": term, "page": 0},
                    timeout=15,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for org in data.get("organizations", [])[:20]:
                        name = org.get("name", "").lower().replace(" ", "")
                        # Try common website patterns
                        if org.get("ein"):
                            # Can't reliably build URLs from EIN alone
                            # but we can search for the org name later
                            pass
                logger.info(f"ProPublica '{term}': checked nonprofits")
                time.sleep(1)
        except Exception as e:
            logger.warning(f"ProPublica API error: {e}")

        return list(urls)

    def close(self):
        """Clean up session resources."""
        self.session.close()

    def run_all(self, skip_commoncrawl: bool = False) -> list[str]:
        """Run all alternative discovery sources and return combined URLs."""
        all_urls = []

        logger.info("Running crt.sh discovery...")
        all_urls.extend(self.search_crtsh())

        if not skip_commoncrawl:
            logger.info("Running Common Crawl discovery...")
            all_urls.extend(self.search_commoncrawl())

        logger.info("Running nonprofit directory discovery...")
        all_urls.extend(self.search_nonprofit_sites())

        logger.info(f"Alternative discovery total: {len(all_urls)} URLs")
        return list(set(all_urls))  # deduplicate
