#!/usr/bin/env python3
"""Create the original Kraehenfels ambience, music beds and SFX.

The generator uses only deterministic NumPy synthesis and FFmpeg encoding. It
does not imitate a named recording, use a sample library or contain speech.
"""

from __future__ import annotations

import math
import subprocess
import wave
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audio" / "generated"
OUT.mkdir(parents=True, exist_ok=True)
SR = 48_000
RNG = np.random.default_rng(1890)


def normalize(x: np.ndarray, peak: float = 0.88) -> np.ndarray:
    x = np.asarray(x, dtype=np.float32)
    m = float(np.max(np.abs(x))) or 1.0
    return (x / m * peak).astype(np.float32)


def fade(x: np.ndarray, ms: float = 30) -> np.ndarray:
    n = min(int(SR * ms / 1000), len(x) // 2)
    if n:
        x[:n] *= np.linspace(0, 1, n, dtype=np.float32)
        x[-n:] *= np.linspace(1, 0, n, dtype=np.float32)
    return x


def periodic_noise(seconds: float, low: float = 0.0, high: float = 1.0, seed: int = 0) -> np.ndarray:
    n = int(seconds * SR)
    rng = np.random.default_rng(seed)
    knot_count = max(4, int(seconds * 7))
    knots = rng.normal(0, 1, knot_count + 1).astype(np.float32)
    knots[-1] = knots[0]
    positions = np.linspace(0, n, knot_count + 1)
    noise = np.interp(np.arange(n), positions, knots).astype(np.float32)
    noise = normalize(noise, 1.0)
    if high > low:
        noise = np.tanh(noise * 2.0) * (high - low) / 2 + (high + low) / 2
    return noise.astype(np.float32)


def sine(freq: float, seconds: float, amp: float = 1.0, phase: float = 0.0) -> np.ndarray:
    t = np.arange(int(seconds * SR), dtype=np.float32) / SR
    return (np.sin(2 * np.pi * freq * t + phase) * amp).astype(np.float32)


def bell(freq: float = 440, seconds: float = 3.0, brightness: float = 0.45) -> np.ndarray:
    t = np.arange(int(seconds * SR), dtype=np.float32) / SR
    env = np.exp(-t * (1.0 + 1.5 * brightness))
    tone = (
        np.sin(2 * np.pi * freq * t) * 0.75
        + np.sin(2 * np.pi * freq * 2.71 * t + 0.2) * 0.38 * brightness
        + np.sin(2 * np.pi * freq * 4.08 * t + 0.4) * 0.18 * brightness
    )
    return (tone * env).astype(np.float32)


def crack(seconds: float = 1.3, seed: int = 1) -> np.ndarray:
    n = int(seconds * SR)
    rng = np.random.default_rng(seed)
    t = np.arange(n, dtype=np.float32) / SR
    envelope = np.exp(-t * 6.5)
    white = rng.normal(0, 1, n).astype(np.float32)
    low = np.convolve(white, np.ones(120, dtype=np.float32) / 120, mode="same")
    return normalize((white * 0.45 + low * 4.0) * envelope, 0.85)


def write_wav(path: Path, data: np.ndarray) -> None:
    data = normalize(data)
    pcm = (data * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SR)
        handle.writeframes(pcm.tobytes())


def write_m4a(path: Path, data: np.ndarray) -> None:
    temp = path.with_suffix(".wav")
    write_wav(temp, data)
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(temp),
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(path),
    ], check=True)
    temp.unlink(missing_ok=True)


