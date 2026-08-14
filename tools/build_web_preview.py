#!/usr/bin/env python3
"""Sync the static browser preview with the shipped app resources."""

from __future__ import annotations

import json
import re
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


def sync_selected(source: Path, target: Path, names: set[str]) -> int:
    target.mkdir(parents=True, exist_ok=True)
    for stale in target.iterdir():
        if stale.is_file() and stale.name not in names:
            stale.unlink()
    count = 0
    for name in sorted(names):
        source_file = source / name
        if not source_file.exists():
            raise FileNotFoundError(source_file)
        sync_file(source_file, target / name)
        count += 1
    return count


def main() -> None:
    manifest = json.loads((ROOT / "content" / "manifest.json").read_text(encoding="utf-8"))
    version = manifest.get("meta", {}).get("version", "dev")
    sync_file(ROOT / "content" / "manifest.json", WEB / "data" / "manifest.json")
    index = WEB / "index.html"
    index_source = index.read_text(encoding="utf-8")
    index_source, index_replacements = re.subn(
        r'\./js/app\.js(?:\?v=[^"\']+)?',
        f'./js/app.js?v={version}-r3',
        index_source,
        count=1,
    )
    if index_replacements != 1:
        raise RuntimeError(f"Could not update app shell version in {index}")
    index_source, css_replacements = re.subn(
        r'\./styles\.css(?:\?v=[^"\']+)?',
        f'./styles.css?v={version}-r3',
        index_source,
        count=1,
    )
    if css_replacements != 1:
        raise RuntimeError(f"Could not update stylesheet version in {index}")
    index.write_text(index_source, encoding="utf-8")
    art_names = {scene["art"] for scene in manifest["scenes"] if scene.get("art")}
    audio_names = {cue["file"] for cue in manifest["audioCues"]}
    art_count = sync_selected(APP / "Art", WEB / "assets" / "art", art_names)
    audio_count = sync_selected(APP / "Audio", WEB / "assets" / "audio", audio_names)
    sync_file(ROOT / "altstore" / "icon.png", WEB / "assets" / "icon.png")
    service_worker = WEB / "service-worker.js"
    service_worker_source = service_worker.read_text(encoding="utf-8")
    # Bump the shell suffix when the web layout changes so an installed service
    # worker cannot keep serving a previous HTML/CSS/JS shell.
    cache_name = f"kraehenfels-web-v{version}-shell7"
    service_worker_source, replacements = re.subn(
        r'const CACHE = "[^"]+";',
        f'const CACHE = "{cache_name}";',
        service_worker_source,
        count=1,
    )
    if replacements != 1:
        raise RuntimeError(f"Could not update service-worker cache name in {service_worker}")
    service_worker.write_text(service_worker_source, encoding="utf-8")
    print(f"Synced browser preview v{version}: {art_count} artwork files and {audio_count} audio files")


if __name__ == "__main__":
    main()
