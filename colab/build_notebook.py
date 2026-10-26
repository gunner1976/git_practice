"""Build colab/tecolutla_seismic_extract.ipynb from tecolutla_extract_core.py plus the Drive driver cells.
Usage: python colab/build_notebook.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
core = (HERE / "tecolutla_extract_core.py").read_text()

MD_INTRO = """# Tecolutla: seismic and large-log extract (run in Google Colab)

This notebook reads the Tecolutla files that are too large for the Drive connector and writes small outputs to
**My Drive / For Claude / tecolutla_colab_out**, where the analysis can pick them up.

**How to run:** Runtime → Run all. When asked, allow access to your Google account (this is Google's own sign-in for
Colab; nothing is shared with anyone). It takes roughly 10–20 minutes, mostly downloads.

**What it reads (read-only):** the DMI PSDM volume `Tec_PSDM2019.zgy`, the two PEMEX PSTM cuts (554702, 554703),
`Petrel.zip` (listing only), nine large LAS/archive files and the TEC-7 drilling expediente zip.

**What it writes:** volume metadata and headers (JSON/text), a field-area sub-cube of each volume (int16, split into
parts under ~4 MB), gzip copies of the large LAS files, a quick-look image, and `manifest.json` with a SHA256 for every
source file and output. Nothing in the data room is modified.
"""

INSTALL = """%%capture
!pip -q install pyzgy segyio lasio
!apt-get -qq install -y unrar > /dev/null"""

DRIVER = r'''import io, os, json, time, hashlib, subprocess, traceback, zipfile, glob
from google.colab import auth
auth.authenticate_user()
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

drive = build("drive", "v3")
FOR_CLAUDE = "17XnC9X24OuBNkGtD8KwO_SeiDrjf0640"   # My Drive / For Claude
OUT_NAME = "tecolutla_colab_out"
WORK, OUT = "/content/work", "/content/out"
os.makedirs(WORK, exist_ok=True); os.makedirs(OUT, exist_ok=True)

q = (f"name = '{OUT_NAME}' and '{FOR_CLAUDE}' in parents and "
     "mimeType = 'application/vnd.google-apps.folder' and trashed = false")
hit = drive.files().list(q=q, fields="files(id)", supportsAllDrives=True, includeItemsFromAllDrives=True).execute()["files"]
OUT_ID = hit[0]["id"] if hit else drive.files().create(
    body={"name": OUT_NAME, "parents": [FOR_CLAUDE], "mimeType": "application/vnd.google-apps.folder"},
    fields="id", supportsAllDrives=True).execute()["id"]
print("output folder id:", OUT_ID)

MANIFEST = {"run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "sources": [], "outputs": [], "errors": []}

def download(fid, dest_dir=WORK):
    m = drive.files().get(fileId=fid, fields="id,name,size,md5Checksum,modifiedTime", supportsAllDrives=True).execute()
    dest = os.path.join(dest_dir, m["name"])
    req = drive.files().get_media(fileId=fid, supportsAllDrives=True)
    with io.FileIO(dest, "wb") as fh:
        dl, done = MediaIoBaseDownload(fh, req, chunksize=128 * 1024 * 1024), False
        while not done:
            st, done = dl.next_chunk()
            if st: print(f"  {m['name']}: {int(st.progress() * 100)} %", end="\r")
    h = hashlib.md5()
    with open(dest, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 24), b""): h.update(blk)
    md5 = h.hexdigest()
    rec = dict(id=fid, name=m["name"], size=int(m.get("size", 0)), modifiedTime=m.get("modifiedTime"),
               drive_md5=m.get("md5Checksum"), md5_ok=(md5 == m.get("md5Checksum")) if md5 else None, sha256=sha256(dest))
    MANIFEST["sources"].append(rec); print(f"  downloaded {m['name']} ({rec['size']:,} B)")
    return dest

def upload(path):
    for p in split_if_large(path):
        meta = drive.files().create(body={"name": os.path.basename(p), "parents": [OUT_ID]},
                                    media_body=MediaFileUpload(p, resumable=True), fields="id,name,size",
                                    supportsAllDrives=True).execute()
        MANIFEST["outputs"].append(dict(name=meta["name"], id=meta["id"], size=int(meta["size"]), sha256=sha256(p)))
        print("  uploaded", meta["name"], f"{int(meta['size']):,} B")

def run(label, fn):
    print(f"== {label}")
    try:
        fn()
    except Exception as e:
        MANIFEST["errors"].append(dict(step=label, error=repr(e), trace=traceback.format_exc()[-2000:]))
        print("  ERROR:", repr(e))'''

ZGY = r'''def do_zgy():
    p = download("1qdKlGUK5l9hETyrwmcy1FSbZDwmrBf7I")          # Tec_PSDM2019.zgy (710 MB)
    for f in zgy_extract(p, OUT, "psdm2019"): upload(f)
    os.remove(p)
run("PSDM ZGY", do_zgy)'''

SEGY = r'''def do_segy(fid, stem):
    def f():
        p = download(fid)
        for o in segy_extract(p, OUT, stem): upload(o)
        os.remove(p)
    return f
run("PSTM 554702 (SFSG, raw)", do_segy("1lQKERhnPRXSZakFLZdTQtqT6Ux5R_U9q", "pstm554702"))
run("PSTM 554703 (CFCG, filtered/gained)", do_segy("1AjJBD3_VS6_ACKBtBmykYBi293JcIB0D", "pstm554703"))'''

LOGS = r'''LAS_IDS = {
    "1KV6MOZabsOBQ8zzBrpUIX3uFHP-Dte19": "TEC-10 Logs.LAS (11.1 MB)",
    "1XFSRmaMqUKiV76klvATRTE0IU-7BrInA": "TEC-10 CXD propiedades mecanicas 26-04-2018 (12.4 MB)",
    "1JTheUJnv_4RJy_RWcYX0dPWk7kOIekwa": "TEC-10 OH 8750 intermedio (9.9 MB)",
    "1A16SHkKJFxlQAmqfcbYSD4tMpXVtsIjO": "TEC-11 LAS GAM_SST (14.8 MB)",
    "1GqeskvfspUq8renDGLwirnUbCDRSLT15": "TEC-11 tonalli GAM_SST 28012019 (14.8 MB)",
    "1Tae8Ed5MLxLW1jhrWkVrp29wPt1LvfJF": "TEC-6 IDWD/SCD/CCL 2007 (6.5 MB)",
}
ARCHIVES = {
    "1llYILh-8fYR2EST4U7xjSt5Dl1cI13u6": "TON_REGISTROS_TEC_10 LAS zip (8.9 MB)",
    "1CdBdw_NpGSP0rTPp-FeTh_aY-e6voqCa": "TEC-11 GAM_SST rar",
    "1XC4UrNN0Yn1t-OKQwdxWv3f6MOaz3yPQ": "TEC-11 GAM_SST rebuilt rar",
    "1GFD8njgiRes5G7eljiNtSi2796LeiRtd": "TEC-7 expediente de perforacion zip (14.3 MB)",
}
def do_las():
    for fid, label in LAS_IDS.items():
        def one(fid=fid):
            p = download(fid)
            upload(gzip_file(p, os.path.join(OUT, os.path.basename(p) + ".gz")))
            os.remove(p)
        run(label, one)
def do_archives():
    for fid, label in ARCHIVES.items():
        def one(fid=fid):
            p = download(fid); d = os.path.join(WORK, os.path.basename(p) + "_x"); os.makedirs(d, exist_ok=True)
            if p.lower().endswith(".zip"):
                zipfile.ZipFile(p).extractall(d)
            else:
                subprocess.run(["unrar", "x", "-o+", p, d + "/"], check=True, capture_output=True)
            for f in sorted(glob.glob(d + "/**/*", recursive=True)):
                if os.path.isfile(f):
                    safe = os.path.basename(p) + "__" + os.path.relpath(f, d).replace("/", "__")
                    upload(gzip_file(f, os.path.join(OUT, safe + ".gz")))
            os.remove(p)
        run(label, one)
def do_petrel():
    p = download("1cxtvuC5-2RkldobWZcCS4B2eN_blSKJy")          # Petrel.zip (17 MB): listing only
    fn = os.path.join(OUT, "petrel_zip_listing.json"); json.dump(zip_listing(p), open(fn, "w"), indent=1); upload(fn)
    os.remove(p)
run("large LAS files", do_las)
run("LAS archives and TEC-7 expediente", do_archives)
run("Petrel.zip listing", do_petrel)'''

QUICKLOOK = r'''def do_quicklook():
    import numpy as np, matplotlib.pyplot as plt
    parts = sorted(glob.glob(os.path.join(OUT, "psdm2019_cube_part*.npz")))
    if not parts: print("  no PSDM parts to plot"); return
    z = np.load(parts[len(parts) // 2]); a = z["data"].astype(np.float32) * float(z["scale"])
    il = a.shape[0] // 2; v = np.percentile(np.abs(a), 98)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(a[il].T, cmap="gray_r", vmin=-v, vmax=v, aspect="auto",
              extent=[z["crossline"][il, 0], z["crossline"][il, -1], z["z"][-1], z["z"][0]])
    ax.set_xlabel("crossline"); ax.set_ylabel("z (volume units)")
    ax.set_title(f"PSDM quick look: inline {z['inline'][il, 0]:.0f} (middle of the field window)")
    fn = os.path.join(OUT, "psdm2019_quicklook.png"); plt.tight_layout(); plt.savefig(fn, dpi=110); plt.show(); upload(fn)
run("quick look", do_quicklook)'''

FINISH = r'''fn = os.path.join(OUT, "manifest.json")
json.dump(MANIFEST, open(fn, "w"), indent=1, default=str)
drive.files().create(body={"name": "manifest.json", "parents": [OUT_ID]}, media_body=MediaFileUpload(fn),
                     supportsAllDrives=True).execute()
print(f"\nDone: {len(MANIFEST['sources'])} source files read, {len(MANIFEST['outputs'])} outputs written, "
      f"{len(MANIFEST['errors'])} errors.")
for e in MANIFEST["errors"]: print(" -", e["step"], e["error"])
print("Outputs are in My Drive / For Claude /", OUT_NAME, "- tell Claude when this has finished.")'''


def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src.splitlines(keepends=True)}


def code(src):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": src.splitlines(keepends=True)}


cells = [md(MD_INTRO), md("## 1. Install readers"), code(INSTALL),
         md("## 2. Extraction functions"), code(core),
         md("## 3. Sign in and set up the output folder"), code(DRIVER),
         md("## 4. PSDM volume (ZGY, depth)"), code(ZGY),
         md("## 5. PEMEX PSTM volumes (SEG-Y, time)"), code(SEGY),
         md("## 6. Large LAS files, archives, TEC-7 expediente, Petrel listing"), code(LOGS),
         md("## 7. Quick look"), code(QUICKLOOK),
         md("## 8. Manifest"), code(FINISH)]
nb = {"cells": cells, "metadata": {"colab": {"name": "tecolutla_seismic_extract.ipynb", "provenance": []},
                                   "kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 0}
out = HERE / "tecolutla_seismic_extract.ipynb"
out.write_text(json.dumps(nb, indent=1))
print("wrote", out.name, len(cells), "cells")
