#!/usr/bin/env python3
"""Import replacement audio files into all Kraehenfels app targets.

The script expects audio generated from the production prompts. It keeps the
manifest filenames stable and converts incoming files with FFmpeg when needed.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "content" / "manifest.json"
AUDIO_GENERATED = ROOT / "audio" / "generated"
APP_AUDIO = ROOT / "app" / "Kraehenfels" / "Resources" / "Audio"
WEB_AUDIO = ROOT / "web" / "assets" / "audio"
SUPPORTED_EXTENSIONS = [".wav", ".m4a", ".mp3", ".aac", ".flac", ".ogg", ".opus", ".aiff", ".aif"]


@dataclass(frozen=True)
class Cue:
    filename: str
    category: str
    mode: str

    @property
    def stem(self) -> str:
        return Path(self.filename).stem

    @property
    def suffix(self) -> str:
        return Path(self.filename).suffix.lower()


def load_cues() -> list[Cue]:
    with MANIFEST.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    return [
        Cue(filename=item["file"], category=item["category"], mode=item["mode"])
        for item in manifest["audioCues"]
    ]


def find_source(input_dir: Path, cue: Cue) -> Path | None:
    exact = input_dir / cue.filename
    if exact.exists():
        return exact

    for extension in SUPPORTED_EXTENSIONS:
        candidate = input_dir / f"{cue.stem}{extension}"
        if candidate.exists():
            return candidate

    return None


def loudness_filter(cue: Cue) -> str:
    if cue.category in {"ambient", "music"}:
        return "loudnorm=I=-22:TP=-1.5:LRA=11"
    if cue.mode == "loop":
        return "loudnorm=I=-20:TP=-1.5:LRA=10"
    return "loudnorm=I=-18:TP=-1.5:LRA=8"


def convert_audio(source: Path, target: Path, cue: Cue, normalize: bool) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-i",
        str(source),
        "-ar",
        "48000",
        "-ac",
        "2",
    ]

    if normalize:
        command.extend(["-af", loudness_filter(cue)])

    if cue.suffix == ".m4a":
        command.extend(["-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart"])
    elif cue.suffix == ".wav":
        command.extend(["-c:a", "pcm_s16le"])
    else:
        raise ValueError(f"Unsupported target extension: {cue.suffix}")

    command.append(str(target))
    subprocess.run(command, check=True)


def copy_to_targets(source: Path, cue: Cue, targets: list[Path], normalize: bool, dry_run: bool) -> None:
    generated_target = AUDIO_GENERATED / cue.filename
    if dry_run:
        print(f"DRY {source.name} -> {generated_target.relative_to(ROOT)}")
    else:
        convert_audio(source, generated_target, cue, normalize)

    for target_dir in targets:
        target = target_dir / cue.filename
        if dry_run:
            print(f"DRY {generated_target.relative_to(ROOT)} -> {target.relative_to(ROOT)}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(generated_target, target)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import replacement audio files for Kraehenfels.")
    parser.add_argument("input_dir", type=Path, help="Folder containing replacement audio files.")
    parser.add_argument("--no-normalize", action="store_true", help="Skip FFmpeg loudness normalization.")
    parser.add_argument("--sync-web", action="store_true", help="Also copy converted files into web/assets/audio.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned imports without writing files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_dir = args.input_dir.resolve()
    if not input_dir.is_dir():
        print(f"Input folder does not exist: {input_dir}", file=sys.stderr)
        return 2

    if shutil.which("ffmpeg") is None:
        print("FFmpeg is required but was not found in PATH.", file=sys.stderr)
        return 2

    targets = [APP_AUDIO]
    if args.sync_web:
        targets.append(WEB_AUDIO)

    cues = load_cues()
    missing: list[str] = []
    imported = 0

    for cue in cues:
        source = find_source(input_dir, cue)
        if source is None:
            missing.append(cue.filename)
            continue
        copy_to_targets(source, cue, targets, normalize=not args.no_normalize, dry_run=args.dry_run)
        imported += 1

    print(f"Imported {imported} of {len(cues)} audio files")
    if missing:
        print("Missing files:")
        for filename in missing:
            print(f"  {filename}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
