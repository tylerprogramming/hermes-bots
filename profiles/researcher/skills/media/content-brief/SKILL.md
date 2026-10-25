---
name: content-brief
description: Morning content brief: pipeline, numbers, 3 openings, reply loop.
version: 1.0.0
author: tylerreed
---

# content-brief

Researcher's morning job. Read the state of Tyler's channel, pick 3 things worth making next,
send one message that ends with "reply with a number." When Tyler replies with a number, that
IS the go: run the research and hand it to @packager. Never ask a follow-up question first.

## Inputs (read all four, in this order)

1. `~/content/youtube/notes/status.md`: what is filming / editing / publish / packaged. The
   rows at the top of the table are current. Note the newest `IDEA` rows; Tyler wrote those.
2. `~/content/youtube/analytics/daily/` newest `YYYY-MM-DD.json` (written 7:30am by the
   analytics cron): `week.perVideo` for the last 7 days, `day.analytics.views` for the latest
   finalized day, `month.recentVideos[0]` for the newest upload. If the file for today is
   missing, use yesterday's and say so in one word ("stale").
3. `~/content/youtube/ideas/video-ideas.md` `## Active Ideas`: Tyler's own list, top entries
   first.
4. `~/content/research/` and `~/content/research/searches/`: anything dated in the last 7
   days is research already done; do not propose it again unless it has no package.

## Picking the 3

One from each lane when possible:
- **Tyler's idea**: the newest Active Idea or IDEA row that has no package yet.
- **Trend**: a sub-term on the channel's head terms (Claude Code, Hermes Agent, AI agents)
  where a competitor video passed 50K in the last 14 days. Run
  `python3 ~/.hermes/profiles/researcher/skills/media/yt-search/scripts/search_youtube.py "<term>" --days 14 --top 5 --search-count 15 --no-thumbnails`
  on 2 terms max; it takes ~30s each. Cite the biggest video and its views.
- **Follow-up**: the newest upload's strongest chapter or comment thread, or a video Tyler
  deleted/parked that the numbers now argue for.

Skip anything in `status.md` as filming/editing/publish. Skip Arcade (underperformed lane).

## Output shape (Telegram or Slack, plain text, under 900 chars)

```
Content, <Day Mon D>. <newest upload short title>: <views> views day <n>, <ret>% ret.
Pipeline: <NNN> <stage>, <NNN> <stage>.
3 openings:
1. <title-shaped line>. <one proof: creator + views + age, or "your idea from <day>">
2. ...
3. ...
Reply with a number and I'll research it and hand it to Packager.
```

Numbers only from the files. If a number is not in the files, leave it out; never guess.

## The reply (this is the whole point)

The cron delivers with `attach_to_session: true`, so Tyler's reply lands in the same session
and you can see the brief you sent. When the reply is a number (or "1 and 3", or "the hermes
one"):

1. Say "On it: <title>" in one line. Nothing else.
2. Run `yt-search` on the topic (`--days 30 --top 15`), then `transcribe` on the top 2
   long-form results. Both scripts live under this profile's `skills/media/`.
3. If the top result is a course-shaped video (20+ min, tutorial), also run
   `creator-breakdown` on its transcript.
4. Hand off to @packager with `message_agent`: the research report path, the transcript
   paths, the breakdown path if any, and the angle in 3 lines. Tell Packager to build the
   package and to STOP at the package (no PR, no Coder) until Tyler says build.
5. Reply to Tyler: "Research done: <report path>, <n> videos, <n> transcripts. Handed to
   @packager." One message. Then stop.

If the reply is anything other than a pick ("skip", "none", a question), answer in one line
and do not research.

## Hard rules

- Never publish, post, schedule, open a PR, or ping Coder from this job.
- One brief per morning. If the cron fires twice, the second run says nothing.
- No em dashes, no hype words, counts not adjectives.
