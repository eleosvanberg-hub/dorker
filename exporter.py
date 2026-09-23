"""CSV export functionality for found donation sites."""

import os
import tempfile
from storage import Storage
from logger_setup import setup_logger

logger = setup_logger("cern.exporter")


class Exporter:

    def __init__(self, storage: Storage):
        self.storage = storage

    def export_to_file(self, gateway_filter: str = None) -> str | None:
        """Export found sites to a temp CSV file. Returns file path or None."""
        csv_data = self.storage.export_csv(gateway_filter)
        if not csv_data:
            return None

        suffix = f"_{gateway_filter}" if gateway_filter else ""
        fd, path = tempfile.mkstemp(suffix=f"{suffix}.csv", prefix="cern_export_")
        with os.fdopen(fd, "w") as f:
            f.write(csv_data)

        logger.info(f"Exported to {path}")
        return path

    def generate_summary(self) -> str:
        """Generate a text summary of today's findings."""
        stats = self.storage.get_today_stats()
        total = self.storage.get_total_stats()

        lines = [
            "📊 Daily Summary",
            "━━━━━━━━━━━━━━━━━━━━━",
            f"🆕 Sites found today: {stats['sites_found']}",
            f"🔍 Queries used today:",
        ]
        for provider, count in stats.get("queries_used", {}).items():
            lines.append(f"   • {provider}: {count}")

        lines.append(f"\n📈 All-time total: {total['total_sites']} sites")

        if total.get("gateways"):
            lines.append("\n💳 Gateway breakdown:")
            for gw, count in sorted(total["gateways"].items(), key=lambda x: -x[1]):
                lines.append(f"   • {gw}: {count}")

        if total.get("platforms"):
            lines.append("\n🏪 Platform breakdown:")
            for plat, count in sorted(total["platforms"].items(), key=lambda x: -x[1]):
                lines.append(f"   • {plat}: {count}")

        return "\n".join(lines)
