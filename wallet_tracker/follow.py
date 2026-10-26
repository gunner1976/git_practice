"""Watchlist: follow chosen wallets and alert on every new trade."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field

from .models import DAY, EventKind
from .prices import PriceBook
from .reconstruct import build_events

DEFAULT_STATE = os.path.expanduser("~/.wallet_tracker/watchlist.json")


@dataclass
class Watchlist:
    path: str = DEFAULT_STATE
    wallets: dict[str, dict] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str = DEFAULT_STATE) -> "Watchlist":
        if os.path.exists(path):
            with open(path) as fh:
                return cls(path, json.load(fh).get("wallets", {}))
        return cls(path)

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w") as fh:
            json.dump({"wallets": self.wallets}, fh, indent=2)
        os.replace(tmp, self.path)

    def add(self, address: str, from_block: int, note: str = "") -> None:
        self.wallets.setdefault(address.lower(), {"last_block": from_block, "added": int(time.time()),
                                                  "note": note})

    def remove(self, address: str) -> bool:
        return self.wallets.pop(address.lower(), None) is not None


def qty(x: float) -> str:
    return f"{x:,.0f}" if x >= 1000 else f"{x:.4g}"


def describe(ev, book: PriceBook) -> tuple[str, float]:
    def leg(tok: str, amt: float) -> tuple[str, float]:
        p = book.price(tok, ev.timestamp)
        usd = abs(amt) * p if p else 0.0
        sym = ev.symbols.get(tok, tok[:10])
        return (f"{qty(abs(amt))} {sym}" + (f" (${usd:,.0f})" if p else "")), usd

    sold = [leg(t, a) for t, a in ev.sold.items()]
    bought = [leg(t, a) for t, a in ev.bought.items()]
    usd = max(sum(u for _, u in sold), sum(u for _, u in bought))
    if ev.kind is EventKind.SWAP:
        text = f"SWAP  sold {', '.join(s for s, _ in sold)}  ->  bought {', '.join(s for s, _ in bought)}"
    elif ev.kind is EventKind.DEPOSIT:
        text = f"IN    received {', '.join(s for s, _ in bought)}"
    else:
        text = f"OUT   sent {', '.join(s for s, _ in sold)}"
    return text, usd


def poll(watch: Watchlist, provider, price_source, alerts_path: str | None = None,
         min_usd: float = 0.0, swaps_only: bool = False) -> list[dict]:
    """Fetch activity since each wallet's last seen block; return new alerts."""
    alerts: list[dict] = []
    head = provider.latest_block()
    for address, st in watch.wallets.items():
        hist = provider.history(address, st["last_block"] + 1, check_contract=False)
        events = [e for e in build_events(hist.transfers) if e.kind is not EventKind.FEE]
        if swaps_only:
            events = [e for e in events if e.kind is EventKind.SWAP]
        if events:
            tokens = {t for e in events for t in e.legs} | {"eth"}
            series = price_source.daily_prices(tokens, events[0].timestamp - DAY, events[-1].timestamp)
            book = PriceBook(series)
            for e in events:
                text, usd = describe(e, book)
                if usd < min_usd:
                    continue
                alerts.append({"wallet": address, "note": st.get("note", ""), "time": e.timestamp,
                               "block": e.block, "tx": e.tx_hash, "kind": e.kind.value,
                               "usd": round(usd, 2), "text": text})
        st["last_block"] = max([head] + [e.block for e in events])
    watch.save()
    if alerts_path and alerts:
        os.makedirs(os.path.dirname(alerts_path) or ".", exist_ok=True)
        with open(alerts_path, "a") as fh:
            for a in alerts:
                fh.write(json.dumps(a) + "\n")
    return alerts
