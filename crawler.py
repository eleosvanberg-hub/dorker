"""
Link crawler: extracts donation-related links from fetched pages
and feeds them back into the detection pipeline.
"""

import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from config import DONATE_LINK_KEYWORDS, CRAWLER_MAX_DEPTH
from logger_setup import setup_logger

logger = setup_logger("cern.crawler")


class DonationCrawler:

    def extract_donate_links(self, base_url: str, html: str,
                              max_depth: int = CRAWLER_MAX_DEPTH) -> list[str]:
        """Extract donation-related links from a page.
        Returns list of absolute URLs to check."""
        if max_depth <= 0:
            return []

        links = set()
        base_domain = urlparse(base_url).hostname or ""

        try:
            soup = BeautifulSoup(html, "html.parser")
        except Exception:
            return []

        for tag in soup.find_all("a", href=True):
            href = tag.get("href", "").strip()
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue

            # Build absolute URL
            absolute = urljoin(base_url, href)
            parsed = urlparse(absolute)

            # Same domain only
            if not parsed.hostname:
                continue
            link_domain = parsed.hostname
            if link_domain.startswith("www."):
                link_domain = link_domain[4:]
            if base_domain.startswith("www."):
                base_domain_clean = base_domain[4:]
            else:
                base_domain_clean = base_domain
            if link_domain != base_domain_clean:
                continue

            # Check if URL or link text contains donation keywords
            href_lower = href.lower()
            link_text = tag.get_text(strip=True).lower()
            combined = href_lower + " " + link_text

            if any(kw in combined for kw in DONATE_LINK_KEYWORDS):
                # Clean URL (remove fragments)
                clean = f"{parsed.scheme}://{parsed.hostname}{parsed.path}"
                if parsed.query:
                    clean += f"?{parsed.query}"
                links.add(clean)

        # Also try common donation page paths on the root domain
        root = f"{urlparse(base_url).scheme}://{urlparse(base_url).hostname}"
        common_paths = [
            "/donate", "/giving", "/give", "/donations", "/donate-now",
            "/ways-to-give", "/make-a-gift", "/support-us/donate",
            "/get-involved/donate", "/contribution",
        ]
        for path in common_paths:
            links.add(root + path)

        # Remove the original URL
        links.discard(base_url)

        logger.debug(f"Crawled {base_url}: found {len(links)} donate links")
        return list(links)
