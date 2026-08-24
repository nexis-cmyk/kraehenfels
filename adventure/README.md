# Krähenfels authoring layer

`canon.json` is the narrative source for the active adventure. `guide.json` contains the guided GM flow, preparation checklist and ready-to-play characters. `rules.json` contains the short HTBAH reference. The build step combines all three into the runtime manifest consumed by SwiftUI and the offline web app.

The folders below are the readable GM layer. They intentionally keep location notes, evidence text and the run sheet close to the data without copying the unlicensed DM Asset Forge repository.

- `locations/` contains one short location brief per playable place.
- `evidence/` contains player-facing evidence copy and handout intent.
- `session/` contains the run sheet and fail-forward guidance.
- `indexes/` contains the clue matrix and asset register.

Run `python tools/build_content_v5.py` after changing any adventure source. The script writes `content/manifest.json` and the two runtime copies. Run `python tools/validate_guided_flow.py` to check step IDs, scene destinations, cues and handouts.
