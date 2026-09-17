# Tonalli Energía / Tecolutla (AC-24) — accounting summary 2016 → 2024

Compiled 17 Sep 2026 from four accounting workbooks rendered to text by the Google Drive connector, cross-checked against the Sept-2020 op-cost sheet and the Sept-2019 directors' memo (`drive_reads_notes.md`, "Operations / marketing"), the PEMEX settlements (`docs/15_pemex_settlements.md`), the TEC-10 / TEC-11 drilling-cost workbooks in `data/raw/`, and the fiscal terms in `docs/01_econ_2023.md`.

Conventions. Amounts are quoted in the currency the sheet uses; USD unless marked MXN or CAD. FX only where the sheet states it. Every figure carries `workbook › sheet › row label`. Nothing is estimated or back-filled: where the sheets are silent the cell says "not in sheets". Two of the four renderings were cut off by the connector at ~1.04 M characters (section 10), so their later sheets are absent.

Partners as the sheets name them. 2016–2019 sheets: "Contributions - Tecolutla", "IDESA costs", "MexCan" (no split by partner). 2022–2024 sheets: **Jaguar Exploración y Producción de Hidrocarburos S.A.P.I. de C.V. ("JEPH", "Jaguar")** and **Petro Frontera / Petrofrontera ("PF")**, the latter being IFR's Mexican holding vehicle (its share is reported in CAD "per IFR FS"). Grupo Idesa appears only as "IDESA costs / IDESA Rent" in 2018 G&A and as "COBRO IDESA / COBRO DECORPI 23" receipts in 2022. No document in this set records a share sale; Jaguar simply is the counterparty from August 2022 (section 6, 8).

---

## 1. Sources

| # | File (Drive title) | Sheets seen in the rendering | What it holds | Currency / FX |
|---|---|---|---|---|
| A | `TONALLI BUDGET - Actual 2019 Forecast 2020 (Forecast update 01132020).xlsx` (1.04 M chars, **truncated**) | `Budget to Actual`; `2019 Actual` (quarterly 2018A, 2019A, 2020F); `2020 Forecast`; `Forecast Presented 09182019`; `Monthly Summary` (monthly Jan-18…Dec-19 actuals, capital by project); `Monthly Forecast` (line-item G&A and regulatory with a "2016/2017" column; cut off inside the Regulatory block) | Revenue, royalties, opex, G&A, regulatory, capital by project, VAT, contributions, cash balances 2016/17–2019, forecast 2020 | USD ("CASHFLOW FORECAST ($USD)", "Budget (US$)") |
| B | `Tonalli Cash (December 31, 2022).xlsx` (1.04 M chars, **truncated**) | `Cash` (bank reconciliation 31-Dec-2022 vs 31-Dec-2021, trial-balance note); `1102-001-201 (2)` (BBVA MXN ledger 2022 + unrecorded Aug–Dec 2022 entries); `1102-001-202 (2)` (Banco Base MXN ledger, cut off in Apr-2022) | Cash balances 2021/2022, 2022 receipts and payments by counterparty, Dec-2022 Jaguar cash calls, severance | MXN (USD accounts shown at MXN equivalent; "Ex. Rate December 31, 2022 = 20.3615") |
| C | `Tonalli - Summary of Cash Calls - September 2024.xlsx` (129 k chars, complete) | `2024 Payments/Contributions to September 30, 2024`; `TOTAL JAGUAR CONTRIBUTIONS` (each 2024 cash call, JOA split, CAD for IFR FS); dilution calc; `Per Tonalli Banks Statements`; `Payment Detail - 2024` (every payment Jan–Jul 2024 by vendor); `Sheet2` (AP list Jul–Aug 2024); `Exchange Rates`; `CashFlow Tonalli` (daily 2024 cash forecast, opening "INICIAL BALANCE NOVEMBER 2022"); `Dilucion` (Jaguar working paper Dec-2023, "notes in blue added by IFR"); `Dec 2023 Notice`; `Notice` (Oct-1-2023 default notice, every JEPH and PF contribution Sep-2022…Sep-2023) | Partner funding 2022–2024, share capital and dilution, 2024 payments incl. fines and royalties, AP | USD, MXN, CAD; FX per line (Banxico FIX; 31-Dec-2023 16.8935; 30-Sep-2024 19.629 MXN/USD, 1.3499 CAD/USD) |
| D | `06_CashFlow acumulado Tonalli.xlsx` (0.48 M chars, complete) | `Cash Flow FY23` (actually "Estado de Flujo de Efectivo del 1 de enero al 30 de Junio de 2024 (NO AUDITADO)", monthly Jan–Jun 2024 with cumulative column); `Mov P2 D6` (GL detail, each 2024 bank movement with MXN and USD, cost centre, "Capex/Expenses" tag) | H1-2024 cash flow statement: opening/closing cash, operating outflows, JEPH loans | USD in the statement (ties to C); GL lines carry both MXN and USD |
| E | `data/raw/drilling_costs/TEC-10 Updated Drilling Cost Summary 15Jun2018.xlsx` | `AFE Cover`, `Drilling_Cost_Summary` | TEC-10 AFE and cost to 15-Jun-2018 | USD (unlabelled; see `docs/08_afe.md` §3) |
| F | `data/raw/drilling_costs/TEC-11 Drilling Cost Tracker 26Dec2018.xlsx` | `TEC-11 Cost Estimate` | TEC-11 AFE TON2018DR002 and daily cost tracker to 26-Dec-2018 | USD |
| G | `data/raw/development_plan/Tec 11 Summary of Costs (Actual and Budgeted).xlsx` | `Actual`, `TEC-11 Drill Cost Estimate`, `Formato_costo_pozos`, `TEC-11 Completion` | TEC-11 actual vs budget by phase | USD ("Costos totales – Dólares") |
| H | `docs/15_pemex_settlements.md` | — | Realised revenue 2020–2022 from PEMEX comprobantes | USD |
| I | `drive_reads_notes.md` › Operations / marketing | `Tonalli Op Cost 290920.xlsx`; directors' memo 6-Sep-2019 | Sept-2020 monthly opex; 2019 funding, payables, VAT | USD / MXN at 21 |

---

## 2. Capital spend by year and project (USD, cash basis)

Source A › `Monthly Summary` › block "Capital Costs" (columns Jan-18…Dec-18 "Total", Jan-19…Dec-19 "Total", and the "TOTAL 2018/2019" column). 2016/2017 capital is in the truncated part of `Monthly Forecast` and is **not in sheets** (only the opening-cash and contribution lines of that column survived).

