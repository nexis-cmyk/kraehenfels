#!/usr/bin/env python3
"""Cross-check the shared guided flow against the generated content graph."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "content" / "manifest.json"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    guide = manifest.get("guide")
    if not guide:
        fail("manifest has no shared guide")

    scene_ids = {scene["id"] for scene in manifest["scenes"]}
    scenes_by_id = {scene["id"]: scene for scene in manifest["scenes"]}
    steps_by_scene = guide.get("steps", {})
    step_ids = {step["id"] for steps in steps_by_scene.values() for step in steps}
    step_scenes = set(steps_by_scene)
    if not step_ids:
        fail("no guided steps found")
    if step_scenes != scene_ids:
        fail(f"guided scenes differ from manifest: missing={sorted(scene_ids - step_scenes)}, extra={sorted(step_scenes - scene_ids)}")

    cue_ids = {cue["id"] for cue in manifest["audioCues"]}
    handout_ids = {handout["id"] for handout in manifest["handouts"]}
    npc_ids = {npc["id"] for npc in manifest.get("npcs", [])}
    ending_ids = {ending["id"] for ending in manifest["endings"]}
    item_locations = guide.get("itemFindLocations", [])
    items = guide.get("items", [])
    if len(item_locations) != 3:
        fail(f"expected exactly three item find locations, got {len(item_locations)}")
    if len(items) != 6:
        fail(f"expected exactly six adventure items, got {len(items)}")
    location_ids = [location.get("id") for location in item_locations]
    if any(not location_id for location_id in location_ids) or len(set(location_ids)) != len(location_ids):
        fail("item find locations have duplicate or empty ids")
    item_ids = [item.get("id") for item in items]
    if any(not item_id for item_id in item_ids) or len(set(item_ids)) != len(item_ids):
        fail("adventure items have duplicate or empty ids")
    item_id_set = set(item_ids)
    mapped_item_ids = []
    for location in item_locations:
        if not location.get("title") or not location.get("detail"):
            fail(f"item find location {location.get('id')} has no title or detail")
        listed = location.get("itemIDs", [])
        if not isinstance(listed, list):
            fail(f"item find location {location.get('id')} has invalid itemIDs")
        mapped_item_ids.extend(listed)
    if set(mapped_item_ids) != item_id_set or len(mapped_item_ids) != len(item_ids):
        fail("each adventure item must be mapped to exactly one find location")
    all_consequence_ids = {
        consequence.get("id")
        for steps in steps_by_scene.values()
        for step in steps
        for consequence in step.get("roll", {}).get("failureConsequences", [])
    }
    for item in items:
        item_id = item.get("id")
        for required_key in ("title", "locationID", "detail", "effects"):
            if not item.get(required_key):
                fail(f"item {item_id} has no {required_key}")
        if not item.get("playerCardDetail") or not item.get("playerCardUses"):
            fail(f"item {item_id} has no player-safe card copy")
        if item.get("locationID") not in set(location_ids):
            fail(f"item {item_id} references missing find location {item.get('locationID')}")
        uses = item.get("initialUses")
        if not isinstance(uses, int) or isinstance(uses, bool) or uses < 1:
            fail(f"item {item_id} has invalid initialUses")
        effects = item.get("effects", [])
        effect_ids = [effect.get("id") for effect in effects]
        if any(not effect_id for effect_id in effect_ids) or len(set(effect_ids)) != len(effect_ids):
            fail(f"item {item_id} has duplicate or empty effect ids")
        for effect in effects:
            if not effect.get("title") or not effect.get("detail"):
                fail(f"effect {effect.get('id')} in {item_id} has no title or detail")
            if effect.get("timing") not in {"beforeRoll", "afterFailure"}:
                fail(f"effect {effect.get('id')} in {item_id} has invalid timing")
            modifier = effect.get("modifier")
            if modifier is not None and (not isinstance(modifier, int) or isinstance(modifier, bool)):
                fail(f"effect {effect.get('id')} in {item_id} has a non-integer modifier")
            invalid_steps = set(effect.get("stepIDs", [])) - step_ids
            if invalid_steps:
                fail(f"effect {effect.get('id')} references missing steps: {sorted(invalid_steps)}")
            invalid_scenes = set(effect.get("sceneIDs", [])) - scene_ids
            if invalid_scenes:
                fail(f"effect {effect.get('id')} references missing scenes: {sorted(invalid_scenes)}")
            invalid_consequences = set(effect.get("consequenceIDs", [])) - all_consequence_ids
            if invalid_consequences:
                fail(f"effect {effect.get('id')} references missing consequences: {sorted(invalid_consequences)}")
            invalid_endings = set(effect.get("endingIDs", [])) - ending_ids
            if invalid_endings:
                fail(f"effect {effect.get('id')} references missing endings: {sorted(invalid_endings)}")
        weapon = item.get("weapon")
        if weapon is not None:
            if not isinstance(weapon, dict) or not weapon.get("skill") or not weapon.get("damageDice"):
                fail(f"item {item_id} has an invalid weapon")
            if not isinstance(weapon.get("ammunition"), int) or weapon["ammunition"] < 1:
                fail(f"item {item_id} has invalid weapon ammunition")
    if guide.get("characters"):
        fail("guide must use player-supplied characters, not fixed story characters")
    destinations: set[str] = set()
    for scene_id, steps in steps_by_scene.items():
        for step in steps:
            if step.get("sceneID") != scene_id:
                fail(f"step {step['id']} has sceneID {step.get('sceneID')}, expected {scene_id}")
            cue_id = step.get("audioCueID")
            if cue_id and cue_id not in cue_ids:
                fail(f"guided flow references missing audio cue {cue_id}")
            for handout_id in [step.get("handoutID"), *step.get("handoutIDs", [])]:
                if handout_id and handout_id not in handout_ids:
                    fail(f"guided flow references missing handout {handout_id}")
                if handout_id and handout_id not in set(scenes_by_id[scene_id].get("handoutIds", [])):
                    fail(f"{step['id']} exposes {handout_id} outside its scene handout list")
            referenced_npcs = [step.get("npcID"), *step.get("npcIDs", [])]
            invalid_npcs = {npc_id for npc_id in referenced_npcs if npc_id and npc_id not in npc_ids}
            if invalid_npcs:
                fail(f"guided flow references missing NPCs: {sorted(invalid_npcs)}")
            for npc_id in referenced_npcs:
                if npc_id:
                    npc = next(entry for entry in manifest.get("npcs", []) if entry["id"] == npc_id)
                    if scene_id not in {appearance.get("sceneId") for appearance in npc.get("appearances", [])}:
                        fail(f"{step['id']} references {npc_id} without a scene-specific appearance in {scene_id}")
            for option in step.get("options", []):
                destination = option.get("destinationSceneID")
                if destination:
                    destinations.add(destination)
                ending_id = option.get("endingID")
                if ending_id and ending_id not in ending_ids:
                    fail(f"guided flow references missing ending {ending_id}")
            roll = step.get("roll")
            if roll:
                consequences = roll.get("failureConsequences", [])
                if not isinstance(consequences, list):
                    fail(f"roll {step['id']} has invalid failure consequences")
                if any(not isinstance(consequence, dict) for consequence in consequences):
                    fail(f"roll {step['id']} has a non-object consequence")
                consequence_ids = [consequence.get("id") for consequence in consequences]
                if not consequences:
                    fail(f"roll {step['id']} has no failure consequence")
                if len(set(consequence_ids)) != len(consequence_ids) or any(not consequence_id for consequence_id in consequence_ids):
                    fail(f"roll {step['id']} has duplicate or empty consequence ids")
                for consequence in consequences:
                    for required_key in ("title", "detail"):
                        if not consequence.get(required_key):
                            fail(f"consequence {consequence.get('id')} in {step['id']} has no {required_key}")
                    ending_ids_value = consequence.get("endingIDs", [])
                    if not isinstance(ending_ids_value, list) or any(not isinstance(ending_id, str) for ending_id in ending_ids_value):
                        fail(f"consequence {consequence.get('id')} has invalid ending ids")
                    invalid_endings = set(ending_ids_value) - ending_ids
                    if invalid_endings:
                        fail(f"consequence {consequence['id']} references missing endings: {sorted(invalid_endings)}")
                    effect = consequence.get("effect", {})
                    if not isinstance(effect, dict):
                        fail(f"consequence {consequence.get('id')} has an invalid effect")
                    if set(effect) - {"threatDelta", "minimumThreat", "timeDelta", "warmthDelta", "trustDelta", "injuryDelta"}:
                        fail(f"consequence {consequence['id']} in {step['id']} has an unsupported effect")
                    for effect_key in effect:
                        if not isinstance(effect[effect_key], int) or isinstance(effect[effect_key], bool):
                            fail(f"consequence {consequence['id']} has a non-integer {effect_key}")
            for clue_id in [step.get("clueID"), *step.get("clueIDs", [])]:
                if clue_id and clue_id not in {clue["id"] for clue in manifest.get("clues", [])}:
                    fail(f"guided flow references missing clue {clue_id}")
                if clue_id and clue_id not in set(scenes_by_id[scene_id].get("clueIds", [])):
                    fail(f"{step['id']} exposes {clue_id} outside its scene clue list")
            required_scenes = set()
            for option in step.get("options", []):
                required = option.get("requiresCompletedSceneIDs", [])
                if not isinstance(required, list) or any(scene_id not in scene_ids for scene_id in required):
                    fail(f"option {option.get('id')} in {step['id']} has invalid scene requirements")
                required_scenes.update(required)
            if step["id"] in {"S03_NEXT", "S04_NEXT", "S05_NEXT"}:
                archive = next((option for option in step.get("options", []) if option.get("destinationSceneID") == "S06"), None)
                if not archive or set(archive.get("requiresCompletedSceneIDs", [])) != {"S03", "S04", "S05"}:
                    fail(f"{step['id']} must gate S06 behind S03, S04 and S05")
            if step["id"] == "S07_DANGER":
                    for ending_id in sorted(ending_ids):
                        available = [
                            consequence
                            for consequence in consequences
                            if not consequence.get("endingIDs") or ending_id in consequence["endingIDs"]
                        ]
                        if len(available) != 2:
                            fail(f"S07_DANGER must expose exactly two consequences for {ending_id}")

    if not destinations <= scene_ids:
        fail(f"guided flow references missing destination scenes: {sorted(destinations - scene_ids)}")

    required_steps = {"S01_READ", "S01_ITEMS", "S01_DISTRIBUTE", "S01_CLUE", "S02_CHOICE", "S06_TRIGGER", "S07_DANGER", "S08_NEXT"}
    if not required_steps <= step_ids:
        fail(f"required guide steps missing: {sorted(required_steps - step_ids)}")

    combat = guide.get("combat")
    if not isinstance(combat, dict) or not isinstance(combat.get("enemy"), dict):
        fail("guide must define a combat configuration")
    enemy = combat["enemy"]
    for key in ("id", "name", "damageDice", "notes"):
        if not enemy.get(key):
            fail(f"combat enemy has no {key}")
    for key in ("maxLP", "initiative", "attackSkill"):
        if not isinstance(enemy.get(key), int) or isinstance(enemy.get(key), bool) or enemy[key] < 1:
            fail(f"combat enemy has invalid {key}")
    if enemy.get("parryable") is not False:
        fail("the Knochenhirsch must be marked as not parryable")
    victories = combat.get("victoryByEnding", {})
    if set(victories) != ending_ids or any(not isinstance(value, str) or not value for value in victories.values()):
        fail("combat victory text must cover exactly all three endings")

    material_steps = {
        "S01_READ", "S01_ITEMS", "S01_DISTRIBUTE", "S01_CLUE",
        "S02_READ", "S02_ACT", "S02_CLUE",
        "S03_READ", "S03_CLUE",
        "S04_READ", "S04_CLUE",
        "S05_READ", "S05_CLUE",
        "S06_READ", "S06_CLUE", "S06_NEXT",
        "S07_READ", "S07_CHOICE",
        "S08_READ",
    }
    missing_material_steps = {
        step["id"]
        for steps in steps_by_scene.values()
        for step in steps
        if step["id"] in material_steps and not step.get("materialInstruction")
    }
    if missing_material_steps:
        fail(f"material instructions missing: {sorted(missing_material_steps)}")

    print(f"Guided flow QA: PASS ({len(step_ids)} steps, {len(step_scenes)} scenes, {len(destinations)} destinations)")


if __name__ == "__main__":
    main()
