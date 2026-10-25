---
name: hermes-multi-agent-ops
description: "Use when Hermes bots, kanban, or desktop pool need work."
---

# Hermes multi-agent ops on the Mac Studio

Four bot profiles (coder, researcher, packager, coder-reviewer) plus default. One launchd gateway
`ai.hermes.gateway` multiplexes them. Dashboard runs as launchd `ai.hermes.dashboard` on 127.0.0.1:9119
(see skill `hermes-conduit-tailscale`).

## Slow bot chats in the desktop app

- Cold start per profile is ~3.3s (`time hermes -p <profile> -z "reply ok"`). A 10s+ spinner is the
  desktop **backend pool**, not the bot: default cap 3 warm backends, 10 min idle reap. Queue waits log as
  `waiting for a free local slot` in `~/.hermes/logs/desktop.log`.
- Fix in Settings -> Config -> Warm Bot Backends (set >= bots+1) and Backend Idle Timeout (ms; 86400000 = 24h).
  Persisted at `~/Library/Application Support/Hermes/pool-limits.json`; deleting it restores defaults.

## Kanban board (the handoff mechanism)

- Desktop Kanban plugin ships OFF: Settings -> Capabilities -> Plugins -> Kanban. Then a sidebar row and `/kanban`.
  Orchestration settings live on the board page, not in Settings.
- Dispatcher runs inside the gateway every 60s (`kanban dispatcher [default]: spawned=...` in gateway.log).
  Ready + assignee -> claimed -> spawned as that profile -> Running. Children in Todo promote when parents Done.
- Give a bot the kanban tools with `hermes -p <profile> tools enable kanban` (also `--platform slack`). Desktop
  Bot Chat reads the `cli` toolset list, so there is no gui platform to enable.
- Create: `hermes kanban create "title" --assignee <profile> --workspace dir:/path --priority 2 --json --body "..."`.
  For repo work: `hermes project create ... /path` once, then `--project <slug> --workspace worktree --branch <name>`
  (`--branch` is rejected without `--workspace worktree`). Link with `hermes kanban link <parent> <child>`.
- Steer a running worker with `hermes kanban comment <id> "From Tyler: ..."`; it is delivered mid-run as a /steer.
- Headless workers get NO approval prompts: exporting API keys, writing `.env`, heredocs, and writing CLAUDE.md
  are blocked. Say so in the card body (skip key-dependent runs, skip CLAUDE.md) or the worker burns minutes retrying.
  Write CLAUDE.md from the main thread; it still needs explicit user approval (clarify first, then write).
- Real result 2026-09-15: research -> package + code -> review for video 058 ran end to end in ~35 min, PR
  https://github.com/tylerprogramming/ai/pull/22. Script restructure to the Tina beat table came from a follow-up card
  pointing at `research/youtube/creator-breakdowns/`.

## Gateway gotchas

- `hermes gateway restart` from a tool call can leave an orphan `gateway run` outside launchd (status says
  "running but service not active"). Fix: kill the PID, `launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway`.
- "pulled new code but did not restart running gateways" on every CLI call = restart needed before trusting the dispatcher.
- MCP servers with `auth: oauth` and no cached token (ClickUp on coder-reviewer) retry on every open and park;
  authorize with `hermes -p <profile> mcp login <name>` in a real terminal or set `enabled: false`.

## Telegram

- One bot token per profile; Telegram rejects two gateways polling one token. Tokens go in each profile's `.env`
  as TELEGRAM_BOT_TOKEN + TELEGRAM_ALLOWED_USERS. App path: Settings -> Messaging -> Telegram -> Create with QR, per profile.
- Multiple chats inside one bot = forum topics in the DM; cron gets its own via TELEGRAM_CRON_THREAD_ID.