| Project (row label as in sheet) | 2018 | 2019 | 2018+2019 | Notes |
|---|---|---|---|---|
| Landowner Fees | 73,485 (Jan-18) | – | 73,485 | |
| Seismic | 61,000 (Sep-18) | – | 61,000 | |
| Tec-10 Drill and Complete | 2,437,831 | 147,013 | **2,584,844** | monthly: Jan 3,500; Feb 76,900; Mar 56,195; Apr 150,000; Jun 279,810; Jul 511,770; Aug 641,925; Sep 108,000; Oct 172,450; Nov 422,777; Dec 14,504; 2019: Jan 70,065, Mar 58,358, May 18,590 |
| Tec-2 Workover (Initial) | 605,975 | 50,315 | 656,290 | Feb–Nov 2018 |
| Tec-2 Add. Perf and Workover | – | 101,118 | 101,118 | Feb 1,310; Jun 11,800; Sep 88,008 (2019) |
| Tec 11 Drill | 816,438 (Nov–Dec 18) | 1,505,035 | **2,321,473** | 2019: Jan 157,228; Feb 299,860; Mar 511,150; Apr 357,625; May 109,282; Jun 69,890 |
| Tec 11 Complete | – | 209,909 | 209,909 | Apr 35,026; May 92,901; Jun 51,005; Jul 15,692; Aug 15,286 |
| Tec 11 Complete – Tantayuca | – | 4,520 | 4,520 | Aug-19 |
| Tec-7 Workover | 30,220 | 65,628 | 95,848 | 2019: Jun 50,797; Aug 14,831 (water-injection well) |
| Additional Road Work | – | 28,345 | 28,345 | |
| Separator | – | 11,350 | 11,350 | Dec-19 |
| Tec 2/Tec & Pipelines | – | 24,409 | 24,409 | Oct/Dec-19 |
| Water Injection well Equipment; Turbine meter; **Tec 12** | – | – | – | rows exist, all "$-" |
| Payment of Accrued Capital Costs | 110,761 | 188,050 | 298,811 | |
| **Total capital (sheet total row)** | **4,135,710** | **2,335,691** | **6,455,531** | the quarterly `2019 Actual` sheet books 2019 as "Payment of accrued capital costs" 1,171,046 + 800,416 + 138,336 + 190,135 plus separator/pipelines 35,759 = 2,335,691 (same total); its 2018 column shows only 110,761 because the well costs sit in the monthly sheet |
| Round 3.2/3.3/Pemex JV costs (data purchases 214,040; registration 14,180) | 228,220 | – | 228,220 | `Monthly Summary` › "Total costs Round 3.2/3.3/ Pemex JV" (separate from Tecolutla) |

2020 forecast (A › `2020 Forecast` › Capital Costs, Jan-2020 update): Separator 32,405; Pipelines 6,152; Pump truck 50,000; **Payment of accrued capital costs 1,965,773** (Q1 386,733; Q2 321,720; Q3 157,321; Q4 1,100,000); total 2,054,331. The Sept-2019 version (`Forecast Presented 09182019`) had 1,432,522. These are the unpaid TEC-11 invoices (see §7).

Well-level AFE vs actual (E, F, G):

| Well | AFE | Actual | Source |
|---|---|---|---|
| TEC-10 (AFE "ST028 Perforación del pozo TEC-10", directional, TD 2,490 m) | **2,924,760** (`AFE Cover` › TOTAL; `Drilling_Cost_Summary` › COSTO TOTAL AFE › ORIGINAL) | 2,039,002 to 15-Jun-2018 (`Drilling_Cost_Summary` › ACTUAL: drilling 1,810,649 + tangibles 228,353); cash paid 2018–19 **2,584,844** (A, above) | E, A |
| TEC-11 drilling (AFE TON2018DR002, spud 9-Nov-2018) | AFE Amt **2,250,000** (F › header); tracker SUB column sums to **3,025,996** at 26-Dec-2018 (rig 582,846; mud 449,500; directional 230,600; production casing 219,000; intermediate casing 215,000; rig move 195,000; location 195,000; cement 232,500) | **3,105,308** vs budget 2,853,870, +251,438 "QMAX over budget and other extra costs" (G › `Actual`) | F, G |
| TEC-11 cement bond log / wellbore clean-up (Jan-2019) | 100,000 | 129,360 | G |
| TEC-11 completion (May/Jun 2019) | 831,000 | 962,850 ("Workstrings invoices") | G |
| TEC-11 Tantayuca (Aug-2019, incl. testing) | 150,000 | 206,225 | G |
| **TEC-11 all-in** | **3,934,870** | **4,403,743** (+468,873, +12 %) | G › `Actual` › Total |

Reconciliation: TEC-11 cash paid through Dec-2019 per A = 2,321,473 + 209,909 + 4,520 = 2,535,902 against 4,403,743 incurred → ≈ 1.87 M unpaid at end-2019, which is the "Payment of accrued capital costs" carried into 2020 (1.97 M) and the directors' memo's "capital payables USD 2.3 MM at 30 Jun 2019, 1.8 MM at 31 Aug".

---

## 3. Revenue by year (bbl, USD)

| Year | Sales bbl | Revenue USD | USD/bbl | Royalties USD (% rev) | Source |
|---|---|---|---|---|---|
| 2016–2017 | – | – | – | – | no production; not in sheets |
| 2018 (first sales Sep-18) | 15,414.66 (Sep 1,719.93; Oct 5,053.92; Nov 4,440.82; Dec 4,200.00) | **920,662** (Sep 109,026; Oct 350,813; Nov 266,670; Dec 194,153) | 59.73 | 379,450 (41.21 %) | A › `Monthly Summary` › Total Sales Volumes / Revenue / Royalties |
| 2019 | 32,747.41 (Q1 8,027; Q2 8,357; Q3 9,544; Q4 6,820) | **1,731,700** (Q1 407,656; Q2 472,595; Q3 505,657; Q4 345,791) | 52.88 | 706,221 (40.78 %) | A › `2019 Actual` (ACTUAL columns); `Budget to Actual`: forecast was 34,286 bbl / 1,841,364 |
| 2020 | 19,041 (no deliveries Apr–Jun) | **681,874** | 35.81 | not in sheets (2020F royalty 41.44 %) | H (PEMEX comprobantes); A › `2020 Forecast` had 29,053 bbl / 1,510,748 |
| 2021 | 17,546 | **939,419** | 53.54 | not in sheets | H |
| 2022 (field shut in Feb) | 2,740 (Jan–Feb, then Nov–Dec) | **178,032** | 64.97 | not in sheets | H |
| 2023 | Jan-2023 invoice only (H §2, 57.33 USD/bbl); no 2023 sales in C/D | – | – | – | C › `Cash Flow FY23` shows no "Cobro clientes terceros" Jan–Jun 2024 |
| **2018–2022** | **87,489** | **4,451,687** | 50.9 | | |

Cross-checks. (i) 2019 monthly realised prices in A (46.83–59.57 USD/bbl, Dec-19 51.34) match the Dec-2019 CFDI invoice in H (51.34). (ii) 2022 cash receipts from PEMEX in B › `1102-001-201 (2)`: "COBRO PEMEX" 31-May-22 MXN 1,883,735.12; 30-Jun-22 MXN 1,972,616.37 + 1,972,616.37 + 1,419,882.64 + 689,700.74; "PAGO PEPE 07" 27-Jul-22 MXN 270,310.09 → **MXN 8,208,861** (≈ USD 0.40 M at ~20.4), i.e. the late-2021/early-2022 deliveries were collected 3–5 months late. (iii) 2024 payment detail (C) shows **CNH "Royalties" USD 232,481 paid 23-Apr-2024** together with block fee MXN 717,140 and "Penalties" MXN 303,220 + USD 150,390 (total that day USD 442,894) — royalty arrears settled with penalties, not current production.

---

## 4. Operating costs by year and category (USD)

