"""Command line interface.

  python -m wallet_tracker rank --demo
  python -m wallet_tracker rank --addresses wallets.txt --json out.json
  python -m wallet_tracker rank --discover 0x1f98...,0x5149... --top 25
  python -m wallet_tracker analyze 0xabc...
  python -m wallet_tracker follow add 0xabc... --note "rotator"
  python -m wallet_tracker follow poll --loop --interval 300
  python -m wallet_tracker follow report
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

from .analyze import fetch_series
from .config import Config
from .follow import DEFAULT_STATE, Watchlist, poll
from .html_report import render_html
from .identity import load_file as load_identities
from .identity import resolve
from .knowledge import KnowledgeBase
from .models import DAY, WalletClass, history_from_json, history_to_json
from .pipeline import run_study
from .metrics import compound
from .migration import classify_destinations, universe_breakdown
from .prices import STABLES, PriceBook
from .sectors import SectorMap
from .strategy import Leader, Rules, funnel, portfolio_returns, select, walk_forward
from .report import num, pct, rolling, short, study_text, table, to_json, wallet_text


class Env:
    """Bundles the history provider, price source and clock."""

    def __init__(self, args):
        if args.demo:
            from .providers.synthetic import SyntheticWorld
            self.world = SyntheticWorld(seed=args.seed)
            self.provider = self.prices = self.world
            self.labels = {}
            self.now = self.world.end + DAY - 1
            self.head = self.world.latest_block()
        else:
            from .providers.defillama import DefiLlamaPrices
            from .providers.etherscan import Etherscan
            labels = {}
            if getattr(args, "labels", None):
                with open(args.labels) as fh:
                    labels = json.load(fh)
            self.world = None
            self.labels = labels
            self.provider = Etherscan(chain_id=args.chain_id, labels=labels,
                                      max_pages=getattr(args, "max_pages", 15))
            chains = {1: "ethereum", 10: "optimism", 8453: "base", 42161: "arbitrum"}
            if args.chain_id not in chains:
                raise SystemExit(f"chain {args.chain_id} unsupported; ETH-native chains: {sorted(chains)}")
            self.prices = DefiLlamaPrices(chains[args.chain_id])
            self.now = int(time.time())
            self.head = self.provider.latest_block()


def _addresses(args, env: Env) -> list[str]:
    out: list[str] = []
    for a in args.addresses or []:
        if os.path.exists(a):
            with open(a) as fh:
                out += [ln.split("#")[0].strip() for ln in fh if ln.split("#")[0].strip()]
        else:
            out += [x.strip() for x in a.split(",") if x.strip()]
    if getattr(args, "discover", None):
        out += env.provider.discover(args.discover.split(","), top=args.discover_top)
    if getattr(args, "discover_swappers", False):
        print("  discovering persistent DEX traders…", file=sys.stderr)
        out += env.provider.discover_swappers(days=args.discover_days, top=args.discover_top)
    if env.world is not None and not out:
        out = env.world.addresses()
    seen, uniq = set(), []
    for a in out:
        if a.lower() not in seen:
            seen.add(a.lower())
            uniq.append(a.lower())
    return uniq


def _history(env: Env, address: str, args):
    """Fetch one wallet's history, through an optional on-disk cache."""
    start = 0
    if env.world is None and getattr(args, "since_days", 0):
        start = max(0, env.head - int(args.since_days * 7_200))
    cache_dir = getattr(args, "history_cache", None)
    path = os.path.join(cache_dir, f"{address}-{args.chain_id}-{getattr(args, 'since_days', 0)}.json") if cache_dir else None
    if path and os.path.exists(path):
        with open(path) as fh:
            raw = json.load(fh)
        h = history_from_json(raw)
        if "tx_targets" not in raw and env.world is None:  # cached before venues were tracked
            h.tx_targets = env.provider.tx_targets(address, start)
            with open(path, "w") as fh:
                json.dump(history_to_json(h), fh)
        return h
    h = env.provider.history(address, start)
    if path:
        os.makedirs(cache_dir, exist_ok=True)
        with open(path, "w") as fh:
            json.dump(history_to_json(h), fh)
    return h


def _study(addresses: list[str], env: Env, cfg: Config, args):
    histories = []
    t0 = time.time()
    for i, a in enumerate(addresses, 1):
        print(f"\r  fetching {i}/{len(addresses)} {a}  ({time.time() - t0:.0f}s)", end="",
              file=sys.stderr, flush=True)
        try:
            histories.append(_history(env, a, args))
        except Exception as exc:  # one bad address shouldn't sink a whole screen
            print(f"\n  skip {a}: {exc}", file=sys.stderr)
    print("\n  pricing…", file=sys.stderr)
    series = fetch_series(env.prices, histories, env.now)
    addrs = [h.address for h in histories]
    file_ids = load_identities(args.identities) if getattr(args, "identities", None) else {}
    if env.world is not None:
        file_ids = {**env.world.identities, **file_ids}
    if getattr(args, "ens", False) or getattr(args, "farcaster", False):
        print("  resolving identities…", file=sys.stderr)
    ids = resolve(addrs, file_ids, ens=getattr(args, "ens", False), farcaster=getattr(args, "farcaster", False))
    extra = {}
    if getattr(args, "sectors", None):
        with open(args.sectors) as fh:
            extra = json.load(fh)
    if env.world is not None:
        extra = {**env.world.sector_map, **extra}
    smap = SectorMap(extra, online=getattr(args, "sectors_online", False))
    return run_study(histories, series, cfg, env.now, ids, env.labels, smap, _venue(args, env), _routing(args, env))


def funnel_text(stages: list[dict], study) -> str:
    out = ["\nTHE FUNNEL (each gate keeps the survivors of the one before; the last gate is replication)"]
    top = stages[0]["count"] or 1
    prev = top
    for i, s in enumerate(stages):
        bar = "#" * max(1, round(40 * s["count"] / top)) if s["count"] else ""
        drop = f"  (-{prev - s['count']})" if i else ""
        out.append(f"  {s['count']:>5}  {bar:<40}  {s['stage']}{drop}")
        prev = s["count"]
    final = stages[-1]["survivors"]
    by = {r.address: r for r in study.reports}
    if final:
        out.append("\n  SURVIVORS:")
        for a in final:
            r = by[a]
            mm = r.metrics
            out.append(f"   {a}  {r.group}  CAGR {pct(mm['cagr'])}  Sharpe {num(mm['sharpe'])}  "
                       f"luck {mm.get('dsr', 0):.0%}  copy Sharpe {num(mm.get('venue_copy_sharpe', mm.get('copy_sharpe', 0)))}")
    else:
        last = next((s for s in reversed(stages) if s["count"]), stages[0])
        out.append(f"\n  no wallet clears every gate yet; the furthest anyone got: {last['stage']}")
    return "\n".join(out)


