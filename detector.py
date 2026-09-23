"""
Detection engine: payment gateways, platforms, captcha, server, AVS, 3DS,
integration type, currency, donation amounts, and recurring support.
"""

import re
from typing import Optional
from config import (
    GATEWAY_SIGNATURES, PLATFORM_SIGNATURES, CAPTCHA_SIGNATURES,
    THREE_DS_SIGNATURES, AVS_SIGNATURES, INTEGRATION_SIGNATURES,
    SERVER_HEADERS, SERVER_NAMES, GATEWAY_SHORT, PLATFORM_SHORT,
    INVOICE_SIGNATURES,
)
from logger_setup import setup_logger

logger = setup_logger("cern.detector")


class Detector:

    # ---- Payment Gateways ----

    def detect_all_gateways(self, html: str) -> list[str]:
        html_lower = html.lower()
        found = []
        for gateway, signatures in GATEWAY_SIGNATURES.items():
            for sig in signatures:
                if sig.lower() in html_lower:
                    found.append(gateway)
                    break
        return found

    def _gateway_confidence(self, html: str, gateway: str) -> int:
        """Count how many signatures match for a gateway (0-N)."""
        html_lower = html.lower()
        sigs = GATEWAY_SIGNATURES.get(gateway, [])
        return sum(1 for s in sigs if s.lower() in html_lower)

    # ---- Platform / CMS ----

    def detect_platform(self, html: str) -> str:
        html_lower = html.lower()
        for platform, signatures in PLATFORM_SIGNATURES.items():
            for sig in signatures:
                if sig.lower() in html_lower:
                    return platform
        return "Custom"

    # ---- Captcha ----

    def detect_captcha(self, html: str) -> Optional[str]:
        html_lower = html.lower()
        # Check reCAPTCHA v3 before v2 (v3 signatures are more specific)
        for captcha_type in ["reCAPTCHA v3", "reCAPTCHA v2", "hCaptcha",
                             "Cloudflare Turnstile", "FunCaptcha", "GeeTest"]:
            sigs = CAPTCHA_SIGNATURES.get(captcha_type, [])
            for sig in sigs:
                if sig.lower() in html_lower:
                    return captcha_type
        return None

    # ---- Server / CDN ----

    def detect_server(self, headers: dict) -> str:
        """Detect server from HTTP response headers."""
        if not headers:
            return "Unknown"

        parts = []
        headers_lower = {k.lower(): v for k, v in headers.items()}

        # Check CDN / WAF headers
        for header_key, cdn_name in SERVER_HEADERS.items():
            if header_key.lower() in headers_lower:
                if cdn_name not in parts:
                    parts.append(cdn_name)

        # Check Server header
        server_val = headers_lower.get("server", "").lower()
        if server_val:
            for name_key, server_name in SERVER_NAMES.items():
                if name_key in server_val:
                    if server_name not in parts:
                        parts.append(server_name)
                    break

        # Check x-powered-by
        powered = headers_lower.get("x-powered-by", "")
        if powered:
            parts.append(f"Powered: {powered}")

        return " + ".join(parts) if parts else "Unknown"

    # ---- AVS (Address Verification) ----

    def detect_avs(self, html: str) -> dict:
        html_lower = html.lower()
        found_fields = []
        for field_type, signatures in AVS_SIGNATURES.items():
            for sig in signatures:
                if sig.lower() in html_lower:
                    found_fields.append(field_type)
                    break

        return {
            "enabled": len(found_fields) >= 2,  # need at least street+zip
            "fields": found_fields,
        }

    # ---- 3D Secure ----

    def detect_3ds(self, html: str) -> Optional[str]:
        html_lower = html.lower()
        # Check 3DS2 first (more specific)
        for sig in THREE_DS_SIGNATURES.get("3DS2", []):
            if sig.lower() in html_lower:
                return "3DS2"
        for sig in THREE_DS_SIGNATURES.get("3DS1", []):
            if sig.lower() in html_lower:
                return "3DS1"
        return None

    # ---- Integration Type ----

    def detect_integration_type(self, html: str) -> Optional[str]:
        html_lower = html.lower()
        for int_type, signatures in INTEGRATION_SIGNATURES.items():
            for sig in signatures:
                if sig.lower() in html_lower:
                    return int_type
        return None

    # ---- Currency ----

    def detect_currency(self, html: str) -> list[str]:
        currencies = []

        # Check for explicit currency codes in forms/data attributes
        currency_patterns = [
            (r'currency["\s:=]+["\']?(USD|CAD|GBP|EUR|AUD|NZD|CHF|JPY|SEK|NOK|DKK)', ""),
            (r'data-currency["\s=]+["\']?(USD|CAD|GBP|EUR|AUD)', ""),
        ]
        for pattern, _ in currency_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            currencies.extend(m.upper() for m in matches)

        # Check for currency symbols near amounts
        symbol_map = {
            r'\$\s*\d': "USD",
            r'C\$\s*\d': "CAD",
            r'A\$\s*\d': "AUD",
            r'£\s*\d': "GBP",
            r'€\s*\d': "EUR",
            r'¥\s*\d': "JPY",
        }
        for pattern, code in symbol_map.items():
            if re.search(pattern, html):
                # Don't add USD if we already found CAD/AUD with $ sign
                if code == "USD" and ("CAD" in currencies or "AUD" in currencies):
                    continue
                currencies.append(code)

        return list(dict.fromkeys(currencies))  # deduplicate, preserve order

    # ---- Donation Amounts ----

    def detect_donation_range(self, html: str) -> dict:
        result = {"suggested": [], "min": None, "max": None, "custom": False}

        # Find preset amounts from radio buttons, buttons, or data attributes
        # Match patterns like: $25, $50, $100, $250, $500, $1000
        amount_pattern = r'[\$£€]\s*(\d{1,6}(?:,\d{3})*(?:\.\d{2})?)'
        # Look for amounts near donation-related context
        donate_section = ""
        for pattern in [
            r'(?:donation|gift|give|amount|contribute)[^<]{0,500}',
            r'(?:radio|button|option)[^>]*value=["\']?\d+["\']?[^<]{0,200}',
        ]:
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            donate_section += " ".join(matches)

        if donate_section:
            amounts = re.findall(r'(\d{1,6}(?:\.\d{2})?)', donate_section)
            # Filter reasonable donation amounts
            amounts = [float(a) for a in amounts if 5 <= float(a) <= 100000]
            amounts = sorted(set(amounts))
            if amounts:
                result["suggested"] = [int(a) if a == int(a) else a for a in amounts[:8]]
                result["min"] = result["suggested"][0]
                result["max"] = result["suggested"][-1]

        # Check for custom/other amount field
        custom_patterns = [
            "other amount", "custom amount", "enter amount",
            "your amount", "choose your own", "other gift",
        ]
        html_lower = html.lower()
        result["custom"] = any(p in html_lower for p in custom_patterns)

        return result

    # ---- Recurring Donation ----

    def detect_recurring(self, html: str) -> bool:
        html_lower = html.lower()
        recurring_sigs = [
            "monthly", "recurring", "sustaining", "auto-renew",
            "monthly gift", "monthly donation", "give monthly",
            "recurring donation", "sustaining gift", "annual",
            "weekly", "quarterly", "pledge",
        ]
        return any(sig in html_lower for sig in recurring_sigs)

    # ---- Invoice / Bill Pay Page ----

    def detect_invoice_page(self, html: str, url: str) -> dict:
        """Detect if page is an invoice/bill payment portal."""
        html_lower = html.lower()
        url_lower = url.lower()

        keywords_found = []
        for kw in INVOICE_SIGNATURES["invoice_keywords"]:
            if kw.lower() in html_lower:
                keywords_found.append(kw)

        fields_found = []
        for field in INVOICE_SIGNATURES["invoice_form_fields"]:
            if field.lower() in html_lower:
                fields_found.append(field)

        url_match = any(p in url_lower for p in INVOICE_SIGNATURES["invoice_url_patterns"])

        is_invoice = len(keywords_found) >= 2 or (len(keywords_found) >= 1 and fields_found) or url_match

        if not is_invoice:
            return {"is_invoice": False, "invoice_type": None, "fields_found": []}

        # Classify type
        bill_words = ["bill pay", "pay your bill", "pay bill", "statement", "balance due", "amount due"]
        portal_words = ["payment portal", "quick pay", "express pay", "pay online"]
        if any(w in html_lower for w in bill_words):
            inv_type = "Bill Pay"
        elif any(w in html_lower for w in portal_words):
            inv_type = "Payment Portal"
        else:
            inv_type = "Invoice Payment"

        return {
            "is_invoice": True,
            "invoice_type": inv_type,
            "fields_found": fields_found,
        }

    # ---- Short Code ----

    def format_short_code(self, gateway: str, platform: str) -> str:
        g = GATEWAY_SHORT.get(gateway, gateway[:3].upper())
        p = PLATFORM_SHORT.get(platform, platform[:4].upper())
        return f"{g}+{p}"

    # ---- Full Analysis ----

    def analyze(self, url: str, html: str, headers: dict = None) -> Optional[dict]:
        """Run all detections. Returns result dict or None if no gateway found."""
        gateways = self.detect_all_gateways(html)
        invoice = self.detect_invoice_page(html, url)

        # Must have a gateway OR be an invoice page
        if not gateways and not invoice.get("is_invoice"):
            return None

        platform = self.detect_platform(html)
        captcha = self.detect_captcha(html)
        server = self.detect_server(headers or {})
        avs = self.detect_avs(html)
        three_ds = self.detect_3ds(html)
        integration = self.detect_integration_type(html)
        currency = self.detect_currency(html)
        donation_range = self.detect_donation_range(html)
        recurring = self.detect_recurring(html)

        # Calculate gateway confidence (for primary gateway)
        confidence = self._gateway_confidence(html, gateways[0]) if gateways else 0

        # Determine site type
        if invoice.get("is_invoice"):
            site_type = invoice["invoice_type"]
        else:
            site_type = "Donation"

        return {
            "url": url,
            "gateways": gateways,
            "platform": platform,
            "captcha": captcha,
            "server": server,
            "avs": avs,
            "three_ds": three_ds,
            "integration_type": integration,
            "currency": currency,
            "donation_range": donation_range,
            "recurring": recurring,
            "short_code": self.format_short_code(gateways[0], platform) if gateways else f"INV+{PLATFORM_SHORT.get(platform, platform[:4].upper())}",
            "gateway_confidence": confidence,
            "site_type": site_type,
            "invoice": invoice,
        }
