"""Build data/drive_index.csv from every Drive listing captured in the session
transcript, and resolve each file to a local_dir via a folder map.

The index (id, title, mimeType, size, modifiedTime, parentId, local_dir) is the
audit trail of what was seen on the drive, and lets ingest_all.py place any
downloaded file without a hand-written working-set row.
"""
import csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = {  # drive folder id -> local_dir under data/raw
    "1B5CHFmwGiT4el8V36QKSEJXP5Algn1R-": "tec12_drill",
    "1FuTAXvbpJvxgpoMkHGHOzA8nU6XgX9q8": "tec12_drill/OLD",
    "1c-Idpc_CVfENHfofzJj_kjwK0oT3L54v": "appraisal_plan",
    "19Fm-3SA5OC3d882LiW9hOQKlaYyt4_FL": "development_plan",
    "1N2kdjYLVGfIi_Bxt2dJtRGMlddUGu3XG": "tec12_budget_2021",
    "18Khse1aIWHA4vKMFN0-r_siVXhdLuHhV": "ye2020_reserves",
    "1V_Su_OpLDovMckw5r1A62FxBv-dImWP0": "staff_production",
    "1Mf6YKGl4SoXGOmH3Gbs3Qdgb64Ongk6i": "geology",
    "1Utf__mkt3m3KPT-3J0ZnFcAH_5VwiHRZ": "geology/Tecolutla Well header Information",
    "1b7dINYCGMxcc4o4L7IfiK6tCVPfvyGOK": "geology/Directional Survey",
    "1eS4NV3LT1NF-Hcwjz31owwkv34LTxnI6": "geology/Tecolutla Perforations",
    "1BbEeSgFaxmNewRXhAbOLWa0mYozlRCsM": "geology/Tec-11 DES Sample Descriptions",
    "1dxjw4IG13Fq6kTP8i5HkkGrQHD0aZkrM": "geology/Tecolutla-10 Core and Sample Descriptions",
    "1vlxt0ZJTudEHR9fV7d5GQjpd2xmxG5Lm": "geology/Tecolutla-10 Core and Sample Descriptions/Sample Descriptions",
    "1447LuczmcXdIO1qiT_NIZesLzmfSdC7L": "geology/Tecolutla-10 Core and Sample Descriptions/Core",
    "1MUV4h1iC9cz2zYYUkqu2jyCdB9Oa2bGu": "geology/Tecolutla Well Logs",
    "1a0AaiQMc00Fy5tkcIClRMz5D6JANZGua": "geology/Tecolutla Well Logs/Tecolutla 10",
    "1ujDfBK2soBVxCFX4u-8yk_B4cBIabOMX": "geology/Tecolutla Well Logs/Tecolutla 10/Final Images and Logs",
    "1enIT7tkiG6sbDkTJlWcE7GjrX2XLuB65": "petrophysics",
    "1MQWVxLrO9wWSE4GzdwnrzITym9S38a6r": "petrophysics/LAS",
    "1FivwQDgxkzEufcVJj42AUUValzaPLKyC": "pressures",
    "1-UPYArMlR1TW4m5xg5NdSArwLoGF1jJ0": "pressures/TEC-2_Pressure_Data_Flow_and_Build_2018",
    "1E4f1NeV8pqDDuOV1h073jIbhctbPTN1R": "fluid_analyses",
    "1050EwgEhR2nWTNRqZkpR9BEjylEwlPSd": "tec12_regulatory",
    "1Wj7NZdAcQitn5QbUEVcA8CrM7YKjEym-": "tec12_regulatory",
    "1d8iIb0ZNuYWHxq9L_xsEKq8nzoCJOB_B": "tec12_regulatory",
    "1nedpANNYEF1dPIEMoqF8jHxYSqEWoRvz": "geology/tec10_image_log",
    "1983QlWcFm20lfPCMzz6HDzG7YoSZnQ-u": "geology/tec10_image_log",
    "1vbgBnsSv6HpB_dp9KF9IqK0ku93uAQXg": "geology/tec10_image_log",
    "1Hjmp0xd63M3uM-17ze86XTphOgJnJzy6": "geology/tec10_image_log",
    "1Az0EnFwFu8MRHtWtxcMVQkrk0h0wlaTS": "drilling_costs",
    "1cJi7ZgF5iE02zMCWXGUCe3_4BiRVhYyp": "tec11",
    "1vYsMBoGKAnKCcDjCFVbvGrD3oU0aKRFW": "tec12_2020",
    "1tENlBoFStG1POv6gssUZoxKu1bZOZml8": "tec12_2020",
}
FOLDER_NAMES = {}

transcript = Path(sys.argv[1]).read_text(errors="ignore")
# every file object seen in a search/metadata result, escaped inside the transcript JSON
pat = re.compile(r'\\"canAddChildren\\":(true|false),(.*?)\\"viewUrl\\"')
seen = {}
for m in pat.finditer(transcript):
    body = m.group(2).replace('\\"', '"')
    d = {}
    for k in ("id", "title", "mimeType", "fileSize", "modifiedTime", "parentId"):
        mm = re.search(r'"%s":"((?:[^"\\]|\\.)*)"' % k, body)
        d[k] = mm.group(1) if mm else ""
    if d["id"]:
        d["isFolder"] = m.group(1) == "true"
        seen[d["id"]] = d
for d in seen.values():
    if d["isFolder"]:
        FOLDER_NAMES[d["id"]] = d["title"]

def local_dir(fid):
    p = seen.get(fid, {}).get("parentId", "")
    if p in FOLDERS:
        return FOLDERS[p]
    if p in seen and seen[p].get("parentId") in FOLDERS:
        return FOLDERS[seen[p]["parentId"]] + "/" + seen[p]["title"]
    return "unsorted/" + FOLDER_NAMES.get(p, p)

out = ROOT / "data" / "drive_index.csv"
with out.open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "title", "mimeType", "size_bytes", "modifiedTime", "parentId", "parent_title", "local_dir"])
    for d in sorted(seen.values(), key=lambda x: (x["parentId"], x["title"])):
        if d["isFolder"]:
            continue
        w.writerow([d["id"], d["title"], d["mimeType"], d["fileSize"], d["modifiedTime"], d["parentId"],
                    FOLDER_NAMES.get(d["parentId"], ""), local_dir(d["id"])])
print(f"{sum(not d['isFolder'] for d in seen.values())} files, {sum(d['isFolder'] for d in seen.values())} folders indexed -> {out.relative_to(ROOT)}")