def cmd_rank(args) -> None:
    cfg = Config.load(args.config)
    env = Env(args)
    study = _study(_addresses(args, env), env, cfg, args)
    lb = study.boards
    if study.migrations and hasattr(env.provider, "peek"):
        print(f"  checking {len(study.migrations)} outflow destinations…", file=sys.stderr)
        classify_destinations(study.migrations, env.provider, env.labels)
        study.migration_stats.update(universe_breakdown(study.migrations, study.migration_stats.get("wallets", 0)))
    print(study_text(study, args.top))
    print(funnel_text(funnel(study, _rules(args)), study))
    if args.json:
        with open(args.json, "w") as fh:
            fh.write(to_json(lb))
        print(f"\nwrote {args.json}", file=sys.stderr)
    if args.html:
        with open(args.html, "w") as fh:
            fh.write(render_html(study, demo=bool(args.demo)))
        print(f"wrote {args.html}", file=sys.stderr)
    if args.kb:
        kb = KnowledgeBase(args.kb)
        run = kb.record(study, args.chain_id, note="demo" if args.demo else "")
        kb.close()
        print(f"stored run {run} in {args.kb}", file=sys.stderr)
    if args.follow_top:
        wl = Watchlist.load(args.state)
        head = env.provider.latest_block()
        for r in lb.active[:args.follow_top]:
            # Follow the whole entity (node of control), not just the ranked wallet.
            ent = next((e for e in study.entities if r.address in e.members), None)
            for a in (ent.members if ent else [r.address]):
                wl.add(a, head, note=f"rank {r.rank} score {r.score:.0f}", entity=ent.id if ent else a)
        wl.save()
        print(f"following top {args.follow_top} in {wl.path}", file=sys.stderr)


def cmd_analyze(args) -> None:
    cfg = Config.load(args.config)
    env = Env(args)
    addrs = _addresses(args, env) if args.addresses else []
    target = args.address.lower()
    study = _study(list(dict.fromkeys([target] + addrs)), env, cfg, args)
    print(wallet_text(next(r for r in study.reports if r.address == target)))


def cmd_follow(args) -> None:
    wl = Watchlist.load(args.state)
    if args.action == "list":
        rows = [[a, str(s["last_block"]), s.get("note", "")] for a, s in wl.wallets.items()]
        print(table(["wallet", "last block", "note"], rows) if rows else "watchlist empty")
        return
    if args.action == "remove":
        for a in args.wallets:
            print(("removed " if wl.remove(a) else "not found ") + a)
        wl.save()
        return

    env = Env(args)
    if args.action == "add":
        head = env.provider.latest_block()
        start = head - int(args.backfill_days * DAY / 12)  # ~12s blocks
        for a in args.wallets:
            wl.add(a, start, args.note, entity=args.entity)
        wl.save()
        print(f"following {len(args.wallets)} wallet(s); state in {wl.path}")
    elif args.action == "poll":
        while True:
            for al in poll(wl, env.provider, env.prices, args.alerts, args.min_usd, args.swaps_only,
                           args.follow_migrations, args.migration_usd, args.flow_alert_usd):
                when = datetime.fromtimestamp(al["time"], timezone.utc).strftime("%Y-%m-%d %H:%M")
                tag = f" [{al['note']}]" if al["note"] else ""
                print(f"{when}  {short(al['wallet'])}{tag}  {al['text']}")
            if not args.loop:
                break
            time.sleep(args.interval)
    elif args.action == "report":
        cfg = Config.load(args.config)
        reports = _study(list(wl.wallets), env, cfg, args).reports
        rows = []
        for r in reports:
            m, rec = r.metrics, rolling(r, 90)
            flags = []
            if r.wallet_class is not WalletClass.ACTIVE:
                flags.append(r.wallet_class.value)
            if rec["sharpe"] < 0:
                flags.append("90d Sharpe<0")
            if rec["current_drawdown"] > 0.5 * max(m["max_drawdown"], 0.1):
                flags.append("deep in drawdown")
            if m.get("copy_capture", 1) < 0.3:
                flags.append("hard to copy")
            if r.reputation and r.reputation.flags:
                flags += r.reputation.flags
            rows.append([short(r.address), wl.wallets[r.address].get("note", ""),
                         f"{r.reputation.tier} {r.reputation.score:.0f}", r.group, pct(m["cagr"]),
                         num(m["sharpe"]), pct(rec["return"]), num(rec["sharpe"]), pct(-rec["current_drawdown"]),
                         pct(m.get("copy_cagr", float("nan"))), ", ".join(flags) or "ok"])
        print(table(["wallet", "note", "rep", "operator", "CAGR", "Sharpe", "90d ret", "90d Sharpe", "cur DD", "copy CAGR",
                     "flags"], rows))


def _venue(args, env: Env):
    """The execution venue copies are simulated on, or None for frictionless spot copying."""
    name = getattr(args, "venue", None)
    if not name:
        return None
    if env.world is not None:
        from .venue import StaticVenue
        return StaticVenue(env.world.venue_coins, name="demo venue")
    from .venue import Hyperliquid
    return Hyperliquid()


def _routing(args, env: Env) -> dict | None:
    """--route spot,proxy: let untradable positions go to DEX spot and/or proxies."""
    kinds = {k.strip() for k in (getattr(args, "route", "") or "").split(",") if k.strip()}
    if not kinds or not getattr(args, "venue", None):
        return None
    liq = None
    if "spot" in kinds:
        if env.world is not None:
            liq = env.world.liquidity
        else:
            from .routing import Dexscreener
            liq = Dexscreener()
    return {"liquidity": liq, "proxy": "proxy" in kinds, "capital": args.copy_capital,
            "min_liquidity": args.min_liquidity}


def _rules(args) -> Rules:
    return Rules(min_dsr=args.min_dsr, min_copy_sharpe=args.min_copy_sharpe, reaction_days=args.reaction_days,
                 require_identity=args.require_identity, max_leaders=args.max_leaders,
                 min_tradable_share=args.min_tradable,
                 max_weight=args.max_weight, cash_buffer=args.cash_buffer)


def _inputs(args, env: Env, cfg: Config):
    """Histories, prices, identities and sectors - the same inputs `rank` uses."""
    histories = [_history(env, a, args) for a in _addresses(args, env)]
    series = fetch_series(env.prices, histories, env.now)
    file_ids = load_identities(args.identities) if args.identities else {}
    if env.world is not None:
        file_ids = {**env.world.identities, **file_ids}
    ids = resolve([h.address for h in histories], file_ids, ens=args.ens)
    extra = {**(env.world.sector_map if env.world is not None else {})}
    return histories, series, ids, SectorMap(extra)


def _leader_rows(leaders) -> str:
    return table(["leader", "wallets", "weight", "copy Sharpe", "copy CAGR", "RRS", "rep"],
                 [[p.label, str(len(p.members)), f"{p.weight:.0%}", num(p.stats["copy_sharpe"]),
                   pct(p.stats["copy_cagr"]), num(p.stats["rrs"]), f"{p.stats['reputation']:.0f}"]
                  for p in leaders]) if leaders else "  no entity passed the selection rules"


