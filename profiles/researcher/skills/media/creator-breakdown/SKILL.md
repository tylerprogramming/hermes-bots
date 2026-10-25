---
name: creator-breakdown
description: Use when prepping a video vs a reference creator's.
version: 1.0.0
author: tylerreed
---

# Creator breakdown

Tyler preps every long-form video against one or more reference videos on the same topic.
He wants the reference dissected into beats, the creator's technique named, the gaps found,
and then a side-by-side plan he can film from. He explicitly likes this shape ("I like being
presented things like this for a video") and wants the breakdowns kept so the agency
remembers how each creator made their video.

Output file: `~/content/research/youtube/creator-breakdowns/YYYY-MM-DD-<creator>-<slug>.md`.
One file per reference video. Never overwrite; a re-analysis is a new dated file.

## Inputs

- A transcript at `~/content/transcripts/transcript_<videoId>.txt` (timestamped lines `[mm:ss] text`).
  If missing, fetch with `youtube-content`'s script and save it there first.
- The view count, duration, upload date from `~/content/research/*.md` (never invent; mark unverified).
- The target video's package folder, if it exists, so "our beat" can name real prompts.

## Procedure

1. **Find the segment transitions.** Grep the transcript for demo verbs and transition phrases
   (`let's`, `let me`, `so i'm going to`, `click`, `type`, `hey hermes`, `@`, `for example`,
   `here's my`, `now let's move`). Print the matching lines with timestamps; the clusters are
   the beats. Then print the full text of each demo beat (a 60-150 s window) and read it.
   Sampling every N lines misses the actual demos; grep for the verbs.
2. **Write the beat table** with `#`, beat name, time range, and *what she does on screen*
   (the click, the exact prompt she types, what the tool returns). Quote her prompts verbatim.
3. **Name the rhythm.** The reusable technique, not the content. Examples that recur across
   creators: *tell -> show a real past example -> do a new one live* (never demo on empty
   state); *say the seam* when cutting between a fresh and a mature setup; *ease framing*
   ("just ask the agent to set it up"); *save the build for the ending*.
4. **What works / weaknesses.** Weaknesses are our openings. Check for: audience framing we
   own (Claude Code users), demos that prove storage but not use, third-party signups in a
   fundamentals video, unexplained architecture ("why is X capped"), features shipped since
   she filmed (name the current UI labels), payoff that is a toy vs an artifact.
5. **Her beat / our beat / exact prompt table.** One row per beat. "Our beat" is filmable
   today with Tyler's real systems; "exact prompt" is copy-pasteable. Mark anything not yet
   verified on his machine.
6. **Possible extras.** Features we have that the reference did not show. Short list.

## Rules

- Timestamps come from the transcript, not memory.
- Her prompts are quoted; ours are written in Tyler's voice (`~/content/BRAIN/tyler-voice.md`):
  short sentences, no em dashes, no hype words.
- Every "our beat" must be something that exists on his Mac or is explicitly marked *to build*.
  A plan that assumes a demo we have not verified gets sent back.
- Tables over prose. Counts, not adjectives.
- When the target video's package exists, append a pointer to the breakdown in its
  `analysis.md` under `## Creator breakdowns`.

## Existing breakdowns

- `2026-09-12-tina-huang-hermes-fundamentals.md` (video 057). Tina Huang, 29:40, 313,962 views.
