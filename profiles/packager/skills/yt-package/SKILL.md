---
name: yt-package
description: Plan a YouTube video package from research + a reference transcript.
version: 1.0.0
author: tylerreed
---

> Full triggers: youtube video, video script, plan a video, video from transcript, yt plan, package this video, build the package for.

Plan a YouTube video inspired by a reference transcript and research. Output is a full package folder the user films from.

## Step 0 - read the packaging rules FIRST (required)

Before writing any title or thumbnail brief, read all three:

```
~/content/BRAIN/youtube/packaging-rules.md   # operational checklist, measured on Tyler's channel
~/content/BRAIN/youtube/brain.md             # the reasoning and per-video history behind those rules
~/content/BRAIN/tyler-voice.md               # how Tyler talks; every script line follows it
```

Every title and thumbnail you propose must be checkable against packaging-rules.md. If a proposal breaks a rule, fix it or say plainly which rule it breaks and why it is worth breaking here. Standing prohibitions: no money in titles, no em dashes anywhere, never imply Tyler is not a developer, no "Explained" in titles.

## Where things live

| thing | path |
|---|---|
| pipeline truth | `~/content/youtube/notes/status.md` (read the "next to film" rows before numbering) |
| video ideas tracker | `~/content/youtube/ideas/video-ideas.md` |
| research from @researcher | `~/content/research/YYYY-MM-DD-slug.md` (+ `.json`) |
| transcripts | `~/content/transcripts/transcript_<videoId>.txt` |
| **output package** | `~/content/youtube/videos/NNN-slug/` where NNN = next free number in `videos/` |
| thumbnails | `~/content/youtube/thumbnails/<date>-<slug>/` |

Numbering: `ls ~/content/youtube/videos | sort | tail -1`, add one. Never reuse a number.

## Inputs

Accept any of: a transcript path, a research file path, a topic + angle, or a handoff message from @researcher naming the files. If the transcript is missing but a video id is known, say so and ask for it; do not fabricate a structure breakdown.

## Flow

### Step 1: Check the ideas tracker
Read `~/content/youtube/ideas/video-ideas.md`. If an Active/Backlog idea matches, say so and use its angle. If none matches, continue without asking.

### Step 2: Analyze the reference transcript
Produce and present:
- **Structure breakdown** as a table: time, segment, purpose (hook / demo / teaching / CTA)
- **What works** with specific phrases worth noting
- **Weaknesses / gaps** (these are the differentiation)
- **Target audience** and assumed level

If the transcript filename carries a video id, download the reference thumbnail:
```bash
yt-dlp --write-thumbnail --skip-download -o "~/content/youtube/videos/NNN-slug/reference-thumbnails/<source>" "https://youtu.be/<id>"
```
Then write `yt-thumbnail.md`: layout, colors, typography, elements, face, composition, why it is clickable, and 2-3 concepts for ours.

### Step 3: Research the topic (never skip)
Run at least 4-6 web searches: the tool itself (official site, pricing, latest release), competitors, existing YouTube coverage and who made it, gaps, community sentiment, recent news. If @researcher already supplied a research file, read it first and only fill the holes. All URLs go in `analysis.md` under `## Sources`.

### Step 4: Q&A (only what is not already answered)
Ask one at a time, conversationally, skipping anything the user or the handoff already covered:
1. Your angle: what would you do differently or better?
2. What will you show on screen?
3. Who is it for?
4. Anything to include or avoid?

### Step 5: Write the package
Create `~/content/youtube/videos/NNN-slug/` with:

- `titles.md` - 5 options under 70 chars, one line each on why it works, recommended one marked. Each checked against packaging-rules.
- `hooks.md` - 3 word-for-word 30-second opens, each a different technique (contrast, bold claim, story, pattern interrupt), technique labelled.
- `script.md` - full script by section. `## [m:ss - m:ss] Title` headers. Spoken rhythm, short sentences, Tyler's voice. `[SHOW: ...]` for what is on screen, `[NOTE: ...]` for production. Transitions between sections. Ends on a CTA.
- `filming-guide.md` - the "do this, click that" version: pre-recording setup, numbered steps with exact prompts/commands in code blocks, suggested narration in blockquotes, what happens next, dead-air fillers, a timing cheat sheet table, on-camera tips. Someone could film from this without reading the script.
- `description.md` - 1-2 tight paragraphs front-loaded for search, a chapters block (`00:00 - Title`, placeholders marked [UPDATE]), CTA/links. No "what's covered" list, no tags or hashtags in the body.
- `tags.txt` - comma-separated tags for the upload field.
- `analysis.md` - Step 2 analysis + all Step 3 research + `## Sources`.
- `yt-thumbnail.md` - from Step 2.

### Step 6: Thumbnails (ask before spending)
Read `yt-thumbnail.md`, craft 2-3 prompts (one following the reference style, one adding Tyler's face, one fresh take). State the cost (~$0.09/image at 2K) and ask before running:
```bash
python3 ~/.hermes/profiles/packager/skills/yt-package/scripts/generate_thumbnail.py "<prompt>" --count 1 --resolution 2K --slug <slug> --aspect-ratio 16:9
```
Face reference: `~/.hermes/profiles/packager/skills/yt-package/scripts/tylerai.png` via `--reference-images`. No text in prompts; leave room for an overlay. Requires `KIE_API_KEY` in `~/.hermes/.env`.

### Step 7: Present and iterate
Show: recommended title, recommended hook (full text), script outline (headers + times), thumbnail options. Ask what to revise. When done, confirm the folder path and, if asked, add the row to `status.md` (do not touch ClickUp; that is Tyler's or the default agent's job).

## Rules
- Package goes in `~/content/youtube/videos/NNN-slug/`, nowhere else. Slug lowercase-hyphenated.
- Be honest in the analysis; calling out the reference's weaknesses is the point.
- Scripts sound like a person talking. Short sentences. Every line earns its place.
- `[SHOW: ...]` liberally; the user needs to know what to record.
- Never invent a view count, date, or quote. Mark anything unverified.
- Draft only. Tyler publishes and schedules.
