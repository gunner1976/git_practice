#!/usr/bin/env bash
# One-shot, idempotent install of the Anatomy Explorer on the server that hosts gunninginc.click.
# Run ON THE SERVER (over SSH) as a user with sudo:
#
#   curl -fsSL https://raw.githubusercontent.com/gunner1976/git_practice/claude/gaussian-splat-body-viewer-ksbgzs/anatomy/deploy/server-install.sh | sudo bash
#   # or, after cloning: sudo bash anatomy/deploy/server-install.sh
#
# What it does:
#   1. installs git, Node 22 and rsync if missing (Debian/Ubuntu)
#   2. clones or updates this repository under /opt/anatomy-src and builds anatomy/web -> /var/www/anatomy
#   3. serves it at https://anatomy.gunninginc.click using whatever web server is already running:
#        - nginx: writes /etc/nginx/sites-available/anatomy.conf, enables it, obtains a certificate with certbot
#        - Caddy: appends a site block to /etc/caddy/Caddyfile (automatic HTTPS)
#        - nothing on :80/:443: installs nginx + certbot and proceeds as for nginx
#   4. opens 80/443 in ufw if ufw is active (the sovereign-fund VPS setup allows SSH only)
# Re-running updates the checkout, rebuilds and reloads. Override with env vars:
#   DOMAIN, BRANCH, SRC_DIR, WEB_ROOT, CERT_EMAIL
set -euo pipefail
DOMAIN="${DOMAIN:-anatomy.gunninginc.click}"
BRANCH="${BRANCH:-claude/gaussian-splat-body-viewer-ksbgzs}"
REPO="${REPO:-https://github.com/gunner1976/git_practice.git}"
SRC_DIR="${SRC_DIR:-/opt/anatomy-src}"
WEB_ROOT="${WEB_ROOT:-/var/www/anatomy}"
CERT_EMAIL="${CERT_EMAIL:-gunninginc@gmail.com}"
[ "$(id -u)" = 0 ] || { echo "run with sudo"; exit 1; }
log(){ echo "[anatomy] $*"; }

# 1. prerequisites
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq git rsync curl ca-certificates >/dev/null
if ! command -v node >/dev/null || [ "$(node -v | cut -c2-3)" -lt 20 ]; then
  log "installing Node 22"
  curl -fsSL https://deb.nodesource.com/setup_22.x | bash - >/dev/null
  apt-get install -y -qq nodejs >/dev/null
fi
log "node $(node -v), npm $(npm -v)"

# 2. source + build
if [ -d "$SRC_DIR/.git" ]; then
  git -C "$SRC_DIR" fetch -q origin "$BRANCH" && git -C "$SRC_DIR" checkout -q "$BRANCH" && git -C "$SRC_DIR" reset -q --hard "origin/$BRANCH"
else
  git clone -q --depth 1 --branch "$BRANCH" "$REPO" "$SRC_DIR"
fi
log "building $(git -C "$SRC_DIR" rev-parse --short HEAD)"
( cd "$SRC_DIR/anatomy/web" && npm ci --no-audit --no-fund --loglevel=error && npm run build >/dev/null )
mkdir -p "$WEB_ROOT"
rsync -a --delete "$SRC_DIR/anatomy/web/dist/" "$WEB_ROOT/"
chown -R www-data:www-data "$WEB_ROOT" 2>/dev/null || true
log "bundle in $WEB_ROOT ($(du -sh "$WEB_ROOT" | cut -f1))"

# 3. web server
if command -v ufw >/dev/null && ufw status | grep -q "Status: active"; then
  ufw allow 80/tcp >/dev/null; ufw allow 443/tcp >/dev/null; log "ufw: 80/443 allowed"
fi
have_caddy=0; have_nginx=0
systemctl is-active --quiet caddy 2>/dev/null && have_caddy=1
systemctl is-active --quiet nginx 2>/dev/null && have_nginx=1
if [ $have_caddy = 1 ]; then
  CF=/etc/caddy/Caddyfile
  if ! grep -q "^$DOMAIN" "$CF"; then
    cat >> "$CF" <<CADDY

$DOMAIN {
    root * $WEB_ROOT
    file_server
    encode zstd gzip
    header /*.glb Cache-Control "public, max-age=2592000, immutable"
    header /*.webp Cache-Control "public, max-age=2592000, immutable"
}
CADDY
  fi
  caddy validate --config "$CF" >/dev/null && systemctl reload caddy
  log "caddy: $DOMAIN configured (automatic HTTPS)"
else
  if [ $have_nginx = 0 ]; then
    if ss -ltn | grep -qE ':(80|443) '; then
      log "something other than nginx/caddy listens on 80/443; add a vhost for $DOMAIN -> $WEB_ROOT yourself (see nginx-anatomy.conf)"; exit 0
    fi
    log "installing nginx + certbot"
    apt-get install -y -qq nginx certbot python3-certbot-nginx >/dev/null
    systemctl enable --now nginx
  fi
  cat > /etc/nginx/sites-available/anatomy.conf <<NGINX
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;
    root $WEB_ROOT;
    index index.html;
    types { text/html html; text/css css; application/javascript js; application/json json; model/gltf-binary glb; application/wasm wasm; image/webp webp; image/png png; image/svg+xml svg; image/x-exr exr; }
    location / { try_files \$uri \$uri/ /index.html; }
    location ~* \.(glb|webp|exr|wasm)$ { expires 30d; add_header Cache-Control "public, immutable"; }
    location ~* \.(js|css)$ { expires 7d; add_header Cache-Control "public"; }
    gzip on; gzip_types application/javascript text/css application/json image/svg+xml;
}
NGINX
  ln -sf /etc/nginx/sites-available/anatomy.conf /etc/nginx/sites-enabled/anatomy.conf
  nginx -t && systemctl reload nginx
  if command -v certbot >/dev/null || apt-get install -y -qq certbot python3-certbot-nginx >/dev/null; then
    certbot --nginx -n --agree-tos -m "$CERT_EMAIL" -d "$DOMAIN" --redirect || log "certbot failed; site is up on http://$DOMAIN, retry: certbot --nginx -d $DOMAIN"
  fi
  log "nginx: $DOMAIN configured"
fi
log "done: https://$DOMAIN"
