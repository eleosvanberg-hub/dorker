"""
Smart dork mutation engine. Auto-generates and rotates search dorks,
tracks productivity, and retires unproductive patterns.
"""

import random
from datetime import datetime, timedelta, UTC
from config import STATIC_DORKS, DORK_ACTIONS, DORK_SECTORS, DORK_EXCLUSIONS, GATEWAY_SIGNATURES
from storage import Storage
from logger_setup import setup_logger

logger = setup_logger("cern.dork_generator")


class DorkGenerator:

    def __init__(self, storage: Storage):
        self.storage = storage

    def get_dorks_for_cycle(self, count: int = 10) -> list[str]:
        """Get a mix of static, generated, and productive dorks for this cycle."""
        dorks = []

        # 1. Include top productive dorks (if we have history)
        productive = self.storage.get_productive_dorks(limit=5)
        if productive:
            dorks.extend(d["dork"] for d in productive[:3])

        # 2. Pick random static dorks
        static_pool = list(STATIC_DORKS)
        random.shuffle(static_pool)
        remaining = count - len(dorks)
        dorks.extend(static_pool[:max(remaining // 2, 3)])

        # 3. Generate fresh dorks
        remaining = count - len(dorks)
        if remaining > 0:
            dorks.extend(self._generate_random_dorks(remaining))

        # 4. Add a freshness dork (recently indexed pages)
        dorks.append(self._freshness_dork())

        # 5. Remove stale/retired dorks
        stale = set(self.storage.get_stale_dorks(min_uses=10))
        dorks = [d for d in dorks if d not in stale]

        random.shuffle(dorks)
        return dorks[:count]

    def _generate_random_dorks(self, count: int) -> list[str]:
        """Generate dorks by combining action + sector + optional gateway + exclusions."""
        dorks = []
        for _ in range(count):
            action = random.choice(DORK_ACTIONS)
            sector = random.choice(DORK_SECTORS)

            # Sometimes include gateway-specific terms
            gateway_term = ""
            if random.random() < 0.4:
                gateway_name = random.choice(list(GATEWAY_SIGNATURES.keys()))
                gateway_sigs = GATEWAY_SIGNATURES[gateway_name]
                gateway_term = f' "{random.choice(gateway_sigs[:3])}"'

            dork = f'{action} {sector}{gateway_term} {DORK_EXCLUSIONS}'
            dorks.append(dork)

        return dorks

    def _freshness_dork(self) -> str:
        """Generate a dork targeting recently indexed pages."""
        week_ago = (datetime.now(UTC) - timedelta(days=7)).strftime("%Y-%m-%d")
        action = random.choice(DORK_ACTIONS)
        return f'{action} site:.org after:{week_ago} {DORK_EXCLUSIONS}'

    def generate_gateway_focused(self, gateway: str, count: int = 5) -> list[str]:
        """Generate dorks focused on a specific gateway."""
        sigs = GATEWAY_SIGNATURES.get(gateway, [])
        if not sigs:
            return []

        dorks = []
        for _ in range(count):
            sig = random.choice(sigs[:4])
            action = random.choice(DORK_ACTIONS)
            sector = random.choice(DORK_SECTORS)
            dorks.append(f'{action} "{sig}" {sector} {DORK_EXCLUSIONS}')

        return dorks
