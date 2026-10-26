"""Decide what kind of wallet an address is.

Only `ACTIVE` wallets - discretionary, human-paced, actively managed - are
ranked as candidates to follow. Contracts, exchanges/custodians and bots are
excluded because their flows are not someone's trading decisions (or cannot
be replicated by a follower). Buy-and-hold wallets get their own leaderboard
so active management can be judged against simply holding.
"""

from __future__ import annotations

from .config import ClassifierConfig
from .models import WalletClass, WalletHistory
from .reconstruct import GAS


def classify(hist: WalletHistory, m: dict[str, float], cfg: ClassifierConfig) -> tuple[WalletClass, list[str]]:
    reasons: list[str] = []
    if hist.is_contract:
        return WalletClass.CONTRACT, ["address has bytecode"]
    if hist.label:
        return WalletClass.EXCHANGE, [f"known entity: {hist.label}"]

    counterparties = {t.counterparty for t in hist.transfers if t.counterparty and t.counterparty != GAS}
    if len(counterparties) >= cfg.entity_counterparties and m["swaps"] < 0.1 * len(hist.transfers):
        return WalletClass.EXCHANGE, [f"{len(counterparties)} counterparties, mostly plain transfers"]

    if m["history_days"] < cfg.min_history_days:
        return WalletClass.INSUFFICIENT, [f"only {m['history_days']} days of history"]

    # Bot signatures need a sample: a holder's 3-swap initial allocation
    # executed in one minute is not a bot.
    busy = m["swaps"] >= cfg.min_swaps
    if busy and m["median_secs_between_swaps"] < cfg.bot_median_secs_between_swaps:
        reasons.append(f"median {m['median_secs_between_swaps']:.0f}s between swaps")
    if m["swaps_per_active_day"] > cfg.bot_swaps_per_active_day:
        reasons.append(f"{m['swaps_per_active_day']:.0f} swaps per active day")
    if busy and m["same_block_swap_ratio"] > cfg.bot_same_block_ratio:
        reasons.append(f"{m['same_block_swap_ratio']:.0%} of swaps share a block")
    if m["closed_trades"] >= 20 and m["median_hold_days"] < cfg.bot_median_hold_days:
        reasons.append(f"median hold {m['median_hold_days'] * 24:.1f}h")
    if reasons:
        return WalletClass.BOT, reasons

    if (m["swaps"] < cfg.min_swaps
            or m["swaps_per_month"] < cfg.hold_max_swaps_per_month
            or m["annual_turnover"] < cfg.hold_max_annual_turnover
            or m["active_month_ratio"] < cfg.hold_min_active_month_ratio):
        return WalletClass.BUY_HOLD, [
            f"{m['swaps_per_month']:.1f} swaps/month, turnover {m['annual_turnover']:.2f}x/yr, "
            f"active in {m['active_month_ratio']:.0%} of months"]

    # Holding is the strategy for buy-and-hold wallets, so only once-active
    # wallets can go dormant.
    if m["days_since_last_swap"] > cfg.dormant_after_days:
        return WalletClass.DORMANT, [f"no swap for {m['days_since_last_swap']:.0f} days"]

    return WalletClass.ACTIVE, [
        f"{m['swaps_per_month']:.1f} swaps/month, turnover {m['annual_turnover']:.1f}x/yr, "
        f"active in {m['active_month_ratio']:.0%} of months"]
