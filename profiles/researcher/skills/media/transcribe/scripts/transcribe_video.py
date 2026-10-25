"""
Transcribe a YouTube video or local video/audio file using OpenAI Whisper.

Usage:
  python transcribe_video.py <youtube_url>
  python transcribe_video.py <local_file_path>

For YouTube URLs: Downloads audio via yt-dlp, then transcribes.
For local files: Transcribes directly (supports mp4, mp3, wav, m4a, etc.)

Saves the transcript to ~/content/transcripts/transcript_<id>.txt

For large files (>24MB), automatically splits into 30-min chunks via ffmpeg.

Requires:
  - yt-dlp (for YouTube URLs only)
  - ffmpeg (for splitting large files)
  - mlx-whisper (Hermes port: local whisper-large-v3-turbo, no API key)
"""


import sys
import re
import os
import glob
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse, parse_qs




def extract_video_id(url):
    query = urlparse(url)
    if query.hostname == "youtu.be":
        return query.path[1:].split("?")[0]
    if query.hostname in ("www.youtube.com", "youtube.com"):
        if query.path == "/watch":
            p = parse_qs(query.query)
            return p["v"][0]
        if query.path.startswith("/embed/"):
            return query.path.split("/")[2]
        if query.path.startswith("/v/"):
            return query.path.split("/")[2]
        if query.path.startswith("/shorts/"):
            return query.path.split("/")[2]
    return None


def download_audio(url, output_path):
    """Download audio from YouTube at low bitrate mono to minimize file size."""
    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "9",
        "--postprocessor-args", "ffmpeg:-ar 16000 -ac 1 -b:a 32k",
        "-o", output_path,
        "--no-playlist",
        "--quiet",
        "--progress",
        url,
    ]
    print("Downloading audio (32kbps mono for Whisper)...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Fallback without postprocessor args
        cmd_fallback = [
            "yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "9",
            "-o", output_path, "--no-playlist", "--quiet", "--progress", url,
        ]
        result = subprocess.run(cmd_fallback, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"yt-dlp failed: {result.stderr}")

    for candidate in [output_path, output_path + ".mp3"]:
        if os.path.exists(candidate):
            return candidate
    raise FileNotFoundError(f"Audio file not found at {output_path}")


def split_audio(audio_path, tmpdir):
    """Split audio into 30-minute chunks using ffmpeg. Returns sorted chunk paths."""
    pattern = os.path.join(tmpdir, "chunk_%04d.mp3")
    cmd = [
        "ffmpeg", "-i", audio_path,
        "-f", "segment",
        "-segment_time", str(CHUNK_DURATION),
        "-acodec", "libmp3lame",
        "-b:a", "32k",
        "-ar", "16000",
        "-ac", "1",
        pattern,
        "-y", "-loglevel", "error"
    ]
    print("Splitting audio into 30-minute chunks...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg split failed: {result.stderr}")

    chunks = sorted(glob.glob(os.path.join(tmpdir, "chunk_*.mp3")))
    if not chunks:
        raise FileNotFoundError("ffmpeg produced no chunk files")
    print(f"Split into {len(chunks)} chunks")
    return chunks


def is_local_file(path):
    return os.path.exists(path)


def get_file_id(path):
    name, _ = os.path.splitext(os.path.basename(path))
    return name.replace(" ", "_").replace("-", "_")


def format_timestamp(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


MLX_WHISPER = "/Users/tylerreed/YouTube Agency/.venv/bin/mlx_whisper"
MLX_MODEL = "mlx-community/whisper-large-v3-turbo"


class _Seg:
    def __init__(self, start, text): self.start, self.text = start, text


class _Resp:
    def __init__(self, segments, duration, language="en"):
        self.segments, self.duration, self.language = segments, duration, language
        self.text = " ".join(s.text for s in segments)


def transcribe_audio_file(path, _client=None):
    """Local mlx-whisper (turbo). No chunking needed, no API key, no size cap.
    --condition-on-previous-text False stops the repeat-loop hallucination on quiet stretches."""
    with tempfile.TemporaryDirectory() as td:
        wav = os.path.join(td, "a.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", "16000", wav, "-y"], check=True)
        subprocess.run([MLX_WHISPER, wav, "--model", MLX_MODEL, "--condition-on-previous-text", "False",
                        "--output-format", "srt", "--output-dir", td, "--output-name", "out", "--language", "en"],
                       check=True, capture_output=True, text=True)
        srt = open(os.path.join(td, "out.srt")).read()
    segs = []
    for h, m, s, ms, text in re.findall(r"(\d\d):(\d\d):(\d\d)[,.](\d+) --> .*?\n(.*?)\n\n", srt + "\n\n", re.S):
        segs.append(_Seg(int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000, text.replace("\n", " ").strip()))
    return _Resp(segs, segs[-1].start if segs else 0)


def main():

    if len(sys.argv) < 2:
        print("Usage: python transcribe_video.py <youtube_url_or_local_file>")
        sys.exit(1)

    input_path = sys.argv[1]

    if is_local_file(input_path):
        print(f"Local file: {input_path}")
        file_id = get_file_id(input_path)
        response = transcribe_audio_file(input_path)
    else:
        video_id = extract_video_id(input_path)
        if not video_id:
            print(f"Could not extract video ID from: {input_path}")
            sys.exit(1)

        file_id = video_id
        with tempfile.TemporaryDirectory() as tmpdir:
            audio_path = os.path.join(tmpdir, f"audio_{video_id}")
            actual_path = download_audio(input_path, audio_path)
            response = transcribe_audio_file(actual_path)

    # Format output
    lines = []
    if hasattr(response, "segments") and response.segments:
        for seg in response.segments:
            lines.append(f"[{format_timestamp(seg.start)}] {seg.text.strip()}")
        transcript_text = "\n".join(lines)
    else:
        transcript_text = response.text

    # Save
    transcripts_dir = os.path.expanduser("~/content/transcripts")
    os.makedirs(transcripts_dir, exist_ok=True)
    out_file = os.path.join(transcripts_dir, f"transcript_{file_id}.txt")
    with open(out_file, "w") as f:
        f.write(transcript_text)

    duration_str = format_timestamp(response.duration) if hasattr(response, "duration") else "unknown"
    language = getattr(response, "language", "unknown")

    print(f"\n--- Transcript ({duration_str}) ---\n")
    preview = transcript_text[:2000]
    if len(transcript_text) > 2000:
        preview += "\n..."
    print(preview)
    print(f"\n--- End ---")
    print(f"\nFull transcript saved to: {out_file}")
    print(f"Duration: {duration_str} | Language: {language}")


if __name__ == "__main__":
    main()