def cmd_backtest(args) -> None:
    cfg = Config.load(args.config)
    env = Env(args)
    histories, series, ids, smap = _inputs(args, env, cfg)
    res = walk_forward(histories, series, cfg, env.now, args.holdout_days, _rules(args), ids, env.labels, smap,
                       _venue(args, env), _routing(args, env))
    cut = datetime.fromtimestamp(res["cutoff"], timezone.utc).strftime("%Y-%m-%d")
    print(f"WALK-FORWARD: leaders chosen with data up to {cut}, judged on the {args.holdout_days} days after\n")
    print(_leader_rows(res["leaders"]))
    print()
    rows = [[name, pct(res[k]["return"]), pct(res[k]["cagr"]), num(res[k]["sharpe"]), pct(-res[k]["max_drawdown"])]
            for name, k in [("strategy (selected leaders)", "strategy"),
                            ("copy every eligible wallet", "copy_all_eligible"),
                            ("copy top past returns (naive)", "copy_top_past_returns"), ("hold ETH", "eth")]]
    print(table(["after cutoff", "return", "CAGR", "Sharpe", "max DD"], rows))
    print(f"\ninvested {sum(p.weight for p in res['leaders']):.0%}; the rest is cash (capped weights + buffer)")
    if res["leaders"]:
        print("\nLEVERAGE on the strategy (sized only on past copy returns; daily liquidation model, cross margin)")
        print(table(["policy", "avg lev", "return", "CAGR", "Sharpe", "max DD", "liquidated", "survives 10/20/30% crash"],
                    [[x["policy"], f"{x['avg_leverage']:.2f}x", pct(x["return"]), pct(x["cagr"]), num(x["sharpe"]),
                      pct(-x["max_drawdown"]), "YES" if x["liquidated"] else "no",
                      "/".join("no" if v else "yes" for v in x["stress"].values())]
                     for x in res["leverage"]]))


def cmd_paper(args) -> None:
    cfg = Config.load(args.config)
    env = Env(args)
    if args.action == "init":
        histories, series, ids, smap = _inputs(args, env, cfg)
        study = run_study(histories, series, cfg, env.now, ids, env.labels, smap, _venue(args, env),
                          _routing(args, env))
        leaders = select(study, _rules(args))
        state = {"start": env.now, "capital": args.capital, "chain_id": args.chain_id, "venue": args.venue,
                 "leaders": [{"label": p.label, "members": p.members, "weight": p.weight, "stats": p.stats}
                             for p in leaders]}
        os.makedirs(os.path.dirname(args.paper) or ".", exist_ok=True)
        with open(args.paper, "w") as fh:
            json.dump(state, fh, indent=2)
        print(_leader_rows(leaders))
        print(f"\npaper portfolio of ${args.capital:,.0f} started; state in {args.paper}")
        return
    with open(args.paper) as fh:
        state = json.load(fh)
    members = sorted({a for p in state["leaders"] for a in p["members"]})
    histories = [_history(env, a, args) for a in members]
    series = fetch_series(env.prices, histories, env.now)
    args.venue = state.get("venue")
    venue = _venue(args, env)
    study = run_study(histories, series, cfg, env.now, venue=venue)
    leaders = [Leader(p["label"], p["label"], p["members"], p["weight"], p["stats"]) for p in state["leaders"]]
    start_day = state["start"] - state["start"] % DAY
    days, rs = portfolio_returns(study, leaders, start_day)
    eth_days, eth = study.eth
    eth_after = [x for d, x in zip(eth_days, eth) if d > start_day]
    nav = state["capital"] * (1 + compound(rs))
    print(f"PAPER PORTFOLIO since {datetime.fromtimestamp(state['start'], timezone.utc):%Y-%m-%d} "
          f"({len(rs)} days): ${state['capital']:,.0f} -> ${nav:,.0f} ({pct(compound(rs))}); "
          f"ETH {pct(compound(eth_after))}")
    # What to hold now: leaders' latest token weights, blended by allocation.
    target: dict[str, float] = {}
    for p in leaders:
        rs_ = [r for r in study.reports if r.address in p.members]
        eq = sum(r.result.final_equity for r in rs_) or 1.0
        for r in rs_:
            for tok, w in (r.result.weights[-1] if r.result.weights else {}).items():
                target[tok] = target.get(tok, 0.0) + p.weight * w * r.result.final_equity / eq
    capped = [t for t, w in target.items() if w > args.max_token_weight]
    for t in capped:  # leaders crowding into one token is concentration risk: excess stays in cash
        target[t] = args.max_token_weight
    syms = {}
    for r in study.reports:
        syms.update(r.result.symbols)
    cash = 1 - sum(target.values())
    book = PriceBook(series)
    instrument = {}
    if venue is not None:
        untradable = 0.0
        for t in list(target):
            c = venue.coin_for(t, syms.get(t, ""), book.price(t, env.now))
            if c and venue.listed_on(c, env.now - env.now % DAY):
                instrument[t] = f"{c}-PERP long 1x"
            elif t not in STABLES:
                untradable += target.pop(t)
        cash = 1 - sum(target.values())
        if untradable:
            print(f"\n{untradable:.1%} of the leaders' book is not tradable on {venue.name}; held as cash")
    rows = [[syms.get(t, t[:10]), instrument.get(t, "spot" if venue is None else "cash (stablecoin)"), t,
             f"{w:.1%}", f"${w * nav:,.0f}"] for t, w in sorted(target.items(), key=lambda x: -x[1]) if w >= 0.005]
    rows.append(["cash", "", "", f"{cash:.1%}", f"${cash * nav:,.0f}"])
    print("\nTARGET HOLDINGS NOW (leaders' latest positions, blended by allocation"
          + (f"; capped at {args.max_token_weight:.0%} per token" if capped else "") + ")")
    print(table(["token", "instrument", "address", "weight", "value"], rows))


