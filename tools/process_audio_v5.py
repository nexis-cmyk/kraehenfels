#!/usr/bin/env python3
"""Build the native Krähenfels V5 audio bundle from reviewed candidates."""

from __future__ import annotations

import json
import shutil
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "_TMP" / "V5_candidates"
GENERATED = ROOT / "audio" / "generated"
APP_AUDIO = ROOT / "app" / "Kraehenfels" / "Resources" / "Audio"
METADATA_PATH = ROOT / "audio" / "v5" / "metadata.json"
LOCAL_FFMPEG = (
    ROOT
    / "_TMP"
    / "python-deps"
    / "imageio_ffmpeg"
    / "binaries"
    / "ffmpeg-win-x86_64-v7.1.exe"
)

# V6 replaces these twelve native files. V5 still processes them for the
# reviewed archive and similarity metadata, but must not copy them into the
# iOS resource bundle where they would be dead, ambiguous alternatives.
NATIVE_BASELINE_IDS = {"A03", "A04", "A06", "A07", "M01", "M02", "SFX03", "SFX07"}


@dataclass(frozen=True)
class Asset:
    cue_id: str
    title: str
    source: str
    target: str
    category: str
    target_lufs: float
    duration_seconds: int | None = None
    selected_variant: int = 1


ASSETS = [
    Asset("A01", "Kutschenstraße", "V5_A01_Kutschenstrasse_long.wav", "V5_A01_Kutschenstrasse.m4a", "ambient", -25),
    Asset("A02", "Gasthaus", "V5_A02_Gasthaus_long.wav", "V5_A02_Gasthaus.m4a", "ambient", -25),
    Asset("A03", "Krähenfels am Morgen", "V5_A03_Dorf_am_Morgen.mp3", "V5_A03_Dorf_am_Morgen.m4a", "ambient", -25),
    Asset("A04", "Kirche ohne Glocke", "V5_A04_Kirche_ohne_Glocke_long.wav", "V5_A04_Kirche_ohne_Glocke.m4a", "ambient", -25),
    Asset("A05", "Schmiede", "V5_A05_Schmiede.mp3", "V5_A05_Schmiede.m4a", "ambient", -25),
    Asset("A06", "Waldspur", "V5_A06_Waldspur.mp3", "V5_A06_Waldspur.m4a", "ambient", -25),
    Asset("A07", "Rathausarchiv", "V5_A07_Rathausarchiv.mp3", "V5_A07_Rathausarchiv.m4a", "ambient", -25),
    Asset("A08", "Alte Eiche", "V5_A08_Alte_Eiche_long.wav", "V5_A08_Alte_Eiche.m4a", "ambient", -25),
    Asset("M01", "Krähenfels-Motiv", "V5_M01_Kraehenfels_Motiv_long.wav", "V5_M01_Kraehenfels_Motiv.m4a", "musicBed", -27, 240),
    Asset("M02", "Die Prozession", "V5_M02_Prozession_long.wav", "V5_M02_Prozession.m4a", "musicLayer", -25, 90),
    Asset("SFX01", "Achse bricht", "V5_SFX01_Achse_bricht.wav", "V5_SFX01_Achse_bricht.wav", "sfx", -18),
    Asset("SFX02", "Pferde scheuen", "V5_SFX02_Pferde_scheuen.wav", "V5_SFX02_Pferde_scheuen.wav", "sfx", -18),
    Asset("SFX03", "Riegel von außen", "V5_SFX03_Riegel_von_aussen.wav", "V5_SFX03_Riegel_von_aussen.wav", "sfx", -18),
    Asset("SFX04", "Geweih an der Gasthaustür", "V5_SFX04_Geweih_an_der_Tuer.wav", "V5_SFX04_Geweih_an_der_Tuer.wav", "sfx", -18),
    Asset("SFX05", "Einzelner Schmiedeschlag", "V5_SFX05_Einzelner_Schmiedeschlag.wav", "V5_SFX05_Einzelner_Schmiedeschlag.wav", "sfx", -18),
    Asset("SFX06", "Atem hinter einer Figur", "V5_SFX06_Atem_hinter_der_Figur.wav", "V5_SFX06_Atem_hinter_der_Figur.wav", "sfx", -18),
    Asset("SFX07", "Prozessionsschritte", "V5_SFX07_Prozessionsschritte.wav", "V5_SFX07_Prozessionsschritte.wav", "sfx", -18),
    Asset("SFX08", "Knochenhirsch hebt den Kopf", "V5_SFX08_Knochenhirsch.wav", "V5_SFX08_Knochenhirsch.wav", "sfx", -18),
    Asset("SFX09", "Bindung reißt", "V5_SFX09_Bindung_reisst.wav", "V5_SFX09_Bindung_reisst.wav", "sfx", -18),
    Asset("SFX10", "Falscher Glockenschlag", "V5_SFX10_Falscher_Glockenschlag.wav", "V5_SFX10_Falscher_Glockenschlag.wav", "sfx", -18),
]


def ffmpeg_path() -> Path:
    if LOCAL_FFMPEG.exists():
        return LOCAL_FFMPEG
    system = shutil.which("ffmpeg")
    if system:
        return Path(system)
    raise SystemExit("FFmpeg is required. Run the documented local dependency setup first.")


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, text=True, capture_output=True)


