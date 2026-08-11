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
SIMPLE_SILENCE = "__silence_2s__"
SIMPLE_PACK_MAP = {
    "LOOP01_Winterdorf_Wald": [
        "A01_Postkutsche_im_Schneesturm.m4a",
        "A03_Kraehenfels_bei_Tag.m4a",
        "A05_Dorf_nach_Mitternacht.m4a",
        "A07_Weisse_Spur_im_Wald.m4a",
    ],
    "LOOP02_Wirtsstube": [
        "A04_Wirtsstube_am_Abend.m4a",
    ],
    "LOOP03_Kapelle_Glockenturm": [
        "A06_Kapelle_und_Friedhof.m4a",
    ],
    "LOOP04_Grube_Flutstollen": [
        "A09_Grubenluft_Layer.m4a",
        "SFX26_Wasser_im_Flutstollen.wav",
    ],
    "LOOP05_Finale_Froststurm": [
        "A08_Finale_Froststurm.m4a",
        "A10_Frostspannung_Layer.m4a",
    ],
    "MUSIC01_Dunkles_Grundthema": [
        "M01_Ankunft_in_Kraehenfels.m4a",
        "M02_Das_Dorf_verschweigt_etwas.m4a",
        "M03_Die_Weisse_Frau_naht.m4a",
        "M05_Frost_und_Opfer.m4a",
        "M06_Tauwetter_Epilog.m4a",
    ],
    "SFX01_Kutschenunfall": [
        "SFX01_Achse_bricht.wav",
        "SFX02_Pferde_scheuen.wav",
        "SFX03_Hufe_im_Schnee.wav",
    ],
    "SFX02_Fenster_Ast": [
        "SFX04_Astbruch.wav",
        "SFX23_Fensterladen_im_Wind.wav",
        "SFX25_Holz_unter_Spannung.wav",
    ],
    "SFX03_Glocke_Normal": [
        "SFX07_Glocke_normal.wav",
        "SFX24_Fernes_Laeuten.wav",
    ],
    "SFX04_Glocke_Falsch": [
        "SFX08_Glocke_falsch.wav",
        "SFX29_Glockenresonanz.wav",
    ],
    "SFX05_Metall_Kloeppel": [
        "SFX10_Metall_vibriert.wav",
        "SFX17_Kloeppel_schlaegt.wav",
    ],
    "SFX06_Schritte_Schnee": [
        "SFX11_Schritte.wav",
        "SFX27_Wiederhallende_Schritte.wav",
    ],
    "SFX07_Barfuss_Schritte": [
        "SFX12_Barfuss_Schritte.wav",
    ],
    "SFX08_Stimmen_Berg": [
        "SFX13_Stimmen_ohne_Worte.wav",
    ],
    "SFX09_Klopfen_Boden": [
        "SFX14_Schlaege_unter_Boden.wav",
        "SFX28_Klopfen_unter_Boden.wav",
    ],
    "SFX10_Atem_Nah": [
        "SFX15_Atem_hinter_dir.wav",
        "SFX30_Atem_im_Raum.wav",
    ],
    "SFX11_Weisse_Frau_Motiv": [
        "M04_Ihr_altes_Lied.m4a",
        "SFX16_Weisse_Frau_Motiv.wav",
    ],
    "SFX12_Eisbruch_Finale": [
        "SFX18_Frost_breitet_sich_aus.wav",
        "SFX19_Herzschlag.wav",
        "SFX20_Eisbruch.wav",
        "SFX21_Bannung.wav",
        "SFX22_Scheitern.wav",
        "SFX31_Resonanzabbruch.wav",
    ],
    SIMPLE_SILENCE: [
        "SFX05_Kraehen.wav",
        "SFX06_Stille.wav",
        "SFX09_Schmiede.wav",
    ],
}


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


def find_source_by_stem(input_dir: Path, stem: str) -> Path | None:
    for extension in SUPPORTED_EXTENSIONS:
        candidate = input_dir / f"{stem}{extension}"
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


def create_silence(target: Path, cue: Cue) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-f",
        "lavfi",
        "-i",
        "anullsrc=r=48000:cl=stereo",
        "-t",
        "2",
    ]

    if cue.suffix == ".m4a":
        command.extend(["-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart"])
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


def copy_silence_to_targets(cue: Cue, targets: list[Path], dry_run: bool) -> None:
    generated_target = AUDIO_GENERATED / cue.filename
    if dry_run:
        print(f"DRY silence -> {generated_target.relative_to(ROOT)}")
    else:
        create_silence(generated_target, cue)

    for target_dir in targets:
        target = target_dir / cue.filename
        if dry_run:
            print(f"DRY {generated_target.relative_to(ROOT)} -> {target.relative_to(ROOT)}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(generated_target, target)


def simple_pack_plan(cues: list[Cue]) -> list[tuple[str, Cue]]:
    by_filename = {cue.filename: cue for cue in cues}
    plan: list[tuple[str, Cue]] = []
    seen: set[str] = set()

    for source_stem, filenames in SIMPLE_PACK_MAP.items():
        for filename in filenames:
            cue = by_filename.get(filename)
            if cue is None:
                raise ValueError(f"Simple pack target is not in manifest: {filename}")
            if filename in seen:
                raise ValueError(f"Simple pack target is mapped twice: {filename}")
            seen.add(filename)
            plan.append((source_stem, cue))

    missing = sorted(set(by_filename) - seen)
    if missing:
        raise ValueError("Simple pack map does not cover: " + ", ".join(missing))

    return plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import replacement audio files for Kraehenfels.")
    parser.add_argument("input_dir", type=Path, help="Folder containing replacement audio files.")
    parser.add_argument("--no-normalize", action="store_true", help="Skip FFmpeg loudness normalization.")
    parser.add_argument("--simple-pack", action="store_true", help="Use the reduced 5 loops, 1 music track and 12 SFX input names.")
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

    if args.simple_pack:
        plan = simple_pack_plan(cues)
        for source_stem, cue in plan:
            if source_stem == SIMPLE_SILENCE:
                copy_silence_to_targets(cue, targets, dry_run=args.dry_run)
                imported += 1
                continue
            source = find_source_by_stem(input_dir, source_stem)
            if source is None:
                missing.append(source_stem)
                continue
            copy_to_targets(source, cue, targets, normalize=not args.no_normalize, dry_run=args.dry_run)
            imported += 1
    else:
        for cue in cues:
            source = find_source(input_dir, cue)
            if source is None:
                missing.append(cue.filename)
                continue
            copy_to_targets(source, cue, targets, normalize=not args.no_normalize, dry_run=args.dry_run)
            imported += 1

    if args.simple_pack and missing:
        missing = sorted(set(missing))

    if not args.simple_pack:
        label = "audio files"
    else:
        label = "manifest target files from the simple pack"

    print(f"Imported {imported} of {len(cues)} {label}")
    if missing:
        print("Missing files:")
        for filename in missing:
            print(f"  {filename}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