def cmd_perps(args) -> None:
    """Screen Hyperliquid perps traders with the same luck test."""
    from .providers.hyperliquid_accounts import HyperliquidAccounts, deflate, perp_metrics
    from .ranking import _percentiles
    hl = HyperliquidAccounts()
    lb = hl.leaderboard()
    addrs = hl.candidates(args.min_value, args.top)
    from .providers.defillama import DefiLlamaPrices
    now = int(time.time())
    bench = DefiLlamaPrices().daily_prices({"eth", "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599"},
                                           now - 1100 * DAY, now)
    eth, btc = bench.get("eth", {}), bench.get("0x2260fac5e5542a773aa44fbcfedf7c193bc2c599", {})
    rows = []
    for i, a in enumerate(addrs, 1):
        print(f"\r  fetching {i}/{len(addrs)}", end="", file=sys.stderr, flush=True)
        try:
            m = perp_metrics(hl.history(a), eth, btc)
        except Exception as exc:
            print(f"\n  skip {a}: {exc}", file=sys.stderr)
            continue
        m["address"], m["alias"] = a, lb[a]["alias"]
        rows.append(m)
    print(file=sys.stderr)
    luck = deflate(rows)
    scored = [r for r in rows if "dsr" in r and r["span_days"] >= args.min_days]
    for r in scored:
        r["class"] = ("market maker / HFT" if r["annual_turnover"] > args.mm_turnover
                      else "inactive / vault" if r["annual_turnover"] < 5 else "trader")
    traders = [r for r in scored if r["class"] == "trader"]
    weights = {"sharpe": (1.5, True), "dsr": (1.5, True), "max_drawdown": (1.0, False),
               "pct_positive": (1.0, True), "cagr": (1.0, True)}
    for k, (w, hib) in weights.items():
        for r, p in zip(traders, _percentiles([r[k] for r in traders], hib)):
            r["score"] = r.get("score", 0.0) + w * p
    for r in traders:
        r["score"] = 100 * r["score"] / sum(w for w, _ in weights.values())
    traders.sort(key=lambda r: (r["dsr"] >= 0.95, r["score"]), reverse=True)
    print(f"HYPERLIQUID PERPS TRADERS: {len(rows)} screened (accounts >= ${args.min_value:,.0f}, most active), "
          f"{len(traders)} directional traders with >= {args.min_days}d history; set aside: "
          f"{sum(r['class'] == 'market maker / HFT' for r in scored)} market makers / HFT, "
          f"{sum(r['class'] == 'inactive / vault' for r in scored)} inactive. Luck Sharpe {luck:.2f}")
    print(table(["#", "account", "alias", "value", "PnL", "return", "per year", "Sharpe", "luck test", "max DD",
                 "+periods", "turnover", "days"],
                [[str(i), short(r["address"]), (r["alias"] or "")[:22], f"${r['account_value']:,.0f}",
                  f"${r['pnl_usd']:,.0f}", pct(r["total_return"]),
                  pct(r["cagr"]) if r["span_days"] >= 365 else "(<1y)", num(r["sharpe"]), f"{r['dsr']:.0%}",
                  pct(-r["max_drawdown"]), f"{r['pct_positive']:.0%}", f"{r['annual_turnover']:,.0f}x",
                  f"{r['span_days']:.0f}"] for i, r in enumerate(traders[:args.show], 1)]))
    sig = sum(r["dsr"] >= 0.95 for r in traders)
    print(f"\npass the luck test (DSR >= 95%): {sig} of {len(traders)}")
    # Credible: real dollars made, never wiped out, enough monthly blocks to judge consistency.
    credible = [r for r in traders if r["pnl_usd"] >= 50_000 and r["max_drawdown"] < 0.95]
    beat = [r for r in credible if r.get("dsr_vs_eth", 0) >= 0.8 and r.get("dsr_vs_btc", 0) >= 0.8]
    print(f"beat BOTH ETH and BTC with >= 80% luck-test confidence (>= $50k PnL, never wiped out): {len(beat)}")
    best = sorted(credible, key=lambda r: min(r.get("dsr_vs_eth", 0), r.get("dsr_vs_btc", 0)), reverse=True)[:args.show]
    print("\nMARKET-BEATERS (ranked by the weaker of their luck tests vs ETH and vs BTC)")
    print(table(["account", "alias", "value", "PnL", "excess vs ETH", "vs BTC", "IR vs ETH", "luck vs ETH",
                 "luck vs BTC", "months > ETH", "max DD", "days"],
                [[short(r["address"]), (r["alias"] or "")[:18], f"${r['account_value']:,.0f}", f"${r['pnl_usd']:,.0f}",
                  pct(r.get("excess_total_vs_eth", 0)), pct(r.get("excess_total_vs_btc", 0)), num(r.get("ir_vs_eth", 0)),
                  f"{r.get('dsr_vs_eth', 0):.0%}", f"{r.get('dsr_vs_btc', 0):.0%}",
                  f"{r.get('pct_months_beat_eth', 0):.0%}", pct(-r["max_drawdown"]), f"{r['span_days']:.0f}"]
                 for r in best]))
    # Percent vs dollars: good while small, then lost money after scaling up.
    scaled = [r for r in traders if r["total_return"] > 0 and r["pnl_usd"] < 0]
    print(f"positive % return but negative $ PnL (won small, lost big after scaling up): {len(scaled)}")
    # Evidence clock: who is on pace to be proven, and how long until we'll know.
    pool = [r for r in rows if "dsr" in r and r.get("annual_turnover", 0) <= args.mm_turnover
            and r.get("annual_turnover", 0) >= 5 and r["pnl_usd"] > 0 and r["max_drawdown"] < 0.95]
    counts = {k: sum(r.get("evidence") == k for r in pool) for k in ("proven", "on track", "too early", "behind pace")}
    print("\nEVIDENCE CLOCK (beating ETH): " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    def clock_table(title: str, items: list[dict]) -> None:
        print(f"\n{title}")
        print(table(["account", "alias", "history", "days still needed", "luck vs ETH now", "IR vs ETH", "PnL",
                     "max DD"],
                    [[short(r["address"]), (r["alias"] or "")[:16], f"{r['effective_days']}d",
                      "-" if r.get("days_remaining") is None else f"{r['days_remaining']:.0f}d",
                      f"{r.get('dsr_vs_eth', r['dsr']):.0%}", num(r.get("ir_vs_eth", r["sharpe"])),
                      f"${r['pnl_usd']:,.0f}", pct(-r["max_drawdown"])] for r in items[:args.show]])
              if items else "  none")
    by_status = lambda k: sorted([r for r in pool if r.get("evidence") == k],  # noqa: E731
                                 key=lambda r: (r.get("days_remaining") or 0, -r.get("dsr_vs_eth", 0)))
    clock_table("PROVEN: beat ETH with >= 95% luck-test confidence", by_status("proven"))
    clock_table("ON TRACK: 90+ days of history, on pace to prove it (the next leaders, if they keep it up)",
                by_status("on track"))
    # Forward test: once a shortlist is chosen, new data only has to beat the
    # best of the *shortlist* by chance, not the best of everyone screened.
    from .metrics import days_to_proof as _dtp
    from .metrics import expected_max_sharpe as _ems
    shortlist = by_status("proven") + by_status("on track")
    if shortlist:
        star_fwd = _ems(1.0 / 365, len(shortlist))
        print(f"\nFORWARD CLOCK: shortlist of {len(shortlist)}; from here, each must beat the best of "
              f"{len(shortlist)} by chance (Sharpe {star_fwd * 365 ** 0.5:.2f}, vs {luck:.2f} for the full screen)")
        rows_f = []
        for r in shortlist:
            sr = r.get("ir_period_vs_eth", r["sharpe_period"])
            need = _dtp(sr, star_fwd, r.get("ir_skew_vs_eth", r["skew"]), r.get("ir_kurt_vs_eth", r["kurtosis"]))
            rows_f.append((need, r))
        rows_f.sort(key=lambda x: x[0] if x[0] is not None else 1e9)
        print(table(["account", "alias", "IR vs ETH", "forward days of new data to confirm", "max DD"],
                    [[short(r["address"]), (r["alias"] or "")[:16], num(r.get("ir_vs_eth", r["sharpe"])),
                      "-" if need is None else f"{need:.0f}d", pct(-r["max_drawdown"])]
                     for need, r in rows_f[:args.show * 2]]))
    clock_table("TOO EARLY: strong starts under 90 days - watch, don't follow (hot starts rarely last)",
                sorted(by_status("too early"), key=lambda r: -r.get("dsr_vs_eth", 0)))
    if args.kb:
        kb = KnowledgeBase(args.kb)
        kb.record_perps(rows, luck)
        kb.close()
        print(f"stored {len(scored)} accounts in {args.kb}", file=sys.stderr)
    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"luck_sharpe": luck, "traders": traders,
                       "market_makers": [r for r in scored if r["class"] != "trader"]}, fh, indent=1, default=str)


