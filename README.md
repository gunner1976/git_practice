# git_practice

## Wallet tracker — find, rank and follow the best actively-managed crypto wallets

`wallet_tracker/` screens on-chain wallets, throws out everything that isn't a
person (or small team) actively managing money, ranks the rest on a broad set
of risk, return, skill-significance and trade-quality metrics, and lets you
follow the winners with trade alerts. Buy-and-hold wallets get their own
leaderboard so active management can always be judged against just holding.

Pure Python 3.10+ standard library, no dependencies.

```bash
python3 -m wallet_tracker rank --demo                  # synthetic market, runs offline
python3 -m unittest discover -s tests -t .             # tests
```

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

# Deep dive on one wallet (pass peers so it also gets a rank and a luck-adjusted DSR)
python3 -m wallet_tracker analyze 0xWALLET --addresses candidates.txt

# Follow the top 5 and get alerts on every new trade
python3 -m wallet_tracker rank --addresses candidates.txt --follow-top 5
python3 -m wallet_tracker follow add 0xWALLET --note "rotator" --since-days 7
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
* Past performance — even luck-adjusted — is not a guarantee. This is a
  research tool, not financial advice.
