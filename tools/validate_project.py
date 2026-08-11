#!/usr/bin/env python3
"""Validate the content graph, audio bundle and generated print pack."""

from __future__ import annotations

import json
import sys
from hashlib import sha256
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
    npcs = manifest.get("npcs", [])
    clues = manifest.get("clues", [])
    scene_ids = {scene["id"] for scene in scenes}
    handout_ids = {handout["id"] for handout in handouts}
    cue_ids = {cue["id"] for cue in cues}
    npc_ids = {npc["id"] for npc in npcs}
    clue_ids = {clue["id"] for clue in clues}
    if len(scene_ids) != len(scenes): fail("Duplicate scene id")
    if len(handout_ids) != len(handouts): fail("Duplicate handout id")
    if len(cue_ids) != len(cues): fail("Duplicate audio cue id")
    if len(npc_ids) != len(npcs): fail("Duplicate NPC id")
    if len(clue_ids) != len(clues): fail("Duplicate clue id")

    for scene in scenes:
        missing = set(scene["handoutIds"]) - handout_ids
        if missing: fail(f"{scene['id']} references missing handouts: {sorted(missing)}")
        missing = set(scene["audioCueIds"]) - cue_ids
        if missing: fail(f"{scene['id']} references missing audio cues: {sorted(missing)}")
        missing = set(scene["nextSceneIds"]) - scene_ids
        if missing: fail(f"{scene['id']} references missing next scenes: {sorted(missing)}")
        missing = set(scene.get("npcIds", [])) - npc_ids
        if missing: fail(f"{scene['id']} references missing NPCs: {sorted(missing)}")
        missing = set(scene.get("clueIds", [])) - clue_ids
        if missing: fail(f"{scene['id']} references missing clues: {sorted(missing)}")
        if not scene.get("readAloud"): fail(f"{scene['id']} has no read-aloud prompt")
        if not scene.get("checklist"): fail(f"{scene['id']} has no GM checklist")

    for npc in npcs:
        missing = set(npc.get("givesHandoutIds", [])) - handout_ids
        if missing: fail(f"{npc['id']} references missing handouts: {sorted(missing)}")
    for clue in clues:
        fallback = clue.get("handoutId")
        if fallback is not None and fallback not in handout_ids:
            fail(f"Clue {clue['id']} has invalid handout reference")

    app_manifest_path = ROOT / "app" / "Kraehenfels" / "Resources" / "manifest.json"
    if app_manifest_path.read_text(encoding="utf-8") != manifest_path.read_text(encoding="utf-8"):
        fail("App manifest is out of sync with content manifest")
    web_manifest_path = ROOT / "web" / "data" / "manifest.json"
    if web_manifest_path.read_text(encoding="utf-8") != manifest_path.read_text(encoding="utf-8"):
        fail("Web manifest is out of sync with content manifest")

    generated = ROOT / "audio" / "generated"
    bundled = ROOT / "app" / "Kraehenfels" / "Resources" / "Audio"
    for cue in cues:
        if not (generated / cue["file"]).exists(): fail(f"Missing generated audio: {cue['file']}")
        if not (bundled / cue["file"]).exists(): fail(f"Missing app audio: {cue['file']}")
        fallback = cue.get("printFallbackId")
        if cue.get("isClue") and fallback not in handout_ids:
            fail(f"Clue {cue['id']} has invalid printed fallback")

    cues_by_id = {cue["id"]: cue for cue in cues}
    for scene in scenes:
        seen_fingerprints: dict[str, str] = {}
        for cue_id in scene["audioCueIds"]:
            cue = cues_by_id[cue_id]
            fingerprint = sha256((bundled / cue["file"]).read_bytes()).hexdigest()
            duplicate_of = seen_fingerprints.get(fingerprint)
            if duplicate_of:
                fail(f"{scene['id']} exposes duplicate audio resources: {duplicate_of} and {cue_id}")
            seen_fingerprints[fingerprint] = cue_id

    for name in ("01_Karte_Spieler.pdf", "01_Karte_SL.pdf", "01_Grubenplan_H08.pdf", "01_Grubenplan_SL.pdf", "02_Handouts.pdf", "03_Figurenbau.pdf", "10_SL_Abenteuer.pdf", "11_SL_Schnellreferenz.pdf", "12_SL_Am_Tisch.pdf", "13_SL_Spoiler-Handouts.pdf", "14_Soundboard-Cues.pdf"):
        path = ROOT / "outputs" / name
        if not path.exists(): fail(f"Missing PDF: {name}")
        pages = len(PdfReader(str(path)).pages)
        if pages < 1: fail(f"PDF has no pages: {name}")
        print(f"OK: {name} ({pages} pages)")

    player_handouts_text = "\n".join(page.extract_text() or "" for page in PdfReader(str(ROOT / "outputs" / "02_Handouts.pdf")).pages)
    if "H10" in player_handouts_text or "H11" in player_handouts_text:
        fail("Player handouts contain a spoiler handout")
    player_map_text = "\n".join(page.extract_text() or "" for page in PdfReader(str(ROOT / "outputs" / "01_Karte_Spieler.pdf")).pages)
    if "H02" not in player_map_text:
        fail("Player map is missing its handout id")

    for path in [ROOT / "content" / "scenario.md", ROOT / "content" / "handouts.md", ROOT / "content" / "character_creation.md"]:
        path.read_text(encoding="utf-8")
    art_dir = ROOT / "app" / "Kraehenfels" / "Resources" / "Art"
    web_art_dir = ROOT / "web" / "assets" / "art"
    for scene in scenes:
        art = scene.get("art")
        if art and not (art_dir / art).exists(): fail(f"Missing scene art: {art}")
        if art and not (web_art_dir / art).exists(): fail(f"Missing web scene art: {art}")
    web_audio_dir = ROOT / "web" / "assets" / "audio"
    for cue in cues:
        if not (web_audio_dir / cue["file"]).exists(): fail(f"Missing web audio: {cue['file']}")
    print(f"OK: {len(scenes)} scenes, {len(handouts)} handouts, {len(npcs)} NPCs, {len(clues)} clues, {len(cues)} audio cues")


if __name__ == "__main__":
    main()
