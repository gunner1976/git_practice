# OCR of the scanned PDFs

Engines: Tesseract 5.3 (spa+eng, `--psm 6`) installed with apt, and RapidOCR 1.4 (PaddleOCR models on ONNX Runtime) from PyPI. Pages rendered at 300 dpi greyscale with PyMuPDF. Scripts: `src/ocr_pressure_scans.py`, `src/ocr_fluids.py`. Raw text per page and engine is kept under `data/processed/pressure/ocr/` and `data/processed/fluids/ocr/`.

## Pressure survey forms (18 PDFs, 26 pages)

`pressure_scans_ocr_check.csv` compares the OCR reading at each survey's gauge depth with the IFR transcription:

| Result | Surveys |
|---|---|
| Exact match, both engines or RapidOCR | 15 of 16 with a scan |
| Transcription error found | 9 Aug 1971 TEC-6: form 244.6 kg/cm², transcription 248.0 (the 12 Aug value). Corrected in `tecolutla_pressures.csv` (G-51) |
| OCR error caught by the transcription | 2 Dec 1964 TEC-6: RapidOCR 293.63 vs form 193.63 (1/2 confusion); confirmed by eye |
| No scan in the folder | 8 Dec 1964 TEC-2 (its row remains from the transcription) |

RapidOCR read the depth/pressure table on every form (7–15 rows each); Tesseract read the 1971–1998 typewritten forms but not the 1956–1964 carbon-copy forms. Extra facts recovered from the forms: the 2 Dec 1964 TEC-6 survey was flowing on a 3 mm choke at 9 m³/d oil, 1,100 m³/d gas, RGA 122 m³/m³ (685 scf/bbl), 3 % water; TEC-6 KB 5.67 m.

## Fluid analyses (15 PDFs, 40 pages)

| File | What OCR recovered |
|---|---|
| Intertek 26 Nov 2018, TEC-10 | 30.42 °API, 0.8734 g/cm³ at 60 °F, 1.66 % S, BS&W 0.025 % |
| Intertek 14 Dec 2018, TEC-10 | 30.78 °API, 0.8717 g/cm³, BS&W 4.0 % |
| Intertek 18 Jan 2019, TEC-10 | 30.1 °API, SG 0.8681 (20/4 °C), 1.57 % S, BS&W 0.30 % |
| Corelab Aug 2018, TEC-10 distillation | sample densities 0.8863 and 0.8916 |
| TEC-6 gas analysis 28 Aug 1970 | H2S 0.66 %, gas SG 0.730 |
| PEMEX distillation forms 1956–1975 (TEC-2, 6, 7) and the 9-page historical compilation | form headings only; the handwritten density and viscosity entries did not OCR |

None of these is a PVT study: no laboratory Rs, bubble point or Bo exists in the pulled set (G-31 updated).

## Not OCR'd

The Weatherford TEC-10 log plots (`TECOLUTLA-10_DOBLE INDUCCION…pdf`, `…POROSIDAD…pdf`) are curve images whose data already exist in the LAS files. The image-only pages of the two IHS reports are the 2018 gradient survey forms, whose numbers are in the reports' text pages.
