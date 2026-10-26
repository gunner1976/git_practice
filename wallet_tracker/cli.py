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
from .prices import STABLES, PriceBook
from .sectors import SectorMap
from .strategy import Leader, Rules, portfolio_returns, select, walk_forward
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
    return run_study(histories, series, cfg, env.now, ids, env.labels, smap, _venue(args, env))


def cmd_rank(args) -> None:
    cfg = Config.load(args.config)
    env = Env(args)
    study = _study(_addresses(args, env), env, cfg, args)
    lb = study.boards
    print(study_text(study, args.top))
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
            wl.add(r.address, head, note=f"rank {r.rank} score {r.score:.0f}")
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
            wl.add(a, start, args.note)
        wl.save()
        print(f"following {len(args.wallets)} wallet(s); state in {wl.path}")
    elif args.action == "poll":
        while True:
            for al in poll(wl, env.provider, env.prices, args.alerts, args.min_usd, args.swaps_only,
                           args.follow_migrations, args.migration_usd):
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
                       _venue(args, env))
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


def cmd_paper(args) -> None:
    cfg = Config.load(args.config)
    env = Env(args)
    if args.action == "init":
        histories, series, ids, smap = _inputs(args, env, cfg)
        study = run_study(histories, series, cfg, env.now, ids, env.labels, smap, _venue(args, env))
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
    rows = []
    for i, a in enumerate(addrs, 1):
        print(f"\r  fetching {i}/{len(addrs)}", end="", file=sys.stderr, flush=True)
        try:
            m = perp_metrics(hl.history(a))
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
    print(table(["#", "account", "alias", "value", "PnL", "CAGR", "Sharpe", "luck test", "max DD", "+periods",
                 "turnover", "days"],
                [[str(i), short(r["address"]), (r["alias"] or "")[:22], f"${r['account_value']:,.0f}",
                  f"${r['pnl_usd']:,.0f}", pct(r["cagr"]), num(r["sharpe"]), f"{r['dsr']:.0%}",
                  pct(-r["max_drawdown"]), f"{r['pct_positive']:.0%}", f"{r['annual_turnover']:,.0f}x",
                  f"{r['span_days']:.0f}"] for i, r in enumerate(traders[:args.show], 1)]))
    sig = sum(r["dsr"] >= 0.95 for r in traders)
    print(f"\npass the luck test (DSR >= 95%): {sig} of {len(traders)}")
    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"luck_sharpe": luck, "traders": traders,
                       "market_makers": [r for r in scored if r["class"] != "trader"]}, fh, indent=1, default=str)


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

    r = sub.add_parser("rank", parents=[common], help="screen, classify and rank wallets")
    r.add_argument("--addresses", nargs="*", help="addresses, comma lists, or files of addresses")
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
    f.add_argument("--alerts", default=os.path.expanduser("~/.wallet_tracker/alerts.jsonl"))
    f.set_defaults(fn=cmd_follow)

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
    pz.set_defaults(fn=cmd_perps)

    k = sub.add_parser("kb", help="query the knowledge base")
    k.add_argument("action", choices=["runs", "top", "wallet", "flows", "movers"])
    k.add_argument("address", nargs="?")
    k.add_argument("--kb", default=os.path.expanduser("~/.wallet_tracker/kb.sqlite"))
    k.add_argument("--limit", type=int, default=25)
    k.add_argument("--cohort", choices=["smart", "all"], default="smart")
    k.set_defaults(fn=cmd_kb)

    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
