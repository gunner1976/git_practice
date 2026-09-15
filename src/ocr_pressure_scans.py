"""OCR the 18 PEMEX bottom-hole pressure survey scans (pressures/*.pdf) with two engines (Tesseract 5 and RapidOCR),
parse the depth/pressure tables, and compare against the IFR transcription used in task 5.
Usage: python src/ocr_pressure_scans.py
Outputs: data/processed/pressure/ocr/<file>.<engine>.txt (raw text), pressure_scans_ocr_rows.csv (every depth/pressure row read),
         pressure_scans_ocr_check.csv (reading at the survey's gauge depth vs the transcription), summary printed.
"""
import glob, os, re, json, numpy as np, pandas as pd, pymupdf, pytesseract
from PIL import Image
from rapidocr_onnxruntime import RapidOCR
OUT = "data/processed/pressure/ocr/"; KPA = 98.0665
rapid = RapidOCR()
def render(pdf, dpi=300):
    doc = pymupdf.open(pdf)
    for i, p in enumerate(doc):
        pix = p.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
        yield i + 1, Image.frombytes("L", (pix.width, pix.height), pix.samples)
def ocr_tess(img): return pytesseract.image_to_string(img, lang="spa+eng" if "spa" in pytesseract.get_languages() else "eng", config="--psm 6")
def ocr_rapid(img):
    res, _ = rapid(np.array(img.convert("RGB")))
    if not res: return ""
    # sort boxes top-to-bottom, left-to-right into lines
    items = sorted(((b[0][1], b[0][0], t) for b, t, _ in res))
    lines, cur, y0 = [], [], None
    for y, x, t in items:
        if y0 is None or abs(y - y0) < 18: cur.append((x, t)); y0 = y if y0 is None else y0
        else: lines.append(" ".join(t for _, t in sorted(cur))); cur = [(x, t)]; y0 = y
    if cur: lines.append(" ".join(t for _, t in sorted(cur)))
    return "\n".join(lines)
row_re = re.compile(r"(?<![\d.])(\d{1,4})[\s,]+(\d{2,3}[.,]\d{1,3})\b")   # depth m, pressure kg/cm2
rows, texts = [], {}
for pdf in sorted(glob.glob("data/raw/pressures/*.pdf")):
    name = os.path.basename(pdf)
    for page, img in render(pdf):
        for eng, fn in [("tesseract", ocr_tess), ("rapidocr", ocr_rapid)]:
            txt = fn(img); texts[(name, page, eng)] = txt
            open(OUT + f"{name[:-4]}.p{page}.{eng}.txt", "w").write(txt)
            for m in row_re.finditer(txt.replace(",", ".")):
                depth, pres = int(m.group(1)), float(m.group(2))
                if 0 <= depth <= 3000 and 30 <= pres <= 300: rows.append(dict(file=name, page=page, engine=eng, depth_m=depth, pressure_kgcm2=pres, line=txt[max(0, m.start() - 5):m.end() + 40].replace("\n", " | ")))
    print("done", name)
rows = pd.DataFrame(rows); rows.to_csv(OUT + "pressure_scans_ocr_rows.csv", index=False)
# compare with the task-5 dataset at each survey's gauge depth
p = pd.read_csv("data/processed/pressure/tecolutla_pressures.csv", parse_dates=["date"])
p = p[p.source.str.contains("Pressure Summary")]
MONTH = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
check = []
for r in p.itertuples():
    fname = f"Tecolutla-{r.well.split('-')[1]} Static Gradient {MONTH[r.date.month]} {r.date.day}, {r.date.year}.pdf"
    sub = rows[rows.file == fname]
    rec = dict(date=r.date.date(), well=r.well, scan=fname if os.path.exists("data/raw/pressures/" + fname) else "no scan (2018 xlsx)", gauge_depth_mkb=r.gauge_depth_mkb, transcription_kgcm2=round(r.p_gauge_kpa / KPA, 2))
    for eng in ["tesseract", "rapidocr"]:
        s = sub[sub.engine == eng]
        if len(s):
            s = s.assign(dd=(s.depth_m - r.gauge_depth_mkb).abs()).sort_values("dd")
            best = s.iloc[0]; rec[f"{eng}_depth"] = best.depth_m; rec[f"{eng}_kgcm2"] = best.pressure_kgcm2; rec[f"{eng}_diff_kgcm2"] = round(best.pressure_kgcm2 - rec["transcription_kgcm2"], 2)
            rec[f"{eng}_rows_read"] = len(s)
        else: rec[f"{eng}_rows_read"] = 0
    check.append(rec)
check = pd.DataFrame(check); check.to_csv(OUT + "pressure_scans_ocr_check.csv", index=False)
pd.set_option("display.width", 250); print(check.to_string())
print("rows read per file/engine:"); print(rows.groupby(["file", "engine"]).size().unstack(fill_value=0).to_string())
