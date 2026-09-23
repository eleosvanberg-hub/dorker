"""SQLite storage for found sites, deduplication, query tracking, and stats."""

import json
import sqlite3
import csv
import io
import threading
from datetime import date, datetime
from urllib.parse import urlparse
from logger_setup import setup_logger

logger = setup_logger("cern.storage")


class Storage:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self._lock = threading.Lock()
        self._init_tables()

    def _init_tables(self):
        cur = self.conn.cursor()
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS found_sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                url_normalized TEXT UNIQUE NOT NULL,
                gateways TEXT NOT NULL,
                platform TEXT NOT NULL DEFAULT 'Custom',
                captcha TEXT,
                server TEXT,
                avs_enabled INTEGER DEFAULT 0,
                avs_fields TEXT,
                three_ds TEXT,
                integration_type TEXT,
                currency TEXT,
                donation_range TEXT,
                recurring INTEGER DEFAULT 0,
                quality_score INTEGER DEFAULT 0,
                found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notified INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS query_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                source TEXT NOT NULL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                results_count INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS daily_counter (
                date TEXT NOT NULL,
                provider TEXT NOT NULL,
                queries_used INTEGER DEFAULT 0,
                PRIMARY KEY (date, provider)
            );

            CREATE TABLE IF NOT EXISTS dork_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dork TEXT UNIQUE NOT NULL,
                times_used INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                total_results INTEGER DEFAULT 0,
                total_new_sites INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS learned_dorks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dork TEXT UNIQUE NOT NULL,
                source_url TEXT,
                gateway TEXT,
                times_used INTEGER DEFAULT 0,
                total_new_sites INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_url_normalized ON found_sites(url_normalized);
            CREATE INDEX IF NOT EXISTS idx_found_at ON found_sites(found_at);
            CREATE INDEX IF NOT EXISTS idx_gateways ON found_sites(gateways);
            CREATE INDEX IF NOT EXISTS idx_notified ON found_sites(notified);
            CREATE INDEX IF NOT EXISTS idx_learned_gateway ON learned_dorks(gateway);
        """)
        self.conn.commit()

    # ---- URL normalization and dedup ----

    def normalize_url(self, url: str) -> str:
        """Normalize URL for dedup: strip scheme, www, trailing slash, query, fragment."""
        parsed = urlparse(url)
        host = parsed.hostname or ""
        if host.startswith("www."):
            host = host[4:]
        path = parsed.path.rstrip("/")
        return f"{host}{path}".lower()

    def site_exists(self, url: str) -> bool:
        normalized = self.normalize_url(url)
        cur = self.conn.execute(
            "SELECT 1 FROM found_sites WHERE url_normalized = ?", (normalized,)
        )
        return cur.fetchone() is not None

    # ---- Site CRUD ----

    def add_site(self, result: dict) -> int | None:
        """Insert a new site from a detection result dict. Returns row id or None if duplicate."""
        normalized = self.normalize_url(result["url"])
        with self._lock:
            try:
                cur = self.conn.execute(
                    """INSERT INTO found_sites
                       (url, url_normalized, gateways, platform, captcha, server,
                        avs_enabled, avs_fields, three_ds, integration_type,
                        currency, donation_range, recurring, quality_score)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        result["url"],
                        normalized,
                        json.dumps(result.get("gateways", [])),
                        result.get("platform", "Custom"),
                        result.get("captcha"),
                        result.get("server"),
                        1 if result.get("avs", {}).get("enabled") else 0,
                        json.dumps(result.get("avs", {}).get("fields", [])),
                        result.get("three_ds"),
                        result.get("integration_type"),
                        json.dumps(result.get("currency", [])),
                        json.dumps(result.get("donation_range", {})),
                        1 if result.get("recurring") else 0,
                        result.get("quality_score", 0),
                    ),
                )
                self.conn.commit()
                return cur.lastrowid
            except sqlite3.IntegrityError:
                return None

    def mark_notified(self, site_id: int):
        with self._lock:
            self.conn.execute(
                "UPDATE found_sites SET notified = 1 WHERE id = ?", (site_id,)
            )
            self.conn.commit()

    def get_unnotified(self) -> list[dict]:
        cur = self.conn.execute(
            "SELECT * FROM found_sites WHERE notified = 0 ORDER BY quality_score DESC"
        )
        return [dict(r) for r in cur.fetchall()]

    # ---- Query quota tracking ----

    def get_daily_query_count(self, provider: str) -> int:
        today = date.today().isoformat()
        cur = self.conn.execute(
            "SELECT queries_used FROM daily_counter WHERE date = ? AND provider = ?",
            (today, provider),
        )
        row = cur.fetchone()
        return row["queries_used"] if row else 0

    def increment_query_count(self, provider: str):
        today = date.today().isoformat()
        with self._lock:
            self.conn.execute(
                """INSERT INTO daily_counter (date, provider, queries_used)
                   VALUES (?, ?, 1)
                   ON CONFLICT(date, provider)
                   DO UPDATE SET queries_used = queries_used + 1""",
                (today, provider),
            )
            self.conn.commit()

    def can_query(self, provider: str, limit: int) -> bool:
        return self.get_daily_query_count(provider) < limit

    # ---- Query logging ----

    def log_query(self, query: str, source: str, results_count: int):
        with self._lock:
            self.conn.execute(
                "INSERT INTO query_log (query, source, results_count) VALUES (?, ?, ?)",
                (query, source, results_count),
            )
            self.conn.commit()

    # ---- Dork history ----

    def update_dork_stats(self, dork: str, results: int, new_sites: int):
        with self._lock:
            self.conn.execute(
                """INSERT INTO dork_history (dork, times_used, last_used, total_results, total_new_sites)
                   VALUES (?, 1, CURRENT_TIMESTAMP, ?, ?)
                   ON CONFLICT(dork) DO UPDATE SET
                       times_used = times_used + 1,
                       last_used = CURRENT_TIMESTAMP,
                       total_results = total_results + ?,
                       total_new_sites = total_new_sites + ?""",
                (dork, results, new_sites, results, new_sites),
            )
            self.conn.commit()

    def get_productive_dorks(self, limit: int = 20) -> list[dict]:
        cur = self.conn.execute(
            """SELECT dork, times_used, total_results, total_new_sites,
                      CAST(total_new_sites AS REAL) / MAX(times_used, 1) as efficiency
               FROM dork_history
               ORDER BY efficiency DESC
               LIMIT ?""",
            (limit,),
        )
        return [dict(r) for r in cur.fetchall()]

    def get_stale_dorks(self, min_uses: int = 10) -> list[str]:
        """Get dorks that have been used many times but found 0 new sites."""
        cur = self.conn.execute(
            """SELECT dork FROM dork_history
               WHERE times_used >= ? AND total_new_sites = 0""",
            (min_uses,),
        )
        return [r["dork"] for r in cur.fetchall()]

    # ---- Stats ----

    def get_today_stats(self) -> dict:
        today = date.today().isoformat()
        cur = self.conn.execute(
            "SELECT COUNT(*) as count FROM found_sites WHERE DATE(found_at) = ?",
            (today,),
        )
        sites_today = cur.fetchone()["count"]

        cur = self.conn.execute(
            "SELECT provider, queries_used FROM daily_counter WHERE date = ?",
            (today,),
        )
        queries = {r["provider"]: r["queries_used"] for r in cur.fetchall()}

        return {"sites_found": sites_today, "queries_used": queries}

    def get_total_stats(self) -> dict:
        cur = self.conn.execute("SELECT COUNT(*) as count FROM found_sites")
        total_sites = cur.fetchone()["count"]

        cur = self.conn.execute(
            """SELECT gateways, COUNT(*) as count FROM found_sites
               GROUP BY gateways ORDER BY count DESC"""
        )
        gateway_breakdown = {}
        for row in cur.fetchall():
            for gw in json.loads(row["gateways"]):
                gateway_breakdown[gw] = gateway_breakdown.get(gw, 0) + row["count"]

        cur = self.conn.execute(
            """SELECT platform, COUNT(*) as count FROM found_sites
               GROUP BY platform ORDER BY count DESC"""
        )
        platform_breakdown = {r["platform"]: r["count"] for r in cur.fetchall()}

        return {
            "total_sites": total_sites,
            "gateways": gateway_breakdown,
            "platforms": platform_breakdown,
        }

    def get_top_sites(self, limit: int = 10, gateway_filter: str = None) -> list[dict]:
        if gateway_filter:
            cur = self.conn.execute(
                """SELECT * FROM found_sites
                   WHERE gateways LIKE ?
                   ORDER BY quality_score DESC LIMIT ?""",
                (f"%{gateway_filter}%", limit),
            )
        else:
            cur = self.conn.execute(
                "SELECT * FROM found_sites ORDER BY quality_score DESC LIMIT ?",
                (limit,),
            )
        return [dict(r) for r in cur.fetchall()]

    # ---- Learned Dorks ----

    def add_learned_dork(self, dork: str, source_url: str, gateway: str) -> bool:
        """Store a learner-generated dork. Returns True if it's new."""
        with self._lock:
            try:
                self.conn.execute(
                    """INSERT INTO learned_dorks (dork, source_url, gateway)
                       VALUES (?, ?, ?)""",
                    (dork, source_url, gateway),
                )
                self.conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False  # already exists

    def get_learned_dorks(self, limit: int = 20) -> list[dict]:
        """Return learned dorks, prioritising untested ones, then productive ones."""
        cur = self.conn.execute(
            """SELECT dork, gateway, times_used, total_new_sites
               FROM learned_dorks
               ORDER BY
                   -- Untested first
                   CASE WHEN times_used = 0 THEN 0 ELSE 1 END,
                   -- Then by efficiency
                   CAST(total_new_sites AS REAL) / MAX(times_used, 1) DESC,
                   created_at DESC
               LIMIT ?""",
            (limit,),
        )
        return [dict(r) for r in cur.fetchall()]

    def update_learned_dork_stats(self, dork: str, new_sites: int):
        with self._lock:
            self.conn.execute(
                """UPDATE learned_dorks
                   SET times_used = times_used + 1,
                       last_used  = CURRENT_TIMESTAMP,
                       total_new_sites = total_new_sites + ?
                   WHERE dork = ?""",
                (new_sites, dork),
            )
            self.conn.commit()

    def get_learned_dork_stats(self) -> dict:
        cur = self.conn.execute(
            """SELECT COUNT(*) as total,
                      SUM(CASE WHEN times_used = 0 THEN 1 ELSE 0 END) as untested,
                      SUM(total_new_sites) as total_finds
               FROM learned_dorks"""
        )
        row = cur.fetchone()
        return dict(row) if row else {}

    # ---- Export ----

    def export_csv(self, gateway_filter: str = None) -> str:
        """Export found sites to CSV string."""
        if gateway_filter:
            cur = self.conn.execute(
                "SELECT * FROM found_sites WHERE gateways LIKE ? ORDER BY quality_score DESC",
                (f"%{gateway_filter}%",),
            )
        else:
            cur = self.conn.execute(
                "SELECT * FROM found_sites ORDER BY quality_score DESC"
            )
        rows = cur.fetchall()
        if not rows:
            return ""

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "URL", "Gateways", "Platform", "Captcha", "Server", "AVS",
            "AVS Fields", "3DS", "Integration", "Currency", "Amounts",
            "Recurring", "Quality Score", "Found At",
        ])
        for row in rows:
            writer.writerow([
                row["url"],
                row["gateways"],
                row["platform"],
                row["captcha"] or "None",
                row["server"] or "Unknown",
                "Yes" if row["avs_enabled"] else "No",
                row["avs_fields"],
                row["three_ds"] or "No",
                row["integration_type"] or "Unknown",
                row["currency"],
                row["donation_range"],
                "Yes" if row["recurring"] else "No",
                row["quality_score"],
                row["found_at"],
            ])
        return output.getvalue()

    def close(self):
        self.conn.close()
