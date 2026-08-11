# Handoff 16 – Audio-Oberfläche 2.0.6

## Stand

Die technische Audio-Bibliothek bleibt aus Kompatibilitätsgründen bei 46 Dateien. In den neun Szenen werden aber nur noch hörbar unterschiedliche Cues gezeigt. Stumme und doppelte Platzhalter sind aus den Szenen entfernt.

## Änderungen

- Das Manifest trägt Version `2.0.6` und ist in `content/`, `app/` und `web/` synchronisiert.
- Der Epilog besitzt keine Tonspur mehr: App und Web erklären stattdessen bewusst, dass nach dem Finale Stille wirken soll.
- Das gedruckte Soundboard und die Tischreferenz nennen ausschließlich sichtbare Cues.
- Die Finaltexte nutzen nur die finale Auswahl `A08`, `M05` und `SFX20`.
- `tools/validate_project.py` erkennt nun zwei bytegleiche Audiodateien in derselben Szene.

## Prüfung

`python tools/build_web_preview.py`, `python tools/build_print_pack.py`, `python tools/validate_project.py` und `node --check web/js/app.js` sind erfolgreich durchgelaufen. `outputs/14_Soundboard-Cues.pdf` wurde als PNG gerendert und visuell kontrolliert.

## Release

Der iOS-Compile-Check für Commit `35a58eb` und der Release-Workflow für Tag `v2.0.6` sind erfolgreich. Die veröffentlichte IPA wurde heruntergeladen und geprüft:

- Größe: `66060736` Bytes
- SHA-256: `eee2270d1a269b738c24e527d5178649a551439c4b913d433dd545fbadc21de0`

`altstore/source.json` verweist auf genau diese Datei. Nach dem folgenden Push kann AltStore 2.0.6 laden.
