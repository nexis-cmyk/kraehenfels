"""Render the compact, distinct Krähenfels 3.0 audio set."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "_TMP" / "mixkit_audio"
OUT = ROOT / "audio" / "generated"
BUNDLES = [ROOT / "app" / "Kraehenfels" / "Resources" / "Audio", ROOT / "web" / "assets" / "audio"]


def run(*args: str) -> None:
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args]
    subprocess.run(command, check=True)


def render_loop(name: str, inputs: list[str], graph: str, seconds: int) -> None:
    args: list[str] = []
    for item in inputs:
        args.extend(["-stream_loop", "-1", "-i", str(SRC / item)])
    args.extend(["-filter_complex", graph, "-map", "[mix]", "-t", str(seconds), "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "160k", str(OUT / name)])
    run(*args)


def render_shot(name: str, inputs: list[str], graph: str, seconds: float) -> None:
    args: list[str] = []
    for item in inputs:
        args.extend(["-i", str(SRC / item)])
    args.extend(["-filter_complex", graph, "-map", "[mix]", "-t", str(seconds), "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(OUT / name)])
    run(*args)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    render_loop("V3_A01_Kutschenstrasse.m4a", ["wind_forest.mp3", "horse_gallop.mp3"], "[0:a]volume=0.48,highpass=f=65,lowpass=f=5200[a];[1:a]volume=0.08,lowpass=f=1800[b];[a][b]amix=inputs=2:duration=longest:dropout_transition=2,alimiter=limit=0.85[mix]", 36)
    render_loop("V3_A02_Gasthaus.m4a", ["tomb_ambience.mp3", "door_creak.mp3"], "[0:a]volume=0.3,lowpass=f=3900[a];[1:a]volume=0.035,highpass=f=170,lowpass=f=2600,adelay=7000|7000[b];[a][b]amix=inputs=2:duration=longest,alimiter=limit=0.85[mix]", 40)
    render_loop("V3_A03_Dorf.m4a", ["wind_forest.mp3", "wood_hit.mp3"], "[0:a]volume=0.35,highpass=f=100,lowpass=f=6800[a];[1:a]volume=0.018,adelay=12000|12000[b];[a][b]amix=inputs=2:duration=longest,alimiter=limit=0.85[mix]", 36)
    render_loop("V3_A04_Kirche.m4a", ["tomb_ambience.mp3", "low_bell.mp3"], "[0:a]volume=0.22,lowpass=f=3000[a];[1:a]volume=0.08,lowpass=f=1600,adelay=18000|18000[b];[a][b]amix=inputs=2:duration=longest,alimiter=limit=0.85[mix]", 42)
    render_loop("V3_A05_Waldspur.m4a", ["wind_forest.mp3", "tunnel_steps.mp3", "breath.mp3"], "[0:a]volume=0.44,highpass=f=150,lowpass=f=7200[a];[1:a]volume=0.12,highpass=f=110,lowpass=f=2400[b];[2:a]volume=0.025,lowpass=f=1800,adelay=15000|15000[c];[a][b][c]amix=inputs=3:duration=longest,alimiter=limit=0.82[mix]", 38)
    render_loop("V3_A06_Alte_Eiche.m4a", ["storm_wind.mp3", "wood_hit.mp3", "breath.mp3"], "[0:a]volume=0.42,lowpass=f=5200[a];[1:a]volume=0.035,lowpass=f=1100,adelay=9000|9000[b];[2:a]volume=0.035,lowpass=f=1600,adelay=19000|19000[c];[a][b][c]amix=inputs=3:duration=longest,alimiter=limit=0.8[mix]", 42)
    render_loop("V3_M01_Verdacht.m4a", ["forest_mist_music.mp3"], "[0:a]volume=0.28,lowpass=f=1100,highpass=f=55,aecho=0.8:0.7:700:0.18,alimiter=limit=0.75[mix]", 84)
    render_loop("V3_M02_Prozession.m4a", ["forest_mist_music.mp3", "low_bell.mp3"], "[0:a]volume=0.2,lowpass=f=850,highpass=f=45,aecho=0.8:0.7:500:0.2[a];[1:a]volume=0.06,lowpass=f=900,adelay=18000|18000[b];[a][b]amix=inputs=2:duration=longest,alimiter=limit=0.72[mix]", 86)

    render_shot("V3_SFX01_Achse.wav", ["branch_break.mp3", "wood_hit.mp3"], "[0:a]volume=0.9,lowpass=f=4800,afade=t=out:st=1.7:d=0.8[a];[1:a]volume=0.45,adelay=120|120,afade=t=out:st=1.8:d=0.6[b];[a][b]amix=inputs=2:duration=longest,alimiter=limit=0.82[mix]", 2.6)
    render_shot("V3_SFX02_Pferde.wav", ["horse_neigh.mp3", "horse_gallop.mp3"], "[0:a]volume=0.78,highpass=f=90,afade=t=out:st=2.5:d=0.8[a];[1:a]volume=0.3,highpass=f=70,lowpass=f=2500,afade=t=out:st=2.3:d=0.8[b];[a][b]amix=inputs=2:duration=longest,alimiter=limit=0.82[mix]", 3.3)
    render_shot("V3_SFX03_Riegel.wav", ["door_creak.mp3", "wood_hit.mp3"], "[0:a]volume=0.8,lowpass=f=4600,afade=t=out:st=2.0:d=0.7[a];[1:a]volume=0.7,adelay=900|900,afade=t=out:st=1.8:d=0.8[b];[a][b]amix=inputs=2:duration=longest,alimiter=limit=0.82[mix]", 2.8)
    render_shot("V3_SFX04_Geweih.wav", ["branch_break.mp3", "wood_hit.mp3"], "[0:a]volume=0.65,asetrate=52000,aresample=48000,lowpass=f=3300,adelay=500|500[a];[1:a]volume=0.24,highpass=f=180,adelay=1200|1200[b];[a][b]amix=inputs=2:duration=longest,aecho=0.8:0.6:370:0.25,alimiter=limit=0.78[mix]", 3.4)
    render_shot("V3_SFX05_Schmiedeschlag.wav", ["church_bell.mp3", "wood_hit.mp3"], "[0:a]volume=0.3,lowpass=f=4200,afade=t=out:st=4.0:d=1.5[a];[1:a]volume=0.55,adelay=40|40,afade=t=out:st=1.0:d=0.8[b];[a][b]amix=inputs=2:duration=longest,aecho=0.8:0.7:500:0.26,alimiter=limit=0.8[mix]", 5.4)
    render_shot("V3_SFX06_Stimme.wav", ["breath.mp3", "tunnel_steps.mp3"], "[0:a]volume=0.35,lowpass=f=2200,asetrate=44000,aresample=48000,aecho=0.8:0.65:260:0.45[a];[1:a]volume=0.14,adelay=700|700,lowpass=f=1900[b];[a][b]amix=inputs=2:duration=longest,alimiter=limit=0.78[mix]", 4.5)
    render_shot("V3_SFX07_Prozession.wav", ["snow_steps.mp3", "wood_hit.mp3"], "[0:a]volume=0.55,lowpass=f=2600,adelay=0|0[a];[1:a]volume=0.25,lowpass=f=1000,adelay=1600|1600[b];[a][b]amix=inputs=2:duration=longest,aecho=0.8:0.75:420:0.3,alimiter=limit=0.8[mix]", 6.0)
    render_shot("V3_SFX08_Knochenhirsch.wav", ["breath.mp3", "branch_break.mp3", "snow_steps.mp3"], "[0:a]volume=0.38,lowpass=f=1700,aecho=0.8:0.7:550:0.3[a];[1:a]volume=0.5,adelay=1100|1100,lowpass=f=3100[b];[2:a]volume=0.24,adelay=2200|2200,lowpass=f=1800[c];[a][b][c]amix=inputs=3:duration=longest,alimiter=limit=0.78[mix]", 5.2)
    render_shot("V3_SFX09_Bindung.wav", ["final_impact.mp3", "water_ice.mp3"], "[0:a]volume=0.48,lowpass=f=3000,afade=t=out:st=2.3:d=1.8[a];[1:a]volume=0.35,adelay=900|900,lowpass=f=4200,afade=t=out:st=2.7:d=1.7[b];[a][b]amix=inputs=2:duration=longest,alimiter=limit=0.78[mix]", 5.0)
    render_shot("V3_SFX10_Waldatem.wav", ["wind_forest.mp3", "breath.mp3"], "[0:a]volume=0.36,lowpass=f=2200,afade=t=out:st=3.5:d=1.5[a];[1:a]volume=0.2,lowpass=f=1450,adelay=1000|1000,afade=t=out:st=3.4:d=1.4[b];[a][b]amix=inputs=2:duration=longest,aecho=0.8:0.65:430:0.22,alimiter=limit=0.78[mix]", 5.0)

    for bundle in BUNDLES:
        bundle.mkdir(parents=True, exist_ok=True)
        for file in OUT.glob("V3_*"):
            shutil.copy2(file, bundle / file.name)
    print(f"Built {len(list(OUT.glob('V3_*')))} V3 audio files")


if __name__ == "__main__":
    main()
