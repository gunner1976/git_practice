"""Decode Drive-connector download results into data/raw.

Two sources:
  1. A spooled tool-result file (large results the harness saves to disk):
       python src/ingest_toolresult.py --result <path.txt> <local_dir> [<modified_time>]
  2. The session transcript (.jsonl), for small results that came inline:
       python src/ingest_toolresult.py --transcript <path.jsonl> <file_id> <local_dir> [<modified_time>]

Both write data/raw/<local_dir>/<title> and append a manifest row (SHA256, md5,
size, Drive id, mime). Idempotent: an identical existing file is skipped.
"""
import base64, csv, hashlib, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "manifest.csv"
FIELDS = ["file_id", "path", "size_bytes", "modified_time", "drive_md5", "sha256",
          "mime_type", "pulled_at", "source_kind", "export_note"]


def manifest_ids():
    if not MANIFEST.exists():
        return {}
    with MANIFEST.open(newline="") as f:
        return {r["file_id"]: r for r in csv.DictReader(f)}


def record(payload: dict, local_dir: str, modified: str) -> str:
    raw = base64.b64decode(payload["content"])
    name = payload["title"].replace("/", "_").strip()
    dest = ROOT / "data" / "raw" / local_dir / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    sha = hashlib.sha256(raw).hexdigest()
    if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest() == sha:
        return f"skip (identical) {dest.relative_to(ROOT)}"
    dest.write_bytes(raw)
    row = {"file_id": payload["id"], "path": str(dest.relative_to(ROOT)), "size_bytes": len(raw),
           "modified_time": modified, "drive_md5": hashlib.md5(raw).hexdigest(), "sha256": sha,
           "mime_type": payload.get("mimeType", ""),
           "pulled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "source_kind": "drive-connector", "export_note": ""}
    new = not MANIFEST.exists()
    with MANIFEST.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new: w.writeheader()
        w.writerow(row)
    return f"{row['path']}  {len(raw):,} B  sha256 {sha[:12]}"


def from_result_file(path: str) -> dict:
    return json.loads(Path(path).read_text())


_INLINE, _INLINE_SRC = {}, None


def index_transcript(path: str) -> dict:
    """One pass over the transcript: id -> payload for every inline download
    result. Tool results are stored as JSON strings, so quotes are escaped."""
    global _INLINE, _INLINE_SRC
    if _INLINE_SRC == path:
        return _INLINE
    pat = re.compile(r'\{\\"content\\":\\"([A-Za-z0-9+/=]*)\\",\\"id\\":\\"([^"\\]+)\\",'
                     r'\\"mimeType\\":\\"([^"\\]*)\\",\\"title\\":\\"((?:[^"\\]|\\\\.)*?)\\"\}')
    text = Path(path).read_text(errors="ignore")
    found = {}
    for m in pat.finditer(text):
        title = m.group(4).replace('\\\\"', '"').encode().decode("unicode_escape")
        found[m.group(2)] = {"content": m.group(1), "id": m.group(2), "mimeType": m.group(3), "title": title}
    _INLINE, _INLINE_SRC = found, path
    return found


def from_transcript(path: str, file_id: str) -> dict:
    found = index_transcript(path)
    if file_id not in found:
        sys.exit(f"no inline result for {file_id} in {path}")
    return found[file_id]


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "--result":
        payload, local_dir, modified = from_result_file(a[1]), a[2], (a[3] if len(a) > 3 else "")
    elif a[0] == "--transcript":
        payload, local_dir, modified = from_transcript(a[1], a[2]), a[3], (a[4] if len(a) > 4 else "")
    else:
        sys.exit(__doc__)
    print(record(payload, local_dir, modified))
