#!/usr/bin/env python3
"""Sync the static browser preview with the shipped app resources."""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
APP = ROOT / "app" / "Kraehenfels" / "Resources"


def sync_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def sync_directory(source: Path, target: Path, pattern: str) -> int:
    target.mkdir(parents=True, exist_ok=True)
    count = 0
    for file in source.glob(pattern):
        sync_file(file, target / file.name)
        count += 1
    return count


def main() -> None:
    sync_file(ROOT / "content" / "manifest.json", WEB / "data" / "manifest.json")
    art_count = sync_directory(APP / "Art", WEB / "assets" / "art", "*.png")
    audio_count = sync_directory(APP / "Audio", WEB / "assets" / "audio", "*")
    sync_file(ROOT / "altstore" / "icon.png", WEB / "assets" / "icon.png")
    print(f"Synced browser preview: {art_count} artwork files and {audio_count} audio files")


if __name__ == "__main__":
    main()
