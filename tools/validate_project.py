#!/usr/bin/env python3
"""Validate the content graph, audio bundle and generated print pack."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def main() -> None:
    manifest_path = ROOT / "content" / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        fail(f"Manifest cannot be read: {exc}")
    continuity = json.loads((ROOT / "content" / "continuity.json").read_text(encoding="utf-8"))
    for required_name in ("Elisabeth Abele", "Der Widerhall unter dem Stein", "Rosa Ketterer", "Emil Bopp"):
        if required_name not in continuity.get("names", {}).values():
            fail(f"Continuity name missing: {required_name}")

    scenes = manifest["scenes"]
    handouts = manifest["handouts"]
    cues = manifest["audioCues"]
    scene_ids = {scene["id"] for scene in scenes}
    handout_ids = {handout["id"] for handout in handouts}
    cue_ids = {cue["id"] for cue in cues}
    if len(scene_ids) != len(scenes): fail("Duplicate scene id")
    if len(handout_ids) != len(handouts): fail("Duplicate handout id")
    if len(cue_ids) != len(cues): fail("Duplicate audio cue id")

    for scene in scenes:
        missing = set(scene["handoutIds"]) - handout_ids
        if missing: fail(f"{scene['id']} references missing handouts: {sorted(missing)}")
        missing = set(scene["audioCueIds"]) - cue_ids
        if missing: fail(f"{scene['id']} references missing audio cues: {sorted(missing)}")
        missing = set(scene["nextSceneIds"]) - scene_ids
        if missing: fail(f"{scene['id']} references missing next scenes: {sorted(missing)}")

    generated = ROOT / "audio" / "generated"
    bundled = ROOT / "app" / "Kraehenfels" / "Resources" / "Audio"
    for cue in cues:
        if not (generated / cue["file"]).exists(): fail(f"Missing generated audio: {cue['file']}")
        if not (bundled / cue["file"]).exists(): fail(f"Missing app audio: {cue['file']}")
        fallback = cue.get("printFallbackId")
        if cue.get("isClue") and fallback not in handout_ids:
            fail(f"Clue {cue['id']} has invalid printed fallback")

    for name in ("01_Karte_Spieler.pdf", "01_Karte_SL.pdf", "01_Grubenplan_H08.pdf", "01_Grubenplan_SL.pdf", "02_Handouts.pdf", "03_Figurenbau.pdf", "10_SL_Abenteuer.pdf", "11_SL_Schnellreferenz.pdf", "14_Soundboard-Cues.pdf"):
        path = ROOT / "outputs" / name
        if not path.exists(): fail(f"Missing PDF: {name}")
        pages = len(PdfReader(str(path)).pages)
        if pages < 1: fail(f"PDF has no pages: {name}")
        print(f"OK: {name} ({pages} pages)")

    for path in [ROOT / "content" / "scenario.md", ROOT / "content" / "handouts.md", ROOT / "content" / "character_creation.md"]:
        path.read_text(encoding="utf-8")
    print(f"OK: {len(scenes)} scenes, {len(handouts)} handouts, {len(cues)} audio cues")


if __name__ == "__main__":
    main()
