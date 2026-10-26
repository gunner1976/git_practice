# Decision log

Every fork in the strategy, why it went the way it did, and how to re-test it.
When new information arrives, re-run the listed test; if the other branch
now wins, record the reversal here rather than silently changing the code.

Status: **active** (current choice), **revised** (changed after evidence), **open** (not yet tested both ways).

| # | Decision | Chosen | Alternatives | Evidence at the time | Re-test | Status |
|---|---|---|---|---|---|---|
| D1 | What counts as performance | Time-weighted returns; deposits/withdrawals excluded | Raw balance change; money-weighted | Funding a wallet must not look like profit | `tests` PortfolioTest | active |
| D2 | Benchmark for "skill" | Own buy-and-hold twin + ETH + BTC (min across numeraires) | USD only | USD-only rewards riding a bull market (D-numeraire test) | `rank` → `min_numeraire_sharpe` | active |
| D3 | Luck bar | Expected max Sharpe of N skill-less traders, variance 1/T | Cross-sectional variance of Sharpes; MAD | Cross-sectional variance treated real skill as noise and raised the bar for everyone (synthetic: 2.98 → 1.75) | `rank --demo`; `perps` luck Sharpe | **revised** |
| D4 | Forward-test luck bar | Best of the *shortlist* by chance | Best of the full screen | Selection already paid the multiple-testing penalty | `perps` forward clock | active |
| D5 | Wallet size tier | Peak capital put in | Average/final balance | Balance-based tiers counted skilled minnows as whales | `rank` whales vs minnows | **revised** |
| D6 | Eligibility needs dollar profit | Yes | % return only | Real data: +485% TWR wallets that lost $67k (won small, lost big / flow noise) | `rank` funnel stage 3 | active |
| D7 | Min average equity to rank | $2,500 | $10,000 | Let small skilled wallets compete | `--config` eligibility | open |
| D8 | Illiquid-market cap | ≤ 50% of volume in no-market tokens | No cap | Manipulation-prone, uncopyable | funnel stage 4 | open |
| D9 | Token valuation without a market price | Own implied price, only up to quantity bought; flows at market price only | Implied price on all balances | Airdropped spam valued at $13T / flows at $124T | tests: spam, WETH | **revised** |
| D10 | History lookback | 540 days + opening-balance seeding | Full history | Cost; seeding fixes pre-window holdings | compare `--since-days` | open |
| D11 | Candidate discovery (Ethereum) | Repeat DEX-router senders | Token movers; large-wallet seeds | Pool turned out micro-cap / retail heavy (0 survive funnel) | `rank --discover-swappers` vs other seeds | **open – likely revise** |
| D12 | Primary hunting ground | Hyperliquid accounts (+ vaults) | Ethereum spot wallets | Replicable on venue; 0 of 400 Ethereum wallets survive the delay gate | funnel comparison | active |
| D13 | Execution venue | Hyperliquid perps, then DEX spot, then correlated proxy, else cash | Perps only | Median tradable share 13% → 38% with routing | `rank --route spot,proxy` | active |
| D14 | Leverage measured against | Total visible wealth (perps + spot stables) | Perps account only | Leaders hold more idle USDC than perps equity (Loco 0.79x → 0.18x) | `networth`; `group` | **revised** |
| D15 | Leader leverage ceiling | 3x of total wealth (live), **no volatility cap at selection** | Vol cap 60/100/150% | Audit: vol caps cut median return (to -16%) and beat-ETH rate without reducing blow-ups (25-33%) | `perps-backtest --audit` | **revised** (vol cap rejected; live leverage ceiling kept, untested historically) |
| D16 | Recency gate | Profitable over last 60 days (30 days a candidate) | None; 30/90 days | Audit: none +9% median vs +42% with it; 30d +48% (5/6 dates), 90d +12% | `perps-backtest --audit` | active - evidence supports; 30d vs 60d within noise |
| D17 | Kill switch | Live risk control only, not a selection filter | 20/30/50% at selection | Audit: none/20/30/50% all +42-49% median; recency already catches falling traders | `perps-backtest --audit` | **revised** |
| D18 | Minimum history / evidence status | Proven or on track (90d+); "too early" excluded | Admit too-early starts | Audit: admitting too-early → +8% median, 36% blow-ups (vs +42%, 30%) | `perps-backtest --audit` | active - evidence supports |
| D19 | Leader weighting | Confidence / drawdown, capped 35% | Equal; inverse vol | — | portfolio backtest (planned) | open |
| D20 | Group limits | 35% per coin, 1.5x gross | Uncapped | Caps removed most of the group's return (kept ~0% vs 35–50% uncapped) | `group --max-coin --max-gross` | **open – trade-off** |
| D21 | Copy reaction time | 1 day | Minutes (automated) | Daily fidelity 0.6–0.8 per leader; hourly not yet measurable | `group` fidelity | open |
| D22 | Leaderboards | Candidate pools only, never rankings | Copy leaderboard tops | Backtest: top-by-PnL / top-by-return worst on median and blow-ups | `perps-backtest` | active |
| D24 | Where blow-up risk is controlled | Portfolio level: diversification + volatility-targeted sizing + live stops | Selection filters | Audit: ~30% blow-ups in every selection variant | portfolio backtest (planned) | open |
| D23 | Vaults | Screen vaults through the same gates; deposit = exact replication | Copy their trades | Vault deposit has zero delay and no basket mismatch | vault screen (planned) | open |

## How to revisit a decision

1. Find its re-test command above and run it on current data.
2. For open forks with an audit flag, `perps-backtest --audit` replays both branches on the same histories.
3. If the other branch wins consistently (several cutoffs, not one), change the default,
   mark the row **revised**, and add a line below.

## Revisions

- Fork audit 1 (3,000 sampled Hyperliquid accounts, 6 cutoffs 60-300 days back, 60-day horizon):
  recency gate and minimum history confirmed; kill switch neutral at selection (kept as live control);
  volatility cap rejected. Every variant still saw ~30% of picks suffer a >50% drawdown within 60 days,
  so blow-up risk must be handled by sizing and diversification, not selection.

- D3 — luck bar switched from cross-sectional variance to 1/T after synthetic worlds showed it penalised real skill.
- D5 — size tiers switched from balance to capital put in; balance let skill masquerade as size.
- D9 — valuation of unpriced tokens restricted after the first real screen produced trillion-dollar wallets.
- D14 — leverage measured against total wealth after `networth` showed leaders keep most cash in Hyperliquid spot.
