
"""
Gaming Shorts Automator
Main application entry point.
"""

import os
from pathlib import Path

APP_NAME = "Gaming Shorts Automator"
VERSION = "1.0.0"

VIDEO_FOLDER = Path("videos")
OUTPUT_FOLDER = Path("output")


def setup():
    """Create required project folders."""
    VIDEO_FOLDER.mkdir(exist_ok=True)
    OUTPUT_FOLDER.mkdir(exist_ok=True)
    print(f"{APP_NAME} v{VERSION}")
    print("Project initialized successfully.")


def main():
    setup()
    print("Gaming Shorts automation system is ready.")
    print("Next: configure video processing and YouTube API.")


if __name__ == "__main__":
    main()
