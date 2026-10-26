"""Deterministic synthetic market + wallets for demos and tests.

Contains every archetype the pipeline must tell apart: skilled active
managers, unskilled (random) active traders, buy-and-hold wallets, a bot,
an exchange-like hub, a contract and a wallet that went dormant. Skill is
modelled as foresight: with probability `skill` the wallet rotates into the
token with the best forward return, otherwise it picks at random.
"""

from __future__ import annotations

import math
import random

from ..models import DAY, Transfer, WalletHistory
from ..reconstruct import GAS

USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
GENESIS = 1_438_269_973
SLIPPAGE = 0.003
GAS_ETH = 0.0015


def block_at(ts: int) -> int:
    return (ts - GENESIS) // 12


def addr(n: int) -> str:
    return "0x" + f"{n:040x}"


class SyntheticWorld:
    def __init__(self, seed: int = 7, days: int = 540, end: int = 1_790_000_000, n_tokens: int = 8):
        self.rng = random.Random(seed)
        self.end = end - end % DAY
        self.start = self.end - (days - 1) * DAY
        self.days = [self.start + i * DAY for i in range(days)]
        self.tokens = [addr(0xA000 + i) for i in range(n_tokens)]
        self.symbols = {t: f"TOK{i}" for i, t in enumerate(self.tokens)} | {"eth": "ETH", USDC: "USDC"}
        self._make_prices()
        self.histories: dict[str, WalletHistory] = {}
        self._counter = 0
        self._build_population()

    # ------------------------------------------------------------------ market
    def _make_prices(self) -> None:
        rng = self.rng
        eth = [2500.0]
        eth_r = [rng.gauss(0.0002, 0.03) for _ in self.days[1:]]
        for r in eth_r:
            eth.append(eth[-1] * math.exp(r))
        self.prices: dict[str, dict[int, float]] = {"eth": dict(zip(self.days, eth))}
        for t in self.tokens:
            beta, vol, p = rng.uniform(0.7, 1.3), rng.uniform(0.02, 0.045), [rng.uniform(0.5, 20)]
            for r in eth_r:
                # Zero arithmetic idiosyncratic drift: no free lunch from merely holding alts.
                p.append(p[-1] * math.exp(beta * r + rng.gauss(-0.5 * vol * vol, vol)))
            self.prices[t] = dict(zip(self.days, p))

    def daily_prices(self, tokens, start, end):
        return {t: {d: p for d, p in s.items() if start - DAY <= d <= end}
                for t, s in self.prices.items() if t in tokens}

    def px(self, tok: str, d: int) -> float:
        return 1.0 if tok == USDC else self.prices[tok][d]

    # ----------------------------------------------------------------- helpers
    def _tx(self) -> str:
        self._counter += 1
        return "0x" + f"{self._counter:064x}"

    def _ts(self, d: int) -> int:
        return d + self.rng.randint(3600, DAY - 3600)

    def _deposit(self, out: list, d: int, tok: str, amt: float, cp: str | None = None) -> None:
        ts = self._ts(d)
        out.append(Transfer(self._tx(), ts, block_at(ts), tok, self.symbols[tok], amt,
                            cp or addr(self.rng.randint(1, 10**9))))

    def _swap(self, out: list, ts: int, sell: str, amt: float, buy: str, d: int) -> float:
        got = amt * self.px(sell, d) / self.px(buy, d) * (1 - SLIPPAGE)
        h, b = self._tx(), block_at(ts)
        out += [Transfer(h, ts, b, sell, self.symbols[sell], -amt, "router"),
                Transfer(h, ts, b, buy, self.symbols[buy], got, "router"),
                Transfer(h, ts, b, "eth", "ETH", -GAS_ETH, GAS)]
        return got

    # ---------------------------------------------------------------- wallets
    def trader(self, skill: float, capital: float, stop_day: int | None = None,
               hold=(3, 9), start_day: int = 0) -> str:
        rng, a, out = self.rng, addr(0xB000 + len(self.histories)), []
        self._deposit(out, self.days[start_day], USDC, capital)
        self._deposit(out, self.days[start_day], "eth", 1.0)
        cur, bal = USDC, capital
        i = start_day + 1
        last = len(self.days) - 1 if stop_day is None else stop_day
        universe = self.tokens + ["eth"]
        while i < last:
            h = rng.randint(*hold)
            j = min(i + h, len(self.days) - 1)
            if rng.random() < skill:
                nxt = max(universe, key=lambda t: self.px(t, self.days[j]) / self.px(t, self.days[i]))
            else:
                nxt = rng.choice(universe)
            # Skilled wallets also sit in stables when everything looks bad.
            if skill and rng.random() < skill and self.px(nxt, self.days[j]) < self.px(nxt, self.days[i]):
                nxt = USDC
            if nxt != cur:
                sell_amt = bal - (GAS_ETH * 50 if cur == "eth" else 0)
                bal = self._swap(out, self._ts(self.days[i]), cur, sell_amt, nxt, self.days[i])
                cur = nxt
            if rng.random() < 0.03:  # occasional top-up - must not count as profit
                self._deposit(out, self.days[i], USDC, capital * 0.2)
            i = j
        self.histories[a] = WalletHistory(a, out)
        return a

    def holder(self, capital: float, n_tokens: int = 3) -> str:
        rng, a, out = self.rng, addr(0xC000 + len(self.histories)), []
        d0 = self.days[rng.randint(0, 30)]
        self._deposit(out, d0, USDC, capital)
        self._deposit(out, d0, "eth", 0.5)
        picks = rng.sample(self.tokens + ["eth"], n_tokens)
        ts = self._ts(d0)
        for t in picks:
            self._swap(out, ts, USDC, capital / n_tokens, t, d0)
            ts += 60
        self.histories[a] = WalletHistory(a, out)
        return a

    def bot(self, capital: float) -> str:
        rng, a, out = self.rng, addr(0xD000 + len(self.histories)), []
        self._deposit(out, self.days[0], USDC, capital)
        self._deposit(out, self.days[0], "eth", 5.0)
        for d in self.days[-200:]:
            ts = d + 3600
            for _ in range(rng.randint(40, 80)):
                eth = self._swap(out, ts, USDC, capital * 0.1, "eth", d)
                # Unwind in the same block at a tiny edge.
                h, b = self._tx(), block_at(ts)
                out += [Transfer(h, ts, b, "eth", "ETH", -eth, "pool"),
                        Transfer(h, ts, b, USDC, "USDC", capital * 0.1 * 1.0007, "pool")]
                ts += rng.randint(5, 40)
        self.histories[a] = WalletHistory(a, out)
        return a

    def exchange(self) -> str:
        rng, a, out = self.rng, addr(0xE000 + len(self.histories)), []
        for d in self.days:
            for _ in range(rng.randint(2, 6)):
                self._deposit(out, d, USDC, rng.uniform(100, 50_000))
            for _ in range(rng.randint(1, 5)):
                self._deposit(out, d, USDC, -rng.uniform(100, 40_000))
        self.histories[a] = WalletHistory(a, out)
        return a

    def _build_population(self) -> None:
        rng = self.rng
        for _ in range(4):
            self.trader(skill=rng.uniform(0.15, 0.3), capital=rng.uniform(50_000, 400_000))
        for _ in range(14):
            self.trader(skill=0.0, capital=rng.uniform(20_000, 300_000))
        for _ in range(6):
            self.holder(capital=rng.uniform(20_000, 500_000))
        self.trader(skill=0.15, capital=150_000, stop_day=len(self.days) - 120)  # dormant
        self.trader(skill=0.15, capital=3_000)                                   # too small
        self.bot(capital=250_000)
        self.exchange()
        c = self.trader(skill=0.15, capital=100_000)
        self.histories[c].is_contract = True

    # ---------------------------------------------------- provider interface
    def addresses(self) -> list[str]:
        return list(self.histories)

    def latest_block(self) -> int:
        return block_at(self.end + DAY - 1)

    def history(self, address: str, start_block: int = 0, check_contract: bool = True) -> WalletHistory:
        h = self.histories[address.lower()]
        return WalletHistory(h.address, [t for t in h.transfers if t.block >= start_block],
                             h.is_contract, h.label)