def cmd_group(args) -> None:
    """Build one proxy portfolio tracking a group of Hyperliquid leaders, and test its fidelity."""
    from .consensus import HyperliquidBooks, combine_books, fidelity, leader_weights, reconstruct
    from .providers.hyperliquid_accounts import HyperliquidAccounts, interp
    with open(args.perps) as fh:
        screen = json.load(fh)["traders"]
    by_addr = {r["address"]: r for r in screen}
    if args.addresses:
        leaders = [by_addr[a.lower()] for a in args.addresses if a.lower() in by_addr]
    else:
        leaders = [r for r in screen if r["pnl_usd"] >= 50_000 and r["max_drawdown"] < 0.95
                   and r.get("dsr_vs_eth", 0) >= args.min_conf and r.get("dsr_vs_btc", 0) >= args.min_conf
                   and r["annual_turnover"] <= args.max_turnover]
    if not leaders:
        print("no leaders match")
        return
    hb = HyperliquidBooks()
    books = {r["address"]: hb.book(r["address"]) for r in leaders}
    gone = [r for r in leaders if books[r["address"]].account_value < 10_000]
    if gone:
        print(f"skipping {len(gone)} leader(s) whose accounts are now closed or near-empty: "
              + ", ".join(short(r["address"]) for r in gone))
    leaders = [r for r in leaders if books[r["address"]].account_value >= 10_000]
    # Lessons from the group test: their return is their leverage, and levered
    # winners blow up. Follow only moderate leverage, still working, not falling.
    from .providers.hyperliquid_accounts import recent_stats
    hl0 = HyperliquidAccounts()
    now0 = int(time.time())
    kept, dropped = [], []
    for r in leaders:
        a = r["address"]
        gross = sum(abs(x) for x in books[a].weights.values())
        rec = recent_stats(hl0.history(a), args.recent_days, now0)
        r.update(rec, live_gross=gross)
        why = []
        if gross > args.max_leader_leverage:
            why.append(f"running {gross:.1f}x of total wealth > {args.max_leader_leverage:g}x")
        if rec["recent_return"] <= 0:
            why.append(f"{rec['recent_return']:+.0%} over the last {args.recent_days}d")
        if rec["off_peak"] > args.kill_switch:
            why.append(f"{rec['off_peak']:.0%} below recent peak (kill switch {args.kill_switch:.0%})")
        (dropped if why else kept).append((r, why))
    if dropped:
        print("dropped by leverage / recency / kill switch:")
        for r, why in dropped:
            print(f"  {short(r['address'])} {(r.get('alias') or ''):14} " + "; ".join(why))
    leaders = [r for r, _ in kept]
    if not leaders:
        print("\nno leader passes the leverage, recency and kill-switch gates right now: the basket is 100% cash")
        return
    books = {r["address"]: books[r["address"]] for r in leaders}
    alloc = leader_weights(leaders, args.max_leader)
    print(f"GROUP PROXY of {len(leaders)} Hyperliquid leaders (weights: luck-test confidence / drawdown, "
          f"capped {args.max_leader:.0%})")
    print(table(["leader", "alias", "weight", "wealth (perps + spot cash)", "gross vs wealth", "positions"],
                [[short(a), (by_addr[a].get("alias") or "")[:14], f"{alloc[a]:.0%}", f"${books[a].account_value:,.0f}",
                  f"{sum(abs(x) for x in books[a].weights.values()):.2f}x",
                  ", ".join(f"{c} {x:+.2f}x" for c, x in sorted(books[a].weights.items(), key=lambda kv: -abs(kv[1]))[:4])]
                 for a in alloc]))
    target = combine_books({a: b.weights for a, b in books.items()}, alloc, args.max_coin, args.max_gross)
    mids = hb.mids()
    print(f"\nTARGET for ${args.capital:,.0f} (net per coin, max {args.max_coin:.0%} per coin, gross <= {args.max_gross:.1f}x)")
    print(table(["coin", "side", "weight", "notional", "mid", "size"],
                [[c, "LONG" if w > 0 else "SHORT", f"{w:+.1%}", f"${abs(w) * args.capital:,.0f}",
                  f"{mids.get(c, 0):,.4g}", f"{abs(w) * args.capital / mids[c]:,.4g}" if mids.get(c) else "-"]
                 for c, w in sorted(target.items(), key=lambda kv: -abs(kv[1]))]))
    print(f"gross {sum(abs(x) for x in target.values()):.2f}x, net {sum(target.values()):+.2f}x")
    # Where each position comes from: the leaders behind every basket line.
    print("\nBASKET SOURCES (leader contribution to each net weight, before limits)")
    for c in sorted(target, key=lambda c: -abs(target[c])):
        parts = [f"{(by_addr[a].get('alias') or short(a))} {alloc[a] * books[a].weights[c]:+.2f}"
                 for a in alloc if c in books[a].weights]
        print(f"  {c:6} " + ", ".join(parts))

    if args.no_fidelity:
        return
    # Fidelity: rebuild books from fills and compare with the leaders' own returns,
    # daily and hourly - fast traders can only be followed by a fast copier.
    hl = HyperliquidAccounts()
    now = int(time.time())
    fills_by = {}
    for r in leaders:
        fills_by[r["address"]] = hb.fills(r["address"], (now - (args.days + 3) * DAY) * 1000)
    coins = {f["coin"] for fs in fills_by.values() for f in fs} | {c for b in books.values() for c in b.weights}
    hist = {r["address"]: hl.history(r["address"]) for r in leaders}
    for step, label, lags, horizon in ((DAY, "day", (0, 1, 2), args.days), (3600, "hour", (0, 1, 4, 12), min(args.days, 28))):
        end = now - now % step - step
        grid = [end - i * step for i in range(int(horizon * DAY / step))][::-1]
        start = grid[0] - 2 * step
        closes = {c: hb.closes(c, start - step, end + step, step) for c in coins}
        books_by_day, actual = {}, {}
        for r in leaders:
            a = r["address"]
            av, pn = dict(hist[a]["account_value"]), dict(hist[a]["pnl"])
            pts = [grid[0] - step] + grid
            av_d = {d: interp(av, d + step - 1) for d in pts}
            pn_d = {d: interp(pn, d + step - 1) for d in pts}
            actual[a] = [(pn_d[d] - pn_d[d - step]) / av_d[d - step] if av_d[d - step] > 100 else 0.0 for d in grid]
            books_by_day[a] = reconstruct(fills_by[a], av_d, closes, grid, step,
                                          {c: x["size"] for c, x in books[a].detail.items()})
        print(f"\nFIDELITY by the {label}, last {horizon} days: proxy rebuilt from fills, acting late, vs the leaders' own returns")
        rows = []
        for lag in lags:
            f = fidelity(books_by_day, actual, alloc, closes, grid, lag, max_coin=args.max_coin,
                         max_gross=args.max_gross, step=step)
            if f.get("days", 0) < 5:
                continue
            rows.append([f"{lag} {label}(s) late", pct(f["group_return"]), pct(f["proxy_return"]), num(f["correlation"]),
                         f"{f['capture']:.0%}", num(f["group_sharpe"]), num(f["proxy_sharpe"])])
        print(table(["delay", "group return", "proxy return", "corr", "kept", "group Sharpe", "proxy Sharpe"], rows)
              if rows else "  not enough overlapping data")
    print("  (our limits cut exposure well below the leaders' own leverage, so 'kept' below 100% partly reflects lower risk)")


