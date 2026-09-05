# Deploying the Anatomy Explorer to gunninginc.click

The app is a static bundle (`anatomy/web/dist`: HTML, JS, Meshopt glTF, WebP,
EXR). It has no backend and is relocatable, so it runs unchanged at
`https://gunninginc.click/anatomy/` or `https://anatomy.gunninginc.click/`
(the wildcard DNS for `*.gunninginc.click` already resolves to the same
server). Total size is about 110 MB, dominated by the organ-system files that
load on demand (skeleton first, 16 MB).

## Chosen path: the Hetzner server, at anatomy.gunninginc.click

Run once on the server over SSH (any sudo user):

```
curl -fsSL https://raw.githubusercontent.com/gunner1976/git_practice/claude/gaussian-splat-body-viewer-ksbgzs/anatomy/deploy/server-install.sh | sudo bash
```

`deploy/server-install.sh` installs git, Node 22 and rsync if needed, clones
this branch into `/opt/anatomy-src`, builds the bundle into
`/var/www/anatomy`, opens 80/443 in ufw if it is active, and configures
whatever serves the site already: an nginx vhost with a certbot certificate,
a Caddy site block (automatic HTTPS), or, if nothing listens on 80/443,
installs nginx and certbot. Re-run the same command to update after a push.
Override `DOMAIN`, `BRANCH`, `WEB_ROOT` or `CERT_EMAIL` with environment
variables if needed.

Other paths kept in `deploy/` for reference:

| Path | When | What to run |
|---|---|---|
| **Server over SSH** (`deploy/rsync-to-server.sh`) | gunninginc.click is served by your own box (the domain's IP is a Hetzner server, like the sovereign-fund VPS) | `DEPLOY_HOST=gunninginc.click DEPLOY_USER=<ssh user> DEPLOY_DEST=/var/www/anatomy anatomy/deploy/rsync-to-server.sh`, then add `deploy/nginx-anatomy.conf` (or `deploy/Caddyfile-anatomy`) to the web server and reload it |
| **Vercel** (`deploy/vercel.json`) | you want it next to the SRDE knowledge app on Vercel | import this repo as a Vercel project with root `anatomy/web` (or copy `vercel.json` to the repo root), then add `anatomy.gunninginc.click` as the project domain and create the CNAME Vercel shows |
| **GitHub Pages** (`.github/workflows/deploy-anatomy.yml`) | zero-infrastructure fallback | enable Pages (Settings → Pages → Source: GitHub Actions); the workflow publishes on every push to `anatomy/web`; set repository variable `PAGES_CUSTOM_DOMAIN=anatomy.gunninginc.click` and a CNAME DNS record to `gunner1976.github.io` for the custom domain |

Checklist after any of them: open the URL, the status line should reach
"432,196 triangles in 1 systems" within a few seconds on desktop; the glTF
files must be served with `Content-Type: model/gltf-binary` (the snippets set
it) and ideally with long cache headers, since they are content-addressed by
the build.

The derived assets are CC-BY-SA 4.0 (Z-Anatomy / BodyParts3D); the About panel
in the app carries the required attribution.
