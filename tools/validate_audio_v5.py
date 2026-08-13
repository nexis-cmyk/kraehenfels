#!/usr/bin/env python3
"""Run deterministic technical QA for the native Krähenfels V6 audio set."""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "app" / "Kraehenfels" / "Resources" / "Audio"
METADATA = ROOT / "audio" / "v6" / "metadata.json"
REPORT_JSON = ROOT / "_TMP" / "audio-v6-report.json"
REPORT_MD = ROOT / "_DOCS" / "AUDIO-V6-QA.md"
FFMPEG = (
    ROOT
    / "_TMP"
    / "python-deps"
    / "imageio_ffmpeg"
    / "binaries"
    / "ffmpeg-win-x86_64-v7.1.exe"
)


@dataclass(frozen=True)
class Measurement:
    cue_id: str
    file: str
    duration: float
    sample_rate: int
    channels: int
    integrated_lufs: float
    true_peak: float
    max_sample: float
    clipped_samples: int
    seam_ratio: float | None
    fingerprint: list[float]
    sha256: str
    passed: bool
    notes: list[str]


def command(args: list[str], binary: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(FFMPEG), *args],
        check=True,
        capture_output=True,
        text=not binary,
    )


def probe(path: Path) -> tuple[float, int, int]:
    result = command(["-hide_banner", "-i", str(path), "-f", "null", "NUL"])
    text = result.stderr
    duration_match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", text)
    audio_match = re.search(r"Audio:.*?,\s*(\d+) Hz,\s*([^,]+)", text)
    if not duration_match or not audio_match:
        raise RuntimeError(f"Cannot probe {path.name}")
    hours, minutes, seconds = duration_match.groups()
    duration = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    sample_rate = int(audio_match.group(1))
    layout = audio_match.group(2).strip()
    channels = 1 if layout == "mono" else 2 if layout == "stereo" else 0
    return duration, sample_rate, channels


def loudness(path: Path) -> tuple[float, float]:
    result = command(
        [
            "-hide_banner",
            "-nostats",
            "-i",
            str(path),
            "-af",
            "loudnorm=I=-23:TP=-1.5:LRA=8:print_format=json",
            "-f",
            "null",
            "NUL",
        ]
    )
    start = result.stderr.rfind("{\n")
    end = result.stderr.rfind("}\n")
    if start < 0 or end < start:
        raise RuntimeError(f"No loudness report for {path.name}")
    report = json.loads(result.stderr[start : end + 1])
    return float(report["input_i"]), float(report["input_tp"])


def decode(path: Path, sample_rate: int = 8_000) -> np.ndarray:
    result = command(
        [
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(path),
            "-ac",
            "1",
            "-ar",
            str(sample_rate),
            "-f",
            "f32le",
            "pipe:1",
        ],
        binary=True,
    )
    return np.frombuffer(result.stdout, dtype="<f4")


def feature_vector(samples: np.ndarray, sample_rate: int = 8_000) -> list[float]:
    if samples.size == 0:
        return [0.0] * 14
    window_size = sample_rate
    windows = []
    for start in range(0, min(samples.size, sample_rate * 240), window_size):
        frame = samples[start : start + window_size]
        if frame.size < window_size // 4:
            continue
        frame = frame * np.hanning(frame.size)
        spectrum = np.abs(np.fft.rfft(frame)) + 1e-9
        freqs = np.fft.rfftfreq(frame.size, 1 / sample_rate)
        total = float(np.sum(spectrum))
        centroid = float(np.sum(freqs * spectrum) / total) / (sample_rate / 2)
        flatness = float(np.exp(np.mean(np.log(spectrum))) / np.mean(spectrum))
        rms = float(np.sqrt(np.mean(frame * frame)))
        zcr = float(np.mean(np.diff(np.signbit(frame))))
        bands = []
        for low, high in ((0, 200), (200, 800), (800, 2_000), (2_000, 4_000)):
            mask = (freqs >= low) & (freqs < high)
            bands.append(float(np.sum(spectrum[mask]) / total))
        windows.append([rms, zcr, centroid, flatness, *bands])
    array = np.asarray(windows or [[0.0] * 8], dtype=np.float64)
    return np.concatenate([array.mean(axis=0), array.std(axis=0)[:6]]).tolist()


def cosine(left: list[float], right: list[float]) -> float:
    a = np.asarray(left, dtype=np.float64)
    b = np.asarray(right, dtype=np.float64)
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denominator) if denominator else 0.0