def cmd_networth(args) -> None:
    """Aggregated value across venues and a leverage profile, per address (or summed as one entity)."""
    from .networth import networth
    provider = prices = None
    if not args.no_ethereum and os.environ.get("ETHERSCAN_API_KEY"):
        from .providers.defillama import DefiLlamaPrices
        from .providers.etherscan import Etherscan
        provider, prices = Etherscan(max_pages=args.max_pages), DefiLlamaPrices()
    cfg = Config.load(args.config)
    results = [networth(a, provider, prices, cfg, with_history=not args.no_history) for a in args.addresses]
    for r in results:
        lev, hist = r["leverage"], r["history"]
        print(f"\n{r['address']}   TOTAL VISIBLE VALUE ${r['total']:,.0f}")
        for k, v in r["components"].items():
            note = r["notes"].get(k, "")
            print(f"  {k:22} ${v:>14,.0f}   {note[:110]}")
        print(f"  {'not visible':22} {r['not_visible']}")
        print("  LEVERAGE (effective = position notional / equity; exchange max settings ignored)")
        print(f"    gross ${lev['gross_notional']:,.0f}, net ${lev['net_notional']:+,.0f}  |  "
              f"{lev['leverage_vs_perps_equity']:.2f}x of perps equity, {lev['leverage_vs_total_wealth']:.2f}x of "
              f"total visible wealth (net {lev['net_leverage_vs_total_wealth']:+.2f}x)")
        if lev["liq_distance_weighted"] is not None:
            print(f"    distance to liquidation (notional-weighted): {lev['liq_distance_weighted']:.0%}")
        else:
            print("    distance to liquidation: no liquidation price reported (well collateralised)")
        for p in lev["positions"][:6]:
            ld = f"{p['liq_distance']:.0%}" if p["liq_distance"] is not None else "-"
            print(f"      {p['coin']:6} {p['side']:5} ${p['notional']:>12,.0f}  liq dist {ld:>5}  "
                  f"unrealised ${p['unrealized']:+,.0f}  ({p['margin']}, max {p['max_leverage_setting']}x allowed)")
        if hist:
            rpl = hist["return_per_unit_leverage"]
            print(f"    last {hist['days']}d: avg leverage {hist['avg_leverage']:.2f}x, peak {hist['peak_leverage']:.2f}x, "
                  f"return {pct(hist['return'])}" + (f", return per unit of leverage {pct(rpl)}" if rpl is not None else ""))
    if args.entity and len(results) > 1:
        total = sum(r["total"] for r in results)
        gross = sum(r["leverage"]["gross_notional"] for r in results)
        net = sum(r["leverage"]["net_notional"] for r in results)
        print(f"\nENTITY TOTAL ({len(results)} addresses): ${total:,.0f} visible; gross ${gross:,.0f} "
              f"({gross / total if total else 0:.2f}x), net {net / total if total else 0:+.2f}x of total wealth")


def cmd_perps_backtest(args) -> None:
    """Re-run the Hyperliquid leader selection at past dates and score what the picks did next."""
    import random
    from .perps_backtest import run, summarise
    from .providers.defillama import DefiLlamaPrices
    from .providers.hyperliquid_accounts import HyperliquidAccounts
    hl = HyperliquidAccounts()
    lb = hl.leaderboard()
    pool = [a for a, r in lb.items() if r["allTime"]["vlm"] >= args.min_volume]
    random.Random(args.seed).shuffle(pool)
    sample = pool[:args.sample]
    print(f"sampling {len(sample)} of {len(pool)} accounts with >= ${args.min_volume:,.0f} lifetime volume "
          f"(random, includes accounts that later blew up)", file=sys.stderr)
    histories = {}
    for i, a in enumerate(sample, 1):
        print(f"\r  fetching {i}/{len(sample)}", end="", file=sys.stderr, flush=True)
        try:
            histories[a] = hl.history(a)
        except Exception:
            continue
    print(file=sys.stderr)
    now = int(time.time())
    bench = DefiLlamaPrices().daily_prices({"eth", "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599"}, now - 1100 * DAY, now)
    eth, btc = bench.get("eth", {}), bench.get("0x2260fac5e5542a773aa44fbcfedf7c193bc2c599", {})
    volume = {a: lb[a]["allTime"]["vlm"] for a in histories}
    cutoffs = [int(x) for x in args.cutoffs.split(",")]
    from .perps_backtest import AUDIT
    results = run(histories, eth, btc, volume, cutoffs, args.horizon, now, top_n=args.top_n,
                  strategies=AUDIT if args.audit else None)
    if args.audit:
        summ = summarise(results)
        base = summ.get("everyone screened (profitable, non-MM)", {})
        by_cut = {}
        for r in results:
            by_cut.setdefault(r["cutoff_days_ago"], {})[r["strategy"]] = r
        print("FORK AUDIT: each open decision replayed both ways on the same histories and dates "
              f"(next {args.horizon} days after each cutoff; see docs/DECISIONS.md)\n")
        rows = []
        for name, v in summ.items():
            wins = sum(1 for c in by_cut.values() if name in c and c[name]["with_data"]
                       and c[name]["median_return"] > c["everyone screened (profitable, non-MM)"]["median_return"])
            rows.append([name, f"{v['avg_picked']:.1f}", f"{v['cutoffs_with_picks']}/{v['cutoffs']}",
                         pct(v["avg_median_return"]), f"{v['avg_beat_eth']:.0%}", f"{v['avg_blew_up']:.0%}",
                         f"{wins}/{v['cutoffs_with_picks']}"])
        print(table(["variant", "picks/date", "dates w/ picks", "median fwd return", "beat ETH", "blew up",
                     "dates beating 'everyone'"], rows))
        print(f"\nreference: everyone profitable at the time - median {pct(base.get('avg_median_return', 0))}, "
              f"beat ETH {base.get('avg_beat_eth', 0):.0%}, blew up {base.get('avg_blew_up', 0):.0%}")
        if args.json:
            with open(args.json, "w") as fh:
                json.dump(results, fh, indent=1)
        return
    print(f"BACKTEST OF THE SELECTION PROCESS: leaders picked at each past date using only data up to then, "
          f"judged on the next {args.horizon} days (their own returns = a perfect, instant copy)\n")
    print(table(["days ago", "strategy", "picked", "equal-wt return", "median", "beat ETH", "blew up (>50% DD)", "ETH"],
                [[str(r["cutoff_days_ago"]), r["strategy"], str(r["picked"]), pct(r["equal_weight_return"]),
                  pct(r["median_return"]), f"{r['beat_eth']:.0%}", f"{r['blew_up']:.0%}", pct(r["eth_return"])]
                 for r in results]))
    print("\nAVERAGE ACROSS CUTOFFS")
    print(table(["strategy", "avg picked", "equal-wt return", "median", "beat ETH", "blew up", "ETH"],
                [[k, f"{v['avg_picked']:.1f}", pct(v["avg_equal_weight_return"]), pct(v["avg_median_return"]),
                  f"{v['avg_beat_eth']:.0%}", f"{v['avg_blew_up']:.0%}", pct(v["avg_eth_return"])]
                 for k, v in summarise(results).items()]))
    print("\nnotes: candidates sampled by lifetime volume from today's leaderboard (blown-up accounts stay in; "
          "accounts that vanished entirely are missing, flattering all strategies alike). Market-maker detection "
          "uses lifetime volume, a mild look-ahead.")
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(results, fh, indent=1)


