"""Render the script as HTML and save it as a Google Doc in Drive."""
from __future__ import annotations

import html
import io
import json
import os
from datetime import date
from zoneinfo import ZoneInfo

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from .writer import Script

SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER_MIME = "application/vnd.google-apps.folder"
DOC_MIME = "application/vnd.google-apps.document"


def load_credentials():
    """Credentials from the environment.

    - GOOGLE_OAUTH_REFRESH_TOKEN (+ CLIENT_ID / CLIENT_SECRET): act as a real
      user. Required for personal @gmail.com Drives, because service accounts
      have no storage quota of their own.
    - GOOGLE_SERVICE_ACCOUNT_JSON (key contents) or GOOGLE_APPLICATION_CREDENTIALS
      (key path): service account. Works with a Shared Drive folder, or with
      Workspace domain-wide delegation via GOOGLE_IMPERSONATE_USER.
    """
    if os.environ.get("GOOGLE_OAUTH_REFRESH_TOKEN"):
        from google.oauth2.credentials import Credentials

        return Credentials(
            token=None,
            refresh_token=os.environ["GOOGLE_OAUTH_REFRESH_TOKEN"],
            client_id=os.environ["GOOGLE_OAUTH_CLIENT_ID"],
            client_secret=os.environ["GOOGLE_OAUTH_CLIENT_SECRET"],
            token_uri="https://oauth2.googleapis.com/token",
            scopes=SCOPES,
        )

    from google.oauth2 import service_account

    if raw := os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"):
        creds = service_account.Credentials.from_service_account_info(json.loads(raw), scopes=SCOPES)
    elif path := os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        creds = service_account.Credentials.from_service_account_file(path, scopes=SCOPES)
    else:
        raise RuntimeError(
            "No Google credentials: set GOOGLE_SERVICE_ACCOUNT_JSON, "
            "GOOGLE_APPLICATION_CREDENTIALS, or the GOOGLE_OAUTH_* variables"
        )
    if subject := os.environ.get("GOOGLE_IMPERSONATE_USER"):
        creds = creds.with_subject(subject)
    return creds


def drive_service():
    return build("drive", "v3", credentials=load_credentials(), cache_discovery=False)


def find_folder(drive, name: str) -> str:
    if folder_id := os.environ.get("DRIVE_FOLDER_ID"):
        return folder_id
    escaped = name.replace("\\", "\\\\").replace("'", "\\'")
    result = drive.files().list(
        q=f"name = '{escaped}' and mimeType = '{FOLDER_MIME}' and trashed = false",
        fields="files(id, name)",
        corpora="allDrives",
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        pageSize=10,
    ).execute()
    files = result.get("files", [])
    if not files:
        raise RuntimeError(
            f"Drive folder {name!r} not found. Create it and share it with the "
            "service account's email as Editor (or set DRIVE_FOLDER_ID)."
        )
    if len(files) > 1:
        raise RuntimeError(
            f"{len(files)} folders named {name!r} are visible; set DRIVE_FOLDER_ID to pick one: "
            + ", ".join(f["id"] for f in files)
        )
    return files[0]["id"]


def render_html(script: Script, run_date: date, tz: str) -> str:
    e = html.escape

    def when(story) -> str:
        return story.published.astimezone(ZoneInfo(tz)).strftime("%b %d, %I:%M %p %Z")

    roundup = "".join(
        f"<li><p>{e(r.line)}</p>"
        f'<p style="color:#666">Source: <a href="{e(r.story.url)}">{e(r.story.title)}</a>'
        f" ({e(r.story.source)})</p></li>"
        for r in script.roundup
    )
    sources = "".join(
        f'<li><a href="{e(r.story.url)}">{e(r.story.title)}</a> - {e(r.story.source)}, '
        f"{e(when(r.story))}<br><i>Why it made the cut:</i> {e(r.why)}</li>"
        for r in script.roundup
    )
    return f"""<html><head><meta charset="utf-8"></head><body>
<h1>{e(script.episode_title)}</h1>
<p><b>Date:</b> {run_date.isoformat()} &nbsp; <b>Words:</b> {script.word_count}
 &nbsp; <b>Est. runtime:</b> ~{script.est_seconds}s</p>
<h2>Hook</h2><p>{e(script.hook)}</p>
<h2>Roundup</h2><ol>{roundup}</ol>
<h2>The Take</h2><p>{e(script.take)}</p>
<p style="color:#666">On: <a href="{e(script.take_story.url)}">{e(script.take_story.title)}</a></p>
<h2>Sign-off</h2><p>{e(script.signoff)}</p>
<hr><h2>Sources</h2><ol>{sources}</ol>
</body></html>"""


def create_doc(drive, folder_id: str, title: str, body_html: str) -> tuple[str, str]:
    media = MediaIoBaseUpload(io.BytesIO(body_html.encode("utf-8")), mimetype="text/html", resumable=False)
    created = drive.files().create(
        body={"name": title, "mimeType": DOC_MIME, "parents": [folder_id]},
        media_body=media,
        fields="id, webViewLink",
        supportsAllDrives=True,
    ).execute()
    return created["id"], created["webViewLink"]
