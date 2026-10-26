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


CURRENT = "https://coins.llama.fi/prices/current/"


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

    def known(self, tokens: set[str]) -> set[str]:
        """Tokens DefiLlama prices at all (one call per 100 tokens)."""
        wanted = sorted(t for t in tokens if t not in STABLES)
        found = set()
        for i in range(0, len(wanted), 100):
            chunk = wanted[i:i + 100]
            keys = {llama_key(t, self.chain): t for t in chunk}
            data = self.http.get_json(CURRENT + ",".join(keys), {"searchWidth": "4w"})
            for key, info in (data.get("coins") or {}).items():
                if key in keys and info.get("price") and info.get("confidence", 1) >= 0.5:
                    found.add(keys[key])
        return found

    def daily_prices_ranges(self, ranges: dict[str, tuple[int, int]]) -> dict[str, dict[int, float]]:
        """Like daily_prices, but each token only over the window it was used.
        Tokens with similar windows are batched together."""
        out: dict[str, dict[int, float]] = {}
        by_start: dict[int, list[str]] = {}
        for tok, (start, _) in ranges.items():
            if tok in STABLES:
                continue
            by_start.setdefault(day_of(start) // (30 * DAY), []).append(tok)
        for bucket in by_start.values():
            start = min(ranges[t][0] for t in bucket)
            end = max(ranges[t][1] for t in bucket)
            for i in range(0, len(bucket), BATCH):
                out.update(self.daily_prices(set(bucket[i:i + BATCH]), start, end))
        return out
