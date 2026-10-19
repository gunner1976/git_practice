# AI Channel Script Bot

Every morning at 6:00 a.m. America/Edmonton time, this bot:

1. Fetches the RSS/Atom feeds listed in [`config.yaml`](config.yaml) and keeps entries published in the last 24 hours.
2. Drops stories already used in earlier episodes (tracked in SQLite at `data/stories.db`) and duplicates across feeds.
3. Asks Claude (`claude-opus-5-5`) to rank the top 5 AI stories and write a ~90-second YouTube script with a **hook**, a **roundup**, **one opinionated take**, and a **self-aware AI-host sign-off**.
4. Saves the script as a Google Doc named `AI Daily Script - YYYY-MM-DD` in the Drive folder **AI Channel Scripts**. The doc includes a source link for every story and a one-line reason each one was picked.
5. Records the stories it used, so they aren't repeated.

```
scriptbot/
  feeds.py     fetch + 24h filter + dedupe
  store.py     SQLite: used_stories, runs (one script per local day)
  writer.py    Claude ranking + script (structured JSON output, validated)
  gdoc.py      HTML render -> Google Doc via the Drive API
  __main__.py  CLI
.github/workflows/daily-script.yml   cron schedule
```

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
export ANTHROPIC_API_KEY=sk-ant-...
export GOOGLE_APPLICATION_CREDENTIALS=$PWD/service-account.json   # see below

python -m scriptbot --dry-run   # print the script; no Drive, no DB writes
python -m scriptbot             # create today's Google Doc
python -m scriptbot --force     # write another one even if today's exists
pytest                          # offline unit tests
```

## Google setup

### 1. Create the service account

1. Open <https://console.cloud.google.com/> and create a project (or pick an existing one).
2. **APIs & Services → Library**: enable the **Google Drive API**. The Docs API isn't needed, because the bot uploads HTML and Drive converts it into a Google Doc.
3. **IAM & Admin → Service Accounts → Create service account**. Give it a name such as `ai-script-bot`. It doesn't need any project roles, so skip that step.
4. Open the new account, go to **Keys → Add key → Create new key → JSON**, and download the file. Treat it like a password. `.gitignore` already blocks `*service-account*.json` and `credentials*.json`.
5. Copy the account's email address (`ai-script-bot@<project>.iam.gserviceaccount.com`).

### 2. Give it somewhere to write

Service accounts have **no Drive storage of their own**. If the bot creates a file in a regular "My Drive" folder, the file is owned by the service account and the upload fails with `403 storageQuotaExceeded`. Choose the option that fits your account:

| Your account | What to do |
|---|---|
| **Google Workspace with Shared Drives** (recommended) | Create a Shared Drive and a folder in it called **AI Channel Scripts**. Add the service account's email to the Shared Drive as a **Content manager**. |
| **Google Workspace, no Shared Drives** | Set up domain-wide delegation: in Admin console → Security → API controls → Domain-wide delegation, add the service account's *Client ID* with the scope `https://www.googleapis.com/auth/drive`. Then set `GOOGLE_IMPERSONATE_USER=you@yourdomain.com`. Docs will be owned by that user. Create **AI Channel Scripts** in that user's Drive. |
| **Personal @gmail.com** | Service accounts can't own files here, so use OAuth as yourself (see below). |

**OAuth mode for personal Gmail accounts:**

1. In the same Cloud project, go to **APIs & Services → OAuth consent screen**. Choose *External* and add yourself as a user. Then click **Publish app**. While the app stays in "Testing" status, its refresh tokens expire after 7 days. An unverified app you only use yourself is fine to publish: you'll just click through a warning when you sign in.
2. Go to **Credentials → Create credentials → OAuth client ID → Desktop app** and download the JSON.
3. On your own computer, run:
   ```bash
   pip install google-auth-oauthlib
   python tools/get_refresh_token.py ~/Downloads/client_secret_*.json
   ```
4. Store the three values it prints as GitHub secrets: `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, and `GOOGLE_OAUTH_REFRESH_TOKEN`. When these are set, the bot uses them instead of the service account.

### 3. Point at the folder (optional, recommended)

The bot looks the folder up by name. If more than one folder with that name is visible, it stops and lists their IDs. To skip the lookup, open the folder in Drive and copy the ID from the URL (`drive.google.com/drive/folders/<ID>`). Set it as `DRIVE_FOLDER_ID`.

## GitHub Actions setup

1. Push this repository to GitHub. Scheduled workflows run **only from the default branch**, so merge to it.
2. In **Settings → Secrets and variables → Actions**, add these:
   - **Secrets**
     - `ANTHROPIC_API_KEY`
     - `GOOGLE_SERVICE_ACCOUNT_JSON`: paste the entire JSON key file. Or use the three `GOOGLE_OAUTH_*` secrets instead.
   - **Variables** (optional)
     - `DRIVE_FOLDER_ID`
     - `GOOGLE_IMPERSONATE_USER`
3. The workflow commits `data/stories.db` back to the repository after each run, because Actions runners start empty and this is how the bot remembers used stories. The workflow asks for `contents: write`. If your default branch is protected, allow `github-actions[bot]` to push to it.
4. To test, go to **Actions → Daily AI script → Run workflow**. Tick *force* to write a script even if today's already exists.

### The 6 a.m. Edmonton schedule

GitHub cron runs in UTC only, and Edmonton switches between MST (UTC-7) and MDT (UTC-6). The workflow therefore runs twice:

| UTC trigger | Summer (MDT) | Winter (MST) |
|---|---|---|
| `0 12 * * *` | 06:00 local → **writes the script** | 05:00 local → skipped (`--not-before-hour 6`) |
| `0 13 * * *` | 07:00 local → skipped (already done today) | 06:00 local → **writes the script** |

The once-per-day check uses the `runs` table, keyed by the Edmonton date. That means a run GitHub starts late (scheduled jobs are often delayed 5–30 minutes) still produces exactly one doc per day.

GitHub also turns off scheduled workflows after 60 days with no repository activity. The daily database commit counts as activity, so the schedule stays on.

## Tuning

Everything is in `config.yaml`:

- `feeds`: the RSS/Atom feeds to read.
- `lookback_hours`: how far back to look for stories.
- `top_n`: how many stories go in the roundup.
- `max_candidates` / `max_summary_chars`: how much feed text is sent to Claude.
- `recent_history_days`: how many days of recently used titles are shown to Claude. This lets it skip follow-ups about the same event, even when the follow-up has a different URL.
- `anthropic.model` / `anthropic.effort`: the Claude model and effort level.

The prompt and output schema are in `scriptbot/writer.py`. The model can only refer to stories by the IDs it was given, so every link in the doc comes straight from the feed and can't be made up.

If Claude's safety classifier declines a request by mistake, the request is retried on a fallback model chosen by Anthropic (`fallbacks: "default"`). To turn this off, remove `betas`/`fallbacks` in `writer.py`.