def measure(record: dict[str, object]) -> Measurement:
    cue_id = str(record["id"])
    filename = str(record["file"])
    category = str(record["category"])
    target_lufs = float(record["targetLufs"])
    path = AUDIO / filename
    notes: list[str] = []
    duration, sample_rate, channels = probe(path)
    integrated, true_peak = loudness(path)
    samples = decode(path)
    max_sample = float(np.max(np.abs(samples))) if samples.size else 0.0
    clipped = int(np.count_nonzero(np.abs(samples) >= 0.999))
    seam_ratio = None
    if category in {"ambient", "musicBed", "musicLayer"} and samples.size > 100:
        rms = float(np.sqrt(np.mean(samples * samples))) + 1e-8
        seam_ratio = float(abs(float(samples[-1] - samples[0])) / rms)

    if sample_rate != 48_000:
        notes.append(f"sample rate {sample_rate} Hz")
    if channels != 2:
        notes.append(f"channel count {channels}")
    loudness_tolerance = 3.5 if category == "sfx" else 1.2
    if abs(integrated - target_lufs) > loudness_tolerance:
        notes.append(f"loudness {integrated:.1f} LUFS, target {target_lufs:.1f}")
    if true_peak > -1.0:
        notes.append(f"true peak {true_peak:.1f} dBTP")
    if max_sample < 0.003:
        notes.append("practically silent")
    # The decoded 8 kHz analysis stream can touch full scale during resampling.
    # True-peak measurement above is the authoritative clipping gate.
    if seam_ratio is not None and seam_ratio > 4.5:
        notes.append(f"loop seam ratio {seam_ratio:.2f}")
    if cue_id == "M01" and not 239 <= duration <= 241:
        notes.append(f"music bed duration {duration:.2f}s")
    if cue_id == "M02" and not 89 <= duration <= 91:
        notes.append(f"music layer duration {duration:.2f}s")
    if cue_id.startswith("A") and not 2 <= duration <= 31:
        notes.append(f"ambient duration {duration:.2f}s")
    if cue_id.startswith("SFX") and not 0.4 <= duration <= 30:
        notes.append(f"one-shot duration {duration:.2f}s")

    return Measurement(
        cue_id=cue_id,
        file=filename,
        duration=duration,
        sample_rate=sample_rate,
        channels=channels,
        integrated_lufs=integrated,
        true_peak=true_peak,
        max_sample=max_sample,
        clipped_samples=clipped,
        seam_ratio=seam_ratio,
        fingerprint=feature_vector(samples),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        passed=not notes,
        notes=notes,
    )


def main() -> None:
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    measurements = [measure(record) for record in metadata["assets"]]
    duplicates = []
    for index, left in enumerate(measurements):
        for right in measurements[index + 1 :]:
            if left.sha256 == right.sha256:
                duplicates.append({"left": left.cue_id, "right": right.cue_id, "similarity": 1.0, "exact": True})
                continue
            similarity = cosine(left.fingerprint, right.fingerprint)
            if similarity >= 0.9985:
                duplicates.append({"left": left.cue_id, "right": right.cue_id, "similarity": similarity, "exact": False})

    report = {
        "version": metadata["version"],
        "passed": all(item.passed for item in measurements) and not duplicates,
        "assets": [item.__dict__ for item in measurements],
        "nearDuplicates": duplicates,
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Audio V6: technischer Prüfbericht",
        "",
        f"Stand: 12. August 2026. Paket: `{metadata['version']}`.",
        "",
        "| Cue | Dauer | LUFS | Peak | Seam | Ergebnis |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in measurements:
        seam = "-" if item.seam_ratio is None else f"{item.seam_ratio:.2f}"
        result = "OK" if item.passed else "; ".join(item.notes)
        lines.append(
            f"| {item.cue_id} | {item.duration:.2f}s | {item.integrated_lufs:.1f} | {item.true_peak:.1f} | {seam} | {result} |"
        )
    lines.extend(["", "## Ähnlichkeitsprüfung", ""])
    if duplicates:
        for pair in duplicates:
            lines.append(f"- {pair['left']} und {pair['right']}: {pair['similarity']:.4f}")
    else:
        lines.append("Keine exakten oder fast identischen Dateien erkannt.")
    lines.extend(
        [
            "",
            "## Noch offen vor dem finalen Release",
            "",
            "Die technische Prüfung ersetzt keinen Hörtest. In `3.3.0` wird jeder Cue über die vorgesehene Bluetooth-Box und zusätzlich über den iPhone-Lautsprecher als passend oder falsch markiert.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Audio V6 QA: {'PASS' if report['passed'] else 'REVIEW'} ({len(measurements)} assets, {len(duplicates)} similarity flags)")


if __name__ == "__main__":
    main()
