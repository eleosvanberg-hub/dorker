"""
Quality scoring engine. Rates each found site 1-100 based on
multiple factors to help prioritize the best finds.
"""

from config import SCORE_WEIGHTS
from logger_setup import setup_logger

logger = setup_logger("cern.scorer")


class QualityScorer:

    def score(self, result: dict) -> int:
        """Calculate quality score (0-100) for a detection result."""
        score = 0

        # Gateway confidence (0-20)
        confidence = result.get("gateway_confidence", 1)
        gateway_score = min(confidence * 5, SCORE_WEIGHTS["gateway_confidence"])
        score += gateway_score

        # AVS present (+10)
        if result.get("avs", {}).get("enabled"):
            score += SCORE_WEIGHTS["avs_present"]

        # Captcha (+10 if none, -5 if present)
        if result.get("captcha") is None:
            score += SCORE_WEIGHTS["no_captcha"]
        else:
            score += SCORE_WEIGHTS["has_captcha"]

        # Platform identified (+5)
        if result.get("platform", "Custom") != "Custom":
            score += SCORE_WEIGHTS["platform_identified"]

        # Recurring donations (+5)
        if result.get("recurring"):
            score += SCORE_WEIGHTS["has_recurring"]

        # HTTPS (+5)
        url = result.get("url", "")
        if url.startswith("https://"):
            score += SCORE_WEIGHTS["https"]

        # 3D Secure (-5 if present)
        if result.get("three_ds"):
            score += SCORE_WEIGHTS["has_3ds"]

        # Multiple currencies (+5)
        currencies = result.get("currency", [])
        if len(currencies) > 1:
            score += SCORE_WEIGHTS["multi_currency"]

        # Clamp to 0-100
        return max(0, min(100, score))
