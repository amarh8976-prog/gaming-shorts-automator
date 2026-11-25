
import os
import sys
import shutil
import subprocess
from pathlib import Path

import yt_dlp

# Gaming Shorts Automator
VERSION = "1.1.0"

BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
OUTPUT_DIR = BASE_DIR / "output" / "clips"

CLIP_COUNT = 20
CLIP_DURATION = 30
OUTPUT_WIDTH = 1080
OUTPUT_HEIGHT = 1920


def check_tools():
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("FFmpeg is not installed.")

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def download_video(url):
    print("Downloading source video...")

    # Read cookies file path supplied by GitHub Actions
    cookies_file = os.environ.get(
        "YOUTUBE_COOKIES_FILE", ""
    ).strip()

    if not cookies_file:
        raise RuntimeError(
            "YOUTUBE_COOKIES_FILE environment variable is missing."
        )

    cookies_path = Path(cookies_file)

    if not cookies_path.is_file():
        raise RuntimeError(
            "YouTube cookies file was not found."
        )

    # Remove old downloads to avoid using an outdated video
    for old_file in DOWNLOAD_DIR.glob("source.*"):
        if old_file.is_file():
            old_file.unlink()

    options = {
        "format": "bestvideo+bestaudio/best",
        "cookiefile": str(cookies_path),
        "outtmpl": str(DOWNLOAD_DIR / "source.%(ext)s"),
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": False,
        "retries": 3,
        "fragment_retries": 3,
    }

    with yt_dlp.YoutubeDL(options) as downloader:
        info = downloader.extract_info(
            url,
            download=True
        )

    candidates = [
        path for path in DOWNLOAD_DIR.glob("source.*")
        if path.suffix.lower() in (
            ".mp4", ".mkv", ".webm", ".mov"
        )
    ]

    if not candidates:
        raise RuntimeError(
            "Downloaded video file was not found."
        )

    video_path = max(
        candidates,
        key=lambda p: p.stat().st_size
    )

    duration = float(info.get("duration") or 0)

    if duration <= 0:
        raise RuntimeError(
            "Could not determine video duration."
        )

    print(f"Downloaded: {info.get('title', 'Video')}")
    print(f"Duration: {duration:.1f} seconds")

    return video_path, duration


def create_clips(video_path, duration):
    clip_length = min(CLIP_DURATION, duration)

    if duration < 5:
        raise RuntimeError(
            "Video is too short to create clips."
        )

    count = min(
        CLIP_COUNT,
        max(1, int(duration // clip_length))
    )

    if count == 1:
        start_times = [0]
    else:
        last_start = max(0, duration - clip_length)

        start_times = [
            round(i * last_start / (count - 1), 2)
            for i in range(count)
        ]

    print(f"Creating {count} vertical clips...")

    for index, start in enumerate(
        start_times, start=1
    ):
        output_file = (
            OUTPUT_DIR / f"gaming_short_{index:02d}.mp4"
        )

        command = [
            "ffmpeg",
            "-y",
            "-ss", str(start),
            "-i", str(video_path),
            "-t", str(clip_length),
            "-vf",
            f"scale={OUTPUT_WIDTH}:{OUTPUT_HEIGHT}:"
            "force_original_aspect_ratio=increase,"
            f"crop={OUTPUT_WIDTH}:{OUTPUT_HEIGHT}",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            str(output_file),
        ]

        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"FFmpeg failed on clip {index}: "
                f"{result.stderr[-2000:]}"
            )

        print(f"Created: {output_file.name}")


def main():
    print(f"Gaming Shorts Automator v{VERSION}")

    try:
        check_tools()

        video_url = os.environ.get(
            "INPUT_VIDEO_URL", ""
        ).strip()

        if not video_url:
            raise RuntimeError(
                "No video URL supplied."
            )

        video_path, duration = download_video(
            video_url
        )

        create_clips(video_path, duration)

        print("\nAll clips created successfully.")
        print(f"Output folder: {OUTPUT_DIR}")

    except Exception as error:
        print(f"\nERROR: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
