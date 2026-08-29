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
    if manifest["meta"].get("version") != "5.1.0": fail("Native manifest must be the 5.1.0 content release")
    if len(npcs) != 6: fail(f"5.1.0 must expose exactly six NPCs, got {len(npcs)}")

    location_ids = {entry["id"] for entry in manifest.get("locations", [])}
    fact_ids = {fact["id"] for fact in manifest.get("facts", [])}
    for fact in manifest.get("facts", []):
        clue_refs = fact.get("clueIds", [])
        if not clue_refs or len(clue_refs) != len(set(clue_refs)):
            fail(f"Fact {fact['id']} has duplicate or empty clue references")
        missing = set(clue_refs) - clue_ids
        if missing:
            fail(f"Fact {fact['id']} references missing clues: {sorted(missing)}")
    for handout in handouts:
        linked = handout.get("linkedClueIds", [])
        if len(linked) != len(set(linked)):
            fail(f"Handout {handout['id']} has duplicate linked clues")
        missing = set(linked) - clue_ids
        if missing:
            fail(f"Handout {handout['id']} references missing clues: {sorted(missing)}")

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
        missing = set(scene.get("locationIds", [])) - location_ids
        if missing: fail(f"{scene['id']} references missing locations: {sorted(missing)}")
        if scene.get("phaseId") not in phase_ids: fail(f"{scene['id']} has invalid phase")
        if not scene.get("readAloud"): fail(f"{scene['id']} has no read-aloud prompt")
        if not scene.get("checklist"): fail(f"{scene['id']} has no GM checklist")
        plan_ids = [entry.get("cueId") for entry in scene.get("audioPlan", [])]
        if plan_ids != scene["audioCueIds"]: fail(f"{scene['id']} audio plan does not match its cue order")
        for entry in scene.get("audioPlan", []):
            if not entry.get("playWhen") or not entry.get("gmInstruction"):
                fail(f"{scene['id']} has an incomplete audio instruction for {entry.get('cueId')}")

    guide = manifest.get("guide", {})
    guide_steps = guide.get("steps", {})
    guide_step_ids = {step.get("id") for steps in guide_steps.values() for step in steps}
    valid_presence_modes = {"always", "conditional", "afterClue", "afterStep", "state", "ending", "manual", "contextual", "never"}
    legacy_appearance_fields = {"when", "playAs", "openingLine", "turn"}
    appearance_count = 0
    for npc in npcs:
        missing = set(npc.get("givesHandoutIds", [])) - handout_ids
        if missing: fail(f"{npc['id']} references missing handouts: {sorted(missing)}")
        appearances = npc.get("appearances", [])
        appearance_count += len(appearances)
        appearance_scene_ids = [entry.get("sceneId") for entry in appearances]
        if not appearances: fail(f"{npc['id']} has no scene-specific appearances")
        if len(appearance_scene_ids) != len(set(appearance_scene_ids)):
            fail(f"{npc['id']} has duplicate appearance scenes")
        for appearance in appearances:
            scene_id = appearance.get("sceneId")
            if scene_id not in scene_ids: fail(f"{npc['id']} has appearance in missing scene {scene_id}")
            if npc["id"] not in next(scene for scene in scenes if scene["id"] == scene_id).get("npcIds", []):
                fail(f"{npc['id']} appearance is not listed in {scene_id}")
            if legacy_appearance_fields.intersection(appearance):
                fail(f"{npc['id']} appearance in {scene_id} still contains dialogue fields: {sorted(legacy_appearance_fields.intersection(appearance))}")
            presence = appearance.get("presence")
            if not isinstance(presence, dict):
                fail(f"{npc['id']} appearance in {scene_id} has no structured presence rule")
            if presence.get("mode") not in valid_presence_modes:
                fail(f"{npc['id']} appearance in {scene_id} has invalid presence mode {presence.get('mode')!r}")
            for required_key in ("instruction", "absentInstruction"):
                if not isinstance(presence.get(required_key), str) or not presence[required_key].strip():
                    fail(f"{npc['id']} appearance in {scene_id} has no presence {required_key}")
            after_clue = presence.get("afterClueID")
            if after_clue is not None and after_clue not in clue_ids:
                fail(f"{npc['id']} appearance in {scene_id} references missing afterClueID {after_clue}")
            after_step = presence.get("afterGuideStepID")
            if after_step is not None:
                if after_step not in guide_step_ids:
                    fail(f"{npc['id']} appearance in {scene_id} references missing afterGuideStepID {after_step}")
                if not after_step.startswith(f"{scene_id}_"):
                    fail(f"{npc['id']} appearance in {scene_id} gates on a step from another scene: {after_step}")
            minimum_state = presence.get("minimumStateIndex")
            if minimum_state is not None and (not isinstance(minimum_state, int) or isinstance(minimum_state, bool) or not 0 <= minimum_state < len(npc.get("states", []))):
                fail(f"{npc['id']} appearance in {scene_id} has invalid minimumStateIndex")
            required_endings = presence.get("requiredEndingIDs", [])
            if not isinstance(required_endings, list) or any(ending not in {entry["id"] for entry in manifest.get("endings", [])} for ending in required_endings):
                fail(f"{npc['id']} appearance in {scene_id} has invalid requiredEndingIDs")
            if presence.get("mode") not in {"always", "never"} and not any((after_clue, after_step, minimum_state is not None, required_endings)):
                fail(f"{npc['id']} appearance in {scene_id} is conditional but has no machine-readable gate")
            for required_key in ("reason", "mood", "goal", "behavior", "nextAction"):
                if not isinstance(appearance.get(required_key), str) or not appearance[required_key].strip():
                    fail(f"{npc['id']} appearance in {scene_id} has no direction {required_key}")
            reactions = appearance.get("clueReactions", [])
            if not isinstance(reactions, list):
                fail(f"{npc['id']} appearance in {scene_id} has invalid clueReactions")
            reaction_ids = [reaction.get("clueID") for reaction in reactions]
            if len(reaction_ids) != len(set(reaction_ids)):
                fail(f"{npc['id']} appearance in {scene_id} has duplicate clue reactions")
            for reaction in reactions:
                if reaction.get("clueID") not in clue_ids:
                    fail(f"{npc['id']} appearance in {scene_id} reacts to missing clue {reaction.get('clueID')}")
                for required_key in ("reaction", "reveals", "nextAction"):
                    if not isinstance(reaction.get(required_key), str) or not reaction[required_key].strip():
                        fail(f"{npc['id']} reaction to {reaction.get('clueID')} has no {required_key}")
                target_state = reaction.get("targetState")
                if target_state is not None and target_state not in npc.get("states", []):
                    fail(f"{npc['id']} reaction to {reaction.get('clueID')} targets unknown state {target_state!r}")
        reachable_state_indexes = {0}
        for appearance in appearances:
            for reaction in appearance.get("clueReactions", []):
                target_state = reaction.get("targetState")
                if target_state in npc.get("states", []):
                    reachable_state_indexes.add(npc["states"].index(target_state))
        for appearance in appearances:
            presence = appearance.get("presence", {})
            minimum_state = presence.get("minimumStateIndex")
            if presence.get("mode") == "state" and isinstance(minimum_state, int) and minimum_state > 0:
                if not any(index >= minimum_state for index in reachable_state_indexes):
                    fail(f"{npc['id']} has a state-gated appearance that no clue reaction can unlock")
    if appearance_count != 20: fail(f"5.1.0 must expose exactly 20 NPC appearances, got {appearance_count}")
    for scene in scenes:
        for npc_id in scene.get("npcIds", []):
            npc = next(entry for entry in npcs if entry["id"] == npc_id)
            if scene["id"] not in {appearance["sceneId"] for appearance in npc.get("appearances", [])}:
                fail(f"{scene['id']} lists {npc_id} without a scene-specific appearance")
    h09 = next((handout for handout in handouts if handout["id"] == "H09"), None)
    if not h09 or h09.get("spoiler"):
        fail("H09 must be a regular player handout")
    if "H09" not in next(scene for scene in scenes if scene["id"] == "S06").get("handoutIds", []):
        fail("S06 must expose H09 as a player handout")
    if "N06" in next(scene for scene in scenes if scene["id"] == "S07").get("npcIds", []):
        fail("Leni must remain safe and cannot be present at the Old Oak finale")
    for clue in clues:
        fallback = clue.get("handoutId")
        if fallback is not None and fallback not in handout_ids:
            fail(f"Clue {clue['id']} has invalid handout reference")
        if clue.get("factId") is not None and clue["factId"] not in fact_ids:
            fail(f"Clue {clue['id']} has invalid fact reference")
        if clue.get("locationId") is not None and clue["locationId"] not in location_ids:
            fail(f"Clue {clue['id']} has invalid location reference")
        if fallback is not None:
            linked = next(handout for handout in handouts if handout["id"] == fallback).get("linkedClueIds", [])
            if clue["id"] not in linked:
                fail(f"Clue {clue['id']} is not linked back from handout {fallback}")

    combat = guide.get("combat")
    if not isinstance(combat, dict) or not isinstance(combat.get("enemy"), dict):
        fail("Guide combat configuration is missing")
    enemy = combat["enemy"]
    expected_enemy = {"id": "enemy-bone-stag", "maxLP": 120, "initiative": 7, "attackSkill": 65, "damageDice": "7W10", "parryable": False}
    for key, expected in expected_enemy.items():
        if enemy.get(key) != expected:
            fail(f"Combat enemy {key} must be {expected!r}")
    if set(combat.get("victoryByEnding", {})) != {"E01", "E02", "E03"}:
        fail("Combat victory text must cover all three endings")
    for scene_id, steps in guide_steps.items():
        for step in steps:
            clue_refs = [step.get("clueID"), *step.get("clueIDs", [])]
            if set(filter(None, clue_refs)) - clue_ids:
                fail(f"{step['id']} references a missing clue")
            for option in step.get("options", []):
                required = option.get("requiresCompletedSceneIDs", [])
                if set(required) - scene_ids:
                    fail(f"{step['id']} has an option with a missing scene requirement")
            for npc_id in [step.get("npcID"), *step.get("npcIDs", [])]:
                if npc_id:
                    npc = next(entry for entry in npcs if entry["id"] == npc_id)
                    if scene_id not in {appearance.get("sceneId") for appearance in npc.get("appearances", [])}:
                        fail(f"{step['id']} references {npc_id} without a scene-specific appearance in {scene_id}")
            if step.get("id") in {"S03_NEXT", "S04_NEXT", "S05_NEXT"}:
                archive = next((option for option in step.get("options", []) if option.get("destinationSceneID") == "S06"), None)
                if not archive or set(archive.get("requiresCompletedSceneIDs", [])) != {"S03", "S04", "S05"}:
                    fail(f"{step['id']} does not gate S06 behind all three investigation scenes")

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
    if "H09" not in player_handouts_text:
        fail("Player handouts are missing H09")
    spoiler_handouts_text = "\n".join(page.extract_text() or "" for page in PdfReader(str(ROOT / "outputs" / "13_SL_Spoiler-Handouts.pdf")).pages)
    if "H09" in spoiler_handouts_text:
        fail("H09 must not be duplicated in the spoiler handout PDF")
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
    if len(final_player.pages) != 20: fail(f"Final player session pack must have 20 pages, got {len(final_player.pages)}")
    if len(final_npcs.pages) != 7: fail(f"NPC direction guide must have 7 pages, got {len(final_npcs.pages)}")
    player_page_texts = [page.extract_text() or "" for page in final_player.pages]
    def unique_page_for(marker: str) -> int:
        matches = [index for index, text in enumerate(player_page_texts) if marker in text]
        if len(matches) != 1:
            fail(f"Final player session pack must contain exactly one page with {marker}, got {len(matches)}")
        return matches[0]

    # The generated PDF font encoding may normalize umlauts and middle dots;
    # the stable handout IDs are sufficient to identify each page.
    h10_page = unique_page_for("H10")
    h05_page = unique_page_for("H05")
    h09_page = unique_page_for("H09")
    if not h10_page < h05_page < h09_page:
        fail("Final player session pack must order H10 before H05 and H09")
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
    web_handout_dir = ROOT / "web" / "assets" / "materials" / "handouts"
    for handout in handouts:
        preview_asset = handout.get("previewAsset")
        if preview_asset and not (web_handout_dir / preview_asset).exists():
            fail(f"Missing web handout preview: {preview_asset}")
    web_item_dir = ROOT / "web" / "assets" / "materials" / "items"
    for item in manifest.get("guide", {}).get("items", []):
        card_asset = item.get("playerCardAsset")
        if card_asset and not (web_item_dir / card_asset).exists():
            fail(f"Missing web item card: {card_asset}")
    for name in ("Einladung_Kraehenfels.pdf", "Kraehenfels-Druckpaket.zip", "Kraehenfels-Audio.zip"):
        if not (ROOT / "outputs" / name).exists(): fail(f"Missing shareable output: {name}")
    print(f"OK: {len(scenes)} scenes, {len(handouts)} handouts, {len(npcs)} NPCs, {len(clues)} clues, {len(cues)} audio cues")


if __name__ == "__main__":
    main()
