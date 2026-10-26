# Field opex 2018–2025: data, the leanest level, and why it fell

Files:
- `opex_monthly.csv`: Jul-2018 to Dec-2025.
- `opex_annual.csv`: 2018–2025, totals and grouped categories.
- `opex_annual_lines.csv`: line items as named in each lease operating statement (LOS).
- `opex_breakdown.json`: the leanest cost structure and the model assumptions.

All amounts are USD as booked. The only conversion is the Sep-2020 cost sheet, at the 21 MXN/USD stated in that sheet. Field opex excludes G&A, regulatory costs and area charges.

## What is monthly and what is annual

| Period | Opex granularity | Source |
|---|---|---|
| Sep-2018 to Dec-2019 | **Monthly actuals** (`opex_usd`), cash basis | `accounting_notes.md` Appendix A (Monthly Summary, "Operating Costs"). Also used by `src/overview_figures.py` figure 23. Sums: 2018 288,134; 2019 839,052. |
| Jul–Aug 2018 | 0 ("-" in Monthly Summary) | Test period; costs sat in capital |
| 2020, 2021, 2022 | **Annual only**, with category split | LOS 2020 (1MUDIBfZ), final 2021 and 2022 (1l_gSKHt), via `acc_review.csv` / `acc_findings.md` |
| Jul–Nov 2020 | A range only: 24.3–25.4 k/month | `acc_findings.md` finding 2; no monthly figures in the repo |
| 2023 | Annual total 627,273, no split | LOS 2023 (1Co9-h-R) |
| 2024, 2025 | Annual totals 289 k and 248 k | Tonalli P&L, via `res_findings.md` item 5 |

For years with no monthly actuals, `opex_period_avg_usd_per_month` gives the annual total divided by 12 (2018 LOS: 4 months). It is labelled in every row as **not a monthly actual**. Use it only as a step line.

Two 2018 figures exist on different bases: 288,134 (cash) and 291,365 (LOS, accrual). 2019 is 839,052 on cash and in the LOS, and 884,463 on the trial balance.

## Volumes in `opex_monthly.csv`

Each volume column has its own source column.

- **`oil_bbl`**:
  - Default: `pemex_statement_sales` (Sep-2018 to Nov-2020, the invoiced basis).
  - Where there is no statement: `tonalli_trucking_sales` (Mar-2020 and Dec-2020 to Nov-2022).
  - Dec-2022: the LOS figure (733 bbl). The ticket row books 0 oil for a 740 bbl shipment.
  - Apr–Jun 2020 and Jul–Oct 2022: the CNH filing (production, not sales).
  - Mar–Jun 2022: LOS sales of 0.
  - Also given for comparison: `oil_trucking_tickets_bbl`, `oil_tec10_wellhead_daily_bbl` (`tonalli_daily_sum`) and `sales_bbl_accounting` (Monthly Summary for 2018–19; LOS for 2022).
- **`water_bbl`** (produced water):
  - 2018-09 to 2019-11: TEC-10 wellhead water from `tonalli_daily_sum`, plus TEC-2 trucking water.
  - 2020–21 and Jul–Nov 2022: `cnh_production_filings_2020_2022.csv`.
  - Blank for Dec-2019, Jan–Jun 2022 and Dec-2022.
- **`water_trucked_bbl`**: water hauled by truck. This was the cost driver. It runs at 1.2–13.6 kbbl/month up to Aug-2019. The peak, 10.0–13.6 kbbl in Jun–Jul 2019, includes the TEC-2, TEC-7 and TEC-11 hauls. It falls to under 10 bbl/month once TEC-7 took the water from Sep-2019.

## The lowest sustained opex, and what it consisted of

**While producing:**
- Jul–Nov 2020 ran at **USD 24.3–25.4 k/month**.
- 2021 averaged **29.1 k/month** (349,282 for the year), for 48 bbl/d of oil.
- These are about one third of the 2019 level of 54–83 k/month, average 69.9 k.

**The Sep-2020 cost sheet** (`Tonalli Op Cost 290920.xlsx`) is USD 28,155/month at 21 MXN/USD:

