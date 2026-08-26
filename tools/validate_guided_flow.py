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
    steps_by_scene = guide.get("steps", {})
    step_ids = {step["id"] for steps in steps_by_scene.values() for step in steps}
    step_scenes = set(steps_by_scene)
    if not step_ids:
        fail("no guided steps found")
    if step_scenes != scene_ids:
        fail(f"guided scenes differ from manifest: missing={sorted(scene_ids - step_scenes)}, extra={sorted(step_scenes - scene_ids)}")

    cue_ids = {cue["id"] for cue in manifest["audioCues"]}
    handout_ids = {handout["id"] for handout in manifest["handouts"]}
    ending_ids = {ending["id"] for ending in manifest["endings"]}
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
                    if set(effect) - {"threatDelta", "minimumThreat"}:
                        fail(f"consequence {consequence['id']} in {step['id']} has an unsupported effect")
                    for effect_key in effect:
                        if not isinstance(effect[effect_key], int) or isinstance(effect[effect_key], bool):
                            fail(f"consequence {consequence['id']} has a non-integer {effect_key}")
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

    required_steps = {"S01_READ", "S01_CLUE", "S02_CHOICE", "S06_TRIGGER", "S07_DANGER", "S08_NEXT"}
    if not required_steps <= step_ids:
        fail(f"required guide steps missing: {sorted(required_steps - step_ids)}")

    print(f"Guided flow QA: PASS ({len(step_ids)} steps, {len(step_scenes)} scenes, {len(destinations)} destinations)")


if __name__ == "__main__":
    main()
