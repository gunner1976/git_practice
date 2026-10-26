# git_practice

## Wallet tracker — find, rank and follow the best actively-managed crypto wallets

`wallet_tracker/` screens on-chain trading wallets, throws out exchanges,
contracts and MEV bots, and ranks the actively managed rest on risk, return,
luck-adjusted significance, trade quality, long-term persistence and
behaviour across market regimes. Each wallet also gets a reputation score, a
human-vs-automated estimate, links to other wallets the same operator runs,
and a copy-trade simulation. Buy-and-hold wallets get their own leaderboard
so active management can always be judged against just holding.

Pure Python 3.10+ standard library, no dependencies.

```bash
python3 -m wallet_tracker rank --demo --html report.html   # synthetic market, runs offline
python3 -m unittest discover -s tests -t .                 # tests
```

`--html` writes a self-contained visual report: copy-trade curves for each
operator group, for the top wallets individually (actual vs copied) and for
each linked-wallet cluster; operator x regime and operator x quarter heatmaps;
the wallet x regime risk matrix; and the ranked table with reputation tiers.

### Real data

* Wallet histories: [Etherscan v2 API](https://etherscan.io/apis) (free key) —
  `export ETHERSCAN_API_KEY=...`. Ethereum mainnet by default; `--chain-id`
  10 / 8453 / 42161 for Optimism / Base / Arbitrum.
* Prices: DefiLlama's free coins API (no key), cached in `~/.cache/wallet_tracker`.

```bash
# Rank a list of candidate wallets (file = one address per line, # comments ok)
python3 -m wallet_tracker rank --addresses candidates.txt --json results.json

# ...or source candidates from the heaviest recent movers of some tokens
python3 -m wallet_tracker rank --discover 0x1f9840a85d5af5bf1d1762f925bdaddc4201f984,0x514910771af9ca656af840dff83e8264ecf986ca

# Add identity attestations: curated public labels, self-published ENS names, Farcaster verified addresses
python3 -m wallet_tracker rank --addresses candidates.txt --identities ids.json --ens --farcaster --html report.html

# Deep dive on one wallet (pass peers so it also gets a rank and a luck-adjusted DSR)
python3 -m wallet_tracker analyze 0xWALLET --addresses candidates.txt

# Follow the top 5 and get alerts on every new trade
python3 -m wallet_tracker rank --addresses candidates.txt --follow-top 5
python3 -m wallet_tracker follow add 0xWALLET --note "rotator" --backfill-days 7
python3 -m wallet_tracker follow poll --loop --interval 300 --min-usd 5000 --swaps-only
python3 -m wallet_tracker follow report      # live scorecard + drift flags for followed wallets
```

Alerts are printed and appended to `~/.wallet_tracker/alerts.jsonl` (one JSON
object per trade) so they can be piped into Slack, Telegram, etc.

**Where to get good candidates:** `--discover` is a blunt seed. Better seeds are
lists of addresses that traded on DEXs recently — e.g. a Dune query over
`dex.trades` grouped by `tx_from` with a minimum volume and trade count —
saved to a file and passed via `--addresses`. The pipeline does the filtering.

### How it works

```
transfers ──► events ──► daily portfolio replay ──► metrics ──► classify ──► gates ──► score/rank ──► follow
 (Etherscan)   swap/       TWR returns, passive      ~60 per     active /     history,   percentile     alerts,
               deposit/    twin, FIFO lots,           wallet      hold / bot /  equity,    composite +    copy-trade
               withdraw    weights                                CEX / ...     coverage   luck test      scorecard
```

1. **Reconstruction** (`reconstruct.py`). Transfers (native, internal, ERC-20)
   are netted per transaction. A tx where the wallet gave something and got
   something is a **swap** (a trading decision); one-sided txs are
   **deposits/withdrawals** (external flows); gas is a **cost**. WETH is
   treated as ETH so wraps don't look like trades.
2. **Portfolio replay** (`portfolio.py`). Holdings are valued daily, and
   returns are **time-weighted** — funding a wallet never counts as profit,
   and withdrawing never counts as loss. Tokens with no market price are valued
   at the price implied by the wallet's own swaps against priced assets. Every
   buy opens a FIFO lot, so sells produce realised trades with true cost basis.
3. **Passive twin.** Alongside the real wallet the engine runs a twin that
   freezes the wallet's *own* initial allocation (after its first week) and
   then just holds it, receiving the same deposits/withdrawals. *Active
   premium* and *information ratio* measure whether the trading actually beat
   holding their own picks — the buy-and-hold relative-performance question.
4. **Classification** (`classify.py`) — only `active_manager` wallets are ranked:

   | class | rule of thumb (tunable in `config.py`) |
   |---|---|
   | `contract` | address has bytecode (pools, vaults, smart accounts) |
   | `exchange_or_entity` | known CEX label, or hundreds of counterparties with few swaps |
   | `bot_or_mev` | median < 2 min between swaps, > 40 swaps per active day, same-block round trips, or median hold < 1 h |
   | `buy_hold` | < 12 swaps, < 1 swap/month, turnover < 0.75×/yr, or active in < 25% of months |
   | `dormant` | once active, but no swap in 45 days |
   | `insufficient_data` | < 90 days of history |
   | `active_manager` | everything else — human-paced, regularly re-allocating |

5. **Eligibility gates** — ≥ 120 days live, ≥ 10 closed trades, ≥ $10k average
   equity, ≥ 85% of swaps priced, no single trade > 60% of gross profit, active
   in ≥ 50% of months.
6. **Scoring** (`ranking.py`). Each metric below is percentile-ranked across
   eligible wallets (robust to outliers) and combined with weights from
   `config.py`:

   | family | metrics |
   |---|---|
   | risk-adjusted return | Sharpe, Sortino, Calmar, CAGR |
   | skill vs luck / passive | Probabilistic Sharpe, alpha vs ETH, information ratio & active premium vs own buy-and-hold |
   | risk | max drawdown, Ulcer index, downside capture vs ETH |
   | consistency | % positive months, worst month |
   | trade quality | profit factor, win rate, payoff ratio, top-trade concentration |
   | followability | Sharpe of a copy-trader who mirrors the wallet **one day late** paying 30 bps per trade |

7. **Luck correction.** Screen 5,000 wallets and some will look brilliant by
   chance. Each wallet's Sharpe is tested against the best Sharpe that many
   skill-less wallets would be expected to show (the **Deflated Sharpe
   Ratio**, Bailey & López de Prado), accounting for track-record length,
   skew and fat tails. Wallets with DSR ≥ 95% are marked `signif` and ranked
   above the rest; the header prints the "luck Sharpe" for the sample.

`analyze` also reports beta/correlation/up-down capture vs ETH, realised and
unrealised PnL, fees, median holding period, turnover, monthly returns and
the last-90-day record. `follow report` flags followed wallets that changed
class (went dormant or bot-like), have negative 90-day Sharpe, are deep in
drawdown, or whose edge a copy-trader can't capture.

### Market-regime risk matrix

Every day is labelled from ETH itself, using its trailing 30-day trend
(bull > +10%, bear < -10%, else range) × its 30-day volatility (above or
below median). Crash days (ETH's worst 5%) are tracked as a seventh column.
Each wallet's excess return over ETH is measured inside each regime, which
gives a wallet × regime matrix. That matrix rolls up into one number:

**Regime Robustness Score (RRS)** = mean over regimes of the wallet's
information ratio vs ETH − ½ × its standard deviation across regimes.

A wallet that only shines in bull markets scores low. One that adds a little
in every regime scores high. Up-, down- and crash-day betas, the worst-regime
excess and the share of regimes beaten are reported alongside. RRS,
worst-regime excess and crash-day excess are all in the ranking weights.

### Long-term performance and reputation

Persistence metrics: share of rolling 90-day windows beating ETH and beating
the wallet's own buy-and-hold, Sharpe of the first vs second half of the
record, days to recover from the max drawdown, and time spent >10% under water.

The **reputation score** (0–100, tiers A ≥ 75 / B ≥ 55 / C ≥ 35 / D) combines:

| component | what it measures |
|---|---|
| longevity | wallet age (3+ years = full marks) |
| track record | luck-adjusted significance (deflated Sharpe) |
| persistence | rolling-window hit rate vs ETH, both halves of the record profitable |
| robustness | Regime Robustness Score |
| provenance | first funded from a KYC'd exchange, a plain address, or a mixer |
| identity | self-published or publicly sourced attestation |

Red flags subtract points and are always listed: mixer funding or
interaction, contracts deployed by the wallet (possible issuer trading its
own token), and membership of a large linked cluster (an operator with many
wallets can show you only the winner). Use
`"eligibility": {"min_reputation": 55}` to rank only tiers A and B.

### Human vs automated, and linked wallets

**Behavioural operator score** (`operator_type.py`): people sleep (a
contiguous quiet block every day), cluster activity in waking hours, type
round numbers, act in bursts, and don't swap dozens of times a day. These
combine into a human-likeness score in [0, 1], shrunk toward 0.5 when there
are too few transactions. On-chain data can't tell an AI agent from a
conventional algorithm, so both count as *automated*. Declared AI agents (from
an agent registry or your identities file) are their own group.

Groups: `human (attested)`, `human (behavioural)`, `uncertain`,
`automated (behavioural)`, `AI agent (declared)`, `hft/mev bot`, plus a
`buy-and-hold` reference row. The report tracks them as matrices against
market regime and calendar quarter, with an equal-weight copy basket per
group.

**Identity** (`identity.py`) uses only what owners publish themselves (an ENS
reverse record, a Farcaster verified address via `NEYNAR_API_KEY`) or
public attributions you supply with a source (`--identities`, kinds `person`,
`fund`, `entity`, `ai_agent`). The tool does not try to unmask anonymous
wallets.

**Clusters** (`cluster.py`): wallets are linked when value moves directly
between them, when they share a first funder that isn't an exchange and
funded only a few of the screened wallets, or when they repeatedly buy the same
token within the same hour. Each cluster reports value-weighted combined
performance and an equal-weight copy basket.

### Capital map: entities, sectors and flows

Linked wallets roll up into **entities** (a cluster, or one unlinked
wallet). Each entity reports AUM, operator group, best reputation, and its
**sector mix**: time-weighted from daily portfolio weights, and the latest one.

Tokens are tagged into sectors (`sectors.py`): ETH & staking, Bitcoin, DeFi,
Infrastructure, AI, Memes, Gaming & NFT, **RWA & tokenized treasuries**
(BUIDL, USDY, OUSG, ONDO, … so TradFi capital arriving on-chain is its own
line), Stablecoins and Other. Tagging comes from a curated map, your own
`--sectors file.json`, and optionally CoinGecko categories (`--sectors-online`,
cached 30 days, slow on the public rate limit).

**Smart-money flows** are net USD bought minus sold per sector per month,
from swaps only (funding moves never count), summed over the "smart" cohort:
eligible wallets that pass the luck test or have reputation tier A/B. The same
flows for all traders are kept for comparison.

### Wallet migrations

Do good traders hide their record by moving to new wallets? `migration.py`
measures it. A migration is one withdrawal of at least half a wallet's value
to an unlabelled address, after which the wallet stops trading. If the
destination is a screened wallet that started around then, it is a
**verified successor**: the two are linked as one entity and their records
are stitched into one continuous track record. The universe migration rate is
reported, so the "most don't bother" assumption is checked against data.

Following: `follow poll --follow-migrations` flags any outflow ≥
`--migration-usd` (default $50k) to an unlabelled address as a possible
migration and adds the destination to the watchlist, so a followed trader
isn't lost when they switch wallets. Exchange deposit addresses are unique per
customer and unlabelled, so some flagged destinations will be exchanges.
Check before acting on them.

### Copy strategy, frequency and execution venue

* `backtest` runs a **walk-forward**: leaders are chosen using only data up to
  `--holdout-days` ago, then judged on what copying them earned afterwards,
  against copying every eligible wallet, naively copying the top past returns,
  and holding ETH. `paper init` / `paper update` run the strategy forward with
  imaginary capital and print blended target holdings.
* **Trading frequency**: each wallet gets a tier from its median holding
  period, and an **edge half-life**: how many days late a copier can act
  before keeping only half the trader's own Sharpe. Leaders need a half-life
  of at least twice `--reaction-days`.
* **Execution venue** (`--venue hyperliquid`): copies are simulated on what we
  can actually trade. Each token maps to a listed Hyperliquid perp (held long
  at 1x) only if the perp's price matches the token's (1,000x for `k`
  contracts), and only from the perp's listing date. Real funding is charged
  (last 90 days fetched, older days use that average), plus venue costs.
  Untradable exposure is held as cash. Leaders need at least 80%
  (`--min-tradable`) of their risk book tradable, and are judged on the venue
  copy. Funding on long perps has run about 10–13% a year, which weighs most
  on slow, long-holding leaders.

### Tuning

Pass `--config my.json` to override any threshold or weight, e.g.

```json
{
  "eligibility": {"min_avg_equity_usd": 50000, "min_closed_trades": 25},
  "classifier": {"dormant_after_days": 30},
  "weights": {"copy_sharpe": [3.0, true], "win_rate": [0, true]},
  "copy_lag_days": 2,
  "copy_cost_bps": 50
}
```

Extra exchange/entity addresses to exclude: `--labels labels.json` with
`{"0xaddr": "Some Exchange"}`.

### Limitations

* Daily valuation: intraday timing and exact execution prices are
  approximated by daily closes (realised trades use the actual amounts
  swapped, so slippage is captured there).
* Only on-chain spot activity in one address is seen — CEX trading, perps
  and multi-wallet operators are invisible. Lending/LP positions show up as
  transfers to contracts (withdrawals) unless the receipt token is priced.
* Price coverage for long-tail tokens depends on DefiLlama; the coverage gate
  stops poorly priced wallets from ranking.
* Etherscan's free tier allows 5 requests/s; screening thousands of wallets
  takes a while (3 calls + paging per wallet).
* Human/automated labels are behavioural estimates, not proof. A person
  running a script, or a bot built to imitate human hours, will be
  misread. Treat attested identity as the stronger signal.
* The luck test is deliberately conservative. On synthetic data it never
  passed a skill-less wallet, but it also confirmed only part of the
  genuinely skilled ones, especially with short records.
* Past performance, even luck-adjusted, is not a guarantee. This is a
  research tool, not financial advice.
