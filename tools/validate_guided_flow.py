#!/usr/bin/env python3
"""Cross-check the hand-authored Swift guide against the generated content graph."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FLOW = ROOT / "app" / "Kraehenfels" / "Models" / "GuidedFlowModels.swift"
MANIFEST = ROOT / "content" / "manifest.json"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def main() -> None:
    source = FLOW.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    step_ids = set(re.findall(r'GuideStep\(id: "([^"]+)"', source))
    step_scenes = set(re.findall(r'GuideStep\(id: "[^"]+", sceneID: "([^"]+)"', source))
    if not step_ids:
        fail("no guided steps found")
    scene_ids = {scene["id"] for scene in manifest["scenes"]}
    if step_scenes != scene_ids:
        fail(f"guided scenes differ from manifest: missing={sorted(scene_ids - step_scenes)}, extra={sorted(step_scenes - scene_ids)}")

    cue_ids = {cue["id"] for cue in manifest["audioCues"]}
    for cue_id in re.findall(r'audioCueID: "([^"]+)"', source):
        if cue_id not in cue_ids:
            fail(f"guided flow references missing audio cue {cue_id}")

    handout_ids = {handout["id"] for handout in manifest["handouts"]}
    for handout_id in set(re.findall(r'"(H[0-9]{2})"', source)):
        if handout_id not in handout_ids:
            fail(f"guided flow references missing handout {handout_id}")

    destinations = set(re.findall(r'destinationSceneID: "([^"]+)"', source))
    if not destinations <= scene_ids:
        fail(f"guided flow references missing destination scenes: {sorted(destinations - scene_ids)}")

    required_steps = {"S01_READ", "S01_CLUE", "S02_CHOICE", "S06_TRIGGER", "S07_DANGER", "S08_NEXT"}
    if not required_steps <= step_ids:
        fail(f"required guide steps missing: {sorted(required_steps - step_ids)}")

    print(f"Guided flow QA: PASS ({len(step_ids)} steps, {len(step_scenes)} scenes, {len(destinations)} destinations)")


if __name__ == "__main__":
    main()
