"""Pull the Tecolutla working set from the `International Frontier` shared drive.

Reads data/working_set.csv (columns: id, kind, local_dir, name, priority, notes),
downloads each file — recursing into folders — into data/raw/<local_dir>/...,
and appends a row per file to data/manifest.csv with id, path, size, modified
time, Drive md5 and a locally computed SHA256.

Authentication (one of):
  GOOGLE_APPLICATION_CREDENTIALS=/path/to/service_account.json
      Service account. It must be added as a member (Viewer) of the shared
      drive, or of the specific folders, by a drive manager.
  GDRIVE_TOKEN_JSON=/path/to/authorized_user.json
      OAuth "authorized user" token for Kevin's own Google account, produced
      once with `python src/pull_drive.py --login` using a client_secret.json
      (Desktop app) — needs a browser on the machine that runs --login.

Never syncs the whole drive: only IDs listed in working_set.csv are touched.
Files already present with a matching size and md5 are skipped (idempotent).

Usage:
  python src/pull_drive.py --dry-run          # list what would be pulled
  python src/pull_drive.py                    # pull everything in the working set
  python src/pull_drive.py --only 1RjSZUq4t8TQQWcoJJT_22gbVyufKuGH4
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
WORKING_SET = ROOT / "data" / "working_set.csv"
MANIFEST = ROOT / "data" / "manifest.csv"

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
FOLDER = "application/vnd.google-apps.folder"

# Google-native types are exported to Office formats so openpyxl/python-docx
# can read them. Everything else is downloaded byte-for-byte.
EXPORT = {
    "application/vnd.google-apps.spreadsheet": (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"),
    "application/vnd.google-apps.document": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx"),
    "application/vnd.google-apps.presentation": (
        "application/vnd.openxmlformats-officedocument.presentationml.presentation", ".pptx"),
}

MANIFEST_FIELDS = ["file_id", "path", "size_bytes", "modified_time", "drive_md5",
                   "sha256", "mime_type", "pulled_at", "source_kind", "export_note"]


def credentials():
    from google.oauth2 import service_account
    from google.oauth2.credentials import Credentials

    sa = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    tok = os.environ.get("GDRIVE_TOKEN_JSON")
    if sa:
        return service_account.Credentials.from_service_account_file(sa, scopes=SCOPES)
    if tok:
        return Credentials.from_authorized_user_file(tok, SCOPES)
    sys.exit("No credentials: set GOOGLE_APPLICATION_CREDENTIALS or GDRIVE_TOKEN_JSON "
             "(see module docstring).")


def login(client_secret: str, out: str) -> None:
    """One-time OAuth flow producing an authorized-user token file."""
    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
    creds = flow.run_local_server(port=0)
    Path(out).write_text(creds.to_json())
    print(f"token written to {out}; export GDRIVE_TOKEN_JSON={out}")


def service():
    from googleapiclient.discovery import build

    return build("drive", "v3", credentials=credentials(), cache_discovery=False)


def meta(svc, file_id: str) -> dict:
    return svc.files().get(
        fileId=file_id, supportsAllDrives=True,
        fields="id,name,mimeType,size,modifiedTime,md5Checksum,parents").execute()


def children(svc, folder_id: str):
    token = None
    while True:
        resp = svc.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            supportsAllDrives=True, includeItemsFromAllDrives=True,
            corpora="allDrives", pageSize=200, pageToken=token,
            fields="nextPageToken,files(id,name,mimeType,size,modifiedTime,md5Checksum)").execute()
        yield from resp.get("files", [])
        token = resp.get("nextPageToken")
        if not token:
            break


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def md5_of(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_name(name: str) -> str:
    return name.replace("/", "_").strip()


def download(svc, m: dict, dest: Path, dry: bool) -> dict | None:
    from googleapiclient.http import MediaIoBaseDownload

    export_note = ""
    if m["mimeType"] in EXPORT:
        export_mime, ext = EXPORT[m["mimeType"]]
        dest = dest.with_suffix(dest.suffix + ext) if not dest.suffix else dest.with_suffix(ext)
        request = svc.files().export_media(fileId=m["id"], mimeType=export_mime)
        export_note = f"exported from {m['mimeType']} as {export_mime}"
    else:
        request = svc.files().get_media(fileId=m["id"], supportsAllDrives=True)

    if dest.exists() and m.get("md5Checksum") and md5_of(dest) == m["md5Checksum"]:
        print(f"  skip (md5 match) {dest.relative_to(ROOT)}")
        return None
    print(f"  {'would pull' if dry else 'pull'} {dest.relative_to(ROOT)}  [{m.get('size', '?')} B]")
    if dry:
        return None

    dest.parent.mkdir(parents=True, exist_ok=True)
    buf = io.FileIO(dest, "wb")
    dl = MediaIoBaseDownload(buf, request, chunksize=8 << 20)
    done = False
    while not done:
        _, done = dl.next_chunk(num_retries=5)
    buf.close()

    return {
        "file_id": m["id"], "path": str(dest.relative_to(ROOT)),
        "size_bytes": dest.stat().st_size, "modified_time": m.get("modifiedTime", ""),
        "drive_md5": m.get("md5Checksum", ""), "sha256": sha256_of(dest),
        "mime_type": m["mimeType"], "pulled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_kind": "drive", "export_note": export_note,
    }


def walk(svc, file_id: str, local_dir: Path, dry: bool):
    m = meta(svc, file_id)
    if m["mimeType"] == FOLDER:
        sub = local_dir / safe_name(m["name"])
        print(f"folder {sub.relative_to(ROOT)}")
        for c in children(svc, file_id):
            if c["mimeType"] == FOLDER:
                yield from walk(svc, c["id"], sub, dry)
            else:
                row = download(svc, c, sub / safe_name(c["name"]), dry)
                if row:
                    yield row
    else:
        row = download(svc, m, local_dir / safe_name(m["name"]), dry)
        if row:
            yield row


def append_manifest(rows: list[dict]) -> None:
    new = not MANIFEST.exists()
    with MANIFEST.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="pull a single Drive ID from the working set")
    ap.add_argument("--login", nargs=2, metavar=("CLIENT_SECRET_JSON", "TOKEN_OUT"),
                    help="run the one-time OAuth flow and write a token file")
    a = ap.parse_args()
    if a.login:
        login(*a.login)
        return

    svc = service()
    with WORKING_SET.open(newline="") as f:
        items = [r for r in csv.DictReader(f) if r["id"]]
    if a.only:
        items = [r for r in items if r["id"] == a.only] or [{"id": a.only, "local_dir": "adhoc"}]

    rows: list[dict] = []
    for it in items:
        rows.extend(walk(svc, it["id"], RAW / it["local_dir"], a.dry_run))
    if rows:
        append_manifest(rows)
        print(f"{len(rows)} file(s) recorded in {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
