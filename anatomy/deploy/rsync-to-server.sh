#!/usr/bin/env bash
# Build the explorer and copy the static bundle to a server over SSH (rsync).
#
#   DEPLOY_HOST=gunninginc.click DEPLOY_USER=sovereign DEPLOY_DEST=/var/www/anatomy ./rsync-to-server.sh
#
# The bundle is fully static (HTML, JS, glTF, WebP, EXR) and relocatable: it works at
# https://gunninginc.click/anatomy/ or at https://anatomy.gunninginc.click/ without rebuilding.
set -euo pipefail
HOST="${DEPLOY_HOST:?set DEPLOY_HOST}"
USER_="${DEPLOY_USER:-sovereign}"
DEST="${DEPLOY_DEST:-/var/www/anatomy}"
HERE="$(cd "$(dirname "$0")" && pwd)"
WEB="$HERE/../web"
( cd "$WEB" && npm ci --no-audit --no-fund && npm run build )
ssh "$USER_@$HOST" "mkdir -p '$DEST'"
rsync -az --delete --info=progress2 "$WEB/dist/" "$USER_@$HOST:$DEST/"
echo "deployed to $USER_@$HOST:$DEST — now include nginx-anatomy.conf or Caddyfile-anatomy in the server config (see DEPLOY.md)"
