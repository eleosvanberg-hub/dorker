"""
DorkLearner: extract unique phrases from confirmed payment pages and
auto-generate new hunting dorks. Every found site teaches the engine
how to find more sites like it.
"""

import re
from bs4 import BeautifulSoup
from logger_setup import setup_logger

logger = setup_logger("cern.learner")

# One strong signature per gateway — used to anchor learned dorks
GATEWAY_ANCHOR = {
    "Braintree":    "braintree-hosted-fields",
    "AuthorizeNet": "Accept.js",
    "NMI":          "CollectJS",
    "Cybersource":  "flex-microform",
    "Adyen":        "adyen-checkout",
    "Heartland":    "SecureSubmit",
    "CardConnect":  "cardpointe",
    "Spreedly":     "Spreedly.init",
    "Checkout.com": "Frames.init",
    "Nuvei":        "safecharge",
    "Payflow":      "payflowlink",
    "Chase":        "orbital",
    "Worldpay":     "wpwlOptions",
    "Moneris":      "moneris-checkout",
    "Bambora":      "bamboracheckout",
    "BlueSnap":     "bluesnap-hosted",
    "Paysafe":      "hosted.paysafe.com",
    "Clover":       "clover-sdk",
    "USAePay":      "usaepay",
    "Payeezy":      "payeezy",
    "PayTrace":     "paytrace.js",
    "Vanco":        "vancopayments",
    "Helcim":       "helcimPay",
    "Shift4":       "i4go.js",
    "OpenEdge":     "openedgepay.com",
    "Stax":         "fattjs",
    "Payrix":       "payrix.js",
    "iATS":         "iatspayments",
    "Blackbaud":    "bbpayments",
    "TouchNet":     "uPay",
    "Flywire":      "flywire.com",
    "Convergepay":  "myvirtualmerchant",
}

# Phrases so common they'd match half the internet — never make dorks from these
_PHRASE_BLACKLIST = {
    "credit card", "card number", "expiration date", "expiry date",
    "security code", "cvv", "cvc", "billing address", "submit",
    "pay now", "checkout", "payment", "amount", "total", "subtotal",
    "first name", "last name", "email address", "phone number",
    "zip code", "postal code", "country", "state", "city",
    "order summary", "order total", "cart total", "your cart",
    "continue", "cancel", "back", "next", "confirm",
    "secure payment", "secure checkout", "safe checkout",
    "powered by", "all rights reserved", "privacy policy",
    "terms of service", "return policy", "contact us",
}

# Single words that by themselves don't narrow anything
_BORING_WORDS = {
    "the", "and", "for", "this", "that", "with", "your", "our",
    "you", "are", "will", "have", "has", "was", "not", "can",
    "please", "click", "here", "more", "all", "any", "new",
    "get", "use", "its", "may", "been", "from", "into",
}


