"""Ingest every Drive-connector download result available on this machine.

Sources: the harness spool directory (large results) and the session transcript
(inline results). Files are matched to data/working_set.csv by Drive id to get
local_dir and modified_time. Already-manifested ids are skipped. Spooled result
files are deleted after a successful ingest to reclaim disk.

Usage: python src/ingest_all.py <spool_dir> <transcript.jsonl>
"""
import csv, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest_toolresult import ROOT, manifest_ids, record  # noqa: E402

spool, transcript = Path(sys.argv[1]), Path(sys.argv[2])
ws = {r["id"]: r for r in csv.DictReader((ROOT / "data" / "working_set.csv").open(newline=""))}
idx_path = ROOT / "data" / "drive_index.csv"
if idx_path.exists():
    for r in csv.DictReader(idx_path.open(newline="")):
        ws.setdefault(r["id"], {"id": r["id"], "kind": "file", "local_dir": r["local_dir"],
                                "name": r["title"], "modified_time_observed": r["modifiedTime"]})
have = manifest_ids()
done, unknown = 0, []

for f in sorted(spool.glob("mcp-Google_Drive-download_file_content-*.txt")):
    try:
        payload = json.loads(f.read_text())
    except Exception as e:
        print(f"unreadable spool {f.name}: {e}"); continue
    fid = payload.get("id")
    if fid in have:
        f.unlink(); continue
    meta = ws.get(fid)
    if not meta:
        unknown.append((fid, payload.get("title"))); continue
    print(record(payload, meta["local_dir"], meta["modified_time_observed"]))
    have[fid] = True; done += 1
    f.unlink()

# inline results: one indexing pass over the transcript
from ingest_toolresult import index_transcript  # noqa: E402
for fid, payload in index_transcript(str(transcript)).items():
    if fid in have:
        continue
    meta = ws.get(fid)
    if not meta:
        unknown.append((fid, payload.get("title"))); continue
    print(record(payload, meta["local_dir"], meta["modified_time_observed"]))
    have[fid] = True; done += 1

print(f"\n{done} file(s) ingested this run; {len(have)} in manifest")
for fid, title in unknown:
    print(f"NOT IN WORKING SET (left in spool): {fid} {title}")