| Item | Per month |
|---|---|
| Crew / field supervision | MXN 280,000 (≈ USD 13.3 k) |
| Vacuum truck (Kefren) | MXN 108,000 (5.1 k) |
| Diesel | MXN 60,000 (2.9 k) |
| Consumables | MXN 40,000 (1.9 k) |
| Frac tank (Oro Negro) | MXN 32,000 (1.5 k) |
| Water analysis | MXN 21,000 (1.0 k) |
| Intertek crude analysis | USD 1,468 |
| Demulsifier | USD 925 |

**2021 by category** (full year, LOS):

| Category | USD | Share |
|---|---|---|
| Field supervision | 159,745 | 46 % |
| Trucking | 102,720 | 29 % |
| Injection pump and stimulations | 29,154 | |
| Sampling | 25,624 | |
| Tanks | 24,639 | |
| Demulsifier | 7,400 | |

There was no separator rental, no water trucking and no disposal fee.

**Not producing:**

| Period | Opex | Note |
|---|---|---|
| Mar–Oct 2022 shut-in | about 5–8 k/month | Supervision 3.3 k, tanks 2 k, fees 1.3 k |
| 2023 | 52 k/month | Care and maintenance, no split (G-70) |
| 2024–25 | 21–24 k/month | Holding cost |

## Why opex fell (stated reasons, with sources)

1. **Separator rental ended.**
   - It cost 186,456 in 2019 (MXN 216,000/month) and 89,334 in Sep–Dec 2018. The last invoice was Mar-2020.
   - It was replaced by an owned separator bought in Dec-2019 (tax pool: 22,407).
   - Sources: `acc_findings.md` finding 2; `accounting_notes.md` §4; briefing A9.
2. **Water handling moved into the field.**
   - TEC-7 was converted to a disposal/injection well in Aug-2019. Water trucking (83,944 in 2019) and the third-party disposal fee (1.33 USD/bbl, 32,534, Feb–Aug 2019) stopped.
   - The rented injection pump (75,680 Aug–Dec 2019; 46,778 Jan–Mar 2020) was replaced by a refurbished owned pump (30,647).
   - The operations log calls the TEC-7 conversion "opex reduction".
3. **Fewer wells and one battery.**
   - TEC-2 was shut in as uneconomic in Sep-2019, with an 8 k demobilisation. Its 2019 LOS shows opex of 164,675 against a net operating income (NOI) of only 6,982.
   - The TEC-10 to TEC-2 flowline (Nov–Dec 2019; 29,243) consolidated tankage and testing at one battery.
   - A 60 m³ tank was bought (10,302).
   - Shared costs of about 14 k/month were moved to TEC-10.
4. **Leaner staffing.**
   - "Site engineers" cost 173,474 in 2019. A single "field supervision" contract replaced them (MXN about 270 k/month, about 109–160 k/yr).
   - This follows the 2018 plan to replace the Vordcab, PIURZA and SIP Omega crews with one contractor (SEIICO proposal, MXN 262,730/month).
   - The 2018 plan's rent-vs-buy case: USD 64,900/month renting against 39,600/month owning.
5. **Less trucking per month.** Oil trucking fell as rates fell, from about 130 bbl/d in Oct-2018 to about 48 bbl/d in 2021. Trucking stayed the second-largest line in 2021, at 102,720.
6. **The COVID shut-in** (Apr–Jun 2020, no sales) lowered the 2020 total.

**Per-barrel opex did not fall in step**, because the rate declined. It was 19.16 USD/bbl in 2018, 25.66 in 2019, 17.66 in 2020 and 19.91 in 2021, then 61.06 in 2022 and 1,183.53 in 2023.

The cumulative field netback for 2018–23 is about zero, before G&A and about 7.6 MM of capital (`acc_findings.md` §1).

## Gaps

- No monthly opex for Jan-2020 to Dec-2025. Only the Jul–Nov 2020 range is quoted.
- No category split for 2023–25.
- 2018–19 monthly opex has no category split. Categories exist only annually.
- Produced water is not recorded per month for Dec-2019 or Jan–Jun 2022.
