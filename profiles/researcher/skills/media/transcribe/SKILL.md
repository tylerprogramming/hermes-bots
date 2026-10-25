---
name: transcribe
description: Transcribe a YouTube URL or local video to a timestamped .txt.
version: 1.0.0
author: tylerreed
---

> Full triggers: transcribe this video, get transcript, transcribe youtube, what does this
> video say, convert video to text, transcribe this file.

Ported from `~/.claude/skills/transcribe`, with OpenAI Whisper replaced by local mlx-whisper
(`whisper-large-v3-turbo`, no API key, no 24 MB chunking, no HF token). Same output contract
so `yt-search` and `creator-breakdown` keep working: `~/content/transcripts/transcript_<id>.txt`,
one `[MM:SS] text` line per segment.

```bash
python3 ~/.hermes/profiles/researcher/skills/media/transcribe/scripts/transcribe_video.py <youtube_url_or_file>
# (researcher profile path; ~/.hermes/skills/ is the default profile's copy)
```

YouTube URLs are downloaded with `yt-dlp` (audio only) then transcribed. Local files go
straight through ffmpeg → mlx. A 30-minute video takes 3 to 5 minutes; run it in the
background and read the file when it lands. If a transcript shows one line repeated more than
5 times, rerun; the `--condition-on-previous-text False` flag is already set, so a repeat means
the audio itself is silent or music.