def ambient(kind: str, seconds: float = 32.0) -> np.ndarray:
    n = int(seconds * SR)
    t = np.arange(n, dtype=np.float32) / SR
    stable_seed = sum((index + 1) * ord(char) for index, char in enumerate(kind))
    wind = periodic_noise(seconds, -0.35, 0.35, stable_seed & 0xFFFF)
    hiss = periodic_noise(seconds, -0.08, 0.08, (stable_seed + 44) & 0xFFFF)
    if kind == "coach":
        rumble = np.sin(2 * np.pi * 1.3 * t) * 0.14 + np.sin(2 * np.pi * 3.8 * t) * 0.07
        creak = np.sin(2 * np.pi * 0.67 * t + np.sin(t) * 2) * 0.11
        return normalize(wind * 0.23 + hiss * 0.18 + rumble + creak)
    if kind == "day":
        crows = np.zeros(n, dtype=np.float32)
        for at in (4.1, 14.4, 26.2):
            start = int(at * SR)
            chirp = sine(620, 0.22, 0.25) + sine(510, 0.22, 0.18)
            crows[start:start + len(chirp)] += fade(chirp, 25)
        return normalize(wind * 0.14 + hiss * 0.08 + crows)
    if kind == "tavern":
        murmur = periodic_noise(seconds, -0.18, 0.18, 13)
        crackle = np.abs(periodic_noise(seconds, -0.6, 0.6, 81)) ** 3 * 0.16
        return normalize(wind * 0.08 + murmur * 0.42 + crackle)
    if kind == "night":
        return normalize(wind * 0.34 + hiss * 0.13 + sine(47, seconds, 0.045))
    if kind == "chapel":
        air = wind * 0.12 + hiss * 0.09
        drone = sine(98, seconds, 0.09) + sine(147, seconds, 0.035)
        return normalize(air + drone)
    if kind == "mine":
        drops = np.zeros(n, dtype=np.float32)
        for at in (3.3, 10.7, 19.8, 28.4):
            start = int(at * SR)
            drop = bell(185, 0.32, 0.2) * 0.22
            drops[start:start + len(drop)] += drop
        return normalize(wind * 0.25 + hiss * 0.12 + sine(38, seconds, 0.08) + drops)
    if kind == "mine_deep":
        water = periodic_noise(seconds, -0.32, 0.32, 902) * 0.22
        pressure = sine(31, seconds, 0.12) + sine(61, seconds, 0.035)
        return normalize(wind * 0.18 + hiss * 0.18 + pressure + water)
    if kind == "tension":
        swell = 0.5 + 0.5 * np.sin(2 * np.pi * 0.035 * t)
        wire = sine(122, seconds, 0.07) + sine(244, seconds, 0.025)
        return normalize(wind * 0.29 + hiss * 0.16 + wire * swell + sine(42, seconds, 0.06))
    if kind == "finale":
        pulse = sine(0.85, seconds, 0.18) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.085 * t))
        return normalize(wind * 0.34 + hiss * 0.14 + pulse + sine(71, seconds, 0.06))
    return normalize(wind * 0.25 + hiss * 0.12)


def music(kind: str, seconds: float = 32.0) -> np.ndarray:
    n = int(seconds * SR)
    out = np.zeros(n, dtype=np.float32)
    motifs = {
        "arrival": [196, 233, 262, 233],
        "secret": [147, 174, 164, 130],
        "woman": [523, 466, 392, 349],
        "frost": [110, 130, 98, 87],
        "thaw": [262, 294, 330, 392],
    }
    notes = motifs.get(kind, motifs["secret"])
    beat = 2.0
    for index, freq in enumerate(notes * 4):
        start = int(index * beat * SR)
        length = min(int(beat * SR), n - start)
        if length <= 0:
            break
        tone = sine(freq, length / SR, 0.17) + sine(freq * 2, length / SR, 0.05, 0.15)
        env = np.minimum(np.linspace(0, 1, min(int(SR * 0.12), length)), 1)
        tone[:len(env)] *= env
        tone *= np.exp(-np.linspace(0, 1.0, length, dtype=np.float32))
        out[start:start + length] += tone
    # a quiet, continuous floor keeps the loop from feeling abruptly cut
    out += sine(49, seconds, 0.025) + periodic_noise(seconds, -0.015, 0.015, 721)
    return normalize(out, 0.72)


