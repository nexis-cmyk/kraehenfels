# Handoff 20 · GPT-Karten und Beweisstücke

## Stand

Die bisherigen skizzenhaften Detailkarten wurden ersetzt. Die Kartenplatten für Dorf, Gasthaus, Kirche, Schmiede, Rathausarchiv und Waldheiligtum stammen aus der GPT-Bildgenerierung. Sie enthalten keine eingebrannte Schrift. Titel, Spieler- oder SL-Status, Fundstück-IDs und Fußzeilen werden im reproduzierbaren Python-Build gesetzt.

Die Spielerfassung bleibt spoilerfrei. Die SL-Fassung verwendet rostrote Markierungen, damit H01, H04, H06, H10 und die übrigen Fundstellen auf einen Blick erkennbar sind. Die Detailkarten sind im Druckpaket und in App sowie Web verfügbar.

## Beweisstücke

H06, H07 und H08 verwenden eigene GPT-Bildplatten für Werkzeichnung, Kinderzeichnung und Holzabreibung. H01, H02, H03, H04 und H05 behalten ihre jeweils passende Requisitenform. H02 ist als Zeitung gesetzt und besitzt zusätzlich eine untere Gemeinderats- und Kleinanzeigenleiste. Jedes Spielerhandout hat eine gestrichelte Außenlinie und die Spurgruppe am oberen Rand.

## Build und Prüfung

```powershell
python tools/build_content_v3.py
python tools/build_visual_assets_v3.py
python tools/build_print_pack_v3.py
python tools/build_web_preview.py
python tools/build_archives_v3.py
python tools/validate_project.py
node --check web/js/app.js
```

Die Prüfung läuft mit sechs Karten, acht Szenen, zehn Handouts, sechs NPCs, elf Hinweisen und 18 Audio-Cues durch. Die PDFs wurden mit Poppler gerendert und visuell geprüft. Die Audio-Dateien sind in diesem Handoff unverändert; eine separate Audio-Neuerstellung darf erst nach Hörtest als abgeschlossen gelten.
