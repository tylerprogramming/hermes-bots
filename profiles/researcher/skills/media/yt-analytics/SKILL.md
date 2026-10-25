---
name: yt-analytics
description: YouTube channel analytics: views, retention, traffic, per video.
version: 1.0.0
author: tylerreed
---

# YouTube analytics

> Full triggers: analytics, how are my videos doing, youtube stats, channel performance,
> video performance, check my analytics, how did my video do.

Ported from `~/.claude/skills/yt-analytics`. Reads the YouTube Data API v3 and the YouTube
Analytics API for Tyler's channel (@tylerreedai) and turns the JSON into a read: what is
working, what is not, and what to change.

## Prerequisites (shared with the Claude Code copy, do not duplicate)

- OAuth client at `~/.claude/gmail/credentials.json`; YouTube token cached at
  `~/.claude/analytics/yt_token.json`. Both agents share one auth; the script refreshes the
  token headlessly and only opens a browser when the refresh token itself has expired (about
  every 6 months, or after a Google password change).
- The Google API libs live only in `~/.claude/skills/.venv`. The script re-execs itself into
  that venv; do not pip install anything.

## Fetch

```bash
python3 ~/.hermes/skills/media/yt-analytics/scripts/yt_analytics.py --days 28 --json
python3 ~/.hermes/skills/media/yt-analytics/scripts/yt_analytics.py --video VIDEO_ID --days 90 --json
python3 ~/.hermes/skills/media/yt-analytics/scripts/yt_analytics.py --shorts --json
```

JSON on stdout, status lines on stderr. Keys: `period`, `channel`, `analytics` (views,
estimatedMinutesWatched, averageViewDuration, averageViewPercentage, subscribersGained/Lost,
likes, comments, shares), `trafficSources[]`, `searchTerms[]`, `perVideo[]` (per-video
analytics with `isShort`), `recentVideos[]` (last 20 uploads).

**Data lag:** YouTube Analytics finalizes a day 2 to 3 days after it ends. The window ends
`--lag` days back (default 3). A window ending today returns zeros for the newest days, which
looks like a crash in views. Never report "0 views yesterday"; say which date the data runs
through.

## Morning brief (cron)

`~/.hermes/scripts/youtube_analytics_brief.py` builds one Slack Block Kit card from three
pulls (1, 7, 28 days): latest finalized day vs the 7-day daily average, top 3 long-form and top
short of the week, the newest upload's first days, traffic mix, net subs. Snapshot saved to
`~/content/youtube/analytics/daily/YYYY-MM-DD.json`. Cron `YouTube: analytics` runs it
daily 7:30am ET as a `no_agent` script to Slack. `--json` prints the card without posting;
`hermes cron run "YouTube: analytics"` posts for real.

## Presenting a channel overview (interactive)

In this order: channel snapshot (subs, total views, count, period) · period summary (views,
watch hours, avg duration, retention %, net subs, likes/comments/shares) · top long-form table
(Video / Published / Views / Avg duration / Retention / Subs / Engagement = (likes+comments)/views)
· shorts table if any (under 61s) · top 5 traffic sources with % · top 10 search terms, noting
legacy vs current strategy · then analysis: what is working, what is not, demand the search
terms show that is unfilled, retention patterns by length, growth signals, 2 to 3 next steps.

## Single video deep dive

Stats · analytics (avg duration, retention, subs) · traffic sources for this video · search
terms for this video · daily view curve (first 7 days vs steady state) · comparison to channel
average.

## Title/thumbnail tracking

Each package `~/content/youtube/videos/NNN-slug/` may carry `performance.md`: current live
title/thumbnail, title history table, thumbnail history table, performance snapshots, next to
try, notes. Create or update it when a video underperforms, when Tyler asks how a video is
doing and it needs help, or when a title/thumbnail changes. Before suggesting a change read
`performance.md`, `titles.md`, `seo.md`; never re-suggest a tried title; be specific about
thumbnail changes (text, colour, expression, layout).

## Rules

- Long-form and shorts are different strategies; always split them.
- Retention % is the headline metric for long-form; views and completion for shorts.
- Compare against channel averages; numbers without a baseline get sent back.
- Note content eras (CrewAI, n8n, Claude Code) when search terms show them. Legacy search
  traffic (crewai, splay tree, radix sort) is passive; do not suggest dropping it, do not call
  it growth.
- External URL traffic is social distribution working; if it drops, say so.
- Suggested/related under 10% means a title + thumbnail CTR opportunity.
- No em dashes.
