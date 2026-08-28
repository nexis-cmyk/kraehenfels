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
    map_ids = {entry["id"] for entry in manifest.get("maps", [])}
    phase_ids = {entry["id"] for entry in manifest.get("phases", [])}
    if len(scene_ids) != len(scenes): fail("Duplicate scene id")
    if len(handout_ids) != len(handouts): fail("Duplicate handout id")
    if len(cue_ids) != len(cues): fail("Duplicate audio cue id")
    if len(npc_ids) != len(npcs): fail("Duplicate NPC id")
    if len(clue_ids) != len(clues): fail("Duplicate clue id")
    if map_ids != {"MAP01", "MAP02", "MAP03", "MAP04", "MAP05", "MAP06"}: fail("V3 map set is incomplete")
    if phase_ids != {"P01", "P02", "P03", "P04", "P05"}: fail("V3 phase set is incomplete")
    if len(manifest.get("endings", [])) != 3: fail("V3 must expose exactly three endings")
    if manifest["meta"].get("version") != "3.3.0": fail("Native manifest must be the 3.3.0 content release")

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
        missing = set(scene.get("locationIds", [])) - {entry["id"] for entry in manifest.get("locations", [])}
        if missing: fail(f"{scene['id']} references missing locations: {sorted(missing)}")
        if scene.get("phaseId") not in phase_ids: fail(f"{scene['id']} has invalid phase")
        if not scene.get("readAloud"): fail(f"{scene['id']} has no read-aloud prompt")
        if not scene.get("checklist"): fail(f"{scene['id']} has no GM checklist")
        plan_ids = [entry.get("cueId") for entry in scene.get("audioPlan", [])]
        if plan_ids != scene["audioCueIds"]: fail(f"{scene['id']} audio plan does not match its cue order")
        for entry in scene.get("audioPlan", []):
            if not entry.get("playWhen") or not entry.get("gmInstruction"):
                fail(f"{scene['id']} has an incomplete audio instruction for {entry.get('cueId')}")

    for npc in npcs:
        missing = set(npc.get("givesHandoutIds", [])) - handout_ids
        if missing: fail(f"{npc['id']} references missing handouts: {sorted(missing)}")
        appearances = npc.get("appearances", [])
        appearance_scene_ids = [entry.get("sceneId") for entry in appearances]
        if not appearances: fail(f"{npc['id']} has no scene-specific appearances")
        if len(appearance_scene_ids) != len(set(appearance_scene_ids)):
            fail(f"{npc['id']} has duplicate appearance scenes")
        for appearance in appearances:
            scene_id = appearance.get("sceneId")
            if scene_id not in scene_ids: fail(f"{npc['id']} has appearance in missing scene {scene_id}")
            if npc["id"] not in next(scene for scene in scenes if scene["id"] == scene_id).get("npcIds", []):
                fail(f"{npc['id']} appearance is not listed in {scene_id}")
            for required_key in ("when", "playAs", "openingLine", "turn"):
                if not appearance.get(required_key): fail(f"{npc['id']} appearance in {scene_id} has no {required_key}")
    for scene in scenes:
        for npc_id in scene.get("npcIds", []):
            npc = next(entry for entry in npcs if entry["id"] == npc_id)
            if scene["id"] not in {appearance["sceneId"] for appearance in npc.get("appearances", [])}:
                fail(f"{scene['id']} lists {npc_id} without a scene-specific appearance")
    if "H09" in next(npc for npc in npcs if npc["id"] == "N03").get("givesHandoutIds", []):
        fail("Elias must not expose the GM-only H09 as a regular player handout")
    if "N06" in next(scene for scene in scenes if scene["id"] == "S07").get("npcIds", []):
        fail("Leni must remain safe and cannot be present at the Old Oak finale")
    for clue in clues:
        fallback = clue.get("handoutId")
        if fallback is not None and fallback not in handout_ids:
            fail(f"Clue {clue['id']} has invalid handout reference")

    app_manifest_path = ROOT / "app" / "Kraehenfels" / "Resources" / "manifest.json"
    if app_manifest_path.read_text(encoding="utf-8") != manifest_path.read_text(encoding="utf-8"):
        fail("App manifest is out of sync with content manifest")
    web_manifest_path = ROOT / "web" / "data" / "manifest.json"
    web_manifest = json.loads(web_manifest_path.read_text(encoding="utf-8"))
    if web_manifest["meta"].get("version") != manifest["meta"].get("version"):
        fail("Web test build is out of sync with the content release")

    material_root = ROOT / "app" / "Kraehenfels" / "Resources" / "Materials"
    expected_material_files = {
        Path("Endings") / "ending-cards.png",
    }
    for handout in handouts:
        preview_asset = handout.get("previewAsset")
        if preview_asset:
            expected_material_files.add(Path("Handouts") / preview_asset)
    for item in manifest.get("guide", {}).get("items", []):
        card_asset = item.get("playerCardAsset")
        if card_asset:
            expected_material_files.add(Path("Items") / card_asset)
    if not material_root.exists():
        fail("Native material resource directory is missing")
    for relative_path in expected_material_files:
        if not (material_root / relative_path).exists():
            fail(f"Missing native material asset: {relative_path.as_posix()}")
    actual_material_files = {
        path.relative_to(material_root)
        for path in material_root.rglob("*.png")
    }
    if actual_material_files != expected_material_files:
        fail(
            "Native material bundle differs from manifest: "
            f"missing={sorted(str(path) for path in expected_material_files - actual_material_files)}, "
            f"unexpected={sorted(str(path) for path in actual_material_files - expected_material_files)}"
        )

    generated = ROOT / "audio" / "generated"
    bundled = ROOT / "app" / "Kraehenfels" / "Resources" / "Audio"
    expected_audio_files = {cue["file"] for cue in cues} | {"V5_TEST_Audio.wav"}
    unexpected_audio_files = {path.name for path in bundled.iterdir() if path.is_file()} - expected_audio_files
    if unexpected_audio_files:
        fail(f"Native audio bundle contains unreferenced files: {sorted(unexpected_audio_files)}")
    for cue in cues:
        if not (generated / cue["file"]).exists(): fail(f"Missing generated audio: {cue['file']}")
        if not (bundled / cue["file"]).exists(): fail(f"Missing app audio: {cue['file']}")
        fallback = cue.get("printFallbackId")
        if cue.get("isClue") and fallback not in handout_ids:
            fail(f"Clue {cue['id']} has invalid printed fallback")
        if cue.get("layer") not in {"musicBed", "musicLayer", "ambient", "sfx"}:
            fail(f"Audio cue {cue['id']} has an invalid layer")
        if not cue.get("playWhen") or not cue.get("gmInstruction"):
            fail(f"Audio cue {cue['id']} lacks GM timing")

    expected_scene = {"SFX04": "S02", "SFX05": "S04", "SFX09": "S07", "SFX10": "S03"}
    for cue_id, scene_id in expected_scene.items():
        cue = next((item for item in cues if item["id"] == cue_id), None)
        if cue is None or cue.get("scene") != scene_id:
            fail(f"{cue_id} must belong to {scene_id}")
    sfx09_plan = next(scene for scene in scenes if scene["id"] == "S07")["audioPlan"]
    sfx09_entry = next(entry for entry in sfx09_plan if entry["cueId"] == "SFX09")
    if not sfx09_entry.get("optional"):
        fail("SFX09 must remain optional and exclusive to the destruction ending")
    if not (bundled / "V5_TEST_Audio.wav").exists():
        fail("Missing native audio self-test tone")

    cues_by_id = {cue["id"]: cue for cue in cues}
    seen_fingerprints: dict[str, str] = {}
    for cue in cues:
        fingerprint = sha256((bundled / cue["file"]).read_bytes()).hexdigest()
        duplicate_of = seen_fingerprints.get(fingerprint)
        if duplicate_of:
            fail(f"Native bundle contains duplicate audio resources: {duplicate_of} and {cue['id']}")
        seen_fingerprints[fingerprint] = cue["id"]

    for name in ("00_Spielstart.pdf", "01_Karte_Spieler.pdf", "01_Karte_SL.pdf", "01_Karten_Detail.pdf", "02_Handouts.pdf", "03_Figurenbau.pdf", "04_Gegenstandskarten.pdf", "10_SL_Abenteuer.pdf", "11_SL_Schnellreferenz.pdf", "12_SL_Am_Tisch.pdf", "13_SL_Spoiler-Handouts.pdf", "14_Soundboard-Cues.pdf"):
        path = ROOT / "outputs" / name
        if not path.exists(): fail(f"Missing PDF: {name}")
        pages = len(PdfReader(str(path)).pages)
        if pages < 1: fail(f"PDF has no pages: {name}")
        print(f"OK: {name} ({pages} pages)")

    player_handouts_text = "\n".join(page.extract_text() or "" for page in PdfReader(str(ROOT / "outputs" / "02_Handouts.pdf")).pages)
    if "H09" in player_handouts_text:
        fail("Player handouts contain a spoiler handout")
    player_map_text = "\n".join(page.extract_text() or "" for page in PdfReader(str(ROOT / "outputs" / "01_Karte_Spieler.pdf")).pages)
    if "Spielerkarte" not in player_map_text:
        fail("Player map is missing its player-safe marker")
    item_cards_text = "\n".join(page.extract_text() or "" for page in PdfReader(str(ROOT / "outputs" / "04_Gegenstandskarten.pdf")).pages)
    for title in ("Wolldecke", "Verbandtasche", "Hanfseil", "Sturmlaterne mit Öl", "Werkzeugrolle", "Alter Revolver"):
        if title not in item_cards_text:
            fail(f"Item cards are missing: {title}")

    final_player_path = ROOT / "output" / "pdf" / "Kraehenfels-Spielermaterial-Druck.pdf"
    final_npc_path = ROOT / "output" / "pdf" / "Kraehenfels-NPC-Regie.pdf"
    if not final_player_path.exists(): fail("Missing final player session pack")
    if not final_npc_path.exists(): fail("Missing final NPC direction guide")
    final_player = PdfReader(str(final_player_path))
    final_npcs = PdfReader(str(final_npc_path))
    if len(final_player.pages) != 19: fail(f"Final player session pack must have 19 pages, got {len(final_player.pages)}")
    if len(final_npcs.pages) != 7: fail(f"NPC direction guide must have 7 pages, got {len(final_npcs.pages)}")
    item_page_text = final_player.pages[3].extract_text() or ""
    for spoiler_term in ("Knochenhirsch", "geführten Finale", "Bindung zerstören", "Marta"):
        if spoiler_term in item_page_text:
            fail(f"Player item cards leak the spoiler term: {spoiler_term}")

    for path in [ROOT / "content" / "scenario.md", ROOT / "content" / "handouts.md", ROOT / "content" / "character_creation.md"]:
        path.read_text(encoding="utf-8")
    art_dir = ROOT / "app" / "Kraehenfels" / "Resources" / "Art"
    web_art_dir = ROOT / "web" / "assets" / "art"
    expected_art_files = {scene.get("art") for scene in scenes if scene.get("art")}
    expected_art_files |= {
        asset
        for entry in manifest.get("maps", [])
        for asset in (entry.get("playerAsset"), entry.get("gmAsset"))
        if asset
    }
    unexpected_art_files = {path.name for path in art_dir.iterdir() if path.is_file()} - expected_art_files
    if unexpected_art_files:
        fail(f"Native art bundle contains unreferenced files: {sorted(unexpected_art_files)}")
    for scene in scenes:
        art = scene.get("art")
        if art and not (art_dir / art).exists(): fail(f"Missing scene art: {art}")
        if art and not (web_art_dir / art).exists(): fail(f"Missing web scene art: {art}")
    maps_dir = ROOT / "web" / "assets" / "maps"
    print_assets = ROOT / "print" / "assets"
    for entry in manifest.get("maps", []):
        for key in ("playerAsset", "gmAsset"):
            asset = entry.get(key)
            if asset and not (maps_dir / asset).exists(): fail(f"Missing web map asset: {asset}")
            if asset and not (print_assets / asset).exists(): fail(f"Missing print map asset: {asset}")
    for name in ("Einladung_Kraehenfels.pdf", "Kraehenfels-Druckpaket.zip", "Kraehenfels-Audio.zip"):
        if not (ROOT / "outputs" / name).exists(): fail(f"Missing shareable output: {name}")
    print(f"OK: {len(scenes)} scenes, {len(handouts)} handouts, {len(npcs)} NPCs, {len(clues)} clues, {len(cues)} audio cues")


if __name__ == "__main__":
    main()
