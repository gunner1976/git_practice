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
from wallet_tracker.html_report import render_html
from wallet_tracker.identity import load_file as load_identities
from wallet_tracker.pipeline import run_study
from wallet_tracker.sectors import SectorMap, flows
from wallet_tracker.regimes import REGIMES, MarketRegimes, regime_matrix, robustness
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
        # Real wraps only show the ETH leg (WETH's Deposit event is not a Transfer).
        self.assertEqual(build_events([tr("w", 0, "eth", -1, cp=weth)]), [])
        self.assertEqual(build_events([tr("u", 0, "eth", 1, cp=weth)]), [])

    def test_airdropped_spam_is_not_valued(self):
        spam = "0x" + "5a" * 20
        evs = build_events([tr("a", 0, USDC, 1000), tr("d", 0, spam, 1e12),
                            tr("s", 1, spam, -1), tr("s", 1, USDC, 20)])     # dust sale at $20/token
        book = PriceBook({"eth": {T0 + i * DAY: 2000.0 for i in range(3)}})
        res = simulate(evs, book, T0 + 2 * DAY)
        self.assertLess(res.final_equity, 2000)   # not 1e12 x $20


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


class NumeraireTest(unittest.TestCase):
    def test_eth_holder_is_flat_in_eth_terms(self):
        from wallet_tracker.analyze import numeraire_metrics
        eth = [0.05, -0.02, 0.10, 0.03, -0.01]
        m = numeraire_metrics(eth, eth, [0.0] * 5)
        self.assertAlmostEqual(m["total_return_in_eth"], 0.0)
        self.assertGreater(metrics.compound(eth), 0.1)          # looks good in dollars
        self.assertLessEqual(m["min_numeraire_sharpe"], 0.0 + 1e-9)


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
        cls.study = run_study([cls.world.history(a) for a in cls.world.addresses()], cls.world.prices,
                              cls.cfg, cls.now, cls.world.identities, sector_map=SectorMap(cls.world.sector_map))
        cls.reports = {r.address: r for r in cls.study.reports}
        cls.lb = cls.study.boards
        cls.truth = cls.world.truth

    def test_archetypes_classified(self):
        classes = [r.wallet_class for r in self.reports.values()]
        self.assertEqual(classes.count(WalletClass.BUY_HOLD), 6)
        self.assertEqual(classes.count(WalletClass.BOT), 1)
        self.assertEqual(classes.count(WalletClass.EXCHANGE), 1)
        self.assertEqual(classes.count(WalletClass.CONTRACT), 1)
        migrated = sum("migrated_to" in t for t in self.truth.values())
        self.assertEqual(classes.count(WalletClass.DORMANT), 1 + migrated)   # predecessors stop trading

    def test_luck_test_only_passes_skilled_wallets(self):
        significant = [r for r in self.lb.active if r.metrics["significant"]]
        self.assertGreaterEqual(len(significant), 5)
        for r in significant:
            self.assertGreater(self.truth[r.address]["skill"], 0, r.address)
        self.assertGreater(self.truth[self.lb.active[0].address]["skill"], 0)

    def test_human_vs_automated(self):
        for r in self.lb.active:
            style = self.truth[r.address]["style"]
            score = r.operator["human_score"]
            if style == "agent":
                self.assertLess(score, 0.4, r.address)
            elif style == "human":
                # Short records are shrunk toward 0.5; confident ones must clear 0.6.
                self.assertGreater(score, 0.6 if r.operator["human_confidence"] >= 0.9 else 0.5, r.address)
        declared = [r for r in self.reports.values() if r.group == "AI agent (declared)"]
        self.assertEqual(len(declared), 3)
        bot = next(r for r in self.reports.values() if r.wallet_class is WalletClass.BOT)
        self.assertEqual(bot.group, "hft/mev bot")
        self.assertLess(bot.operator["human_score"], 0.4)

    def test_cluster_recovered(self):
        expected = {a for a, t in self.truth.items() if "cluster" in t}
        cl = next(c for c in self.study.clusters if expected & set(c.members))
        self.assertEqual(set(cl.members), expected)
        kinds = " ".join(cl.evidence)
        for k in ("direct transfer", "common first funder", "co-trading"):
            self.assertIn(k, kinds)
        self.assertLess(cl.stats["copy_sharpe"], cl.stats["sharpe"])

    def test_migration_verified_and_stitched(self):
        old = next(a for a, t in self.truth.items() if "migrated_to" in t)
        new = self.truth[old]["migrated_to"]
        found = [m for m in self.study.migrations if m.source == old]
        self.assertEqual(len(found), 1)
        m = found[0]
        self.assertEqual(m.destination, new)
        self.assertTrue(m.verified)
        self.assertGreater(m.stitched["days"], 500)
        # Successor and predecessor become one entity.
        self.assertTrue(any({old, new} <= set(c.members) for c in self.study.clusters))
        # Nobody else is flagged as migrating.
        self.assertEqual(self.study.migration_stats["migrations"], 1)

    def test_capital_map(self):
        ents = self.study.entities
        self.assertTrue(any(e.smart for e in ents))
        for e in ents:
            self.assertAlmostEqual(sum(e.sectors_avg.values()), 1.0, delta=0.05)
        self.assertTrue(self.study.flows_smart)
        sectors = {k for m in self.study.flows_all.values() for k in m}
        self.assertIn("RWA & tokenized treasuries", sectors)
        self.assertNotIn("Other", sectors)
        # Flows come from swaps only: a wallet that only moves funds in and out has none.
        exch = next(r for r in self.study.reports if r.wallet_class is WalletClass.EXCHANGE)
        self.assertEqual(flows(exch, SectorMap(self.world.sector_map), lambda t, ts: 1.0), {})

    def test_follow_picks_up_successor(self):
        old = next(a for a, t in self.truth.items() if "migrated_to" in t)
        new = self.truth[old]["migrated_to"]
        hand_over = next(t.block for t in self.world.histories[old].transfers if t.counterparty == new)
        with tempfile.TemporaryDirectory() as d:
            wl = Watchlist(os.path.join(d, "wl.json"))
            wl.add(old, hand_over - 10)
            alerts = poll(wl, self.world, self.world, follow_migrations=True)
            self.assertTrue(any(a["kind"] == "possible_migration" for a in alerts))
            self.assertIn(new, wl.wallets)
            later = poll(wl, self.world, self.world)
            self.assertTrue(any(a["wallet"] == new for a in later))

    def test_entity_flow_alerts(self):
        old = next(a for a, t in self.truth.items() if "migrated_to" in t)
        new = self.truth[old]["migrated_to"]
        hand_over = next(t.block for t in self.world.histories[old].transfers if t.counterparty == new)
        with tempfile.TemporaryDirectory() as d:
            # Same entity: the hand-over is an internal shuffle, not an exodus.
            wl = Watchlist(os.path.join(d, "a.json"))
            wl.add(old, hand_over - 10, entity="E")
            wl.add(new, hand_over - 10, entity="E")
            alerts = poll(wl, self.world, self.world, flow_alert_usd=1_000)
            self.assertFalse(any(a["kind"] == "exodus" for a in alerts))
            # Only the old wallet followed: money left the followed operation.
            wl2 = Watchlist(os.path.join(d, "b.json"))
            wl2.add(old, hand_over - 10)
            alerts = poll(wl2, self.world, self.world, flow_alert_usd=1_000)
            self.assertTrue(any(a["kind"] == "exodus" for a in alerts))

    def test_reputation_flags(self):
        flagged = {r.address: r.reputation for r in self.reports.values() if r.reputation.flags}
        texts = " ".join(f for rep in flagged.values() for f in rep.flags)
        self.assertIn("Tornado Cash", texts)
        self.assertIn("deployed 1 contract", texts)
        mixer = next(a for a, rep in flagged.items() if any("Tornado" in f for f in rep.flags))
        self.assertEqual(self.reports[mixer].reputation.components["provenance"], 0.0)
        top = self.lb.active[0].reputation
        self.assertIn(top.tier, "AB")

    def test_matrices_and_html(self):
        self.assertIn("human (behavioural)", self.study.operator_regime)
        self.assertIn("buy-and-hold (reference)", self.study.operator_summary)
        self.assertTrue(self.study.operator_quarter["human (behavioural)"])
        page = render_html(self.study, demo=True)
        for needle in ("Wallet Edge Report", "Copy-trade performance by operator", "Cluster 1",
                       "Human vs automated", "Regime risk matrix", "Capital map", "Where smart money",
                       "Wallet migrations"):
            self.assertIn(needle, page)
        self.assertNotIn("nan", page.replace("Synthetic", ""))

    def test_follow_poll(self):
        with tempfile.TemporaryDirectory() as d:
            wl = Watchlist(os.path.join(d, "wl.json"))
            a = self.lb.active[0].address
            wl.add(a, self.world.latest_block() - 30 * DAY // 12)
            alerts = poll(wl, self.world, self.world, os.path.join(d, "alerts.jsonl"))
            self.assertTrue(alerts)
            self.assertTrue(all(x["wallet"] == a for x in alerts))
            self.assertEqual(poll(wl, self.world, self.world), [])   # nothing new
            with open(os.path.join(d, "wl.json")) as fh:
                self.assertIn(a, json.load(fh)["wallets"])


class KnowledgeBaseTest(unittest.TestCase):
    def test_runs_accumulate(self):
        from wallet_tracker.knowledge import KnowledgeBase
        studies = []
        for seed in (7, 8):
            w = SyntheticWorld(seed=seed)
            studies.append(run_study([w.history(a) for a in w.addresses()], w.prices, Config(),
                                     w.end + DAY - 1, w.identities, sector_map=SectorMap(w.sector_map)))
        with tempfile.TemporaryDirectory() as d:
            kb = KnowledgeBase(os.path.join(d, "kb.sqlite"))
            r1 = kb.record(studies[0], ts=1)
            r2 = kb.record(studies[1], ts=2)
            self.assertEqual([r[0] for r in kb.runs()], [r1, r2])
            top = kb.top(5)
            self.assertEqual([t[0] for t in top], [1, 2, 3, 4, 5])
            self.assertTrue(all(t[11] is not None for t in top))     # previous rank known
            hist = kb.wallet(top[0][1])
            self.assertEqual(len(hist), 2)
            self.assertTrue(kb.flows("smart", 3))
            self.assertTrue(kb.movers()["moved"])
            names = kb.db.execute("SELECT COUNT(*) FROM identities").fetchone()[0]
            self.assertEqual(names, 6)
            kb.close()


class ClusterEdgeTest(unittest.TestCase):
    def test_funder_shared_with_unscreened_wallet(self):
        from wallet_tracker.cluster import find_clusters
        w = SyntheticWorld(seed=7, days=200)
        a, b = w.addresses()[:2]
        rs = [analyze_wallet(w.history(x), w.prices, Config(), w.end) for x in (a, b)]
        # The outsider shares a funder with `a` but is not among the clustered wallets.
        funders = {a: "0xf00", "0xoutsider": "0xf00", b: ""}
        self.assertEqual(find_clusters(rs, {x: w.history(x) for x in (a, b)}, funders), [])


class StrategyTest(unittest.TestCase):
    def test_walk_forward_picks_only_skilled_leaders(self):
        from wallet_tracker.strategy import Rules, walk_forward
        w = SyntheticWorld(seed=7)
        res = walk_forward([w.history(a) for a in w.addresses()], w.prices, Config(), w.end + DAY - 1, 120,
                           Rules(), w.identities, None, SectorMap(w.sector_map))
        self.assertTrue(res["leaders"])
        for p in res["leaders"]:
            self.assertTrue(all(w.truth[a]["skill"] > 0 for a in p.members), p.label)
            self.assertLessEqual(p.weight, 0.25 + 1e-9)
        self.assertLessEqual(sum(p.weight for p in res["leaders"]), 0.9 + 1e-9)
        self.assertGreater(res["strategy"]["sharpe"], res["copy_all_eligible"]["sharpe"])
        self.assertGreater(res["strategy"]["return"], res["eth"]["return"])

    def test_allocation_caps(self):
        from wallet_tracker.strategy import Leader, Rules, allocate
        picks = [Leader(str(i), str(i), [str(i)], v) for i, v in enumerate([100, 1, 1, 1])]
        allocate(picks, Rules(max_weight=0.3, cash_buffer=0.1))
        self.assertAlmostEqual(picks[0].weight, 0.3)
        self.assertAlmostEqual(sum(p.weight for p in picks), 0.9)


class VenueTest(unittest.TestCase):
    def test_untradable_exposure_is_cash_and_funding_is_paid(self):
        from wallet_tracker.venue import StaticVenue, venue_copy
        prices = [1.0, 1.0, 2.0, 2.0]
        other = "0x" + "ef" * 20
        evs = build_events([tr("a", 0, USDC, 2000), tr("b", 1, USDC, -1000), tr("b", 1, TOK, 1000),
                            tr("c", 1, USDC, -1000), tr("c", 1, other, 1000)])
        book = PriceBook({TOK: {T0 + i * DAY: p for i, p in enumerate(prices)},
                          other: {T0 + i * DAY: p for i, p in enumerate(prices)},
                          "eth": {T0 + i * DAY: 2000.0 for i in range(4)}})
        res = simulate(evs, book, T0 + 3 * DAY)
        free = StaticVenue({TOK: "TOK"}, funding_apr=0.0, cost_bps=0.0)
        rs, info = venue_copy(res, free, book, 0)
        self.assertAlmostEqual(info["tradable_share"], 0.5)
        self.assertAlmostEqual(metrics.compound(rs), 0.5)          # only TOK's half doubled
        costly = StaticVenue({TOK: "TOK"}, funding_apr=3.65, cost_bps=0.0)
        rs2, _ = venue_copy(res, costly, book, 0)
        self.assertLess(metrics.compound(rs2), metrics.compound(rs))
        late = StaticVenue({TOK: "TOK"}, funding_apr=0.0, cost_bps=0.0, listed={"TOK": T0 + 3 * DAY})
        rs3, _ = venue_copy(res, late, book, 0)
        self.assertAlmostEqual(metrics.compound(rs3), 0.0)          # not listed yet when it mattered


class RoutingTest(unittest.TestCase):
    def test_spot_then_proxy_then_cash(self):
        from wallet_tracker.routing import ProxyRouter, Router, SpotRouter, PerpRouter, routed_copy
        from wallet_tracker.venue import StaticVenue
        import random
        rng = random.Random(1)
        n = 140
        listed, deep, follower, lone = ("0x" + c * 40 for c in "1234")
        base = [rng.gauss(0, 0.03) for _ in range(n)]
        def path(rets):
            p, out = 1.0, []
            for r in rets:
                p *= 1 + r
                out.append(p)
            return {T0 + i * DAY: v for i, v in enumerate(out)}
        series = {listed: path(base), deep: path([rng.gauss(0, 0.03) for _ in range(n)]),
                  follower: path([1.5 * b + rng.gauss(0, 0.005) for b in base]),
                  lone: path([rng.gauss(0, 0.03) for _ in range(n)]),
                  "eth": {T0 + i * DAY: 2000.0 for i in range(n)}}
        book = PriceBook(series)
        perp = PerpRouter(StaticVenue({listed: "L"}, funding_apr=0.0, cost_bps=0.0))
        class Liq:
            def liquidity(self, t): return 1e9 if t == deep else 0.0
        router = Router([perp, SpotRouter(Liq()), ProxyRouter(perp, book, {listed: "L"})])
        d = T0 + 120 * DAY
        self.assertEqual(router.route(listed, "L", 1, d).kind, "perp")
        self.assertEqual(router.route(deep, "D", 1, d).kind, "spot")
        rt = router.route(follower, "F", 1, d)
        self.assertEqual((rt.kind, rt.target), ("proxy", listed))
        self.assertAlmostEqual(rt.beta, 1.5, delta=0.2)
        self.assertIsNone(router.route(lone, "X", 1, d))
        # A wallet holding the follower token is replicated through its proxy.
        evs = build_events([tr("a", 100, USDC, 10_000), tr("b", 100, USDC, -10_000), tr("b", 100, follower, 10_000)])
        res = simulate(evs, book, T0 + 139 * DAY)
        rs, info = routed_copy(res, router, book, 0)
        self.assertGreater(info["route_shares"]["proxy"], 0.9)
        own = res.returns[-30:]
        cp = rs[-30:]
        mo, mc = sum(own) / 30, sum(cp) / 30
        corr = sum((a - mo) * (b - mc) for a, b in zip(own, cp)) / (
            (sum((a - mo) ** 2 for a in own) * sum((b - mc) ** 2 for b in cp)) ** 0.5)
        self.assertGreater(corr, 0.9)


class LeverageTest(unittest.TestCase):
    def test_leverage_scales_risk_not_sharpe_and_liquidates(self):
        from wallet_tracker.leverage import Policy, apply
        import random
        rng = random.Random(3)
        rs = [rng.gauss(0.002, 0.02) for _ in range(300)]
        one, two = apply(rs, Policy("1x")), apply(rs, Policy("2x", leverage=2.0))
        self.assertAlmostEqual(one["sharpe"], two["sharpe"], places=6)
        self.assertGreater(two["max_drawdown"], one["max_drawdown"])
        crash = rs[:100] + [-0.35] + rs[100:]
        self.assertTrue(apply(crash, Policy("3x", leverage=3.0))["liquidated"])
        self.assertFalse(apply(crash, Policy("1x"))["liquidated"])

    def test_vol_target_sizes_down_in_turbulence(self):
        from wallet_tracker.leverage import Policy, _lev
        calm = [0.001, -0.001] * 40
        wild = [0.06, -0.06] * 40
        p = Policy("vt", kind="vol_target", target_vol=0.4, max_leverage=5)
        self.assertGreater(_lev(p, calm), _lev(p, wild))


class RegimeTest(unittest.TestCase):
    def test_labels_and_robustness(self):
        import random
        rng = random.Random(3)
        eth, p = {}, 2000.0
        for i in range(400):
            p *= 1 + rng.gauss(0.001 if i < 200 else -0.001, 0.03)
            eth[T0 + i * DAY] = p
        reg = MarketRegimes(eth)
        self.assertTrue(set(reg.labels.values()) <= set(REGIMES))
        self.assertTrue(reg.stress)
        days = sorted(eth)[1:]
        bench = [eth[d] / eth[d - DAY] - 1 for d in days]
        steady = [b + 0.001 + rng.gauss(0, 0.002) for b in bench]     # small edge, every regime
        lucky = [b * 1.8 for b in bench]                              # pure leverage
        rob_s = robustness(regime_matrix(days, steady, bench, reg))
        rob_l = robustness(regime_matrix(days, lucky, bench, reg))
        self.assertEqual(rob_s["regimes_beaten"], 1.0)
        self.assertGreater(rob_s["regime_robustness"], rob_l["regime_robustness"])


class IdentityTest(unittest.TestCase):
    def test_file_and_kind_validation(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "ids.json")
            with open(path, "w") as fh:
                json.dump({"0xABC": {"name": "Some Fund", "kind": "fund", "source": "fund website"}}, fh)
            ids = load_identities(path)
            self.assertEqual(ids["0xabc"].kind, "fund")
            self.assertTrue(ids["0xabc"].attested)
            with open(path, "w") as fh:
                json.dump({"0xabc": {"kind": "celebrity"}}, fh)
            with self.assertRaises(ValueError):
                load_identities(path)


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
