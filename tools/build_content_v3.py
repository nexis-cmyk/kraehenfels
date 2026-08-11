"""Build and validate the Krähenfels 3.0 runtime manifest."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "adventure" / "canon.json"
DESTINATIONS = [
    ROOT / "content" / "manifest.json",
    ROOT / "app" / "Kraehenfels" / "Resources" / "manifest.json",
    ROOT / "web" / "data" / "manifest.json",
]


def fail(message: str) -> None:
    raise SystemExit(f"content build failed: {message}")


def validate(data: dict) -> None:
    required = {"meta", "phases", "travelHooks", "threatLevels", "facts", "endings", "maps", "npcs", "clues", "handouts", "scenes", "locations", "audioCues"}
    missing = required - data.keys()
    if missing:
        fail(f"missing top-level fields: {', '.join(sorted(missing))}")

    def unique(items: list[dict], label: str) -> set[str]:
        ids = [str(item.get("id", "")) for item in items]
        if not all(ids):
            fail(f"{label} contains an empty id")
        if len(ids) != len(set(ids)):
            fail(f"{label} contains duplicate ids")
        return set(ids)

    phase_ids = unique(data["phases"], "phases")
    hook_ids = unique(data["travelHooks"], "travelHooks")
    fact_ids = unique(data["facts"], "facts")
    ending_ids = unique(data["endings"], "endings")
    map_ids = unique(data["maps"], "maps")
    npc_ids = unique(data["npcs"], "npcs")
    clue_ids = unique(data["clues"], "clues")
    handout_ids = unique(data["handouts"], "handouts")
    scene_ids = unique(data["scenes"], "scenes")
    location_ids = unique(data["locations"], "locations")
    cue_ids = unique(data["audioCues"], "audioCues")

    if not ending_ids or len(ending_ids) != 3:
        fail("the adventure must expose exactly three endings")
    for fact in data["facts"]:
        if len(fact.get("clueIds", [])) < 2:
            fail(f"fact {fact['id']} needs at least two clue routes")
        if any(clue not in clue_ids for clue in fact.get("clueIds", [])):
            fail(f"fact {fact['id']} references an unknown clue")
    for hook in data["travelHooks"]:
        if any(clue not in clue_ids for clue in hook.get("linkedClueIds", [])):
            fail(f"travel hook {hook['id']} references an unknown clue")
    for ending in data["endings"]:
        if any(fact not in fact_ids for fact in ending.get("requiredFactIds", [])):
            fail(f"ending {ending['id']} references an unknown fact")
    for map_entry in data["maps"]:
        if not map_entry.get("playerAsset") or not map_entry.get("gmAsset"):
            fail(f"map {map_entry['id']} needs player and GM assets")
    for npc in data["npcs"]:
        if len(npc.get("states", [])) != 3:
            fail(f"NPC {npc['id']} needs exactly three manual states")
        if any(handout not in handout_ids for handout in npc.get("givesHandoutIds", [])):
            fail(f"NPC {npc['id']} references an unknown handout")
    for clue in data["clues"]:
        if clue.get("factId") not in fact_ids:
            fail(f"clue {clue['id']} references an unknown fact")
        if clue.get("handoutId") and clue["handoutId"] not in handout_ids:
            fail(f"clue {clue['id']} references an unknown handout")
    for handout in data["handouts"]:
        if any(clue not in clue_ids for clue in handout.get("linkedClueIds", [])):
            fail(f"handout {handout['id']} references an unknown clue")
    for scene in data["scenes"]:
        if scene.get("phaseId") not in phase_ids:
            fail(f"scene {scene['id']} references an unknown phase")
        if any(next_id not in scene_ids for next_id in scene.get("nextSceneIds", [])):
            fail(f"scene {scene['id']} references an unknown next scene")
        for field, ids, universe in (("npcIds", scene.get("npcIds", []), npc_ids), ("clueIds", scene.get("clueIds", []), clue_ids), ("handoutIds", scene.get("handoutIds", []), handout_ids), ("audioCueIds", scene.get("audioCueIds", []), cue_ids), ("locationIds", scene.get("locationIds", []), location_ids)):
            if any(item not in universe for item in ids):
                fail(f"scene {scene['id']} references an unknown {field}")
    for location in data["locations"]:
        if location.get("mapId") not in map_ids:
            fail(f"location {location['id']} references an unknown map")
        for field, ids, universe in (("sceneIds", location.get("sceneIds", []), scene_ids), ("npcIds", location.get("npcIds", []), npc_ids), ("clueIds", location.get("clueIds", []), clue_ids)):
            if any(item not in universe for item in ids):
                fail(f"location {location['id']} references an unknown {field}")
    for cue in data["audioCues"]:
        if cue.get("scene") not in scene_ids:
            fail(f"audio cue {cue['id']} references an unknown scene")
        if not cue.get("file"):
            fail(f"audio cue {cue['id']} has no file")


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    validate(data)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    for destination in DESTINATIONS:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(payload, encoding="utf-8")
    print(f"Built Krähenfels 3.0: {len(data['scenes'])} scenes, {len(data['handouts'])} handouts, {len(data['npcs'])} NPCs, {len(data['clues'])} clues, {len(data['audioCues'])} audio cues")


if __name__ == "__main__":
    main()