class DorkLearner:

    def extract_dorks(self, url: str, html: str, gateways: list, platform: str) -> list[str]:
        """
        Parse a confirmed payment page and return up to 8 candidate dorks.
        Each dork is an exact-phrase Google query ready to be searched.
        """
        if not html or not gateways:
            return []

        try:
            soup = BeautifulSoup(html, "html.parser")
        except Exception as e:
            logger.debug(f"BeautifulSoup parse error for {url}: {e}")
            return []

        primary = gateways[0]
        anchor = GATEWAY_ANCHOR.get(primary, "")
        dorks: list[str] = []

        # ── 1. Page title phrase + gateway anchor ─────────────────────────
        title_tag = soup.find("title")
        if title_tag:
            for phrase in self._phrases(title_tag.get_text(), max_phrases=2):
                if anchor:
                    dorks.append(f'"{phrase}" "{anchor}" -github -docs')
                else:
                    dorks.append(f'"{phrase}" inurl:checkout -github')

        # ── 2. H1 / H2 heading on the payment page ────────────────────────
        for tag in soup.find_all(["h1", "h2"])[:4]:
            text = tag.get_text().strip()
            for phrase in self._phrases(text, max_phrases=1):
                if anchor:
                    dorks.append(f'"{phrase}" "{anchor}" site:.com -github')
                else:
                    dorks.append(f'"{phrase}" "payment" site:.com -github')

        # ── 3. Submit / CTA button text ───────────────────────────────────
        for btn in soup.find_all(["button", "input"])[:20]:
            text = (btn.get_text(strip=True) or btn.get("value", "")).strip()
            words = text.split()
            if 3 <= len(words) <= 6:
                for phrase in self._phrases(text, max_phrases=1):
                    if anchor:
                        dorks.append(f'"{phrase}" "{anchor}" -github')
                    else:
                        dorks.append(f'"{phrase}" inurl:checkout site:.com')

        # ── 4. Form-level labels near the payment form ────────────────────
        pform = self._find_payment_form(soup)
        if pform:
            for label in pform.find_all("label")[:6]:
                text = label.get_text().strip()
                for phrase in self._phrases(text, min_tokens=2, max_tokens=4, max_phrases=1):
                    dorks.append(f'"{phrase}" "payment" inurl:checkout -github')

        # ── 5. Meta description — often unique marketing copy ─────────────
        meta = soup.find("meta", {"name": "description"})
        if meta:
            desc = meta.get("content", "")
            for phrase in self._phrases(desc, max_phrases=2):
                if anchor:
                    dorks.append(f'"{phrase}" "{anchor}" site:.com -github')

        # ── 6. Unique JS variable / function names near gateway code ──────
        js_patterns = self._extract_js_phrases(html, primary)
        for phrase in js_patterns[:2]:
            dorks.append(f'"{phrase}" inurl:checkout -github -npm -docs')

        # ── Deduplicate, validate, cap ────────────────────────────────────
        seen: set[str] = set()
        result: list[str] = []
        for d in dorks:
            if d and d not in seen and self._is_useful(d):
                seen.add(d)
                result.append(d)
            if len(result) >= 8:
                break

        if result:
            logger.info(f"Learned {len(result)} new dorks from {url} ({primary})")
        return result

    # ── Helpers ───────────────────────────────────────────────────────────

    def _phrases(
        self, text: str,
        min_tokens: int = 3,
        max_tokens: int = 6,
        max_phrases: int = 3,
    ) -> list[str]:
        """Extract n-gram phrases from text, filtering noise."""
        cleaned = re.sub(r"[^\w\s'\-]", " ", text.lower())
        words = [w for w in cleaned.split() if len(w) >= 3 and w not in _BORING_WORDS]

        candidates: list[str] = []
        for n in range(min_tokens, min(max_tokens + 1, len(words) + 1)):
            for i in range(len(words) - n + 1):
                phrase = " ".join(words[i : i + n])
                if phrase in _PHRASE_BLACKLIST:
                    continue
                # Must have at least one "interesting" word (not all boring)
                interesting = [w for w in phrase.split() if w not in _BORING_WORDS]
                if len(interesting) < max(1, n // 2):
                    continue
                candidates.append(phrase)

        # Prefer longer phrases — more specific
        candidates.sort(key=lambda p: -len(p.split()))
        return candidates[:max_phrases]

    def _extract_js_phrases(self, html: str, gateway: str) -> list[str]:
        """Extract unique short identifiers from the gateway JS block."""
        phrases: list[str] = []
        anchor = GATEWAY_ANCHOR.get(gateway, "")
        if not anchor:
            return []

        anchor_lower = anchor.lower()
        html_lower = html.lower()
        pos = html_lower.find(anchor_lower)
        if pos == -1:
            return []

        # Grab a 2 KB window around the anchor
        window = html[max(0, pos - 500) : pos + 1500]

        # Extract string literals that look like payment-page specific identifiers
        # e.g. "complete-your-order", "payment-step-2", specific form ids
        string_pattern = re.findall(r'["\']([a-z][a-z0-9\-]{4,40})["\']', window.lower())
        seen: set[str] = set()
        for token in string_pattern:
            if token in seen:
                continue
            seen.add(token)
            # Only keep tokens that look like specific identifiers, not common JS words
            boring = {"true", "false", "null", "none", "auto", "script", "style",
                      "class", "type", "name", "data", "value", "input", "form",
                      "button", "submit", "click", "event", "token", "error",
                      "success", "failed", "loading", "complete", "ready"}
            if token not in boring and "-" in token or len(token) > 8:
                phrases.append(token)
            if len(phrases) >= 4:
                break

        return phrases

    def _find_payment_form(self, soup: BeautifulSoup):
        """Return the most likely payment/checkout form on the page."""
        payment_keywords = [
            "credit", "card", "payment", "checkout", "billing", "braintree",
            "authorize", "stripe", "collect", "hosted-field",
        ]
        for form in soup.find_all("form"):
            form_str = str(form).lower()
            if any(kw in form_str for kw in payment_keywords):
                return form
        return None

    def _is_useful(self, dork: str) -> bool:
        """Quick sanity-check: dork must have a quoted phrase of 2+ words."""
        match = re.search(r'"([^"]{6,})"', dork)
        if not match:
            return False
        phrase = match.group(1)
        return len(phrase.split()) >= 2
