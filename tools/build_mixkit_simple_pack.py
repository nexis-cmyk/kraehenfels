#!/usr/bin/env python3
"""Build the 18-file Kraehenfels simple sound pack from Mixkit source files.

This keeps the downloadable source clips separate from the in-app files. Run
this after downloading the files listed in ``_DOCS/AUDIO-SOURCES.md``.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "_TMP" / "mixkit_audio"
DEFAULT_OUTPUT = ROOT / "audio" / "mixkit_simple_pack"


def run_ffmpeg(*arguments: str) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", *arguments],
        check=True,
    )


def render_clip(source: Path, target: Path, seconds: float, volume: float = 1.0) -> None:
    codec_arguments = ["-c:a", "pcm_s16le"] if target.suffix == ".wav" else ["-c:a", "aac", "-b:a", "160k"]
    run_ffmpeg(
        "-i", str(source),
        "-t", str(seconds),
        "-af", f"volume={volume},afade=t=in:st=0:d=0.08,afade=t=out:st={max(0, seconds - 0.35)}:d=0.35",
        "-ar", "48000", "-ac", "2", *codec_arguments,
        str(target),
    )


def render_graph(inputs: list[Path], target: Path, graph: str, seconds: float) -> None:
    command: list[str] = []
    for source in inputs:
        command.extend(["-i", str(source)])
    command.extend([
        "-filter_complex", graph,
        "-map", "[out]",
        "-t", str(seconds),
        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
        str(target),
    ])
    run_ffmpeg(*command)


def source(directory: Path, name: str) -> Path:
    path = directory / name
    if not path.exists():
        raise FileNotFoundError(f"Missing source clip: {path}")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Kraehenfels Mixkit simple sound pack.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    input_dir = arguments.input.resolve()
    output_dir = arguments.output.resolve()
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    wind = source(input_dir, "wind_forest.mp3")
    tomb = source(input_dir, "tomb_ambience.mp3")
    storm = source(input_dir, "storm_wind.mp3")
    bell = source(input_dir, "church_bell.mp3")
    low_bell = source(input_dir, "low_bell.mp3")
    snow_steps = source(input_dir, "snow_steps.mp3")
    tunnel_steps = source(input_dir, "tunnel_steps.mp3")
    breath = source(input_dir, "breath.mp3")
    wood_hit = source(input_dir, "wood_hit.mp3")
    door_creak = source(input_dir, "door_creak.mp3")
    branch = source(input_dir, "branch_break.mp3")
    gallop = source(input_dir, "horse_gallop.mp3")
    neigh = source(input_dir, "horse_neigh.mp3")
    impact = source(input_dir, "final_impact.mp3")
    water_ice = source(input_dir, "water_ice.mp3")
    music = source(input_dir, "forest_mist_music.mp3")

    render_clip(wind, output_dir / "LOOP01_Winterdorf_Wald.m4a", 25, 0.72)
    render_clip(tomb, output_dir / "LOOP02_Wirtsstube.m4a", 35, 0.28)
    render_clip(low_bell, output_dir / "LOOP03_Kapelle_Glockenturm.m4a", 40, 0.42)
    render_clip(tomb, output_dir / "LOOP04_Grube_Flutstollen.m4a", 40, 0.58)
    render_clip(storm, output_dir / "LOOP05_Finale_Froststurm.m4a", 45, 0.72)
    render_clip(music, output_dir / "MUSIC01_Dunkles_Grundthema.m4a", 90, 0.62)

    render_graph(
        [gallop, neigh, branch], output_dir / "SFX01_Kutschenunfall.wav",
        "[0:a]atrim=0:4,volume=0.85[g];[1:a]atrim=0:2,adelay=500|500,volume=0.8[n];[2:a]atrim=0:1,adelay=1650|1650,volume=1.05[b];[g][n][b]amix=inputs=3:normalize=0,alimiter=limit=0.92,afade=t=out:st=4.3:d=0.7[out]",
        5,
    )
    render_graph(
        [door_creak, branch], output_dir / "SFX02_Fenster_Ast.wav",
        "[0:a]atrim=0:2,volume=0.9[d];[1:a]atrim=0:1,adelay=900|900,volume=1.05[b];[d][b]amix=inputs=2:normalize=0,alimiter=limit=0.9,afade=t=out:st=2.6:d=0.4[out]",
        3,
    )
    render_clip(bell, output_dir / "SFX03_Glocke_Normal.wav", 7, 0.85)
    render_graph(
        [bell], output_dir / "SFX04_Glocke_Falsch.wav",
        "[0:a]atrim=0:6,asetrate=48000*0.89,aresample=48000,aecho=0.8:0.45:190:0.35,volume=0.78,afade=t=out:st=6.4:d=0.6[out]",
        7,
    )
    render_graph(
        [bell], output_dir / "SFX05_Metall_Kloeppel.wav",
        "[0:a]atrim=0:1.2,highpass=f=180,volume=0.8,afade=t=out:st=1.4:d=0.6[out]",
        2,
    )
    render_clip(snow_steps, output_dir / "SFX06_Schritte_Schnee.wav", 10, 0.95)
    render_graph(
        [tunnel_steps], output_dir / "SFX07_Barfuss_Schritte.wav",
        "[0:a]atrim=0:7,asetrate=48000*0.82,aresample=48000,lowpass=f=3500,volume=0.78,afade=t=out:st=7.5:d=0.5[out]",
        8,
    )
    render_graph(
        [storm, breath], output_dir / "SFX08_Stimmen_Berg.wav",
        "[0:a]atrim=0:8,volume=0.25[w];[1:a]atrim=0:5,asetrate=48000*0.72,aresample=48000,lowpass=f=1800,adelay=1200|1200,volume=0.35[v];[w][v]amix=inputs=2:normalize=0,aecho=0.75:0.35:220:0.28,afade=t=out:st=8.4:d=0.6[out]",
        9,
    )
    render_graph(
        [wood_hit], output_dir / "SFX09_Klopfen_Boden.wav",
        "[0:a]atrim=0:1,asplit=3[k1][k2][k3];[k1]adelay=0|0[a];[k2]adelay=720|720[b];[k3]adelay=1540|1540[c];[a][b][c]amix=inputs=3:normalize=0,aecho=0.75:0.25:90:0.2,afade=t=out:st=2.7:d=0.3[out]",
        3,
    )
    render_clip(breath, output_dir / "SFX10_Atem_Nah.wav", 5, 0.78)
    render_graph(
        [storm, breath], output_dir / "SFX11_Weisse_Frau_Motiv.wav",
        "[0:a]atrim=0:7,volume=0.42[w];[1:a]atrim=0:5,asetrate=48000*0.84,aresample=48000,adelay=1150|1150,volume=0.35[b];[w][b]amix=inputs=2:normalize=0,aecho=0.75:0.35:280:0.25,afade=t=out:st=7.4:d=0.6[out]",
        8,
    )
    render_graph(
        [impact, water_ice], output_dir / "SFX12_Eisbruch_Finale.wav",
        "[0:a]atrim=0:5,asetrate=48000*0.82,aresample=48000,volume=0.75[i];[1:a]atrim=0:7,adelay=400|400,volume=0.7[w];[i][w]amix=inputs=2:normalize=0,aecho=0.75:0.25:160:0.2,alimiter=limit=0.92,afade=t=out:st=7.3:d=0.7[out]",
        8,
    )

    print(f"Built {len(list(output_dir.iterdir()))} files in {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