| Year | Opex | USD/bbl | Detail / source |
|---|---|---|---|
| 2018 (Sep–Dec) | **288,134** | 18.69 | A › `Monthly Summary` › Operating Costs: Sep 67,530; Oct 80,000; Nov 72,000; Dec 68,604 |
| 2019 | **839,052** | 25.62 | monthly 53,596–83,409; Q1 190,321; Q2 206,122; Q3 235,677; Q4 206,932 (`2019 Actual`). Sept-2019 forecast was 778,086 (22.69/bbl) |
| 2020 forecast | 460,769 (Jan-2020 update) / 546,415 (Sept-2019 version) | 15.86 / 15.23 | after TEC-2 shut-in (Sept-2019) and moving ≈14 k/month shared costs to TEC-10 (I) |
| Sept-2020 run-rate | ≈ 28,155 / month (≈ 338 k / yr) | – | I › `Tonalli Op Cost 290920.xlsx` (FX 21): crew 280,000 MXN; Kefren/TDH vacuum truck 108,000 MXN; diesel 60,000 MXN; consumables 40,000 MXN; Oro Negro frac tank 32,000 MXN; Mensuranda water analysis 21,000 MXN; Intertek 1,468 USD; Apollo demulsifier 925 USD. Separator rental 216,000 MXN/month Sept-2019–Mar-2020 |
| 2021 | not in sheets | | |
| 2022 (shut in Feb) | not totalled; B ledger shows the same vendors winding down: Kefren (trucking) MXN 407,662 in Jan–Mar 2022; "SERV ADM/ SERV ADMON" MXN 942,925 Jan–Mar 2022; HEPR MXN 1,615,679 (≈160 k/month all year); Dec-2022 still paying Seiico diesel/staff 82,346, Servicios Petroleros ZV tanks 46,400, Petrohaba tanks 30,206, Kefren Nov trucking 90,282, Mensuranda 11,136 (all MXN) | | B › `1102-001-201 (2)` / `1102-001-202 (2)` |
| 2023 | not in sheets (C › `CashFlow Tonalli` daily sheet exists but its 2023 columns did not render usably) | | |
| H1-2024 | "Gastos de operación y administración" **1,351,098** (Jan 35,319; Feb 82,150; Mar 82,978; Apr 485,376; May 626,662; Jun 38,612) + interco admin services (JEYP) 294,959 + insurance 3,052 + taxes 5,118 = **operating outflows 1,653,252** | – | D › `Cash Flow FY23` › "Efectivo pagado por". April and May carry the CNH settlement (442,894) and the SEMARNAT PPCIEM fine (606,093), see §5 |

Field-level opex items visible in 2024 (C › `Payment Detail - 2024`): Servicios Petroleros ZV "Renta de Frac tank 500 bls, Pozo Tecolutla" MXN 23,200/month; SYS Industriales oil/antifreeze for the injection pump MXN 4,799–5,806; EYS "Reportes de controles volumétricos" USD 6,960; Consultoría Científica Multidisciplinaria PPCIEM quarterly OGI-camera monitoring MXN 242,440 and annual report 150,800; GH Medio Ambiente environmental advisory MXN 232,000 + legal audit 108,750; Edenred fuel MXN 20–30 k. No crew, trucking or diesel lines → the field was not producing in H1-2024.

---

## 5. G&A and regulatory by year (USD)

| Year | G&A | Regulatory | Source and detail |
|---|---|---|---|
| 2016/2017 (single column) | **1,373,983** (Subtotal G&A) | ≥ 657,015 from the lines that rendered (subtotal row lost to truncation) | A › `Monthly Forecast` › "2016/2017": G&G/Operations consulting 648,910; Geophysical consulting 94,800; Tonalli salaries 187,750; IDESA costs 78,950; IDESA rent 21,000; Tampico office 4,460; truck 24,000 + insurance 2,860; insurance 82,000; corporate legal/notary 70,110; software 4,700; audit 3,940; travel 172,297; misc 26,250; change in AP +48,044. Regulatory lines: CNIH data 35,480; Data-room costs Round 3.2 (+145,590, "Note 1", a credit); bid-round registration 37,500; ADINCO software 57,000; consulting 58,400; Admin Plan 17,000; regulatory legal (Erick Hernández) 139,080; TEMA admin-plan consultant 60,960; ESIA (UAM) 122,590; ESIA lab (CTIA) 117,260; MIA 4,255; drilling-permit consultant 142,120; implementation plan 10,960 |
| 2018 | **1,309,749** | **671,017** (incl. 228,220 Round 3.2/3.3 bid costs) | A › `Monthly Summary` / `Monthly Forecast` 2018 totals: G&G/ops consulting 390,600; geophysical 144,000; salaries 428,935; IDESA costs 210,000; IDESA rent 46,845; insurance 156,185; software 130,500; travel 115,000; truck 28,225; change in AP +394,928. Regulatory: legal (Erick Hernández) 290,725; data rooms 3.2/3.3 212,800; ADINCO 52,500; consulting 80,000; implementation plan 57,060; change-of-control fee CNH 28,505; MIA modification 12,200. G&A spikes Apr-18 (650,600) and Sep-18 (393,047) |
| 2019 | **673,984** | **112,605** | A › `2019 Actual`: G&A Q1 202,134; Q2 199,343; Q3 117,045; Q4 155,462; salaries 446,046; insurance 158,782; GLJ reserve report 24,670; audit 14,925. Regulatory: legal 36,210; ADINCO 21,000; SMPS 3,500; CNH change-of-control refund +25,000 (Sep-19). Directors' memo (I): "G&A + regulatory USD 820 k for 2019" vs 787 k actual |
| 2020 forecast | 382,100 (Jan-2020) / 329,500 (Sept-2019) | 20,000–65,500 | A › `2020 Forecast`: salaries 264,600 (22,050/month); insurance 63,000; audit 28,000; GLJ 20,000; regulatory legal 42,000 |
| 2021 | not in sheets (`Tonalli G&A Expenses- December 31, 2021.xlsx`, 39 MB, not readable by the connector) | | |
| 2022 | not totalled; B ledger: payroll (NOMINA) MXN 541,978 Jan–Mar; IMSS 594,275; SAT/ISR/other taxes 1,040,365; CNH exploration tax ≈ MXN 15 k/month (Jul-22 15,666; Aug 15,320/14,993; Sep 14,983; Oct 14,678; Nov 14,678; Dec 14,465); Deloitte partial 120,149; notary (Erik Namur) 13,386 + 54,275; **severance ("FINIQUITO DIC22") MXN 659,860 on 15–20 Dec 2022** | | B › `1102-001-201 (2)` unrecorded entries |
| 2023 | not in sheets | | |
| H1-2024 | JEYP "Prestación de servicios especializados / servicios administrativos" USD 53,365–59,136 per month (294,959 for the half-year, "Gastos de operación y administración interco"); Galaz Yamazaki Ruiz Urquiza (Deloitte) audit MXN 367,773 + 150,000 + 217,773; Deloitte transfer-pricing MXN 34,800 + 57,487; GLJ reserves evaluation USD 5,495 + 11,500; Greenberg Traurig **2019** legal invoices USD 14,539 + 9,883 (+ one unpriced) paid 13-Jun-2024; Consultoría Jurídica Sandoval MXN 15,467/month; Govea Mercado Béjar lawyers MXN 348,000 | **CNH annual administration "A24 Transición AC Administración Anual 2024" MXN 806,415 (USD 47,436, 20-Mar-24)**; FMP "Cuota contractual" MXN 29,829/month (USD 1,744–1,753); CRE MXN 25,284; ASEA LAU fee 3,569 and **ASEA bond MXN 303,240 (USD 17,781)**; SEMARNAT MXN 778,050 (USD 47,155, 7-Feb-24); **SEMARNAT "Pago Multa PPCIEM Tonalli Energía" MXN 10,000,536 = USD 606,093 (31-May-24)**; CNH royalties 232,481 + block fee MXN 717,140 + penalties MXN 303,220 and USD 150,390 (23-Apr-24); Tokio Marine bond premium MXN 56,003 | C › `Payment Detail - 2024`; D › `Cash Flow FY23` |