def fx(kind: str) -> np.ndarray:
    if kind == "axle":
        return fade(normalize(crack(1.0, 5) + bell(72, 1.0, 0.1) * 0.35), 8)
    if kind == "horses":
        out = crack(0.55, 11) * 0.55
        tone = sine(118, 0.32, 0.2) + sine(153, 0.32, 0.16)
        out[:len(tone)] += tone
        return fade(normalize(out), 8)
    if kind == "hooves":
        out = np.zeros(int(1.6 * SR), dtype=np.float32)
        for at in (0.05, 0.32, 0.68, 0.97, 1.29):
            start = int(at * SR)
            hit = crack(0.12, int(at * 1000 + 3)) * 0.42
            out[start:start + len(hit)] += hit
        return fade(normalize(out), 5)
    if kind == "branch":
        return fade(normalize(crack(0.65, 17) + sine(81, 0.65, 0.16)), 4)
    if kind == "crow":
        return fade(normalize(sine(780, 0.3, 0.22) + sine(610, 0.3, 0.16) + crack(0.3, 31) * 0.15), 5)
    if kind == "silence":
        return np.zeros(int(1.2 * SR), dtype=np.float32)
    if kind == "bell":
        return fade(normalize(bell(196, 3.8, 0.7) + bell(391, 3.8, 0.22) * 0.4), 5)
    if kind == "wrongbell":
        return fade(normalize(bell(131, 3.1, 0.15) + sine(139, 3.1, 0.13)), 5)
    if kind == "forge":
        return fade(normalize(crack(2.4, 44) * 0.7 + sine(55, 2.4, 0.14)), 5)
    if kind == "metal":
        t = np.arange(int(2.3 * SR), dtype=np.float32) / SR
        return fade(normalize(sine(930, 2.3, 0.45) * np.exp(-t * 2.0) + sine(1870, 2.3, 0.12) * np.exp(-t * 3.2)), 4)
    if kind in {"steps", "baresteps"}:
        out = np.zeros(int(2.2 * SR), dtype=np.float32)
        amp = 0.36 if kind == "steps" else 0.22
        for at in (0.08, 0.52, 0.97, 1.44, 1.89):
            start = int(at * SR)
            hit = crack(0.17, int(at * 1000 + 91)) * amp
            out[start:start + len(hit)] += hit
        return fade(normalize(out), 5)
    if kind == "voices":
        t = np.arange(int(3.2 * SR), dtype=np.float32) / SR
        wobble = np.sin(2 * np.pi * 0.7 * t) * 10
        return fade(normalize(sine(178 + wobble, 3.2, 0.16) + sine(267 + wobble, 3.2, 0.06)), 30)
    if kind == "ground":
        return fade(normalize(crack(1.7, 73) * 0.48 + sine(64, 1.7, 0.18)), 5)
    if kind == "breath":
        t = np.arange(int(2.4 * SR), dtype=np.float32) / SR
        env = np.sin(np.pi * t / 2.4) ** 1.5
        return fade(normalize(periodic_noise(2.4, -1, 1, 48) * env), 25)
    if kind == "woman":
        out = sine(740, 1.8, 0.22) + sine(1046, 1.8, 0.12)
        return fade(normalize(out), 50)
    if kind == "clapper":
        return fade(normalize(bell(235, 2.4, 0.35) + sine(73, 2.4, 0.1)), 4)
    if kind == "frost":
        return fade(normalize(periodic_noise(2.8, -0.7, 0.7, 190) * 0.55 + sine(590, 2.8, 0.13)), 18)
    if kind == "heartbeat":
        out = np.zeros(int(5.0 * SR), dtype=np.float32)
        for at in (0.2, 0.58, 2.7, 3.08):
            start = int(at * SR)
            hit = sine(58, 0.16, 0.5) * np.exp(-np.linspace(0, 4, int(0.16 * SR), dtype=np.float32))
            out[start:start + len(hit)] += hit
        return fade(normalize(out), 6)
    if kind == "ice":
        return fade(normalize(crack(2.0, 212) + sine(320, 2.0, 0.16)), 5)
    if kind == "seal":
        return fade(normalize(bell(294, 2.2, 0.25) + bell(392, 2.2, 0.18)), 12)
    if kind == "fail":
        return fade(normalize(bell(104, 2.2, 0.18) + sine(71, 2.2, 0.17)), 7)
    if kind == "shutter":
        out = crack(0.85, 301) * 0.6 + sine(73, 0.85, 0.16)
        return fade(normalize(out), 6)
    if kind == "distantbell":
        return fade(normalize(bell(156, 4.8, 0.42) + sine(78, 4.8, 0.045)), 8)
    if kind == "strain":
        t = np.arange(int(2.1 * SR), dtype=np.float32) / SR
        creak = sine(190 + 17 * np.sin(2 * np.pi * 0.7 * t), 2.1, 0.23)
        return fade(normalize(creak * np.exp(-t * 0.8) + crack(2.1, 331) * 0.24), 8)
    if kind == "water":
        t = np.arange(int(3.2 * SR), dtype=np.float32) / SR
        droplets = np.zeros_like(t)
        for at, freq in ((0.35, 510), (1.2, 430), (2.05, 620), (2.7, 390)):
            start = int(at * SR)
            drop = bell(freq, 0.28, 0.12) * 0.26
            droplets[start:start + len(drop)] += drop
        flow = periodic_noise(3.2, -0.45, 0.45, 744) * 0.18
        return fade(normalize(flow + droplets), 12)
    if kind == "echo_steps":
        base = fx("steps") * 0.65
        delay = np.zeros_like(base)
        offset = int(0.42 * SR)
        delay[offset:] += base[:-offset] * 0.52
        offset2 = int(0.86 * SR)
        delay[offset2:] += base[:-offset2] * 0.27
        return fade(normalize(base + delay), 7)
    if kind == "knock":
        out = np.zeros(int(2.0 * SR), dtype=np.float32)
        for at in (0.22, 0.56, 0.93):
            start = int(at * SR)
            hit = sine(72, 0.18, 0.45) * np.exp(-np.linspace(0, 7, int(0.18 * SR), dtype=np.float32))
            out[start:start + len(hit)] += hit
        return fade(normalize(out), 8)
    if kind == "resonance":
        t = np.arange(int(3.8 * SR), dtype=np.float32) / SR
        tone = sine(224, 3.8, 0.35) + sine(448, 3.8, 0.14) + sine(671, 3.8, 0.07)
        return fade(normalize(tone * np.exp(-t * 0.75)), 5)
    if kind == "room_breath":
        t = np.arange(int(2.7 * SR), dtype=np.float32) / SR
        env = np.sin(np.pi * t / 2.7) ** 1.25
        return fade(normalize(periodic_noise(2.7, -1, 1, 488) * env * 0.72 + sine(53, 2.7, 0.08)), 30)
    if kind == "resonance_break":
        t = np.arange(int(2.2 * SR), dtype=np.float32) / SR
        rising = sine(224, 2.2, 0.36) + sine(448, 2.2, 0.14)
        cut = np.clip(1.0 - (t - 1.1) * 8.0, 0.0, 1.0)
        return fade(normalize(rising * cut + crack(2.2, 531) * (t > 1.08)), 6)
    return fade(normalize(crack(0.8)), 5)


