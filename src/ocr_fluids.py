"""OCR the image-only fluid-analysis PDFs (fluid_analyses/*.pdf without a text layer) with RapidOCR and Tesseract (spa+eng),
save the text, and pull out the PVT-relevant numbers (API gravity, density, GOR/RGA, bubble point, viscosity).
Usage: python src/ocr_fluids.py
Outputs: data/processed/fluids/ocr/<file>.p<page>.<engine>.txt, fluid_ocr_hits.csv
"""
import glob, os, re, numpy as np, pandas as pd, pymupdf, pytesseract
from PIL import Image
from rapidocr_onnxruntime import RapidOCR
OUT = "data/processed/fluids/ocr/"; rapid = RapidOCR()
def render(pdf, dpi=300):
    for i, p in enumerate(pymupdf.open(pdf)):
        pix = p.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY); yield i + 1, Image.frombytes("L", (pix.width, pix.height), pix.samples)
def ocr_rapid(img):
    res, _ = rapid(np.array(img.convert("RGB")))
    if not res: return ""
    items = sorted(((b[0][1], b[0][0], t) for b, t, _ in res)); lines, cur, y0 = [], [], None
    for y, x, t in items:
        if y0 is None or abs(y - y0) < 18: cur.append((x, t)); y0 = y if y0 is None else y0
        else: lines.append(" ".join(t for _, t in sorted(cur))); cur = [(x, t)]; y0 = y
    if cur: lines.append(" ".join(t for _, t in sorted(cur)))
    return "\n".join(lines)
KEYS = re.compile(r"(API|gravedad|densidad|density|RGA|R\.?G\.?A|GOR|gas.?oil|solution|saturaci[oó]n|bubble|burbuja|Pb\b|viscosi|azufre|sulf|sulphur|agua|water|BS&W|salinid|cloruros|chloride)", re.I)
hits, pages = [], 0
for pdf in sorted(glob.glob("data/raw/fluid_analyses/*.pdf")):
    d = pymupdf.open(pdf)
    if sum(1 for p in d if len(p.get_text().strip()) > 50) == len(d): continue   # has a text layer already
    name = os.path.basename(pdf)
    for page, img in render(pdf):
        pages += 1
        for eng, txt in [("rapidocr", ocr_rapid(img)), ("tesseract", pytesseract.image_to_string(img, lang="spa+eng", config="--psm 6"))]:
            open(OUT + f"{name[:-4]}.p{page}.{eng}.txt", "w").write(txt)
            for line in txt.splitlines():
                if KEYS.search(line) and re.search(r"\d", line): hits.append(dict(file=name, page=page, engine=eng, line=line.strip()[:160]))
    print("done", name, len(d), "pages")
pd.DataFrame(hits).to_csv(OUT + "fluid_ocr_hits.csv", index=False); print("pages OCR'd", pages, "hit lines", len(hits))
