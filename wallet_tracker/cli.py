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

from .analyze import analyze_wallet, fetch_series
from .config import Config
from .follow import DEFAULT_STATE, Watchlist, poll
from .models import DAY, WalletClass
from .ranking import build
from .report import leaderboard_text, num, pct, rolling, short, table, to_json, wallet_text


class Env:
    """Bundles the history provider, price source and clock."""

    def __init__(self, args):
        if args.demo:
            from .providers.synthetic import SyntheticWorld
            self.world = SyntheticWorld(seed=args.seed)
            self.provider = self.prices = self.world
            self.now = self.world.end + DAY - 1
        else:
            from .providers.defillama import DefiLlamaPrices
            from .providers.etherscan import Etherscan
            labels = {}
            if getattr(args, "labels", None):
                with open(args.labels) as fh:
                    labels = json.load(fh)
            self.world = None
            self.provider = Etherscan(chain_id=args.chain_id, labels=labels)
            chains = {1: "ethereum", 10: "optimism", 8453: "base", 42161: "arbitrum"}
            if args.chain_id not in chains:
                raise SystemExit(f"chain {args.chain_id} unsupported; ETH-native chains: {sorted(chains)}")
            self.prices = DefiLlamaPrices(chains[args.chain_id])
            self.now = int(time.time())


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
    if env.world is not None and not out:
        out = env.world.addresses()
    seen, uniq = set(), []
    for a in out:
        if a.lower() not in seen:
            seen.add(a.lower())
            uniq.append(a.lower())
    return uniq


def _analyze_many(addresses: list[str], env: Env, cfg: Config):
    histories = []
    for i, a in enumerate(addresses, 1):
        print(f"\r  fetching {i}/{len(addresses)} {a}", end="", file=sys.stderr, flush=True)
        try:
            histories.append(env.provider.history(a))
        except Exception as exc:  # one bad address shouldn't sink a whole screen
            print(f"\n  skip {a}: {exc}", file=sys.stderr)
    print("\n  pricing…", file=sys.stderr)
    series = fetch_series(env.prices, histories, env.now)
    return [analyze_wallet(h, series, cfg, env.now) for h in histories]


def cmd_rank(args) -> None:
    cfg = Config.load(args.config)
    env = Env(args)
    reports = _analyze_many(_addresses(args, env), env, cfg)
    lb = build(reports, cfg)
    print(leaderboard_text(lb, args.top))
    if args.json:
        with open(args.json, "w") as fh:
            fh.write(to_json(lb))
        print(f"\nwrote {args.json}", file=sys.stderr)
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
    reports = _analyze_many(list(dict.fromkeys([target] + addrs)), env, cfg)
    build(reports, cfg)  # fills eligibility, DSR and (with peers) rank
    print(wallet_text(next(r for r in reports if r.address == target)))


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
        start = head - int(args.since_days * DAY / 12)  # ~12s blocks
        for a in args.wallets:
            wl.add(a, start, args.note)
        wl.save()
        print(f"following {len(args.wallets)} wallet(s); state in {wl.path}")
    elif args.action == "poll":
        while True:
            for al in poll(wl, env.provider, env.prices, args.alerts, args.min_usd, args.swaps_only):
                when = datetime.fromtimestamp(al["time"], timezone.utc).strftime("%Y-%m-%d %H:%M")
                tag = f" [{al['note']}]" if al["note"] else ""
                print(f"{when}  {short(al['wallet'])}{tag}  {al['text']}")
            if not args.loop:
                break
            time.sleep(args.interval)
    elif args.action == "report":
        cfg = Config.load(args.config)
        reports = _analyze_many(list(wl.wallets), env, cfg)
        build(reports, cfg)
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
            rows.append([short(r.address), wl.wallets[r.address].get("note", ""), pct(m["cagr"]),
                         num(m["sharpe"]), pct(rec["return"]), num(rec["sharpe"]), pct(-rec["current_drawdown"]),
                         pct(m.get("copy_cagr", float("nan"))), ", ".join(flags) or "ok"])
        print(table(["wallet", "note", "CAGR", "Sharpe", "90d ret", "90d Sharpe", "cur DD", "copy CAGR",
                     "flags"], rows))


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
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("rank", parents=[common], help="screen, classify and rank wallets")
    r.add_argument("--addresses", nargs="*", help="addresses, comma lists, or files of addresses")
    r.add_argument("--discover", help="comma-separated token contracts to source candidate wallets from")
    r.add_argument("--discover-top", type=int, default=150)
    r.add_argument("--top", type=int, default=20)
    r.add_argument("--json", help="write full results to this file")
    r.add_argument("--follow-top", type=int, default=0, help="add the top N to the watchlist")
    r.set_defaults(fn=cmd_rank)

    a = sub.add_parser("analyze", parents=[common], help="full report for one wallet")
    a.add_argument("address")
    a.add_argument("--addresses", nargs="*", help="peer set, so the wallet gets a rank and luck-adjusted DSR")
    a.set_defaults(fn=cmd_analyze)

    f = sub.add_parser("follow", parents=[common], help="watchlist of wallets to follow")
    f.add_argument("action", choices=["add", "remove", "list", "poll", "report"])
    f.add_argument("wallets", nargs="*")
    f.add_argument("--note", default="")
    f.add_argument("--since-days", type=float, default=0, help="on add: also alert on the last N days")
    f.add_argument("--loop", action="store_true")
    f.add_argument("--interval", type=int, default=300)
    f.add_argument("--min-usd", type=float, default=0)
    f.add_argument("--swaps-only", action="store_true")
    f.add_argument("--alerts", default=os.path.expanduser("~/.wallet_tracker/alerts.jsonl"))
    f.set_defaults(fn=cmd_follow)

    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