AMBIENTS = {
    "A01_Postkutsche_im_Schneesturm.m4a": "coach",
    "A03_Kraehenfels_bei_Tag.m4a": "day",
    "A04_Wirtsstube_am_Abend.m4a": "tavern",
    "A05_Dorf_nach_Mitternacht.m4a": "night",
    "A06_Kapelle_und_Friedhof.m4a": "chapel",
    "A07_Weisse_Spur_im_Wald.m4a": "mine",
    "A08_Finale_Froststurm.m4a": "finale",
    "A09_Grubenluft_Layer.m4a": "mine_deep",
    "A10_Frostspannung_Layer.m4a": "tension",
}
MUSIC = {
    "M01_Ankunft_in_Kraehenfels.m4a": "arrival",
    "M02_Das_Dorf_verschweigt_etwas.m4a": "secret",
    "M03_Die_Weisse_Frau_naht.m4a": "woman",
    "M04_Ihr_altes_Lied.m4a": "woman",
    "M05_Frost_und_Opfer.m4a": "frost",
    "M06_Tauwetter_Epilog.m4a": "thaw",
}
SFX = {
    "SFX01_Achse_bricht.wav": "axle", "SFX02_Pferde_scheuen.wav": "horses", "SFX03_Hufe_im_Schnee.wav": "hooves", "SFX04_Astbruch.wav": "branch", "SFX05_Kraehen.wav": "crow", "SFX06_Stille.wav": "silence", "SFX07_Glocke_normal.wav": "bell", "SFX08_Glocke_falsch.wav": "wrongbell", "SFX09_Schmiede.wav": "forge", "SFX10_Metall_vibriert.wav": "metal", "SFX11_Schritte.wav": "steps", "SFX12_Barfuss_Schritte.wav": "baresteps", "SFX13_Stimmen_ohne_Worte.wav": "voices", "SFX14_Schlaege_unter_Boden.wav": "ground", "SFX15_Atem_hinter_dir.wav": "breath", "SFX16_Weisse_Frau_Motiv.wav": "woman", "SFX17_Kloeppel_schlaegt.wav": "clapper", "SFX18_Frost_breitet_sich_aus.wav": "frost", "SFX19_Herzschlag.wav": "heartbeat", "SFX20_Eisbruch.wav": "ice", "SFX21_Bannung.wav": "seal", "SFX22_Scheitern.wav": "fail", "SFX23_Fensterladen_im_Wind.wav": "shutter", "SFX24_Fernes_Laeuten.wav": "distantbell", "SFX25_Holz_unter_Spannung.wav": "strain", "SFX26_Wasser_im_Flutstollen.wav": "water", "SFX27_Wiederhallende_Schritte.wav": "echo_steps", "SFX28_Klopfen_unter_Boden.wav": "knock", "SFX29_Glockenresonanz.wav": "resonance", "SFX30_Atem_im_Raum.wav": "room_breath", "SFX31_Resonanzabbruch.wav": "resonance_break",
}


def main() -> None:
    for filename, kind in AMBIENTS.items():
        write_m4a(OUT / filename, ambient(kind))
    for filename, kind in MUSIC.items():
        duration = 26.0 if filename.startswith("M04") else 32.0
        write_m4a(OUT / filename, music(kind, duration))
    for filename, kind in SFX.items():
        write_wav(OUT / filename, fx(kind))
    print(f"Generated {len(AMBIENTS) + len(MUSIC) + len(SFX)} audio assets in {OUT}")


if __name__ == "__main__":
    main()
