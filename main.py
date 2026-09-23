"""
Donation Site Scanner - Main Orchestrator
Runs 24/7, discovering donation websites with specific payment gateways.
"""

import asyncio
import signal
import time
from datetime import datetime, timedelta, UTC

from config import (
    DB_PATH, CYCLE_SLEEP_SECONDS,
    CRTSH_INTERVAL_HOURS, COMMONCRAWL_INTERVAL_HOURS,
)
from logger_setup import setup_logger
from storage import Storage
from search import SearchClient, QuotaExhaustedError, SearchNetworkError
from discovery import AlternativeDiscovery
from dork_generator import DorkGenerator
from fetcher import PageFetcher
from crawler import DonationCrawler
from detector import Detector
from scorer import QualityScorer
from notifier import TelegramNotifier
from exporter import Exporter
from learner import DorkLearner

logger = setup_logger()


class PaymentScanner:

    def __init__(self):
        self.storage = Storage(DB_PATH)
        self.search_client = SearchClient(self.storage)
        self.discovery = AlternativeDiscovery()
        self.dork_gen = DorkGenerator(self.storage)
        self.fetcher = PageFetcher()
        self.crawler = DonationCrawler()
        self.detector = Detector()
        self.scorer = QualityScorer()
        self.notifier = TelegramNotifier()
        self.exporter = Exporter(self.storage)
        self.learner = DorkLearner()

        self.running = True
        self.paused = False
        self.start_time = datetime.now(UTC)
        self.last_crtsh = None
        self.last_commoncrawl = None
        self.cycle_count = 0
        self.last_error = None

        # Persistent event loop — avoids stale loop errors from repeated asyncio.run()
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self._register_commands()

    # ---- Telegram Bot Commands ----

    def _register_commands(self):
        self.notifier.register_command("stats", self._cmd_stats)
        self.notifier.register_command("total", self._cmd_total)
        self.notifier.register_command("top", self._cmd_top)
        self.notifier.register_command("export", self._cmd_export)
        self.notifier.register_command("search", self._cmd_search)
        self.notifier.register_command("dorks", self._cmd_dorks)
        self.notifier.register_command("learned", self._cmd_learned)
        self.notifier.register_command("pause", self._cmd_pause)
        self.notifier.register_command("resume", self._cmd_resume)
        self.notifier.register_command("status", self._cmd_status)

    def _cmd_stats(self, args: str, chat_id: str):
        stats = self.storage.get_today_stats()
        msg = f"📊 <b>Today's Stats</b>\n"
        msg += f"🆕 Sites found: {stats['sites_found']}\n"
        msg += f"🔍 Queries used:\n"
        for provider, count in stats.get("queries_used", {}).items():
            msg += f"   • {provider}: {count}\n"
        self.notifier.send(msg, chat_id)

    def _cmd_total(self, args: str, chat_id: str):
        total = self.storage.get_total_stats()
        msg = f"📈 <b>All-Time Stats</b>\n"
        msg += f"📦 Total sites: {total['total_sites']}\n\n"
        msg += "💳 Gateways:\n"
        for gw, count in sorted(total.get("gateways", {}).items(), key=lambda x: -x[1]):
            msg += f"   • {gw}: {count}\n"
        msg += "\n🏪 Platforms:\n"
        for plat, count in sorted(total.get("platforms", {}).items(), key=lambda x: -x[1]):
            msg += f"   • {plat}: {count}\n"
        self.notifier.send(msg, chat_id)

    def _cmd_top(self, args: str, chat_id: str):
        gateway_filter = args.strip() if args.strip() else None
        sites = self.storage.get_top_sites(limit=10, gateway_filter=gateway_filter)
        if not sites:
            self.notifier.send("No sites found yet.", chat_id)
            return
        msg = f"🏆 <b>Top {len(sites)} Sites</b>"
        if gateway_filter:
            msg += f" ({gateway_filter})"
        msg += "\n━━━━━━━━━━━━━━━━━━━━━\n"
        for i, site in enumerate(sites, 1):
            msg += f"{i}. ⭐{site['quality_score']} | {site['url']}\n"
            msg += f"   💳 {site['gateways']} | 🏪 {site['platform']}\n"
        self.notifier.send(msg, chat_id)

    def _cmd_export(self, args: str, chat_id: str):
        gateway_filter = args.strip() if args.strip() else None
        file_path = self.exporter.export_to_file(gateway_filter)
        if file_path:
            caption = f"Export: {'All' if not gateway_filter else gateway_filter} sites"
            self.notifier.send_document(file_path, caption, chat_id)
        else:
            self.notifier.send("No sites to export.", chat_id)

    def _cmd_search(self, args: str, chat_id: str):
        query = args.strip().strip('"').strip("'")
        if not query:
            self.notifier.send("Usage: /search \"your dork here\"", chat_id)
            return
        self.notifier.send(f"🔍 Searching: {query}...", chat_id)
        try:
            urls, provider = self.search_client.search_custom(query)
            new_urls = [u for u in urls if not self.storage.site_exists(u)]
            self.notifier.send(
                f"Found {len(urls)} results ({len(new_urls)} new) via {provider}. Processing...",
                chat_id,
            )
            if new_urls:
                self._loop.run_until_complete(self._process_urls(new_urls, query))
        except Exception as e:
            self.notifier.send(f"❌ Search error: {e}", chat_id)

    def _cmd_dorks(self, args: str, chat_id: str):
        productive = self.storage.get_productive_dorks(limit=10)
        if not productive:
            self.notifier.send("No dork history yet.", chat_id)
            return
        msg = "🎯 <b>Top Productive Dorks</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
        for d in productive:
            eff = d.get("efficiency", 0)
            msg += f"• {d['dork'][:60]}...\n"
            msg += f"  Used: {d['times_used']}x | New: {d['total_new_sites']} | Eff: {eff:.1f}\n\n"
        self.notifier.send(msg, chat_id)

    def _cmd_learned(self, args: str, chat_id: str):
        stats = self.storage.get_learned_dork_stats()
        recent = self.storage.get_learned_dorks(limit=8)
        msg = (
            f"🧠 <b>Self-Learned Dorks</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 Total learned: {stats.get('total', 0)}\n"
            f"🔬 Untested: {stats.get('untested', 0)}\n"
            f"✅ Total finds from learned: {stats.get('total_finds', 0)}\n\n"
            f"<b>Latest:</b>\n"
        )
        for d in recent:
            used = d.get("times_used", 0)
            finds = d.get("total_new_sites", 0)
            gw = d.get("gateway") or "?"
            status = "🆕" if used == 0 else f"✅{finds}" if finds else "⬜"
            msg += f"{status} [{gw}] {d['dork'][:55]}...\n"
        self.notifier.send(msg, chat_id)

    def _cmd_pause(self, args: str, chat_id: str):
        self.paused = True
        self.notifier.send("⏸ Scanner paused. Use /resume to continue.", chat_id)

    def _cmd_resume(self, args: str, chat_id: str):
        self.paused = False
        self.notifier.send("▶️ Scanner resumed.", chat_id)

    def _cmd_status(self, args: str, chat_id: str):
        uptime = datetime.now(UTC) - self.start_time
        hours = int(uptime.total_seconds() // 3600)
        minutes = int((uptime.total_seconds() % 3600) // 60)
        msg = (
            f"🤖 <b>Bot Status</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"⏱ Uptime: {hours}h {minutes}m\n"
            f"🔄 Cycles completed: {self.cycle_count}\n"
            f"{'⏸ PAUSED' if self.paused else '▶️ RUNNING'}\n"
            f"🕐 Last error: {self.last_error or 'None'}\n"
        )
        self.notifier.send(msg, chat_id)

    # ---- Main Loop ----

    def run(self):
        """Main entry point. Runs forever until SIGINT/SIGTERM."""
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

        logger.info("=== Scanner Started ===")
        self.notifier.send("🚀 <b>Scanner started!</b>\nUse /status for info, /help for commands.")

        # Start Telegram command polling
        self.notifier.start_polling()

        consecutive_errors = 0

        while self.running:
            if self.paused:
                self._safe_sleep(10)
                continue

            try:
                self._run_cycle()
                self.cycle_count += 1
                consecutive_errors = 0
                # Sleep between cycles only on success
                self._safe_sleep(CYCLE_SLEEP_SECONDS)

            except QuotaExhaustedError:
                logger.info("All search quotas exhausted — sleeping until midnight")
                consecutive_errors = 0
                self._sleep_until_midnight()

            except SearchNetworkError as e:
                # Transient failure (timeout, 5xx) — NOT a quota issue.
                # Wait 5 minutes then retry; do not sleep until midnight.
                consecutive_errors += 1
                self.last_error = f"{datetime.now(UTC).strftime('%H:%M')} - network: {str(e)[:80]}"
                logger.warning(f"Search network error (#{consecutive_errors}): {e}")
                backoff = min(300 * consecutive_errors, 1800)  # 5m, 10m, 15m, cap 30m
                logger.info(f"Retrying in {backoff}s")
                self._safe_sleep(backoff)

            except Exception as e:
                consecutive_errors += 1
                self.last_error = f"{datetime.now(UTC).strftime('%H:%M')} - {str(e)[:100]}"
                logger.exception(f"Cycle error (#{consecutive_errors}): {e}")

                # Exponential backoff: 60s, 120s, 240s, 480s — cap at 10 min
                backoff = min(60 * (2 ** (consecutive_errors - 1)), 600)
                logger.info(f"Backing off {backoff}s before retry")
                self._safe_sleep(backoff)
                # No extra CYCLE_SLEEP here — retry sooner after errors

        self.notifier.stop_polling()
        self.notifier.close()
        self.search_client.close()
        self.discovery.close()
        self.storage.close()
        self._loop.close()
        logger.info("=== Scanner stopped ===")

    def _run_cycle(self):
        """One full cycle: search, fetch, detect, notify."""
        logger.info(f"--- Cycle {self.cycle_count + 1} starting ---")

        all_urls = []

        # 1. Get dorks and search
        dorks = self.dork_gen.get_dorks_for_cycle(count=10)
        # Track which dorks came from the learner for stats
        learned_dork_set = {d["dork"] for d in self.storage.get_learned_dorks(limit=200)}

        for dork in dorks:
            if not self.running:
                break
            try:
                urls, provider = self.search_client.search(dork)
                self.storage.log_query(dork, provider, len(urls))
                new_count = sum(1 for u in urls if not self.storage.site_exists(u))
                self.storage.update_dork_stats(dork, len(urls), 0)
                if dork in learned_dork_set:
                    self.storage.update_learned_dork_stats(dork, 0)
                all_urls.extend(urls)
                logger.info(f"[{provider}] '{dork[:50]}...' -> {len(urls)} results ({new_count} new)")
                time.sleep(1)
            except (QuotaExhaustedError, SearchNetworkError):
                raise
            except Exception as e:
                logger.warning(f"Search failed for dork: {e}")

        # 2. Alternative discovery (staggered)
        alt_urls = self._run_alternative_discovery()
        all_urls.extend(alt_urls)

        # 3. Filter already-known URLs
        new_urls = [u for u in set(all_urls) if not self.storage.site_exists(u)]
        if not new_urls:
            logger.info("No new URLs this cycle")
            return

        logger.info(f"Processing {len(new_urls)} new URLs")

        # 4. Fetch, crawl, detect, score, notify
        self._loop.run_until_complete(self._process_urls(new_urls))

    async def _process_urls(self, urls: list[str], source_dork: str = None):
        """Fetch pages, crawl links, detect gateways, score, and notify."""
        # Fetch pages
        results = await self.fetcher.fetch_many(urls)

        # Collect crawled links for second pass
        crawl_urls = set()

        for url, fetch_result in results.items():
            if fetch_result is None:
                continue

            # Detect on this page
            detection = self.detector.analyze(url, fetch_result.html, fetch_result.headers)
            if detection:
                # Score it
                detection["quality_score"] = self.scorer.score(detection)

                # Store and notify
                site_id = self.storage.add_site(detection)
                if site_id:
                    success = self.notifier.send_result(detection)
                    if success:
                        self.storage.mark_notified(site_id)
                    logger.info(
                        f"✅ FOUND: {url} | {detection['short_code']} | "
                        f"Score: {detection['quality_score']}"
                    )

                    # Self-learning: extract dorks from this confirmed page
                    new_dorks = self.learner.extract_dorks(
                        url, fetch_result.html,
                        detection.get("gateways", []),
                        detection.get("platform", "Custom"),
                    )
                    added = 0
                    for dork in new_dorks:
                        primary_gw = detection["gateways"][0] if detection["gateways"] else None
                        if self.storage.add_learned_dork(dork, url, primary_gw):
                            added += 1
                    if added:
                        logger.info(f"Learned {added} new dorks from {url}")

            # Crawl for more payment/checkout links
            found_links = self.crawler.extract_donate_links(url, fetch_result.html)
            for link in found_links:
                if not self.storage.site_exists(link):
                    crawl_urls.add(link)

        # Second pass: fetch and analyze crawled links
        if crawl_urls:
            logger.info(f"Crawling {len(crawl_urls)} discovered links")
            crawl_results = await self.fetcher.fetch_many(list(crawl_urls)[:50])  # limit

            for url, fetch_result in crawl_results.items():
                if fetch_result is None:
                    continue
                detection = self.detector.analyze(url, fetch_result.html, fetch_result.headers)
                if detection:
                    detection["quality_score"] = self.scorer.score(detection)
                    site_id = self.storage.add_site(detection)
                    if site_id:
                        success = self.notifier.send_result(detection)
                        if success:
                            self.storage.mark_notified(site_id)
                        logger.info(
                            f"✅ CRAWLED: {url} | {detection['short_code']} | "
                            f"Score: {detection['quality_score']}"
                        )
                        # Learn from crawled finds too
                        new_dorks = self.learner.extract_dorks(
                            url, fetch_result.html,
                            detection.get("gateways", []),
                            detection.get("platform", "Custom"),
                        )
                        for dork in new_dorks:
                            primary_gw = detection["gateways"][0] if detection["gateways"] else None
                            self.storage.add_learned_dork(dork, url, primary_gw)

    def _run_alternative_discovery(self) -> list[str]:
        """Run crt.sh and Common Crawl on their intervals."""
        urls = []
        now = datetime.now(UTC)

        # crt.sh every N hours
        if (self.last_crtsh is None or
                (now - self.last_crtsh).total_seconds() > CRTSH_INTERVAL_HOURS * 3600):
            try:
                logger.info("Running crt.sh discovery...")
                crt_urls = self.discovery.search_crtsh()
                urls.extend(crt_urls)
                self.last_crtsh = now
                logger.info(f"crt.sh: {len(crt_urls)} URLs")
            except Exception as e:
                logger.warning(f"crt.sh discovery failed: {e}")

        # Common Crawl daily
        if (self.last_commoncrawl is None or
                (now - self.last_commoncrawl).total_seconds() > COMMONCRAWL_INTERVAL_HOURS * 3600):
            try:
                logger.info("Running Common Crawl discovery...")
                cc_urls = self.discovery.search_commoncrawl()
                urls.extend(cc_urls)
                self.last_commoncrawl = now
                logger.info(f"Common Crawl: {len(cc_urls)} URLs")
            except Exception as e:
                logger.warning(f"Common Crawl discovery failed: {e}")

        return urls

    # ---- Helpers ----

    def _sleep_until_midnight(self):
        now = datetime.now(UTC)
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=5, second=0, microsecond=0)
        seconds = (tomorrow - now).total_seconds()
        logger.info(f"Sleeping {seconds:.0f}s until midnight UTC")

        # Send daily summary before sleeping
        try:
            summary = self.exporter.generate_summary()
            self.notifier.send(summary)
        except Exception:
            pass

        self._safe_sleep(seconds)

    def _safe_sleep(self, seconds: float):
        """Sleep in small increments so shutdown signals are responsive."""
        end = time.time() + seconds
        while time.time() < end and self.running:
            time.sleep(min(1, end - time.time()))

    def _shutdown(self, signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.notifier.send("🛑 Scanner shutting down...")


if __name__ == "__main__":
    scanner = PaymentScanner()
    scanner.run()
