# Krähenfels 3.0 authoring layer

`canon.json` is the narrative source for the active adventure. The build step copies its validated data into the runtime manifest consumed by SwiftUI and the offline web app.

The folders below are the readable GM layer. They intentionally keep location notes, evidence text and the run sheet close to the data without copying the unlicensed DM Asset Forge repository.

- `locations/` contains one short location brief per playable place.
- `evidence/` contains player-facing evidence copy and handout intent.
- `session/` contains the run sheet and fail-forward guidance.
- `indexes/` contains the clue matrix and asset register.

Run `python tools/build_content_v3.py` after changing the canon. The script validates cross references before writing `content/manifest.json` and the two runtime copies.
