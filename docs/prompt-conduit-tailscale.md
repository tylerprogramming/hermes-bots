# Prompt: connect Hermes Conduit (iPhone) to your Hermes over Tailscale

Copy everything below the line and paste it to your Hermes agent (desktop app, terminal, Telegram, wherever you talk to it). It ends with a QR code you scan in the Conduit app.

Before you paste: install the **Tailscale** app on your Mac and sign in. Install **Tailscale** and **Hermes Conduit** on your iPhone, sign in to the same Tailscale account.

---

I want to use the Hermes Conduit app on my iPhone to talk to you from anywhere, over Tailscale. Conduit signs in to the Hermes web dashboard (`hermes dashboard`, port 9119). Do all of this, verify each step with a real command, and stop to tell me if you need something only I can do.

1. **Preflight.** Check the gateway is running (`hermes gateway status`), whether anything already listens on 9119 (`lsof -nP -iTCP:9119 -sTCP:LISTEN`), and that Tailscale is signed in. The Tailscale CLI is at `/Applications/Tailscale.app/Contents/MacOS/Tailscale` on a Mac and is not on PATH; use the full path. If it says stopped, tell me to open Tailscale and sign in, then continue.

2. **Dashboard sign-in.** Conduit refuses a dashboard without auth. If `HERMES_DASHBOARD_BASIC_AUTH_USERNAME`, `_PASSWORD` and `_SECRET` are not in `~/.hermes/.env`, back up the file and add them. Generate the password and secret with Python `secrets` (24+ chars). Never print them in chat.

3. **Tailscale Serve.** Run `tailscale serve --bg 9119`, confirm with `tailscale serve status` that it shows an `https://<machine>.<tailnet>.ts.net` address proxying to `http://127.0.0.1:9119`, tailnet only. Do not use `tailscale funnel`; that is public. Then `hermes config set dashboard.public_url <that https address>`.

4. **Dashboard that survives reboot.** A dashboard started from a chat shell dies with it. Stop any ad-hoc one, then install a launchd LaunchAgent at `~/Library/LaunchAgents/ai.hermes.dashboard.plist` running `hermes dashboard --no-open --skip-build --host 127.0.0.1 --port 9119` with RunAtLoad and KeepAlive, logs to `~/.hermes/logs/dashboard.log`. `launchctl bootstrap gui/$(id -u) <plist>`. Keep the host on 127.0.0.1; Tailscale proxies to loopback. Verify: `launchctl list | grep ai.hermes.dashboard` shows a PID, `curl http://127.0.0.1:9119/api/sessions` returns 401, and `curl -I https://<address>/` returns a 302 to /login. The first HTTPS probe can return 000 while Tailscale mints the certificate; wait 10 seconds and retry before calling it broken.

5. **Notifications.** `hermes plugins install kaishi00/hermes-conduit-notifier --enable`.

6. **QR code.** Build the sign-in link `conduit://connect?url=ADDRESS&username=USERNAME&password=PASSWORD` with every value percent-encoded and the full https address (never localhost). Render it as a QR image (`uv run --with "qrcode[pil]" python ...` works when the venv has no pip) and show it to me. State the address and username in prose; for the password point me at the `.env` line, do not paste it. Tell me to delete the image after scanning.

7. **Tell me the phone steps:** Tailscale app on, open Conduit, Scan Code.

8. **Give me the rollback:** `tailscale serve --https=443 off`, `launchctl bootout gui/$(id -u)/ai.hermes.dashboard`, restore `.env` from the backup, clear `dashboard.public_url`.

Do not restart the gateway unless a step requires it, and if you must, do it last and tell me first.
