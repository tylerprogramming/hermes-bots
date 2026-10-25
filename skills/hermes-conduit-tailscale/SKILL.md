---
name: hermes-conduit-tailscale
description: "Use when connecting Hermes Conduit on iPhone via Tailscale."
---

# Connect Hermes Conduit (iPhone/iPad) over Tailscale

Conduit is a native iOS client that signs in to the Hermes **web dashboard** (`hermes dashboard`,
port 9119). No Conduit server, no extra account. Tailscale makes the dashboard reachable from the
phone anywhere without opening a port to the internet. End state: a QR code the user scans in Conduit.

Run the steps in order; each has a verification. Do not skip the verifications, the first HTTPS probe
after `tailscale serve` is a false negative (see step 3).

## 0. Preflight

```bash
hermes gateway status                      # gateway supervised by launchd
lsof -nP -iTCP:9119 -sTCP:LISTEN           # is a dashboard already listening?
grep -n '^HERMES_DASHBOARD_BASIC_AUTH' ~/.hermes/.env | sed 's/=.*/=<set>/'
ls /Applications/Tailscale.app && /Applications/Tailscale.app/Contents/MacOS/Tailscale status | head -3
```

The Tailscale CLI is **not on PATH** on a Mac App Store install; always use the full binary path.
If status says `stopped`, tell the user to open Tailscale.app and sign in, then continue.

## 1. Dashboard credentials (never print them)

Conduit refuses a dashboard without auth. Generate, don't ask the user to invent a password.

```bash
cp ~/.hermes/.env ~/.hermes/.env.bak-conduit-$(date +%s)
python3 - <<'EOF'
import secrets, pathlib
p = pathlib.Path.home()/".hermes/.env"; s = p.read_text()
assert "HERMES_DASHBOARD_BASIC_AUTH_USERNAME=" not in s, "already set; edit by hand"
block = ("\n# Hermes Conduit (iPhone) dashboard sign-in\n"
         "HERMES_DASHBOARD_BASIC_AUTH_USERNAME=tyler\n"
         f"HERMES_DASHBOARD_BASIC_AUTH_PASSWORD={secrets.token_urlsafe(18)}\n"
         f"HERMES_DASHBOARD_BASIC_AUTH_SECRET={secrets.token_hex(32)}\n")
p.write_text(s.rstrip("\n") + "\n" + block); print("written")
EOF
```

`_SECRET` keeps the phone signed in across dashboard restarts. Swap the username if the user wants another.

## 2. Tailscale Serve

```bash
TS=/Applications/Tailscale.app/Contents/MacOS/Tailscale
$TS serve --bg 9119
$TS serve status            # expect: https://<mac>.<tailnet>.ts.net (tailnet only) -> proxy http://127.0.0.1:9119
hermes config set dashboard.public_url "https://<mac>.<tailnet>.ts.net"
```

Serve is outbound-only and tailnet-only. Do not use `tailscale funnel`; that is public.

## 3. Dashboard as a launchd service

A dashboard started from a chat tool dies with that shell. Install a LaunchAgent so it survives
logout/reboot. Stop any ad-hoc one first (`hermes dashboard --stop`, then `kill <pid>` from lsof if it lingers).

`~/Library/LaunchAgents/ai.hermes.dashboard.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>ai.hermes.dashboard</string>
  <key>ProgramArguments</key><array>
    <string>/Users/USER/.hermes/hermes-agent/venv/bin/hermes</string>
    <string>dashboard</string><string>--no-open</string><string>--skip-build</string>
    <string>--host</string><string>127.0.0.1</string><string>--port</string><string>9119</string>
  </array>
  <key>EnvironmentVariables</key><dict>
    <key>HOME</key><string>/Users/USER</string>
    <key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
  </dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>/Users/USER/.hermes/logs/dashboard.log</string>
  <key>StandardErrorPath</key><string>/Users/USER/.hermes/logs/dashboard.error.log</string>
</dict></plist>
```

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.dashboard.plist
sleep 8
launchctl list | grep ai.hermes.dashboard                                  # PID, status 0
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:9119/api/sessions   # 401 = auth is on
curl -sI https://<mac>.<tailnet>.ts.net/ | head -3                           # 302 -> /login
```

Keep `--host 127.0.0.1`. Tailscale proxies to loopback; binding wider is unnecessary exposure.
**The first tailnet curl returns `000`** while Tailscale mints the HTTPS cert. Retry after ~10s before
calling it broken.

## 4. Notifier plugin

```bash
hermes plugins install kaishi00/hermes-conduit-notifier --enable   # installs as conduit_push
```

The running gateway hot-loads it ("Gateway reloaded plugins"). No restart needed for hooks.

## 5. QR sign-in link

Format: `conduit://connect?url=<https address>&username=<u>&password=<p>`, each value percent-encoded,
full `https://` address, never localhost. The venv has no pip, so use uv:

```bash
cd /tmp && uv run --quiet --with "qrcode[pil]" python - <<'EOF'
import re, urllib.parse, pathlib, qrcode
kv = dict(re.findall(r'^(HERMES_DASHBOARD_BASIC_AUTH_\w+)=(.*)$', (pathlib.Path.home()/".hermes/.env").read_text(), re.M))
url = "https://<mac>.<tailnet>.ts.net"
q = lambda s: urllib.parse.quote(s, safe='')
link = f"conduit://connect?url={q(url)}&username={q(kv['HERMES_DASHBOARD_BASIC_AUTH_USERNAME'])}&password={q(kv['HERMES_DASHBOARD_BASIC_AUTH_PASSWORD'])}"
qrcode.make(link, box_size=10, border=2).save("/tmp/conduit-signin.png"); print("saved")
EOF
```

Deliver with `MEDIA:/tmp/conduit-signin.png` (desktop) or as a terminal QR. State the address and
username in prose, point at the `.env` line for the password, never paste the password. Tell the user
to delete the PNG after scanning.

## 6. Phone side (tell the user)

1. Install Tailscale on the iPhone, sign in to the same account as the Mac, leave it enabled.
2. Open Conduit -> sign-in screen -> **Scan Code**.

Without Tailscale on the phone the `.ts.net` address does not resolve.

## Rollback

```bash
/Applications/Tailscale.app/Contents/MacOS/Tailscale serve --https=443 off
launchctl bootout gui/$(id -u)/ai.hermes.dashboard && rm ~/Library/LaunchAgents/ai.hermes.dashboard.plist
# restore ~/.hermes/.env from the .env.bak-conduit-* copy, or delete the three HERMES_DASHBOARD_BASIC_AUTH lines
hermes config set dashboard.public_url ""
```

## Pitfalls seen

- `hermes dashboard --status` reports "no dashboard running" even when a non-Hermes-spawned python owns
  9119; trust `lsof`, not `--status`.
- `web_extract` cannot read hermesconduit.app in this setup (search-only backend); `curl | python3` strip works.
- Mid-command interruptions in the chat tool orphan half-finished stop/start sequences; always re-check
  `lsof` + `launchctl list` before the next step instead of assuming.
