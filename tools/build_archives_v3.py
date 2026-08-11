#!/usr/bin/env python3
"""Build the shareable V3 print and audio archives."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs"


def write_archive(path: Path, files: list[Path], base: Path) -> None:
    with ZipFile(path, "w", compression=ZIP_DEFLATED, compresslevel=8) as archive:
        for file in sorted(files):
            archive.write(file, file.relative_to(base).as_posix())


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    print_files = [
        OUTPUT / name
        for name in (
            "00_Spielstart.pdf",
            "Einladung_Kraehenfels.pdf",
            "01_Karte_Spieler.pdf",
            "01_Karte_SL.pdf",
            "01_Karten_Detail.pdf",
            "02_Handouts.pdf",
            "03_Figurenbau.pdf",
            "10_SL_Abenteuer.pdf",
            "11_SL_Schnellreferenz.pdf",
            "12_SL_Am_Tisch.pdf",
            "13_SL_Spoiler-Handouts.pdf",
            "14_Soundboard-Cues.pdf",
        )
    ]
    missing = [file.name for file in print_files if not file.exists()]
    if missing:
        raise SystemExit(f"Missing print outputs: {', '.join(missing)}")
    write_archive(OUTPUT / "Kraehenfels-Druckpaket.zip", print_files, OUTPUT)

    audio_files = [ROOT / "audio" / "generated" / file.name for file in (ROOT / "app" / "Kraehenfels" / "Resources" / "Audio").glob("V3_*")]
    missing_audio = [file.name for file in audio_files if not file.exists()]
    if missing_audio:
        raise SystemExit(f"Missing generated audio: {', '.join(missing_audio)}")
    write_archive(OUTPUT / "Kraehenfels-Audio.zip", audio_files, ROOT / "audio" / "generated")
    print(f"Wrote {len(print_files)} print files and {len(audio_files)} audio files")


if __name__ == "__main__":
    main()
