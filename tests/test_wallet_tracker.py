import json
import os
import tempfile
import unittest

from wallet_tracker import metrics
from wallet_tracker.analyze import analyze_wallet, copy_trade_returns
from wallet_tracker.config import Config
from wallet_tracker.follow import Watchlist, poll
from wallet_tracker.models import DAY, EventKind, Transfer, WalletClass, WalletHistory
from wallet_tracker.portfolio import simulate
from wallet_tracker.prices import PriceBook
from wallet_tracker.providers.synthetic import USDC, SyntheticWorld
from wallet_tracker.ranking import build
from wallet_tracker.reconstruct import GAS, build_events

T0 = 1_700_000_000 - 1_700_000_000 % DAY
TOK = "0x" + "ab" * 20


def tr(h, day, tok, amt, cp="x", sym="T"):
    ts = T0 + day * DAY + 3600
    return Transfer(h, ts, (ts - T0) // 12, tok, sym, amt, cp)


class ReconstructTest(unittest.TestCase):
    def test_kinds_and_gas(self):
        evs = build_events([
            tr("a", 0, USDC, 1000), tr("b", 1, USDC, -1000), tr("b", 1, TOK, 10),
            tr("b", 1, "eth", -0.01, GAS), tr("c", 2, TOK, -5), tr("d", 3, "eth", -0.01, GAS),
        ])
        self.assertEqual([e.kind for e in evs],
                         [EventKind.DEPOSIT, EventKind.SWAP, EventKind.WITHDRAWAL, EventKind.FEE])
        self.assertAlmostEqual(evs[1].fee, 0.01)
        self.assertNotIn("eth", evs[1].legs)

    def test_weth_wrap_nets_out(self):
        weth = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
        self.assertEqual(build_events([tr("w", 0, "eth", -1), tr("w", 0, weth, 1)]), [])


class PortfolioTest(unittest.TestCase):
    def book(self, tok_prices):
        return PriceBook({TOK: {T0 + i * DAY: p for i, p in enumerate(tok_prices)},
                          "eth": {T0 + i * DAY: 2000.0 for i in range(len(tok_prices))}})

    def test_deposits_are_not_returns(self):
        # Flat prices, wallet funded twice: zero performance.
        evs = build_events([tr("a", 0, USDC, 1000), tr("b", 3, USDC, 5000)])
        res = simulate(evs, self.book([1.0] * 6), T0 + 5 * DAY)
        self.assertAlmostEqual(metrics.compound(res.returns), 0.0)
        self.assertAlmostEqual(res.net_flows_usd, 6000)

    def test_twr_fifo_and_passive_twin(self):
        prices = [1.0, 1.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.0, 1.0]
        evs = build_events([
            tr("a", 0, USDC, 1000),
            tr("b", 0, USDC, -1000), tr("b", 0, TOK, 1000),      # buy at 1
            tr("c", 8, TOK, -1000), tr("c", 8, USDC, 2000),      # sell at 2 after the freeze
        ])
        res = simulate(evs, self.book(prices), T0 + 10 * DAY)
        self.assertAlmostEqual(metrics.compound(res.returns), 1.0)          # doubled, then in cash
        self.assertEqual(len(res.closed_trades), 1)
        self.assertAlmostEqual(res.closed_trades[0].pnl, 1000)
        # The twin kept holding TOK and round-tripped back to where it started.
        self.assertAlmostEqual(metrics.compound(res.passive_returns), 0.0)

    def test_implied_price_for_unlisted_token(self):
        unlisted = "0x" + "cd" * 20
        evs = build_events([tr("a", 0, USDC, 1000), tr("b", 0, USDC, -1000), tr("b", 0, unlisted, 50)])
        res = simulate(evs, self.book([1.0] * 3), T0 + 2 * DAY)
        self.assertAlmostEqual(res.final_equity, 1000)
        self.assertEqual(res.price_coverage, 1.0)

    def test_copy_trade_lag(self):
        prices = [1.0, 1.0, 2.0, 2.0]
        evs = build_events([tr("a", 0, USDC, 1000), tr("b", 1, USDC, -1000), tr("b", 1, TOK, 1000)])
        res = simulate(evs, self.book(prices), T0 + 3 * DAY)
        self.assertAlmostEqual(metrics.compound(copy_trade_returns(res, 0, 0)), 1.0)
        # One day late, the follower misses the jump.
        self.assertAlmostEqual(metrics.compound(copy_trade_returns(res, 1, 0)), 0.0)


class MetricsTest(unittest.TestCase):
    def test_drawdown(self):
        self.assertAlmostEqual(metrics.max_drawdown([0.1, -0.5, 0.2]), 0.5)

    def test_psr_grows_with_track_record(self):
        short = metrics.probabilistic_sharpe(0.1, 30, 0, 3)
        long = metrics.probabilistic_sharpe(0.1, 500, 0, 3)
        self.assertLess(short, long)
        self.assertGreater(long, 0.95)

    def test_luck_bar_rises_with_trials(self):
        self.assertLess(metrics.expected_max_sharpe(0.01, 10), metrics.expected_max_sharpe(0.01, 1000))


class PipelineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = SyntheticWorld(seed=7)
        cls.now = cls.world.end + DAY - 1
        cls.cfg = Config()
        cls.reports = {a: analyze_wallet(cls.world.history(a), cls.world.prices, cls.cfg, cls.now)
                       for a in cls.world.addresses()}
        cls.lb = build(list(cls.reports.values()), cls.cfg)

    def test_archetypes_classified(self):
        classes = [r.wallet_class for r in self.reports.values()]
        self.assertEqual(classes.count(WalletClass.BUY_HOLD), 6)
        self.assertEqual(classes.count(WalletClass.BOT), 1)
        self.assertEqual(classes.count(WalletClass.EXCHANGE), 1)
        self.assertEqual(classes.count(WalletClass.CONTRACT), 1)
        self.assertEqual(classes.count(WalletClass.DORMANT), 1)

    def test_skilled_wallets_rank_first_and_random_never_significant(self):
        skilled = set(self.world.addresses()[:4])
        top = {r.address for r in self.lb.active[:4]}
        self.assertGreaterEqual(len(skilled & top), 3)
        random_traders = set(self.world.addresses()[4:18])
        for r in self.lb.active:
            if r.address in random_traders:
                self.assertFalse(r.metrics["significant"], r.address)

    def test_follow_poll(self):
        with tempfile.TemporaryDirectory() as d:
            wl = Watchlist(os.path.join(d, "wl.json"))
            a = self.world.addresses()[0]
            wl.add(a, self.world.latest_block() - 30 * DAY // 12)
            alerts = poll(wl, self.world, self.world, os.path.join(d, "alerts.jsonl"))
            self.assertTrue(alerts)
            self.assertTrue(all(x["wallet"] == a for x in alerts))
            self.assertEqual(poll(wl, self.world, self.world), [])   # nothing new
            with open(os.path.join(d, "wl.json")) as fh:
                self.assertIn(a, json.load(fh)["wallets"])


class ClassifyEdgeTest(unittest.TestCase):
    def test_contract_and_label(self):
        cfg = Config()
        w = SyntheticWorld(seed=1, days=200)
        a = w.addresses()[0]
        h = w.history(a)
        h.label = "Binance 14"
        r = analyze_wallet(h, w.prices, cfg, w.end + DAY - 1)
        self.assertEqual(r.wallet_class, WalletClass.EXCHANGE)
        h2 = WalletHistory(a, h.transfers, is_contract=True)
        self.assertEqual(analyze_wallet(h2, w.prices, cfg, w.end).wallet_class, WalletClass.CONTRACT)


if __name__ == "__main__":
    unittest.main()
