"""
Interactive Telegram bot: sends notifications for new finds
and handles user commands (/stats, /export, /search, /pause, /resume, /top, /status).
"""

import json
import time
import threading
import requests
from typing import Callable, Optional
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, GATEWAY_SHORT, PLATFORM_SHORT
from logger_setup import setup_logger

logger = setup_logger("cern.notifier")


class TelegramNotifier:

    def __init__(self, token: str = None, chat_id: str = None):
        self.token = token or TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.session = requests.Session()
        self._command_handlers: dict[str, Callable] = {}
        self._polling = False
        self._poll_thread: Optional[threading.Thread] = None
        self._last_update_id = 0

    # ---- Sending Messages ----

    def send(self, message: str, chat_id: str = None) -> bool:
        """Send a text message. Returns True on success."""
        target = chat_id or self.chat_id
        if not self.token or not target:
            logger.warning("Telegram not configured, skipping send")
            return False

        for attempt in range(3):
            try:
                resp = self.session.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": target,
                        "text": message,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": True,
                    },
                    timeout=15,
                )
                if resp.status_code == 200:
                    return True
                if resp.status_code == 429:
                    retry_after = resp.json().get("parameters", {}).get("retry_after", 5)
                    logger.warning(f"Telegram rate limited, waiting {retry_after}s")
                    time.sleep(retry_after)
                    continue
                logger.warning(f"Telegram send failed: {resp.status_code} {resp.text[:200]}")
            except requests.RequestException as e:
                logger.warning(f"Telegram send error: {e}")
                time.sleep(2 ** attempt)
        return False

    def send_document(self, file_path: str, caption: str = "", chat_id: str = None) -> bool:
        """Send a file as a document."""
        target = chat_id or self.chat_id
        try:
            with open(file_path, "rb") as f:
                resp = self.session.post(
                    f"{self.base_url}/sendDocument",
                    data={"chat_id": target, "caption": caption},
                    files={"document": f},
                    timeout=30,
                )
            return resp.status_code == 200
        except Exception as e:
            logger.warning(f"Telegram send document error: {e}")
            return False

    # ---- Format Detection Result ----

    def format_result(self, result: dict) -> str:
        """Format a detection result into Telegram message."""
        gateways = result.get("gateways", [])
        platform = result.get("platform", "Custom")
        short_code = result.get("short_code", "")

        # Gateway + integration type
        gw_str = ", ".join(gateways)
        integration = result.get("integration_type")
        if integration:
            gw_str += f" ({integration})"

        # Captcha
        captcha = result.get("captcha")
        captcha_str = captcha if captcha else "None ✅"

        # Server
        server = result.get("server", "Unknown")

        # AVS
        avs = result.get("avs", {})
        if avs.get("enabled"):
            avs_fields = ", ".join(f.title() for f in avs.get("fields", []))
            avs_str = f"Yes ({avs_fields})"
        else:
            avs_str = "No"

        # 3DS
        three_ds = result.get("three_ds", "No") or "No"

        # Currency
        currencies = result.get("currency", [])
        currency_str = ", ".join(currencies) if currencies else "USD"

        # Amounts / pricing
        dr = result.get("donation_range", {})
        if dr.get("suggested"):
            amounts = ", ".join(f"${a}" for a in dr["suggested"])
            if dr.get("custom"):
                amounts += ", Custom"
            amounts_str = amounts
        else:
            amounts_str = "Not detected"
        amounts_label = "Amounts" if site_type in ("Donation", "Event / Ticket") else "Price Range"

        # Recurring
        recurring_str = "Yes" if result.get("recurring") else "No"

        # Quality score
        score = result.get("quality_score", 0)

        # Site type label
        site_type = result.get("site_type", "Checkout / Payment")
        invoice = result.get("invoice", {})
        type_icons = {
            "Donation": "🆕 <b>New Donation Site Found!</b>",
            "Store / Ecommerce": "🛒 <b>New Store / Ecommerce Site Found!</b>",
            "Subscription / Membership": "🔄 <b>New Subscription Site Found!</b>",
            "Event / Ticket": "🎟 <b>New Event / Ticket Site Found!</b>",
            "Invoice Payment": "📋 <b>New Invoice Payment Site Found!</b>",
            "Bill Pay": "🏦 <b>New Bill Pay Portal Found!</b>",
            "Payment Portal": "💳 <b>New Payment Portal Found!</b>",
            "Checkout / Payment": "💰 <b>New Checkout Site Found!</b>",
        }
        type_line = type_icons.get(site_type, f"🆕 <b>New {site_type} Site Found!</b>")

        msg = (
            f"{type_line}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 {result['url']}\n"
            f"📄 <b>Type:</b> {site_type}\n"
            f"💳 <b>Gateway:</b> {gw_str if gw_str else 'Not detected'}\n"
            f"🏪 <b>Platform:</b> {platform} ({short_code})\n"
            f"🛡️ <b>Captcha:</b> {captcha_str}\n"
            f"🌐 <b>Server:</b> {server}\n"
            f"📫 <b>AVS:</b> {avs_str}\n"
            f"🔐 <b>3DS:</b> {three_ds}\n"
            f"💰 <b>Currency:</b> {currency_str}\n"
            f"💵 <b>{amounts_label}:</b> {amounts_str}\n"
            f"🔄 <b>Recurring:</b> {recurring_str}\n"
            f"⭐ <b>Quality:</b> {score}/100"
        )

        # Add invoice fields if present
        if invoice.get("is_invoice") and invoice.get("fields_found"):
            fields_str = ", ".join(invoice["fields_found"][:5])
            msg += f"\n📋 <b>Invoice Fields:</b> {fields_str}"
        return msg

    def send_result(self, result: dict) -> bool:
        """Format and send a detection result."""
        message = self.format_result(result)
        return self.send(message)

    # ---- Command Handling (Polling) ----

    def register_command(self, command: str, handler: Callable):
        """Register a handler for a bot command."""
        self._command_handlers[command.lstrip("/")] = handler

    def start_polling(self):
        """Start polling for bot commands in a background thread."""
        if self._polling:
            return
        self._polling = True
        self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._poll_thread.start()
        logger.info("Telegram command polling started")

    def stop_polling(self):
        self._polling = False
        if self._poll_thread and self._poll_thread.is_alive():
            self._poll_thread.join(timeout=5)

    def close(self):
        """Clean up session resources."""
        self.stop_polling()
        self.session.close()

    def _poll_loop(self):
        """Long-poll for updates from Telegram."""
        while self._polling:
            try:
                resp = self.session.get(
                    f"{self.base_url}/getUpdates",
                    params={
                        "offset": self._last_update_id + 1,
                        "timeout": 30,
                        "allowed_updates": '["message"]',
                    },
                    timeout=35,
                )
                if resp.status_code != 200:
                    time.sleep(5)
                    continue

                data = resp.json()
                for update in data.get("result", []):
                    self._last_update_id = update["update_id"]
                    self._handle_update(update)

            except requests.RequestException:
                time.sleep(5)
            except Exception as e:
                logger.error(f"Polling error: {e}")
                time.sleep(5)

    def _handle_update(self, update: dict):
        """Process a single update from Telegram."""
        message = update.get("message", {})
        text = message.get("text", "").strip()
        chat_id = str(message.get("chat", {}).get("id", ""))

        # Only respond to the configured chat
        if chat_id != self.chat_id:
            return

        if not text.startswith("/"):
            return

        parts = text.split(maxsplit=1)
        command = parts[0].lstrip("/").split("@")[0]  # handle @botname suffix
        args = parts[1] if len(parts) > 1 else ""

        handler = self._command_handlers.get(command)
        if handler:
            try:
                handler(args, chat_id)
            except Exception as e:
                logger.error(f"Command handler error for /{command}: {e}")
                self.send(f"❌ Error: {e}", chat_id)
        else:
            self.send(
                "❓ Unknown command. Available:\n"
                "/stats - Today's stats\n"
                "/total - All-time stats\n"
                "/top - Top quality sites\n"
                "/export [gateway] - Export CSV\n"
                "/search \"query\" - Custom search\n"
                "/dorks - Most productive dorks\n"
                "/learned - Self-learned dork stats\n"
                "/pause - Pause scanner\n"
                "/resume - Resume scanner\n"
                "/status - Bot status",
                chat_id,
            )
