#!/usr/bin/env python3
"""Assemble the approved V6 cue replacements from the local source pack.

The eight cues that passed the listening check keep their V5 files. This tool
only creates the twelve replacement files and mirrors them into the native
bundle, so the manifest can be audited without relying on a network service.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "audio" / "generated"
BUNDLED = ROOT / "app" / "Kraehenfels" / "Resources" / "Audio"
V5_METADATA = ROOT / "audio" / "v5" / "metadata.json"
V6_METADATA = ROOT / "audio" / "v6" / "metadata.json"

REPLACEMENTS = {
    "A01": "V6_A01_Kutschenstrasse.m4a",
    "A02": "V6_A02_Gasthaus.m4a",
    "A05": "V6_A05_Schmiede.m4a",
    "A08": "V6_A08_Alte_Eiche.m4a",
    "SFX01": "V6_SFX01_Achse_bricht.wav",
    "SFX02": "V6_SFX02_Pferde_scheuen.wav",
    "SFX04": "V6_SFX04_Geweih_an_der_Tuer.wav",
    "SFX05": "V6_SFX05_Einzelner_Schmiedeschlag.wav",
    "SFX06": "V6_SFX06_Atem_hinter_der_Figur.wav",
    "SFX08": "V6_SFX08_Knochenhirsch.wav",
    "SFX09": "V6_SFX09_Bindung_reisst.wav",
    "SFX10": "V6_SFX10_Falscher_Glockenschlag.wav",
}

# These reviewed V5 cues remain the canonical files for the eight cues that
# did not need a V6 replacement. They are mirrored explicitly so a clean
# native bundle cannot accidentally depend on legacy files left in the
# resource directory.
BASELINE_FILES = (
    "V5_A03_Dorf_am_Morgen.m4a",
    "V5_A04_Kirche_ohne_Glocke.m4a",
    "V5_A06_Waldspur.m4a",
    "V5_A07_Rathausarchiv.m4a",
    "V5_M01_Kraehenfels_Motiv.m4a",
    "V5_M02_Prozession.m4a",
    "V5_SFX03_Riegel_von_aussen.wav",
    "V5_SFX07_Prozessionsschritte.wav",
)


def run_ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def copy_asset(source: str, target: str) -> None:
    source_path = Path(source)
    target_path = GENERATED / target
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, target_path)
    shutil.copy2(target_path, BUNDLED / target)


def mirror_baseline_assets() -> None:
    for filename in BASELINE_FILES:
        source = GENERATED / filename
        if not source.exists():
            raise FileNotFoundError(f"Missing reviewed baseline audio: {source}")
        shutil.copy2(source, BUNDLED / filename)


def normalize_asset(source: str, target: str, target_lufs: float, duration: float | None = None, audio_filter: str | None = None) -> None:
    target_path = GENERATED / target
    filter_chain = []
    if audio_filter:
        filter_chain.append(audio_filter)
    filter_chain.append(f"loudnorm=I={target_lufs}:TP=-1.5:LRA=8")
    args = ["-i", source]
    if duration is not None:
        args.extend(["-t", str(duration)])
    args.extend(["-ar", "48000", "-ac", "2", "-af", ",".join(filter_chain)])
    if target_path.suffix == ".m4a":
        args.extend(["-c:a", "aac", "-b:a", "192k"])
    else:
        args.extend(["-c:a", "pcm_s16le"])
    args.append(str(target_path))
    run_ffmpeg("-y", *args)
    shutil.copy2(target_path, BUNDLED / target_path.name)


def forge_atmosphere() -> None:
    source = GENERATED / "SFX17_Kloeppel_schlaegt.wav"
    air = GENERATED / "A09_Grubenluft_Layer.m4a"
    target = GENERATED / "V6_A05_Schmiede.m4a"
    run_ffmpeg(
        "-i", str(air),
        "-stream_loop", "-1", "-i", str(source),
        "-filter_complex", "[0:a]volume=0.55,lowpass=f=950[air];[1:a]volume=0.24,highpass=f=450,lowpass=f=5200[metal];[air][metal]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.88,afade=t=out:st=29:d=1,loudnorm=I=-25:TP=-1.5:LRA=8[out]",
        "-map", "[out]", "-t", "30", "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "192k", str(target),
    )
    shutil.copy2(target, BUNDLED / target.name)


def bone_deer() -> None:
    creature = GENERATED / "SFX16_Weisse_Frau_Motiv.wav"
    wood = GENERATED / "SFX25_Holz_unter_Spannung.wav"
    target = GENERATED / "V6_SFX08_Knochenhirsch.wav"
    run_ffmpeg(
        "-i", str(creature), "-i", str(wood),
        "-filter_complex", "[0:a]asetrate=48000*0.72,aresample=48000,lowpass=f=2400,volume=0.72[a];[1:a]lowpass=f=1200,volume=0.5[b];[a][b]amix=inputs=2:duration=longest:normalize=0,aecho=0.7:0.28:180:0.22,alimiter=limit=0.9,afade=t=out:st=7.5:d=0.7,loudnorm=I=-18:TP=-1.5:LRA=8[out]",
        "-map", "[out]", "-t", "8", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(target),
    )
    shutil.copy2(target, BUNDLED / target.name)


def write_metadata() -> None:
    metadata = json.loads(V5_METADATA.read_text(encoding="utf-8"))
    metadata["version"] = "3.3.0"
    metadata["generatedAt"] = "2026-08-12"
    for asset in metadata["assets"]:
        replacement = REPLACEMENTS.get(asset["id"])
        if replacement:
            asset["file"] = replacement
            asset["source"] = "deterministic local V6 assembly"
            asset["provider"] = "Local deterministic assembly"
            asset["selectedVariant"] = 1
    V6_METADATA.parent.mkdir(parents=True, exist_ok=True)
    V6_METADATA.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    mirror_baseline_assets()
    normalize_asset(str(GENERATED / "A01_Postkutsche_im_Schneesturm.m4a"), "V6_A01_Kutschenstrasse.m4a", -25)
    normalize_asset(str(GENERATED / "A04_Wirtsstube_am_Abend.m4a"), "V6_A02_Gasthaus.m4a", -25, duration=30)
    forge_atmosphere()
    normalize_asset(str(GENERATED / "A08_Finale_Froststurm.m4a"), "V6_A08_Alte_Eiche.m4a", -25, duration=30)
    normalize_asset(str(ROOT / "audio" / "mixkit_simple_pack" / "SFX01_Kutschenunfall.wav"), "V6_SFX01_Achse_bricht.wav", -18, audio_filter="lowpass=f=3200")
    normalize_asset(str(GENERATED / "SFX03_Hufe_im_Schnee.wav"), "V6_SFX02_Pferde_scheuen.wav", -18, audio_filter="highpass=f=350,lowpass=f=6000,aecho=0.6:0.35:80:0.15")
    normalize_asset(str(GENERATED / "SFX25_Holz_unter_Spannung.wav"), "V6_SFX04_Geweih_an_der_Tuer.wav", -18, audio_filter="volume=3,alimiter=limit=0.85,highpass=f=160")
    normalize_asset(str(GENERATED / "SFX17_Kloeppel_schlaegt.wav"), "V6_SFX05_Einzelner_Schmiedeschlag.wav", -18)
    normalize_asset(str(GENERATED / "SFX30_Atem_im_Raum.wav"), "V6_SFX06_Atem_hinter_der_Figur.wav", -18)
    bone_deer()
    normalize_asset(str(GENERATED / "SFX31_Resonanzabbruch.wav"), "V6_SFX09_Bindung_reisst.wav", -18)
    normalize_asset(str(GENERATED / "SFX08_Glocke_falsch.wav"), "V6_SFX10_Falscher_Glockenschlag.wav", -18)
    write_metadata()
    print("Built and bundled 12 V6 audio replacements and metadata.")


if __name__ == "__main__":
    main()
