# Shared-drive access plan

Source: Google Shared Drive `International Frontier` (owner `cascadecapture.com`, root `0AHfoefRKXj-LUk9PVA`), ~1.1 TB. Only the working set in `data/working_set.csv` is pulled — never the whole drive.

## What was verified on 2026-09-15 (read-only, nothing downloaded)

- The session's Google Drive connector (Kevin's own account) can see the shared drive: the TEC-12 Drill, Appraisal Plan, Development Plan and Geology folders list correctly with sizes and dates.
- `www.googleapis.com` is reachable from the container through the session proxy, so the Google Drive REST API works from Python.
- `rclone` is not installed and its download host is blocked by the proxy, so rclone is out for this environment.
- PyPI is reachable; the pinned stack in `requirements.txt` installed cleanly. LibreOffice 24.2 is present for headless recalculation.

## Options

**A. Google Drive API from Python, OAuth token for Kevin's account (recommended).**
Kevin creates an OAuth "Desktop app" client in a Google Cloud project he controls, runs the one-time login on his own machine (`python src/pull_drive.py --login client_secret.json token.json`), and passes the resulting `token.json` into the session as an environment variable path (`GDRIVE_TOKEN_JSON`). Scope is `drive.readonly`. No drive membership changes are needed because it is Kevin's own access. The token is never committed (`.gitignore` covers it).

**B. Google Drive API from Python, service account.**
Kevin (or a drive manager at cascadecapture.com) creates a service account and adds its email as a Viewer on the shared drive or on the four working-set folders. The key JSON is passed in as `GOOGLE_APPLICATION_CREDENTIALS`. Cleanest for repeatable pulls, but needs a drive-manager action on the cascadecapture.com side.

**C. Session Drive connector, file by file.**
The connector's download tool returns base64 which can be decoded in the container. It needs no new credentials, but it is one tool call per file with an unknown response-size ceiling, so it does not scale to the 100+ log files. It is a fallback for a handful of small files if A or B are delayed.

Either A or B drives `src/pull_drive.py`, which recurses folders, skips files already present with a matching Drive md5, exports Google-native files to Office formats, and writes `data/manifest.csv` (file ID, path, size, modified time, Drive md5, SHA256, pulled-at).

## Working-set additions beyond the kickoff list

Listing the folders surfaced files the tasks need that were not in the kickoff table. They are in `data/working_set.csv` marked "Added": the GLJ Oct-2020 and Jan-2022 price decks, the Tonalli contractual fee / exploration tax sheet, the two Simmons payout comparisons and the Durum–Simmons participation sheet (tasks 1, 2, 8), the Aug 2020 economic model and three Simmons v1–v3 workbooks in `OLD` (lineage for task 2), TEC-11 actual-versus-budget costs (task 8 escalation anchor), the TEC-2 and TEC-10 IHS pressure-transient reports (task 5), the TEC-10 core descriptions (task 9), and the Transition Plan production chapter and Spanish field summary (task 4 cross-check).

Approximate pull size: about 190 MB for the listed files (the GLJ reserves PDF, the CMI interpreted image and the Aug 2020 back-up slides account for 45 MB of that), plus the well-log folder, which has one subfolder per well (2, 3, 5, 6, 7, 9, 10, 11, 101) and is sized on pull. The 194 MB and 620 MB TEC-10 CMI DLIS files are deliberately excluded.

## Git policy for raw data

`data/raw/` is git-ignored: it holds third-party source files that are large and commercially sensitive. `data/manifest.csv` is tracked so the exact bytes used are auditable. Processed outputs, figures and docs are tracked. If Kevin prefers the raw files under version control (e.g. via Git LFS), that is a one-line change to `.gitignore`.