def analyze_loudness(source: Path, target_lufs: float, should_loop: bool, duration: int | None) -> dict[str, str]:
    command = [str(ffmpeg_path()), "-hide_banner", "-nostats"]
    if should_loop:
        command.extend(["-stream_loop", "-1"])
    command.extend(["-i", str(source)])
    if duration:
        command.extend(["-t", str(duration)])
    command.extend(
        [
            "-af",
            f"loudnorm=I={target_lufs}:TP=-1.5:LRA=8:print_format=json",
            "-f",
            "null",
            "NUL",
        ]
    )
    result = run(command)
    start = result.stderr.rfind("{\n")
    end = result.stderr.rfind("}\n")
    if start < 0 or end < start:
        raise RuntimeError(f"No loudness report for {source.name}")
    return json.loads(result.stderr[start : end + 1])


def loudnorm_filter(target_lufs: float, report: dict[str, str]) -> str:
    return (
        f"loudnorm=I={target_lufs}:TP=-1.5:LRA=8:"
        f"measured_I={report['input_i']}:"
        f"measured_TP={report['input_tp']}:"
        f"measured_LRA={report['input_lra']}:"
        f"measured_thresh={report['input_thresh']}:"
        f"offset={report['target_offset']}:linear=true:print_format=summary"
    )


def seamless_source(asset: Asset, source: Path) -> Path:
    """Rotate and crossfade long generated beds so their loop boundary stays quiet."""
    if not source.name.endswith("_long.wav"):
        return source
    prepared = CANDIDATES / "prepared" / f"{asset.cue_id}.wav"
    prepared.parent.mkdir(parents=True, exist_ok=True)
    filter_graph = (
        "[0:a]asplit=3[tailin][headin][midin];"
        "[tailin]atrim=start=28:end=30,asetpts=PTS-STARTPTS[tail];"
        "[headin]atrim=start=0:end=2,asetpts=PTS-STARTPTS[head];"
        "[tail][head]acrossfade=d=2:c1=tri:c2=tri[seam];"
        "[midin]atrim=start=2:end=28,asetpts=PTS-STARTPTS[mid];"
        "[seam][mid]concat=n=2:v=0:a=1[out]"
    )
    run(
        [
            str(ffmpeg_path()),
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-filter_complex",
            filter_graph,
            "-map",
            "[out]",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "pcm_s24le",
            str(prepared),
        ]
    )
    return prepared


def process(asset: Asset) -> dict[str, object]:
    source = CANDIDATES / asset.source
    if not source.exists():
        raise FileNotFoundError(source)

    source = seamless_source(asset, source)
    target = GENERATED / asset.target
    target.parent.mkdir(parents=True, exist_ok=True)
    should_loop = asset.duration_seconds is not None
    report = analyze_loudness(source, asset.target_lufs, should_loop, asset.duration_seconds)

    command = [str(ffmpeg_path()), "-y", "-hide_banner", "-loglevel", "error"]
    if should_loop:
        command.extend(["-stream_loop", "-1"])
    command.extend(["-i", str(source)])
    if asset.duration_seconds:
        command.extend(["-t", str(asset.duration_seconds)])
    command.extend(["-ar", "48000", "-ac", "2", "-af", loudnorm_filter(asset.target_lufs, report)])
    if target.suffix == ".m4a":
        command.extend(["-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart"])
    else:
        command.extend(["-c:a", "pcm_s16le"])
    command.append(str(target))
    run(command)

    APP_AUDIO.mkdir(parents=True, exist_ok=True)
    if asset.cue_id in NATIVE_BASELINE_IDS:
        shutil.copy2(target, APP_AUDIO / target.name)
    return {
        "id": asset.cue_id,
        "title": asset.title,
        "source": asset.source,
        "file": asset.target,
        "category": asset.category,
        "targetLufs": asset.target_lufs,
        "provider": "ElevenLabs Sound Effects v2",
        "selectedVariant": asset.selected_variant,
    }


def write_test_tone() -> None:
    sample_rate = 48_000
    duration = 1.0
    frame_count = int(sample_rate * duration)
    time = np.arange(frame_count, dtype=np.float64) / sample_rate
    envelope = np.minimum(1.0, time / 0.03) * np.minimum(1.0, (duration - time) / 0.08)
    signal = 0.20 * envelope * np.sin(2 * np.pi * 880.0 * time)
    stereo = np.column_stack([signal, signal])
    pcm = np.int16(np.clip(stereo, -1, 1) * 32767)
    path = APP_AUDIO / "V5_TEST_Audio.wav"
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(pcm.tobytes())


def main() -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    APP_AUDIO.mkdir(parents=True, exist_ok=True)
    records = [process(asset) for asset in ASSETS]
    write_test_tone()
    METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    METADATA_PATH.write_text(
        json.dumps(
            {
                "version": "3.3.0",
                "scope": "native-ios-only",
                "generatedAt": "2026-08-12",
                "assets": records,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Built {len(records)} V5 audio assets and one self-test tone.")


if __name__ == "__main__":
    main()
