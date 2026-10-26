# Production by well: rules and key facts

Files: `production_by_well.csv` (one row per well-month, 1960-01 to 2022-12), `field_annual.csv` (annual oil and water by well, field total, cumulative), `producing_wells.csv` (every well that produced, with cumulative and years). Input: `data/processed/tecolutla_production.csv` (repo, task 4). Nothing is interpolated. Months with no record have no row.

## Selection rule: one source per well-month

| Rule | Period | Well | Source kind used | Not used, and why |
|---|---|---|---|---|
| R1 | 1960-01 to 1965-12 | FIELD (no well split) | `cnh_monthly_field_level` | This is the only source. |
| R2 | 1966-01 to 2016-01 | TEC-2, 6, 7, 9 | `cnh_monthly_pemex_era` | This is the only per-well source. TEC-2 2015-01 to 2016-01 (13 rows) are flagged as hand-entered. |
| R3 | 2018-07 to 2018-08 | TEC-10 | `tonalli_trucking_sales` (test water only) | The daily sheet starts in Sep-2018. |
| R4 | 2018-09 to 2019-11 | TEC-10 | `tonalli_daily_sum` (wellhead oil, water, gas) | Not used: TEC-10 trucking and test-month rows (sales basis, 5–15 % lower) and `pemex_statement_sales` (field total). Both would double count. |
| R5 | 2018-09, 2019-06 to 2019-08 | TEC-2 | `tonalli_trucking_sales` | In Jul and Aug 2019 the tickets book TEC-2 oil in the commingled stream. Oil for those months comes from the TEC-2 2019 lease operating statement (1,746.6 and 1,043.9 bbl; `acc_review.csv` row 1FCUF9Pp). |
| R6 | 2019 | TEC-7, TEC-11 | `tonalli_trucking_sales` | Water hauls only, no oil. |
| R7 | 2019-12 to 2022-12 | FIELD commingled (CAMPO TECO) | `tonalli_trucking_sales` well = FIELD | Not used: Jul–Nov 2019 CAMPO TECO rows, which duplicate R4 + R5. Water is left blank because ticket water after Aug-2019 is BS&W in oil loads; produced water went to TEC-7 injection. Filed water for 2020–22 is in `opex_monthly.csv` (from `cnh_production_filings_2020_2022.csv`). |

The commingled stream is attributed in the `attributed_to` column:
- 2020: TEC-10 + TEC-2 (CNH 2020 filing).
- 2021: TEC-10 only (CNH 2021 filing).
- Nov 2022: TEC-10DES only (CNH VHP).

`pemex_statement_sales` is never used here, because it is a field total that overlaps all of the rows above.

The recorded total is **1,720,182 bbl**. The repo's `tecolutla_field_monthly.csv` gives 1,715,407 bbl. The +4.8 kbbl difference comes from using TEC-10 wellhead volumes and TEC-2 LOS volumes in 2018–19 instead of field sales. Recorded TEC-10 water (2018-07 to 2019-11) is 60,443 bbl.

## Wells that produced oil (more than four)

| Well | Operator | Cum. oil in monthly records, bbl | By Zone allocation total, bbl (Mar-2020) | Oil years |
|---|---|---|---|---|
| TEC-6 | PEMEX | 507,185 | 899,785 | 1956–2006. Monthly records 1966–2006. The 1956–65 wellfile block of 387,989 bbl has no monthly record. |
| TEC-9 | PEMEX | 352,601 | 352,601 | 1973–1999, 2003–2012 |
| TEC-2 | PEMEX, then Tonalli | 325,580 | 369,031 | 1956–72 (wellfile), 1972–2016, 2018–19, then commingled to ~Sep-2020 |
| TEC-7 | PEMEX | 267,028 | 267,028 | 1957 test, 1968, 1971–1990, 2006. Converted to a water injector in Aug-2019. |
| TEC-10 | Tonalli | 44,468 (wellhead, Sep-18 to Nov-19) | 47,811 (to Mar-2020) | 2018–19 per well. Then the main or sole source of the commingled 41,520 bbl, Dec-2019 to Nov-2022. |
| TEC-11 | Tonalli | 0 oil; 4,397 bbl water hauled | none | Water only on test, May–Aug 2019 |
| FIELD 1960–65 | PEMEX | 181,800 | none | No well split |

So **five wells have produced oil**: TEC-2, TEC-6, TEC-7 and TEC-9 under PEMEX, and TEC-10 under Tonalli. TEC-2 also produced under Tonalli in 2018–2020. TEC-3, TEC-5 and TEC-101 never produced. TEC-11 made only water.

## Peak

- **Peak month: March 1972, 28,881 bbl = 932 bbl/d**, from **three wells: TEC-2, TEC-6 and TEC-7**. This matches "field peak 932 bpd in Mar 1972" in `geology_geophysics_notes.md`. TEC-2 and TEC-7 had just been recompleted to the upper El Abra (2,303–2,308 mSS) in Oct-1971 and Jan-1972.
- **Peak year: 1972, 228,557 bbl** (about 626 bbl/d), from 3 wells.
- **Most wells producing together: four** (TEC-2, 6, 7 and 9), first in May 1973. Four wells were on in 70 months between 1973 and 2006. The best year with four wells on was 1973, at 88,053 bbl. 1977 made 126,624 bbl from three wells.

## Zero months in the presentation app (26 Oct 2026)

`src/build_app_data.py` adds explicit zero rows (flag `z=1`) only for months with no record that fall inside a **non-producing** segment of the well's status timeline in `wells.json` (shut in, workover, injector; each segment carries its source). The PEMEX-era internal gaps are CNH-reported zero months: the original CNH CD tables carry 781 explicit zero rows that fill all 66 internal gap runs (G-34, `database_review/cnh_findings.md` §1). Months with no record inside a **producing** segment stay absent and are drawn as breaks or hatched bands: 1956–59 (no monthly record of any kind), TEC-2 Jun 1956–Mar 1957, TEC-7 Jan–Mar 1957, TEC-2's 2019–22 share of the commingled stream, Jan 2023. Plugged wells stop at the plugging month. For the commingled 2019–22 months (shown as TEC-10), water and the 2022 shut-in months come from the CNH filings / LOS rows in `opex_monthly.csv` (flag `f=1`); Dec 2022 oil uses the LOS 733 bbl instead of the ticket row's 0. These are display rules; `production_by_well.csv` is unchanged.

## Caveats

- Gaps with no records:
  - 1956–59, with no monthly data of any kind.
  - 1966–71, which has TEC-6 only.
  - 1978-06 to 1979-09.
  - 2000–2002, and TEC-7 1990–2006.
  - 2016-02 to 2018-06.
  - Apr–Jun 2020: no rows, because the field was shut in. The CNH filing reports zero.
  - Mar–Oct 2022.
  
  Do not draw lines across these gaps.
- About 0.48 MMbbl of the 1.94 MMbbl By Zone cumulative is wellfile allocation with no monthly record (docs/04 §2).
- The Dec-2022 ticket row books 0 oil, although 740 bbl were shipped and the LOS records 733 bbl sold.
