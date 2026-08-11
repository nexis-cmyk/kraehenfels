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

## Nächster Schritt

Nach Commit und Push: iOS-CI abwarten, Tag `v2.0.6` auslösen, die erstellte IPA herunterladen und deren Größe/Checksumme in `altstore/source.json` übernehmen. Erst danach darf der Feed 2.0.6 anbieten.
