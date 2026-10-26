"""Historical daily USD prices from DefiLlama's free coins API (no key)."""

from __future__ import annotations

from ..models import DAY
from ..prices import STABLES, day_of
from .http import Http

BASE = "https://coins.llama.fi/chart/"
BATCH = 5
MAX_POINTS = 500  # API limit: coins x days per request


def llama_key(token: str, chain: str = "ethereum") -> str:
    return "coingecko:ethereum" if token == "eth" else f"{chain}:{token}"


class DefiLlamaPrices:
    def __init__(self, chain: str = "ethereum"):
        self.chain = chain
        self.http = Http(min_interval=0.3, cache_ttl=12 * 3600)

    def daily_prices(self, tokens: set[str], start: int, end: int) -> dict[str, dict[int, float]]:
        wanted = sorted(t for t in tokens if t not in STABLES)
        keys = {llama_key(t, self.chain): t for t in wanted}
        out: dict[str, dict[int, float]] = {t: {} for t in wanted}
        names = list(keys)
        for i in range(0, len(names), BATCH):
            chunk = names[i:i + BATCH]
            t0 = day_of(start)
            while t0 <= end:
                span = min(MAX_POINTS // len(chunk), (end - t0) // DAY + 1)
                data = self.http.get_json(BASE + ",".join(chunk), {
                    "start": t0, "span": span, "period": "1d", "searchWidth": "600"})
                for key, info in (data.get("coins") or {}).items():
                    tok = keys.get(key)
                    if tok is None:
                        continue
                    for pt in info.get("prices", []):
                        out[tok][day_of(int(pt["timestamp"]))] = float(pt["price"])
                t0 += span * DAY
        return out
