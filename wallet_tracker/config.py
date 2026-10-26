"""Tunable thresholds and scoring weights. Override any of these with a JSON
file passed via `--config` (keys mirror the dataclass fields)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field


@dataclass
class ClassifierConfig:
    min_history_days: int = 90
    min_swaps: int = 12
    dormant_after_days: int = 45
    # Bot / MEV signatures
    bot_median_secs_between_swaps: float = 120.0
    bot_swaps_per_active_day: float = 40.0
    bot_same_block_ratio: float = 0.2
    bot_median_hold_days: float = 0.04       # ~1 hour
    # Exchange / custodial entity signatures
    entity_counterparties: int = 400
    # Buy-and-hold signatures
    hold_max_swaps_per_month: float = 1.0
    hold_max_annual_turnover: float = 0.75
    hold_min_active_month_ratio: float = 0.25


@dataclass
class EligibilityConfig:
    min_history_days: int = 120
    min_closed_trades: int = 10
    min_avg_equity_usd: float = 2_500.0       # low, so small but skilled wallets can rank
    min_price_coverage: float = 0.85
    max_top_trade_profit_share: float = 0.6   # one lucky trade shouldn't carry the record
    min_active_month_ratio: float = 0.5
    min_reputation: float = 0.0               # 0 = off; e.g. 55 keeps tiers A/B only
    require_dollar_profit: bool = True        # % return without $ profit = won small, lost big (or flow noise)


# metric -> (weight, higher_is_better). Each metric is percentile-ranked
# across eligible wallets, then combined. Weights need not sum to 1.
DEFAULT_WEIGHTS: dict[str, tuple[float, bool]] = {
    # risk-adjusted return
    "sharpe": (1.5, True),
    "sortino": (1.0, True),
    "calmar": (1.0, True),
    "cagr": (1.0, True),
    # skill vs luck / vs passive
    "psr": (1.5, True),
    "alpha_vs_eth": (1.0, True),
    "information_ratio": (1.5, True),   # vs. its own buy-and-hold twin
    "active_premium": (1.0, True),
    # risk
    "max_drawdown": (1.0, False),
    "ulcer_index": (0.5, False),
    "downside_capture": (0.5, False),
    # consistency
    "pct_positive_months": (1.0, True),
    "worst_month": (0.5, True),
    # trade quality
    "profit_factor": (1.0, True),
    "win_rate": (0.5, True),
    "payoff_ratio": (0.5, True),
    "top_trade_profit_share": (0.5, False),
    # durability across time and market regimes
    "regime_robustness": (1.5, True),
    "worst_regime_excess": (0.5, True),
    "pct_windows_beat_eth": (1.0, True),
    "min_half_sharpe": (1.0, True),
    "stress_excess": (0.5, True),
    # can a follower actually capture it?
    "copy_sharpe": (1.0, True),
}


@dataclass
class Config:
    classifier: ClassifierConfig = field(default_factory=ClassifierConfig)
    eligibility: EligibilityConfig = field(default_factory=EligibilityConfig)
    weights: dict[str, tuple[float, bool]] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))
    copy_lag_days: int = 1
    copy_cost_bps: float = 30.0
    significance_level: float = 0.95

    @classmethod
    def load(cls, path: str | None) -> "Config":
        cfg = cls()
        if not path:
            return cfg
        with open(path) as fh:
            raw = json.load(fh)
        for k, v in raw.get("classifier", {}).items():
            setattr(cfg.classifier, k, v)
        for k, v in raw.get("eligibility", {}).items():
            setattr(cfg.eligibility, k, v)
        for k, v in raw.get("weights", {}).items():
            cfg.weights[k] = tuple(v)  # type: ignore[assignment]
        for k in ("copy_lag_days", "copy_cost_bps", "significance_level"):
            if k in raw:
                setattr(cfg, k, raw[k])
        return cfg

    def to_dict(self) -> dict:
        return asdict(self)