def cmd_kb(args) -> None:
    kb = KnowledgeBase(args.kb)
    if args.action == "runs":
        rows = [[str(r[0]), datetime.fromtimestamp(r[1], timezone.utc).strftime("%Y-%m-%d %H:%M"), str(r[2]),
                 str(r[3]), str(r[4]), f"{r[5]:.2f}", r[6] or ""] for r in kb.runs()]
        print(table(["run", "time (UTC)", "wallets", "eligible", "significant", "luck Sharpe", "note"], rows))
    elif args.action == "top":
        rows = []
        for (rank, addr, score, sig, tier, rep, op, cagr, sharpe, rrs, copy, prev, name) in kb.top(args.limit):
            move = "new" if prev is None else (f"{prev - rank:+d}" if prev != rank else "=")
            rows.append([str(rank), move, name or short(addr), f"{score:.0f}", "yes" if sig else "",
                         f"{tier} {rep:.0f}", op, pct(cagr), num(sharpe), num(rrs), pct(copy)])
        print(table(["#", "move", "wallet", "score", "signif", "rep", "operator", "CAGR", "Sharpe", "RRS",
                     "copy CAGR"], rows))
    elif args.action == "wallet":
        rows = [[str(r[0]), datetime.fromtimestamp(r[1], timezone.utc).strftime("%Y-%m-%d"), r[2],
                 str(r[3] or "-"), f"{r[4]:.0f}", "yes" if r[5] else "", f"{r[6]} {r[7]:.0f}", pct(r[8]),
                 num(r[9]), f"${r[10]:,.0f}"] for r in kb.wallet(args.address)]
        print(table(["run", "date", "class", "rank", "score", "signif", "rep", "CAGR", "Sharpe", "equity"], rows)
              if rows else "wallet not in the knowledge base")
    elif args.action == "flows":
        f = kb.flows(args.cohort, args.limit)
        months = sorted(f)
        sectors = sorted({s for m in f.values() for s in m})
        print(table(["sector"] + months, [[sec] + [f"{f[m].get(sec, 0) / 1e6:+.2f}M" for m in months]
                                          for sec in sectors]) if f else "no flows stored")
    elif args.action == "emerging":
        rows = []
        for (a, alias, ev, rem, now_c, first_c, first_ts, span, pnl, dd, n) in kb.emerging(args.limit):
            trend = "" if n < 2 or first_c is None or now_c is None else f"{(now_c - first_c) * 100:+.0f} pts"
            rows.append([short(a), (alias or "")[:16], ev, "-" if rem is None else f"{rem:.0f}d",
                         f"{(now_c or 0):.0%}", trend, str(n), f"{span:.0f}d", f"${pnl:,.0f}", pct(-(dd or 0))])
        print(table(["account", "alias", "status", "days still needed", "luck vs ETH", "since first seen",
                     "snapshots", "history", "PnL", "max DD"], rows) if rows else "no perps screens stored yet")
    elif args.action == "movers":
        mv = kb.movers()
        for k in ("new", "dropped"):
            print(f"{k}: " + (", ".join(f"{short(a)} (#{r})" for a, r in mv[k]) or "none"))
        print("rank changes: " + (", ".join(f"{short(a)} #{b}→#{c}" for a, b, c in mv["moved"]) or "none"))
    kb.close()


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="wallet_tracker", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--demo", action="store_true", help="use the built-in synthetic market")
    common.add_argument("--seed", type=int, default=7)
    common.add_argument("--chain-id", type=int, default=1)
    common.add_argument("--config", help="JSON overrides for thresholds/weights")
    common.add_argument("--labels", help="JSON {address: label} of exchanges/entities to exclude")
    common.add_argument("--state", default=DEFAULT_STATE, help="watchlist file")
    common.add_argument("--route", default="", help="with --venue: route positions the venue can't hold to "
                        "'spot' (buy on a DEX if the pool is deep enough) and/or 'proxy' (most correlated "
                        "tradable instrument), e.g. --route spot,proxy")
    common.add_argument("--copy-capital", type=float, default=100_000, help="copy portfolio size (spot price impact)")
    common.add_argument("--min-liquidity", type=float, default=250_000, help="minimum DEX pool depth for spot")
    common.add_argument("--venue", choices=["hyperliquid"], help="simulate copies on this venue: only listed "
                        "instruments, real funding and fees (demo uses a stand-in venue)")
    common.add_argument("--since-days", type=int, default=540, help="history lookback for each wallet")
    common.add_argument("--max-pages", type=int, default=15,
                        help="max 1,000-record pages per tx type; beyond = machine-scale, classed as bot")
    common.add_argument("--history-cache", help="directory to cache fetched histories (re-runs cost no API calls)")
    common.add_argument("--identities", help="JSON {address: {name, kind, source, url}} of public attributions")
    common.add_argument("--ens", action="store_true", help="look up self-published ENS names")
    common.add_argument("--sectors", help="JSON {token_address: sector} to extend the built-in taxonomy")
    common.add_argument("--sectors-online", action="store_true",
                        help="tag unknown tokens from CoinGecko categories (slow: public rate limit)")
    common.add_argument("--farcaster", action="store_true", help="look up Farcaster verified addresses "
                                                                  "(needs NEYNAR_API_KEY)")
    sub = p.add_subparsers(dest="cmd", required=True)

    strat = argparse.ArgumentParser(add_help=False)
    strat.add_argument("--addresses", nargs="*", help="addresses, comma lists, or files of addresses")
    strat.add_argument("--min-dsr", type=float, default=0.8, help="luck-test confidence a leader needs")
    strat.add_argument("--min-copy-sharpe", type=float, default=1.0)
    strat.add_argument("--reaction-days", type=float, default=1.0,
                       help="how late you act on a leader's trade; leaders need an edge half-life >= 2x this")
    strat.add_argument("--require-identity", action="store_true", help="only entities with an attested identity")
    strat.add_argument("--max-leaders", type=int, default=8)
    strat.add_argument("--min-tradable", type=float, default=0.8,
                       help="share of a leader's risk book that must be tradable on the venue")
    strat.add_argument("--max-weight", type=float, default=0.25)
    strat.add_argument("--cash-buffer", type=float, default=0.10)

    r = sub.add_parser("rank", parents=[common, strat], help="screen, classify and rank wallets")
    r.add_argument("--discover", help="comma-separated token contracts to source candidate wallets from")
    r.add_argument("--discover-swappers", action="store_true",
                   help="source candidates from wallets repeatedly trading through major DEX routers")
    r.add_argument("--discover-days", type=int, default=90)
    r.add_argument("--discover-top", type=int, default=150)
    r.add_argument("--top", type=int, default=20)
    r.add_argument("--json", help="write full results to this file")
    r.add_argument("--html", help="write the visual report (copy-trade curves, regime and operator matrices)")
    r.add_argument("--follow-top", type=int, default=0, help="add the top N to the watchlist")
    r.add_argument("--kb", help="SQLite knowledge base to append this run to")
    r.set_defaults(fn=cmd_rank)

    a = sub.add_parser("analyze", parents=[common], help="full report for one wallet")
    a.add_argument("address")
    a.add_argument("--addresses", nargs="*", help="peer set, so the wallet gets a rank and luck-adjusted DSR")
    a.set_defaults(fn=cmd_analyze)

    f = sub.add_parser("follow", parents=[common], help="watchlist of wallets to follow")
    f.add_argument("action", choices=["add", "remove", "list", "poll", "report"])
    f.add_argument("wallets", nargs="*")
    f.add_argument("--note", default="")
    f.add_argument("--backfill-days", type=float, default=0, help="on add: also alert on the last N days")
    f.add_argument("--loop", action="store_true")
    f.add_argument("--interval", type=int, default=300)
    f.add_argument("--min-usd", type=float, default=0)
    f.add_argument("--swaps-only", action="store_true")
    f.add_argument("--follow-migrations", action="store_true",
                   help="auto-follow the destination of a large outflow to an unlabelled address")
    f.add_argument("--migration-usd", type=float, default=50_000)
    f.add_argument("--flow-alert-usd", type=float, default=250_000,
                   help="alert when an entity's net inflow/outflow in one poll reaches this")
    f.add_argument("--entity", default="", help="on add: group these wallets as one entity")
    f.add_argument("--alerts", default=os.path.expanduser("~/.wallet_tracker/alerts.jsonl"))
    f.set_defaults(fn=cmd_follow)

    b = sub.add_parser("backtest", parents=[common, strat], help="walk-forward test of the copy strategy")
    b.add_argument("--holdout-days", type=int, default=90)
    b.set_defaults(fn=cmd_backtest)

    pp = sub.add_parser("paper", parents=[common, strat], help="paper-trade the copy strategy forward")
    pp.add_argument("action", choices=["init", "update"])
    pp.add_argument("--capital", type=float, default=10_000)
    pp.add_argument("--max-token-weight", type=float, default=0.20, help="cap on any one token in target holdings")
    pp.add_argument("--paper", default=os.path.expanduser("~/.wallet_tracker/paper.json"))
    pp.set_defaults(fn=cmd_paper)

    pz = sub.add_parser("perps", help="screen Hyperliquid perps traders with the same luck test")
    pz.add_argument("--top", type=int, default=200, help="accounts to screen (most active by monthly volume)")
    pz.add_argument("--min-value", type=float, default=50_000)
    pz.add_argument("--min-days", type=int, default=90)
    pz.add_argument("--mm-turnover", type=float, default=5_000, help="annual turnover above which = MM/HFT")
    pz.add_argument("--show", type=int, default=25)
    pz.add_argument("--json")
    pz.add_argument("--kb", help="SQLite knowledge base to append this screen to")
    pz.set_defaults(fn=cmd_perps)

    g = sub.add_parser("group", help="one proxy portfolio tracking a group of Hyperliquid leaders")
    g.add_argument("--perps", required=True, help="JSON written by 'perps --json'")
    g.add_argument("--addresses", nargs="*", help="pick these leaders instead of the automatic selection")
    g.add_argument("--min-conf", type=float, default=0.8, help="min luck-test confidence vs ETH and vs BTC")
    g.add_argument("--max-turnover", type=float, default=1000, help="skip speed-based (MM-like) accounts")
    g.add_argument("--max-leader", type=float, default=0.35)
    g.add_argument("--max-coin", type=float, default=0.35)
    g.add_argument("--max-gross", type=float, default=1.5)
    g.add_argument("--capital", type=float, default=100_000)
    g.add_argument("--days", type=int, default=45)
    g.add_argument("--max-leader-leverage", type=float, default=3.0, help="skip leaders running more gross leverage")
    g.add_argument("--recent-days", type=int, default=60, help="leaders must be profitable over this many days")
    g.add_argument("--kill-switch", type=float, default=0.30, help="drop leaders this far below their recent peak")
    g.add_argument("--no-fidelity", action="store_true", help="skip the (slow) fidelity test")
    g.set_defaults(fn=cmd_group)

    nw = sub.add_parser("networth", help="aggregated value across venues + leverage profile of addresses")
    nw.add_argument("addresses", nargs="+")
    nw.add_argument("--entity", action="store_true", help="also sum the addresses as one entity")
    nw.add_argument("--no-ethereum", action="store_true", help="skip rebuilding Ethereum holdings (slow for busy wallets)")
    nw.add_argument("--no-history", action="store_true", help="skip average/peak leverage from fills")
    nw.add_argument("--max-pages", type=int, default=8)
    nw.add_argument("--config")
    nw.set_defaults(fn=cmd_networth)

    pb = sub.add_parser("perps-backtest", help="backtest the Hyperliquid leader-selection process")
    pb.add_argument("--sample", type=int, default=1500)
    pb.add_argument("--min-volume", type=float, default=2_000_000, help="lifetime volume floor for candidates")
    pb.add_argument("--cutoffs", default="240,180,120,90,60", help="days ago to rewind to")
    pb.add_argument("--horizon", type=int, default=60, help="days after each cutoff to judge the picks")
    pb.add_argument("--top-n", type=int, default=20)
    pb.add_argument("--seed", type=int, default=7)
    pb.add_argument("--json")
    pb.add_argument("--audit", action="store_true", help="replay the open decision forks (docs/DECISIONS.md)")
    pb.set_defaults(fn=cmd_perps_backtest)

    k = sub.add_parser("kb", help="query the knowledge base")
    k.add_argument("action", choices=["runs", "top", "wallet", "flows", "movers", "emerging"])
    k.add_argument("address", nargs="?")
    k.add_argument("--kb", default=os.path.expanduser("~/.wallet_tracker/kb.sqlite"))
    k.add_argument("--limit", type=int, default=25)
    k.add_argument("--cohort", choices=["smart", "all"], default="smart")
    k.set_defaults(fn=cmd_kb)

    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
