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

from ..identity import Identity
from ..labels import EXCHANGES, MIXERS
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
        self.truth: dict[str, dict] = {}            # ground truth, for tests and the demo
        self._state: dict[str, tuple[str, float]] = {}
        sectors = ["DeFi", "DeFi", "AI", "AI", "Memes", "Infrastructure",
                   "RWA & tokenized treasuries", "Gaming & NFT"]
        self.sector_map = {t: sectors[i % len(sectors)] for i, t in enumerate(self.tokens)}
        # Stand-in execution venue: ETH and most tokens listed, the last two not.
        self.venue_coins = {"eth": "ETH", **{t: f"TOK{i}" for i, t in enumerate(self.tokens[:-2])}}
        self.identities: dict[str, Identity] = {}   # fictional attestations
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
    def _ts_for(self, d: int, style: str, tz: float) -> int:
        if style == "agent":            # software: any hour, 24/7
            return d + self.rng.randint(0, DAY - 1)
        local = self.rng.uniform(8.0, 23.5)  # people sleep
        return d + int(((local - tz) % 24) * 3600)

    def _plan(self, skill: float, start_day: int, last: int, style: str) -> list[tuple[int, str]]:
        """A sequence of (day index, token to rotate into)."""
        rng, plan, i = self.rng, [], start_day + 1
        universe = self.tokens + ["eth"]
        while i < last:
            if style == "agent":
                h = 3                               # fixed cadence
            else:
                h = rng.randint(1, 2) if rng.random() < 0.4 else rng.randint(5, 16)  # bursty
            j = min(i + h, len(self.days) - 1)
            if rng.random() < skill:
                nxt = max(universe, key=lambda t: self.px(t, self.days[j]) / self.px(t, self.days[i]))
            else:
                nxt = rng.choice(universe)
            # Skilled wallets also sit in stables when everything looks bad.
            if skill and rng.random() < skill and self.px(nxt, self.days[j]) < self.px(nxt, self.days[i]):
                nxt = USDC
            plan.append((i, nxt))
            i = j
        return plan

    def trader(self, skill: float, capital: float, stop_day: int | None = None, start_day: int = 0,
               style: str = "human", funder: str | None = None, plan=None, ts_plan=None,
               offset_secs: int = 0) -> str:
        rng, a, out = self.rng, addr(0xB000 + len(self.histories)), []
        tz = rng.choice([-5, -4, 0, 1, 2, 8, 9])
        funder = funder or rng.choice(list(EXCHANGES))
        self._deposit(out, self.days[start_day], USDC, capital, funder)
        self._deposit(out, self.days[start_day], "eth", 1.0, funder)
        last = len(self.days) - 1 if stop_day is None else stop_day
        plan = plan if plan is not None else self._plan(skill, start_day, last, style)
        cur, bal = USDC, capital
        for k, (i, nxt) in enumerate(plan):
            if i >= last:
                break
            d = self.days[i]
            if nxt != cur:
                amt = bal - (GAS_ETH * 50 if cur == "eth" else 0)
                if style == "human" and cur in (USDC, "eth"):
                    # People type round numbers into the swap box.
                    step = 500 if cur == USDC else 0.1
                    amt = max(step, math.floor(amt / step) * step)
                ts = (ts_plan[k] if ts_plan else self._ts_for(d, style, tz)) + offset_secs
                bal = self._swap(out, ts, cur, amt, nxt, d)
                cur = nxt
            if rng.random() < 0.03:  # occasional top-up - must not count as profit
                self._deposit(out, d, USDC, capital * 0.2, funder)
        self.histories[a] = WalletHistory(a, out)
        self.truth[a] = {"skill": skill, "style": style}
        self._state[a] = (cur, bal)
        return a

    def migrator(self, skill: float, capital: float) -> tuple[str, str]:
        """A trader that hands its whole book to a fresh wallet half way through."""
        m = len(self.days) // 2
        plan = self._plan(skill, 0, len(self.days) - 1, "human")
        ts_plan = [self._ts_for(self.days[i], "human", 2) for i, _ in plan]
        old = self.trader(skill, capital, stop_day=m, plan=[p for p in plan if p[0] < m],
                          ts_plan=[t for p, t in zip(plan, ts_plan) if p[0] < m])
        cur, bal = self._state[old]
        d = self.days[m]
        out = self.histories[old].transfers
        if cur != USDC:
            bal = self._swap(out, d + 3600, cur, bal, USDC, d)
        new_addr = addr(0xB000 + len(self.histories))
        h, ts = self._tx(), d + 7200
        out.append(Transfer(h, ts, block_at(ts), USDC, "USDC", -bal, new_addr))
        later = [(i, t) for i, t in plan if i > m]
        new = self.trader(skill, bal, start_day=m, funder=old, plan=later,
                          ts_plan=[t for p, t in zip(plan, ts_plan) if p[0] > m])
        assert new == new_addr
        self.truth[old]["migrated_to"] = new
        self.truth[new]["migrated_from"] = old
        return old, new

    def cluster(self, n: int, skill: float) -> list[str]:
        """One operator running several wallets: common funder, shared trade plan."""
        funder = addr(0xF00D0 + len(self.histories))
        plan = self._plan(skill, 0, len(self.days) - 1, "human")
        ts_plan = [self._ts_for(self.days[i], "human", 1) for i, _ in plan]
        members = [self.trader(skill, self.rng.uniform(40_000, 120_000), funder=funder, plan=plan,
                               ts_plan=ts_plan, offset_secs=k * 240) for k in range(n)]
        # The operator moves money between its wallets now and then.
        d = self.days[len(self.days) // 2]
        h, ts = self._tx(), d + 50_000
        self.histories[members[0]].transfers.append(Transfer(h, ts, block_at(ts), "eth", "ETH", -0.5, members[1]))
        self.histories[members[1]].transfers.append(Transfer(h, ts, block_at(ts), "eth", "ETH", 0.5, members[0]))
        for m in members:
            self.truth[m]["cluster"] = funder
        return members

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
        self.truth[a] = {"skill": 0.0, "style": "holder"}
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
        self.truth[a] = {"skill": 0.0, "style": "bot"}
        return a

    def exchange(self) -> str:
        rng, a, out = self.rng, addr(0xE000 + len(self.histories)), []
        for d in self.days:
            for _ in range(rng.randint(2, 6)):
                self._deposit(out, d, USDC, rng.uniform(100, 50_000))
            for _ in range(rng.randint(1, 5)):
                self._deposit(out, d, USDC, -rng.uniform(100, 40_000))
        self.histories[a] = WalletHistory(a, out)
        self.truth[a] = {"skill": 0.0, "style": "exchange"}
        return a

    def _build_population(self) -> None:
        rng = self.rng
        skill = lambda: rng.uniform(0.15, 0.3)  # noqa: E731
        humans = [self.trader(skill(), rng.uniform(50_000, 400_000)) for _ in range(4)]
        humans += [self.trader(0.0, rng.uniform(20_000, 300_000)) for _ in range(10)]
        agents = [self.trader(skill(), rng.uniform(50_000, 400_000), style="agent") for _ in range(4)]
        agents += [self.trader(0.0, rng.uniform(20_000, 300_000), style="agent") for _ in range(4)]
        self.cluster(3, 0.22)
        self.migrator(0.25, 120_000)
        for _ in range(6):
            self.holder(capital=rng.uniform(20_000, 500_000))
        self.trader(0.15, 150_000, stop_day=len(self.days) - 120)        # dormant
        self.trader(0.15, 3_000)                                          # too small
        self.trader(0.0, 80_000, funder=next(iter(MIXERS)))               # mixer-funded
        dep = self.trader(0.0, 90_000)
        self.histories[dep].deployed_contracts = [addr(0xDE9)]             # token deployer
        self.bot(capital=250_000)
        self.exchange()
        c = self.trader(0.15, 100_000)
        self.histories[c].is_contract = True

        # Fictional, clearly-marked attestations so the identity paths are exercised.
        for k, a in enumerate(humans[:2] + humans[5:6]):
            self.identities[a] = Identity(f"demo-trader-{k + 1}.eth", "person",
                                          ["ENS reverse record", "Farcaster verified address"])
        for k, a in enumerate(agents[:2] + agents[5:6]):
            self.identities[a] = Identity(f"demo-agent-{k + 1}", "ai_agent", ["agent registry (demo)"])

    # ---------------------------------------------------- provider interface
    def addresses(self) -> list[str]:
        return list(self.histories)

    def latest_block(self) -> int:
        return block_at(self.end + DAY - 1)

    def history(self, address: str, start_block: int = 0, check_contract: bool = True) -> WalletHistory:
        h = self.histories[address.lower()]
        return WalletHistory(h.address, [t for t in h.transfers if t.block >= start_block],
                             h.is_contract, h.label, list(h.deployed_contracts))
