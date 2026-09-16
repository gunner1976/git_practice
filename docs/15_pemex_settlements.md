# 15. Realised crude price from the PEMEX settlements (G-24 resolved)

Kevin pointed to the PEMEX settlements. They are on the Drive as one "Comprobante de Entrega-Recepción" PDF per month from Pemex Exploración y Producción's Gerencia de Comercialización de Hidrocarburos, January 2020 to December 2022 (35 comprobantes; July 2022 is absent), plus two Tonalli CFDI invoices to PEP (Dec 2019, Jan 2023). All were read through the connector, transcribed to `data/processed/drive_text/PEMEX_Delivery-Reception_settlements_2020-2022.csv` with the Drive id of each PDF, and processed by `src/pemex_settlements.py` against the WTI, Brent and LLS monthly history in Kevin's price file (`Oil_Price_History_WTI_monthly_2018-2023.csv`). Outputs: `data/processed/price/pemex_settlements_monthly.csv`, `pemex_settlements_summary.json`, `figures/17_realised_price.png`.

## 1. How PEMEX prices the crude

Every comprobante applies the same arithmetic, in USD/bbl:

realised (precio de compra) = reference (precio de venta) × C − tarifa PEP − tarifa PL − tarifa TRI − margen comercial

- **Reference price** is PEMEX's monthly crude reference for the delivery point. Tonalli's own `Tecolutla Field Price Determination.xlsx` (Nov 2018 and Nov 2022 sheets) writes it as Pref = (0.4·WTS + 0.4·LLS + 0.2·Brent + K) × 0.9965 with K = 6.50 (Isthmus USGC adjustment) and cites the PMI formula documents. Against the WTI history the comprobante reference ran at 0.91–1.13 × WTI, median 0.97.
- **C, the "constante de rendimiento"**, is the crude-quality constant: 0.916 in 2020 falling to 0.896–0.909 through 2021–22 as delivered API drifted between 25.7 and 30.9 and sulphur sat at 1.5–1.9 %.
- **Fixed deductions**: tarifa PEP 0.59 USD/bbl to 18 Mar 2021 and 0.51 after (Comité de Precios acuerdo 2021-069), tarifa PL 2.20 (gathering/transport/treatment), tarifa TRI 0, and a marketing margin of 3 % of the reference price (1.0–3.4 USD/bbl). Together 3.8–5.3 USD/bbl.
- **Ajuste comercial**: a separate delivery-programme penalty (deliveries outside ±10 % of the programmed 175–180 bbl/d truck loads at 5 % of value) totalled USD 8,314 over the eleven months that carry the page, i.e. 0.5 % of revenue.

## 2. What was realised

| Year | Delivered, bbl | Revenue, USD | Realised, USD/bbl | WTI (volume-weighted) | Realised ÷ WTI | API | S % |
|---|---|---|---|---|---|---|---|
| 2020 | 19,041 | 681,874 | 35.81 | 43.95 | 0.81 | 29.2 | 1.62 |
| 2021 | 17,546 | 939,419 | 53.54 | 66.13 | 0.81 | 29.3 | 1.64 |
| 2022 | 2,740 | 178,032 | 64.97 | 82.34 | 0.79 | 28.5 | 1.72 |
| 2020–22 | 39,327 | 1,799,325 | 45.75 | 56.53 | **0.81** | | |

Monthly realised ÷ WTI has a median of 0.80 and a P10–P90 of 0.77–0.84. The December 2019 invoice (51.34 USD/bbl against WTI 59.86, 0.86) and the January 2023 invoice (57.33 against 78.16, 0.73) sit at the ends of the same band. The delivered volumes match the PEMEX-statement rows in the tracking workbook and the 2021 CNH filing to within 1 %; there were no deliveries in April–June 2020 and March–October 2022.

## 3. What this means for the models

| Model | PEMEX factor used | Against the measured 0.81 |
|---|---|---|
| Aug 2020 IFR model | 0.95 | overstates net price by 17 % |
| Feb 2022 IFR models (all nine) | 0.801 | correct: this is the measured value |
| 2023 IFR model, GLJ YE2020 (88.4 % of Brent ≈ 0.94 × WTI) and the task-10 rebuild | 0.90 | overstates by 11 % |

The task-10 economics were rerun at 0.81 (`src/econ_rebuild.py`, rows with `price_factor 0.81` in `data/processed/econ_rebuild/cases.csv`). NPV10 before tax, USD MM, base capex:

| WTI | 50 | 60 | 70 | 80 | 90 | 100 |
|---|---|---|---|---|---|---|
| stand-alone, base profile | −1.36 | −0.92 | −0.46 | +0.02 | +0.51 | +1.00 |
| incremental to a producing TEC-10, base profile | −0.90 | −0.34 | +0.27 | +0.89 | +1.48 | +2.04 |
| stand-alone, high profile | −0.99 | −0.39 | +0.25 | +0.92 | +1.61 | +2.32 |
| incremental, high profile | −0.49 | +0.27 | +1.15 | +2.00 | +2.81 | +3.59 |

Compared with the 0.90 case in `docs/10_econ_rebuild.md`: the stand-alone base case now breaks even at WTI 80 rather than 72, and the incremental base case at WTI 65 rather than 59 (+0.27 MM at 70 instead of +0.76). The low profile is negative in every case. The conclusion of task 10 stands and hardens: TEC-12 is an incremental well on a producing pad or it is not a well, and the realised price is one of the two reasons the stand-alone case does not work at today's long-dated prices.

## 4. Two things the settlements also settle

- **Oil quality at the point of sale**: 28–31 °API and 1.5–1.9 % sulphur in every month, consistent with the Intertek stock-tank analyses (task 11) and the CNH filings; PEMEX's C reflects a 28 °API, 1 % S basis and the quality penalty is inside the 0.81.
- **The 2020 net-oil question (G-53)**: PEMEX settled 19,041 bbl for 2020 against 18,973 bbl in the CNH filing's monthly column and 19,092 bbl on the tickets. The filing's 16,132 bbl "net" is therefore not what PEMEX paid for and can be set aside as an accounting artefact of that form.

## 5. Not yet on the Drive

The June 2022 and later comprobantes for July 2022, and any 2023 settlements beyond the January invoice, are not present; the CRE semi-annual sales report annexes are still acknowledgement receipts only. Neither changes the factor.
