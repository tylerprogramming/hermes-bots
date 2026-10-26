# hermes-bots

The Hermes Agent bots I run on a Mac Studio for my YouTube channel ([tylerreedai](https://youtube.com/@tylerreedai)), as installable [profile distributions](https://hermes-agent.nousresearch.com/docs/user-guide/profile-distributions), plus the two prompts and two skills from the setup videos.

Three bots, one gateway, one kanban board. Research → package → code → review runs without me routing anything.

## What is in here

| Path | What it is | Install / use |
|---|---|---|
| `profiles/researcher/` | YouTube competitor research. `yt-search`, `transcribe`, `creator-breakdown` (beat tables), `yt-analytics`, `content-brief` weekday 7:45am cron. | `hermes profile install github.com/tylerprogramming/hermes-bots/profiles/researcher --alias` |
| `profiles/packager/` | Turns a research file into a video package: titles, hooks, script, filming guide, description, SEO, thumbnail prompt. Skill `yt-package`. | `hermes profile install github.com/tylerprogramming/hermes-bots/profiles/packager --alias` |
| `profiles/coder/` | Reviews PRs with `gh`, watches CI weekdays 8am, opens small PRs on request. Skill `code-review`. | `hermes profile install github.com/tylerprogramming/hermes-bots/profiles/coder --alias` |
| `skills/hermes-conduit-tailscale/` | Runbook: dashboard auth, Tailscale Serve, dashboard as a service (launchd on macOS, systemd on Linux), Mac keep-awake, QR sign-in for the Conduit iPhone app. | copy to `~/.hermes/skills/` |
| `skills/hermes-multi-agent-ops/` | Bot pool tuning, kanban commands, headless worker blocks, gateway orphan recovery, Telegram per-profile tokens. | copy to `~/.hermes/skills/` |
| `docs/prompt-conduit-tailscale.md` | Copy/paste prompt: phone access over Tailscale on macOS or Linux, ends with a QR code. | paste to Hermes |
| `docs/prompt-kanban-pipeline.md` | Copy/paste prompt: four linked kanban cards that run a video pipeline across the bots. | paste to Hermes |

Each profile folder is a complete distribution: `distribution.yaml`, `SOUL.md`, `config.yaml`, `skills/`, and `cron/jobs.json` where the bot has one. Cron jobs install **paused**; enable them with `hermes -p <bot> cron list` once you have read them.

## Install

If `hermes profile install` does not accept a subfolder URL on your version, clone and point at the directory:

```bash
git clone https://github.com/tylerprogramming/hermes-bots ~/dev/hermes-bots
hermes profile install ~/dev/hermes-bots/profiles/researcher --alias
hermes profile install ~/dev/hermes-bots/profiles/packager --alias
hermes profile install ~/dev/hermes-bots/profiles/coder --alias
```

Then per bot: copy `.env.EXAMPLE` to `.env` in `~/.hermes/profiles/<bot>/` and fill in your keys. Model defaults to Anthropic; change `model.provider` and `model.default` in `config.yaml` for anything else (these run fine on local Ollama models for review work).

The SOULs are written for me by name. Edit `## Who you work for` in each `SOUL.md` before you run them, or the bots will keep calling you Tyler.

## Running them together

- **Desktop app:** every profile shows up in the Bots roster. Set Settings → Config → Warm Bot Backends to bots+1 or the fourth bot queues for 30 seconds on open.
- **Slack:** one Slack app, `SLACK_BOT_TOKEN` per profile `.env`, the gateway multiplexes them (`gateway.multiplex_profiles: true`).
- **Telegram:** one bot token per profile; Telegram rejects two gateways polling the same token.
- **Kanban:** enable the plugin in Settings → Capabilities → Plugins, give a profile the tools with `hermes -p <bot> tools enable kanban`, then use `docs/prompt-kanban-pipeline.md`.

## What happened the first time

Video 058 (OpenAI Agents API), 2026-09-15: four cards, three bots, about 35 minutes, zero manual handoffs. Research file, full package, [PR #22](https://github.com/tylerprogramming/ai/pull/22) with three runnable demos, review verdict. Details in `skills/hermes-multi-agent-ops/SKILL.md`.

## Not in here

`.env`, `auth.json`, memories, sessions, logs, Slack channel IDs. Each installer brings their own.

## Changelog

- **v1.1.0** Conduit prompt and skill: Linux/systemd dashboard service, Mac keep-awake step (system sleep kills Conduit when the screen blanks).
- **v1.0.0** Initial: researcher, packager, coder distributions; Conduit and kanban prompts and skills.

## License

MIT