The directors' memo figure of ≈ USD 14 k/month shared costs and the 2020 salary line of 22,050/month give the post-2019 G&A floor of ≈ 0.35–0.4 M/yr; by 2024 the only recurring G&A is the JEYP service fee (≈ 0.7 M/yr) plus audit and legal.

---

## 6. Cash calls, partner funding and loans

### 6.1 2016–2019 (A; USD; no split by partner in the sheets)

| Period | Contributions | Detail (A › `Monthly Summary` › "Contributions - Tecolutla"; `Monthly Forecast` › "Cash Contributions") |
|---|---|---|
| 2016/2017 | **3,250,000** | single column "2016/2017" |
| 2018 | **6,998,500** | Feb 3,700,000; Aug 1,100,000; Oct 1,000,000; Nov 998,500; Dec 200,000 |
| 2019 | **2,250,000** | Jan 200,000; Feb 330,000; Mar 320,000; Apr 750,000; Jun 150,000; Aug 300,000; Sep 200,000 |
| 2020 forecast | "Additional cashflow required" 1,100,000 (Jan-2020 update: −100,000 Jan, +1,200,000 Oct) / 850,000 (Sept-2019 version, Q4) | A › `2020 Forecast` / `Forecast Presented 09182019` |
| **2016–2019** | **12,498,500** | |
| 2020–2021 actual | not in sheets | |

"SH Loan interest" row exists in `Monthly Forecast` and is "$-" throughout, i.e. the 2016–2019 funding was treated as equity, not loans.

### 6.2 August 2022 – December 2023 (C › `Notice` "WORKING PAPER PREPARED BY JAGUAR - DEFAULT NOTICE OCTOBER 1, 2023", `Dec 2023 Notice`, `Dilucion`)

Every deposit is listed with MXN, USD and the Banxico rate. Sums of the listed rows (73 rows, de-duplicated):

| Period | JEPH (Jaguar) MXN | JEPH USD | Petrofrontera MXN | Petrofrontera USD |
|---|---|---|---|---|
| Aug–Dec 2022 | 6,542,440 (16 deposits; e.g. 15-Sep-22 USD 15,000 "IMPUESTOS Y NOMINA"; 21-Sep-22 USD 66,250 "APORTACION"; 17-Oct-22 MXN 601,194 "NOMINA IMPUESTOS"; Dec-22 MXN 13,400 + 642,000 + 150,000 + 260,000 + 100,000 + 120,000 — the same six Dec entries appear in B as "JAGUAR … CASH CALL TONALLI") | 331,118 | 1,761,690 (30-Aug-22 USD 40,000; 2-Sep-22 USD 48,000) | 88,000 |
| Jan–Jun 2023 | 11,416,091 (35 deposits) | 642,769 | – | – |
| Jul–Sep 2023 | 9,672,471 (19 deposits, incl. 9-Aug-23 MXN 4,500,000 and 20-Sep-23 MXN 2,000,000) | 566,603 | 1,481,086 (24-Aug-23 USD 87,500) | 87,500 |
| Sheet totals to 30-Sep-2023 | **27,631,000** "JEPH - Total Cash call" | **1,540,488** | **3,242,776** "Petrofrontera - Total Cash call" | **175,500** |
| Oct–Dec 2023 (`Dec 2023 Notice`, "Jaguar contributions to Oct 1, 2023 to Dec 31, 2023") | **7,707,837** | **434,305** | – | – |

Dilution mechanics recorded in `Dilucion` (Jaguar working paper, IFR notes): Dec-2022 shareholder resolution — Jaguar "aportado en 2022" 6,543,000; Petrofrontera 1,761,000 paid and **4,782,000 "pendiente de aportación"**; PF paid 1,481,000 in Aug-2023 and Jaguar paid PF's remaining 3,301,000 ("Paga Jaguar adeudo de Petrofrontera"). Notice 1 (1-Oct-2023): Jaguar contributions to 30-Sep-2023 MXN 21,088,532 / USD 1,209,333, less 3,301,000 shares → default amount 17,787,532 / USD 1,028,539, of which PF's 48.28 % = 8,588,323 / USD 496,607. Notice 2 (Dec-2023): 7,707,837 / USD 434,305, PF share 3,721,561 / USD 209,683. "Default amount Petrofrontera" 10,543,612 MXN / USD 604,686. Shares issued to Jaguar: 3,301,000 + 17,787,532 + 7,707,837 (MXN, at 1 peso/share).

Share capital (C › `Dilucion`, `Tonalli Share Capital`):

| Date | Petrofrontera | Jaguar | Total | PF % |
|---|---|---|---|---|
| 31-Dec-2022 | 96,117,000 | 96,117,000 | 192,234,000 | 50.00 % |
| 30-Sep-2023 (after Notice 1) | 92,816,000 | 117,205,000 | 210,021,000 | 44.19 % |
| 31-Dec-2023 | 92,816,000 | 124,913,369 | 217,729,369 | **42.63 %** |
| 29-Feb-2024 "potential dilution" | 92,816,000 | 137,838,661 (+12,925,292) | 230,654,661 | 40.24 % |

### 6.3 2024 (C › `Contributions to September 30, 2024`, `TOTAL JAGUAR CONTRIBUTIONS`; D › `Cash Flow FY23`)

All 2024 funding came from Jaguar and is booked by Tonalli as **loans** ("Préstamo obtenido para Tonalli / Préstamos JEPH-Tonalli recibidos", D) with "Accrued interest per JOA":

| Month 2024 | USD | MXN | Jaguar 57.37 % | PF 42.63 % | PF share CAD |
|---|---|---|---|---|---|
| to 31-Mar | 370,662.24 | 6,302,651.20 | 212,648.93 | 158,013.31 | 213,636.53 ("Agreed to March 31, 2024 FS") |
| April | 532,001.14 | 9,066,729.20 | 305,209.05 | 226,792.09 | 308,494.11 |
| May | 745,098.10 | 12,455,658.00 (incl. 29-May-24 MXN 10,000,000 = USD 600,355) | 427,462.78 | 317,635.32 | 435,435.42 |
| June | 47,593.55 | 826,722.00 | 27,304.42 | 20,289.13 | 27,843.82 |
| July | 163,096.37 | 2,815,904.00 | 93,568.39 | 69,527.98 | 94,990.62 |
| August | 149,571.62 | 2,665,428.00 | 85,809.24 | 63,762.38 | 87,448.69 |
| September | 62,590.23 | 1,067,113.36 | 35,908.02 | 26,682.22 | 36,277.14 |
| **Contributions to 30-Sep-2024** | **2,070,613.25** | **35,200,205.76** | 1,187,910.82 | 882,702.43 | 1,204,126.33 |
| Interest accrued (per JOA) | 121,378.39 | 2,382,536.39 | 69,634.78 | 51,743.61 | 69,850.00 |
| **Total with interest** | **2,191,991.64** | **37,582,742.15** | 1,257,545.61 | 934,446.04 | 1,261,408.71 (after FX gain 12,567.63; "Agreed to September 30, 2024 FS") |

