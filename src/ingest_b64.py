"""Write a base64 payload (from the session Drive connector) into data/raw and
record it in data/manifest.csv. Used when files arrive via the connector
rather than src/pull_drive.py.

Usage: python src/ingest_b64.py <file_id> <local_dir> <filename> <mime> <modified_time> < payload.b64
"""
import base64, csv, hashlib, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "manifest.csv"
FIELDS = ["file_id", "path", "size_bytes", "modified_time", "drive_md5", "sha256",
          "mime_type", "pulled_at", "source_kind", "export_note"]

file_id, local_dir, name, mime, modified = sys.argv[1:6]
raw = base64.b64decode(sys.stdin.read().strip())
dest = ROOT / "data" / "raw" / local_dir / name
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_bytes(raw)
row = {"file_id": file_id, "path": str(dest.relative_to(ROOT)), "size_bytes": len(raw),
       "modified_time": modified, "drive_md5": hashlib.md5(raw).hexdigest(),
       "sha256": hashlib.sha256(raw).hexdigest(), "mime_type": mime,
       "pulled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
       "source_kind": "drive-connector", "export_note": ""}
new = not MANIFEST.exists()
with MANIFEST.open("a", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    if new: w.writeheader()
    w.writerow(row)
print(f"{row['path']}  {len(raw)} B  sha256 {row['sha256'][:12]}")
