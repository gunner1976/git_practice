# Deploying the web app

The app is a single Python process (FastAPI + uvicorn) with a SQLite file for
projects. Anything that runs a Docker container with a persistent disk works.

## Local / office machine
```bash
pip install -e ".[web]"
casingdesign serve --host 0.0.0.0 --port 8000 --db /path/to/casingdesign.db
```

## Docker (any VM)
```bash
docker build -t casingdesign .
docker run -d --name casingdesign -p 8000:8000 -v casingdesign-data:/data \
  -e APP_PASSWORD='choose-a-passphrase' casingdesign
```

## Fly.io (free-tier friendly)
```bash
fly launch --copy-config --no-deploy      # uses fly.toml; pick an app name/region
fly volumes create data --size 1          # persistent disk for the SQLite file
fly secrets set APP_PASSWORD='choose-a-passphrase'
fly deploy
```

## Railway / Render
Point the service at this repository; both detect the Dockerfile. Add a
persistent volume mounted at `/data` and set `CASINGDESIGN_DB=/data/casingdesign.db`
and `APP_PASSWORD`.

## Access control
There are no user accounts (by design, for now). `APP_PASSWORD` turns on a single
site passphrase (HTTP Basic, any user name). Without it, anyone with the URL can open
and edit every well - fine on a private network, not on the public internet.

## Backups
Everything is in the one SQLite file; copy it. Projects can also be exported as JSON
from the app.