D › `Cash Flow FY23` › "Préstamo obtenido para Tonalli": Jan 86,993; Feb 83,369; Mar 200,300; Apr 532,001; May 743,433; Jun 47,594 = **1,693,690** for H1-2024 (ties to C within FX). "Balance per Tonalli June 30, 2024 FS" of the JEPH loan: USD 1,612,346 / MXN 29,630,570 (C › after "Fex loss (gain) (458,267)"). Cash-call deposits per bank statements to 19-Jun-2024 total USD 1,614,214 (C › `Per Tonalli Banks Statements`).

### 6.4 Cumulative partner funding visible (USD)

2016–2019 12,498,500 + 2022 419,118 (JEPH 331,118 + PF 88,000) + 2023 1,731,177 (JEPH 1,209,372 + 434,305; PF 87,500) + 2024 to Sep 2,070,613 = **≈ 16.72 M**, excluding 2020–2021 (not in sheets) and the ≈ 1.1 M "additional cashflow required" forecast for 2020.

---

## 7. VAT recoverable and payables

VAT (USD, A):

| Period | VAT paid on expenses | VAT collected | VAT refunds received | Net VAT cash | Source |
|---|---|---|---|---|---|
| 2018 | – | – | – | **(661,822)** | A › `Monthly Summary` › "VAT, net" (monthly (5,393)…(140,890), heaviest Apr-18 (140,890), Jul (98,388), Nov (98,063)) |
| 2019 | (558,416) | 255,363 | **246,854** (Nov-19 +92,479; Dec-19 +151,884 net) | **(56,198)** | A › `Budget to Actual` (2019 actual) and `Monthly Summary`; the Sept-2019 forecast assumed 644,477 recovery |
| Aug-2019 balance | | | | **≈ 1.2 M recoverable** (Yaxkin Consulting engaged for the 2017–18 filings; 95 k for 2017 and 555 k for 2018 expected; memo assumed 600 k in Q4-19 and 300 k in Q1-20) | I (directors' memo) |
| 2020 forecast | (453,575) | 241,720 | 700,990 (611,090 in Q1-20) | +489,135 | A › `2020 Forecast` |
| 2021–2023 | not in sheets | | | | |
| H1-2024 | | | "Ingreso IVA a Favor (Devuelto)" = – (none) | | D › `Cash Flow FY23` |

Payables:

| Date | Payables position | Source |
|---|---|---|
| 2018 | "Change in Accounts Payable (Actual Payments vs. Accruals)" +394,928 for 2018 (accruals built, esp. Sep-18 (261,532) and Apr-18 (466,885) reversals) | A › `Monthly Forecast` |
| 30-Jun-2019 | capital payables **USD 2.3 M**; 31-Aug-2019 **1.8 M** | I (directors' memo) |
| end-2019 | ≈ 1.87 M TEC-11 costs incurred but unpaid (§2 reconciliation); 2020 forecast "Payment of accrued capital costs" 1,965,773 incl. 1,100,000 in Q4-2020 | A, G |
| 31-Dec-2022 | trial-balance note shows "PY entries to be booked" and adjustments; Deloitte "Partial Payment" MXN 120,149 (21-Dec-22); ASSA "payment of 2 outstanding invoices per agreement"; HEPR "Final payment" 8,055 planned for Dec-22 | B › `Cash` › Note 2; C › `CashFlow Tonalli` › Dec-22 lines |
| 2024 | payments of aged invoices: Greenberg Traurig legal fees dated 11-Apr-2019, 16-May-2019, 9-Oct-2019 paid 13-Jun-2024; Química Apollo invoice 3-Jun-2021 (USD 6,606) paid 13-Jun-2024; GNP insurance invoice Oct-2023 paid Jan-2024; CNH royalties/penalties settled 23-Apr-2024 | C › `Payment Detail - 2024` |
| Jul–Aug 2024 open AP ("Sheet2", "Por pagar") | AXA insurance; Consultoría Científica MXN 242,440 (×2); Sandoval MXN 15,467 (×3); Erik Namur 12,296; GH Medio Ambiente MXN 108,750 + 232,000; JEYP MXN 5,800 + USD 53,365; SYS 4,799 + 5,806; EYS USD 6,960; GNP 15,386; travel and reimbursements < MXN 6 k each. No total row rendered | C › `Sheet2` |
| 2024 forecast | C › `CashFlow Tonalli` › "TOTAL 2024": payments 1,813,957 (Other Rights 722,454; Fixed Cost Administrativos 792,652; Taxes 62,056; Payroll 59,097; Fixed Cost Operativos 45,999; General Suppliers 100,000; Contractual Exploration Commitments 20,118; Insurance/Bonds 11,582) vs inflows 497,366 → **net −1,307,553** (cumulative balance line ends at −1,307,553 in Dec-2024, i.e. the funding still required) | C (column alignment in this daily sheet is approximate) |

---

## 8. Cash position timeline 2016–2024 and key events

| Date | Cash | Currency / source | Event |
|---|---|---|---|
| 2016/2017 opening | 87,500 | USD, A › `Monthly Forecast` › Opening cash balance "2016/2017" | Licence awarded CNH Round 1.3 (2015/16); 3,250,000 contributed over 2016–17; G&A 1.37 M, regulatory ≥ 0.66 M |
| 1-Jan-2018 | **856,195** | USD, A › `Monthly Summary` | |
| Feb-2018 | 4,113,549 after 3,700,000 contribution | USD, A | Landowner fees Jan-18; TEC-2 workover Feb–Nov; TEC-10 drilling Jun–Aug (peak spend Jul–Aug 2018) |
| Sep-2018 | 380,352 | USD, A | first sales (1,720 bbl); seismic 61,000; TEC-11 spud 9-Nov-2018 |
| 31-Dec-2018 | **326,935** (bank line; the formula line reads 5,354,424 and is an artefact) | USD, A › `Monthly Summary` › Closing Cash balance | 2018 net cash flow −7,299,540 (Tecolutla) −228,220 (bid rounds) +6,998,500 contributions |
| 1-Jan-2019 | 231,410 (as carried in `2019 Actual`; 95,525 below the Dec-18 bank line — not reconciled in the sheets) | USD, A | |
| Jun-2019 | **12,281** | USD, A | TEC-11 drilling/completion invoices (Q1-19 capital 1,171,046; Q2 800,416); capital payables 2.3 M at 30-Jun |
| Aug-2019 | 19,363 | USD, A | **Factoring problem**: PEMEX had not loaded the July invoice (USD 263,173 incl. VAT) into the NAFIN portal; Q4 shortfall 1.55 M; VAT ≈ 1.2 M recoverable (I) |
| Sep-2019 | 383,548 | USD, A | **TEC-2 shut in** (uneconomic; 8 k demob); 200,000 contribution |
| 31-Dec-2019 | **422,063** | USD, A › `Budget to Actual` / `Monthly Summary` | 2019 net cash flow −2,059,346 + 2,250,000 contributions; VAT refunds 246,854 received Nov–Dec |
| 2020 (forecast, Jan-2020 update) | closing 39,229 after 1,100,000 additional funding; Q4-2020 capital payments 1,100,000 | USD, A › `2020 Forecast` | **COVID**: no deliveries Apr–Jun 2020; realised 35.81 USD/bbl for the year (H); actual 2020 cash not in sheets |
| 31-Dec-2021 | **MXN 1,624,112.64** (BBVA MXN 924,183.55; Banco Base MXN 503,515.67; BBVA USD 183,078.40 MXN-eq; Base USD 13,335.02 MXN-eq) ≈ USD 79 k at 20.5 | B › `Cash` | |
| Feb-2022 | – | | **Field shut in** (no deliveries Mar–Oct 2022, H); Banco Base MXN ledger shows "CMB" (currency conversion) credits of MXN 3,815,961 Jan–Apr 2022, i.e. USD balances being sold for pesos to fund payroll and suppliers |
| May–Jul 2022 | PEMEX receipts MXN 8,208,861 | B | last significant revenue collections |
| Aug–Sep 2022 | Petrofrontera USD 40,000 + 48,000; JEPH first cash calls 15-Sep-2022 | C | **Jaguar becomes the funding partner**; "COBRO IDESA / DECORPI 23" receipts of MXN 667,658 in Mar–May 2022 are the last Idesa entries |
| 15–20 Dec 2022 | severance MXN 659,860 to five staff | B | Tonalli staff let go; Jaguar cash calls MXN 1,285,400 in Dec-22 |
| 31-Dec-2022 | **MXN 128,976.39** (BBVA MXN 14,192.60; Base MXN −15,344.50; BBVA USD 2,089.61 = MXN 40,314.75; Base USD 4,638.77 = MXN 89,813.55) ≈ **USD 6.3 k** at 20.3615 | B › `Cash` ("Balance per December 31, 2022 FS - Note 2"); bank statements 147,495.08, difference 18,518.69 | |
| 30-Sep-2023 | – | C | **Petrofrontera default notice** (1-Oct-2023): PF diluted to 44.19 %, then 42.63 % at 31-Dec-2023 |
| 31-Dec-2023 | **USD 8,752** | D › `Cash Flow FY23` › "Saldo inicial de efectivo" Enero | |
| Jan–Jun 2024 | month-end 12,736; 12,889; 11,840; 14,141; 11,735; **17,565** (30-Jun-2024) | USD, D | JEPH loans 1,693,690 in; operating outflows 1,653,252; CAPEX-cuota 45,206; CNH arrears + penalties 442,894 (Apr), SEMARNAT PPCIEM fine 606,093 (May) |
| 30-Sep-2024 | – | C | Jaguar loans 2,070,613 + interest 121,378; 2024 forecast still −1.31 M to year-end |

---

## 9. Cumulative money in / money out since 2016 (USD, cash basis, as far as the sheets go)

| | 2016/17 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 (to Jun/Sep) | Visible total |
|---|---|---|---|---|---|---|---|---|---|
| **Money in** | | | | | | | | | |
| Partner contributions / loans | 3,250,000 | 6,998,500 | 2,250,000 | n/s (F 1,100,000) | n/s | 419,118 | 1,731,177 | 2,070,613 (Sep) | **≈ 16.72 M** |
| Oil revenue (gross) | – | 920,662 | 1,731,700 | 681,874 | 939,419 | 178,032 | Jan-23 invoice only | – | **4,451,687** |
| VAT refunds | n/s | 0 | 246,854 | F 700,990 | n/s | n/s | n/s | 0 (H1) | ≥ 246,854 |
| Other receipts (Idesa/DECORPI 2022, MXN 667,658) | | | | | | ≈ 33 k | | | |
| **Money out** | | | | | | | | | |
| Royalties (paid via PEMEX/FMP) | – | 379,450 | 706,221 | n/s (≈41 %) | n/s | n/s | n/s | 232,481 arrears + penalties 150,390 + MXN 303,220 | ≥ 1.47 M |
| Opex | – | 288,134 | 839,052 | F 460,769 | n/s | n/s | n/s | (in 1,351,098) | ≥ 1.13 M |
| G&A | 1,373,983 | 1,309,749 | 673,984 | F 382,100 | n/s | n/s | n/s | 294,959 interco + audit/legal | ≥ 3.65 M |
| Regulatory | ≥ 657,015 | 671,017 | 112,605 | F 20,000–65,500 | n/s | CNH tax ≈ MXN 180 k | n/s | fines/fees ≈ 0.77 M (PPCIEM 606,093; CNH admin 47,436; SEMARNAT 47,155; ASEA 17,781; FMP ≈ 10 k) | ≥ 2.2 M |
| Capital | n/s | 4,135,710 | 2,335,691 | F 2,054,331 | n/s | n/s | n/s | 45,206 (cuota) | ≥ 6.52 M (+ ≈ 1.9 M TEC-11 payables settled after 2019) |
| Bid rounds 3.2/3.3 | – | 228,220 | – | – | – | – | – | – | 228,220 |
| VAT paid (net of collected) | n/s | 661,822 | 303,053 | F 211,855 | n/s | n/s | n/s | n/s | ≥ 0.96 M |
| Cash at period end | 856,195 (1-Jan-18) | 326,935 | 422,063 | F 39,229 | ≈ 79 k | ≈ 6.3 k | 8,752 | 17,565 (Jun) | |

n/s = not in sheets; F = forecast in A (Jan-2020 update). Well-level all-in cost incurred: TEC-10 2.58 M cash 2018–19 (AFE 2.92 M); TEC-11 4.40 M incurred (AFE 3.93 M); TEC-2 workovers 0.76 M; TEC-7 0.10 M. Total identifiable well capital 2018–19 ≈ 7.9 M incurred against 6.46 M paid by end-2019.

Order-of-magnitude reading: ≈ 16.7 M of partner money plus ≈ 4.45 M gross revenue (≈ 2.6 M after royalties) went in; ≈ 6.5 M capital, ≈ 3.7 M G&A, ≈ 2.2 M regulatory/fines, ≈ 1.1 M opex and ≈ 1 M net VAT are visible going out through 2019/2024, leaving 2020–2023 operations (≈ 1.9 M of TEC-11 payables, three years of opex/G&A and the 2021–22 royalties) as the unquantified balance.

---

## 10. Gaps — what the workbooks do not show

1. **Truncation.** A and B were cut by the connector at 1.04 M characters. A stops inside `Monthly Forecast` › Regulatory (2016/17 regulatory subtotal, 2016/17 capital, and any monthly 2020 sheets lost). B stops in the Banco Base MXN ledger at April 2022; the AP, AR, VAT and cash-call sheets the title implied are **absent**, so no 31-Dec-2022 AP/AR/VAT balances.
2. **2020 and 2021 actuals.** No cash, opex, G&A, VAT or contribution actuals for 2020–2021 anywhere in the four files; only the Jan-2020 forecast (A), the Sept-2020 op-cost sheet (I) and revenue from the PEMEX settlements (H). `Tonalli G&A Expenses- December 31, 2021.xlsx` (39 MB) could not be read.
3. **2023 operating costs** — C's daily `CashFlow Tonalli` sheet carries 2023 columns but they did not render into readable totals; D covers only Jan–Jun 2024.
4. **Royalties 2020–2024** are not itemised (the 2024 CNH payment of 232,481 is an arrears settlement; the FMP monthly "cuota contractual" is the only recurring fiscal line).
5. **No P&L or balance sheet**: everything is cash-basis. Depreciation, impairments, the abandonment trust ("Abandonment Trust Fund" column in C is "$-"), and inter-company balances with JEYP/JEPH are not stated.
6. **Share sale / change of partner.** No 2022 share-purchase document; Jaguar (JEPH) appears as funder from Aug/Sep 2022 and the "Dilucion" paper starts from a 50/50 register at 31-Dec-2022 (96,117,000 shares each). The 2018 "Change of Control Fee CNH" (28,505, refunded 25,000 in 2019) is the only earlier ownership-change trace. Whether Jaguar bought Idesa's 50 % or Idesa's vehicle was renamed is **not in sheets**.
7. **Loan terms.** "Accrued interest per JOA" 121,378 on 2,070,613 for Jan–Sep 2024 implies ≈ 10–12 %/yr but the rate and the JOA clause are not quoted.
8. **TEC-12**: row exists in A (all "$-"); no TEC-12 spend anywhere through Sep-2024 (AFE in `docs/08_afe.md`, USD 1.57 M at Nov-2020 pricing).
9. **VAT balance after 2019** — the ≈ 1.2 M recoverable of Aug-2019 minus 246,854 refunded in Q4-2019 and the 700,990 forecast for 2020: whether it was recovered is not in sheets; H1-2024 shows no refunds.
10. **Column alignment in C › `CashFlow Tonalli`** (daily sheet) is approximate after rendering; its "TOTAL 2024" split (§7) should be re-read from the workbook before it goes on a slide.
11. **FX.** 2016–2019 figures are USD as booked by IFR; B is MXN; C/D convert at Banxico daily rates. No single average rate is given for any year, so MXN items in §4–§5 are left in MXN.

---

## Appendix A — 2018 and 2019 by month (USD; source A › `Monthly Summary`, rows "Total Sales Volumes (BBL)", "Revenue", "Royalties", "Operating Costs", "General and administrative", "Regulatory Costs", capital total row, "VAT, net", "Net Casflow - Tecolutla", "Contributions - Tecolutla", "Closing Cash balance")

| Month | Sales bbl | Revenue | Royalties | Opex | G&A | Regulatory | Capital | VAT net | Net cash flow | Contributions | Closing cash |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Jan-18 | - | - | - | - | (27,380) | (63,860) | (78,785) | (11,700) | (181,725) | - | 673,230 |
| Feb-18 | - | - | - | - | (66,260) | (46,180) | (113,400) | (33,840) | (259,680) | 3,700,000 | 4,113,549 |
| Mar-18 | - | - | - | - | 8,745 | (94,121) | (90,280) | (22,686) | (198,342) | - | 3,705,207 |
| Apr-18 | - | - | - | - | (650,600) | (146,120) | (278,205) | (140,890) | (1,215,815) | - | 2,489,392 |
| May-18 | - | - | - | - | 12,000 | (47,415) | (108,025) | (25,204) | (168,644) | - | 2,306,568 |
| Jun-18 | - | - | - | - | (44,830) | (65,975) | (349,610) | (60,672) | (521,087) | - | 1,785,481 |
| Jul-18 | - | - | - | - | (3,880) | (14,685) | (680,400) | (98,388) | (797,353) | - | 985,328 |
| Aug-18 | - | - | - | - | (7,580) | (43,705) | (643,425) | (83,494) | (778,204) | 1,100,000 | 1,307,124 |
| Sep-18 | 1,719.93 | 109,026 | (44,412) | (67,530) | (393,047) | (17,402) | (436,795) | (62,083) | (926,771) | - | 380,352 |
| Oct-18 | 5,053.92 | 350,813 | (151,355) | (80,000) | (43,265) | (22,002) | (327,920) | (5,393) | (555,772) | 1,000,000 | 824,580 |
| Nov-18 | 4,440.82 | 266,670 | (107,225) | (72,000) | (55,107) | (14,387) | (826,738) | (98,063) | (1,258,612) | 998,500 | 564,468 |
| Dec-18 | 4,200.00 | 194,153 | (76,458) | (68,604) | (38,545) | (95,165) | (202,127) | (19,408) | (437,533) | 200,000 | 326,935 |
| **2018** | 15,414.66 | 920,662 | (379,450) | (288,134) | (1,309,749) | (671,017) | (4,135,710) | (661,822) | (7,299,540) | 6,998,500 | 326,935 |
| Jan-19 | 3,924.90 | 183,820 | (73,407) | (68,145) | (83,655) | (19,960) | (250,053) | (25,036) | (166,541) | 200,000 | 264,869 |
| Feb-19 | 2,291.93 | 121,962 | (49,137) | (59,365) | (63,090) | (7,790) | (301,170) | (43,418) | (218,829) | 330,000 | 376,040 |
| Mar-19 | 1,810.17 | 101,875 | (42,259) | (62,812) | (55,390) | (11,700) | (619,823) | (97,506) | (537,019) | 320,000 | 159,021 |
| Apr-19 | 2,199.88 | 131,056 | (54,585) | (53,596) | (70,111) | (32,425) | (392,651) | (73,810) | (535,313) | 750,000 | 373,707 |
| May-19 | 2,400.00 | 137,772 | (57,342) | (69,117) | (39,187) | (37,500) | (236,073) | (36,893) | (361,427) | - | 12,281 |
| Jun-19 | 3,756.77 | 203,767 | (81,126) | (83,409) | (90,044) | - | (171,691) | (5,928) | (97,026) | 150,000 | 65,255 |
| Jul-19 | 4,136.05 | 226,873 | (91,345) | (81,906) | (53,975) | (15,000) | (15,692) | 14,157 | (30,989) | - | 34,266 |
| Aug-19 | 2,819.27 | 143,106 | (61,701) | (80,736) | (32,975) | - | (122,645) | (6,549) | (314,903) | 300,000 | 19,363 |
| Sep-19 | 2,588.48 | 135,678 | (54,912) | (73,034) | (30,094) | 25,000 | - | (13,601) | 164,185 | 200,000 | 383,548 |
| Oct-19 | 2,300.48 | 114,495 | (46,295) | (61,291) | (31,690) | (9,210) | (118,854) | (11,979) | 31,483 | - | 415,031 |
| Nov-19 | 2,140.65 | 109,173 | (45,311) | (70,097) | (94,927) | (520) | (43,040) | 92,479 | (137,592) | - | 277,438 |
| Dec-19 | 2,378.84 | 122,124 | (48,800) | (75,544) | (28,845) | (3,500) | (63,999) | 151,884 | 144,625 | - | 422,063 |
| **2019** | 32,747.41 | 1,731,700 | (706,221) | (839,052) | (673,984) | (112,605) | (2,335,691) | (56,198) | (2,059,346) | 2,250,000 | 422,064 |

Notes: Apr-18 G&A (650,600) and Sep-18 (393,047) are the months in which accrued consulting/insurance were settled ("Change in Accounts Payable" (466,885) and (261,532) in `Monthly Forecast`). Capital peaks Jun–Aug 2018 (TEC-10 drilling) and Oct-18 (826,738: TEC-11 mobilisation + TEC-10 completion) and Feb–Apr 2019 (TEC-11 invoices). Regulatory Sep-19 +25,000 is the CNH change-of-control fee refund. The cash trough is May–Aug 2019 (12,281 → 19,363).

## Appendix B — 2024 payment batches (C › `Payment Detail - 2024`, "Date | USD | Ex. Rate (USD-MXN) | MXN Eq")

| Date | USD | FX | MXN eq | Tagged in sheet / main content |
|---|---|---|---|---|
| 11-Jan-24 | 1,312.29 | 16.93 | 22,223.24 | GNP insurance (Oct-23 invoice), Car One |
| 17-Jan-24 | 67,204.26 | 16.90 | 1,135,637.75 | JEYP USD 58,585.66 (Dec-23 services); Consultoría Científica 121,220; ZV frac tank 23,200 |
| 24-Jan-24 | 18,427.45 | 17.11 | 315,339.74 | CRE 25,284; Consultoría Científica 150,800; Cota 100,384 (MXN) |
| 7-Feb-24 | 47,306.06 | 17.14 | 811,048.21 | SEMARNAT 778,050 MXN |
| 20-Feb-24 | 29,155.45 | 17.06 | 497,397.81 | Galaz Yamazaki (Deloitte) audit 367,773 MXN; ASEA LAU 3,569; EYS USD 5,382 |
| 1-Mar-24 | 17,780.96 | 17.10 | 303,986.80 | **ASEA Bond** (303,240 MXN) |
| 14-Mar-24 | 124,395.90 | 16.83 | 2,093,234.69 | JEYP USD 59,135.84 + 58,289.12; Sandoval, Consultora 27, AXA, Silvia López (field consumables) |
| 20-Mar-24 | 49,201.29 | 16.71 | 822,153.56 | **CNH annual administration 2024** 806,415 MXN; ZV frac tank; JEYP MXN 5,800 |
| 3-Apr-24 | 6,513.77 | 16.66 | 108,505.08 | Quálitas insurance; Tokio Marine bond premium 56,003; Edenred fuel |
| 9-Apr-24 | 13,194.51 | 16.48 | 217,390.11 | AXA, ISSA, Cota, Gallegos, SYS (field suppliers) |
| 18-Apr-24 | 18,789.15 | 17.03 | 319,889.04 | GLJ reserves evaluation USD 5,495.43 + 11,500; ZV; Car One |
| 23-Apr-24 | **442,894.00** | 17.21 | 7,623,091.53 | **CNH: Royalties USD 232,481; Block Fee MXN 717,140; Penalties MXN 303,220 + USD 150,390** |
| 24-Apr-24 | 41,820.88 | 17.12 | 716,153.30 | Govea Mercado Béjar lawyers 348,000; Consultoría Científica PPCIEM annual report 150,800; Deloitte transfer pricing 34,800; Galaz audit 150,000 |
| 13-May-24 | 117,930.71 | 16.87 | 1,989,019.35 | JEYP USD 58,842.90 + 58,400.66; travel; field consumables |
| 16-May-24 | 1,757.58 / 1,744.00 | 16.85 / 16.68 | 29,608.19 / 29,086.78 | ZV frac tank + JEYP; **FMP exploration quota April 2024** 29,828.73 MXN ("Block Fees") |
| 17-May-24 | 1,757.58 | 16.68 | 29,313.27 | |
| 22-May-24 | 13,591.13 | 16.57 | 225,161.53 | GNP employee insurance; Galaz audit 217,773 |
| 31-May-24 | **606,193.09** | 16.95 | 10,274,972.88 | **SEMARNAT "Pago Multa PPCIEM Tonalli Energía" 10,000,536 MXN** |
| 4-Jun-24 | 1,752.81 | 17.02 | 29,828.79 | FMP cuota contractual May-24 |
| 6-Jun-24 | 65,686.31 | 17.86 | 1,173,203.48 | JEYP USD 59,114.09 (May services); travel; Deloitte 57,487 |
| 13-Jun-24 | 31,503.67 | – | – | **Greenberg Traurig legal fees invoiced 11-Apr-2019, 16-May-2019 (14,539.14), 9-Oct-2019 (9,883.23); Química Apollo 3-Jun-2021 6,605.70** (USD) |
| 20-Jun-24 | 71,434.90 | 18.41 | 1,315,316.53 | JEYP USD 59,114.09; Sandoval; Car One; Edenred; ZV |
| **Total to 30-Jun-2024** | **1,791,347.75** | | **30,662,668.88** | sheet row "TOTAL TO JUNE 30, 2024" |
| 4-Jul-24 | 1,623.16 | | | FMP cuota contractual Jun-24 (29,828.70 MXN) |
| 12-Jul-24 | 82,862.13 | | | JEYP USD 53,365.30; Consultoría Científica 242,440; GH Medio Ambiente 108,750; EYS USD 6,960; Sandoval ×2; Namur 12,296 |
| 26-Jul-24 | 854.76 | | | GNP |
| **July** | **85,340.05** | | | |

Recurring 2024 lines by nature: JEYP administrative/specialised services ≈ USD 58.5 k/month (Jaguar-group service company); FMP cuota contractual MXN 29,829/month; Servicios Petroleros ZV frac-tank rental MXN 23,200/month; Consultoría Jurídica Sandoval MXN 15,467/month; Consultoría Científica PPCIEM monitoring MXN 121–242 k/quarter.

## Appendix C — 2022 BBVA MXN account by counterparty (B › `1102-001-201 (2)`, recorded GL lines Jan–Jul 2022 plus "Unrecorded entry" lines Aug–Dec 2022; MXN)

| Counterparty / tag (as in "Description") | MXN (in +, out −) | Reading |
|---|---|---|
| COBRO PEMEX (31-May, 30-Jun ×4) | +7,938,551.24 | oil sales collections (late-2021/Jan–Feb-2022 deliveries) |
| PAGO PEPE 07 (27-Jul) | +270,310.09 | last PEMEX receipt |
| COBRO DECORPI 23 (4-Mar, 11-Mar, 18-Apr) | +500,563.32 | receipts from an Idesa-group entity, nature not stated |
| COBRO IDESA (18-May) | +167,094.66 | idem |
| JAGUAR … CASH CALL TONALLI (9/15/19/20/21/23-Dec) | +1,285,400.00 | first Jaguar funding into the MXN account |
| Transfers from Banco Base ("TRASP", "Transfer from Banco Base") | (internal) | pesos obtained by selling USD on Banco Base ("CMB" credits +3,815,961 MXN Jan–Apr in the Base ledger) and moved to BBVA |
| HEPR (monthly ≈ 156–166 k) | −1,615,679.15 | monthly retainer, twelve payments; likely the regulatory-legal retainer ("Regulatory Legal Fees (Erick Hernandez)" in A) — not confirmed by the sheet |
| SAT / ISR / IMPUESTOS | −1,040,365.00 | income-tax withholdings and monthly taxes |
| IMSS / INFONAVIT / AFORE | −594,274.86 | payroll social security |
| NOMINA (Jan–Mar) | −541,978.48 | payroll |
| SERV ADM / SERV ADMON (Jan–Mar, Base ledger) | −942,925.14 | administrative-services invoices |
| KEFREN (Jan–Mar, Base ledger) | −407,661.64 | crude/water trucking (TDH), last field-operations months |
| FINIQUITO DIC22 / FINIQUITO TONALLI (15–20 Dec) | −659,860.45 | severance, five payments |
| CNH (Jul–Oct exploration tax) | −75,640.00 | ≈ 15 k/month exploration-phase tax (IAEEH) |
| Skandia Life (pension plan), Inbursa cards, Telmex, Deloitte 120,149, notary 67,661, Oro Negro 19,720, Seiico 82,346, Servicios Petroleros 46,400, Petrohaba 30,206, Mensuranda 11,136 | − | Dec-2022 wind-down items |
| Balance 31-Dec-2022 | 14,192.60 | "Agreed to December 31, 2022 Trial Balance (Jan 9, 2023)" |
