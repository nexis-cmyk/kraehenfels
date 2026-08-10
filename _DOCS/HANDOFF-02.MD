# Handoff 02

## Druckpaket, visuelle Überarbeitung

Die Druckunterlagen wurden vollständig neu gestaltet. `tools/build_print_pack.py` erzeugt jetzt einen einheitlichen Look mit warmem Papier, dunklem Tannengrün, Serifentiteln, feinen Rändern und einfachen Holzschnitt-Elementen.

## Neue Grafikquellen

- `print/assets/kraehenfels-cover.png`: winterliches Dorf, Kirche, Grube und die ferne Weiße Frau. Es liegt als Titelbild in `00_Spielstart.pdf` und als Szenenmotiv im SL-Abenteuer vor.
- `print/assets/elisabeth-abele-cabinet-photo.png`: Kabinettfoto für Handout H05.
- `print/assets/bell-and-clapper-etching.png`: Radierung für H06, H10, H11 und die SL-Unterlagen.

## Aufbau

- `00_Spielstart.pdf` hat jetzt ein Titelblatt und eine kurze Briefing-Seite.
- `02_Handouts.pdf` enthält zwei ausschneidbare A5-Karten pro A4-Querformatseite. H01 ist ein Kutschschein, H03 eine Zeitung, H04 ein Kirchenbuch, H05 das Foto, H06 ein Liedblatt, H07 ein Werkbuch und die übrigen Hinweise folgen derselben Papierlogik.
- Dorf- und Grubenkarte wurden mit Papierton, Tannen, Ortszeichen, Wegen, Bach und Grubenförderturm neu gezeichnet.

## Prüfung

Ausgeführt:

```powershell
python tools/build_print_pack.py
python tools/validate_project.py
```

Zusätzlich wurden die finalen Seiten mit dem gebündelten Poppler-Programm nach PNG gerendert und visuell geprüft. Dabei wurde eine zusätzliche, leere Seite im Figurenbau entfernt und die Soundboard-Tabelle auf Zeilenumbruch umgestellt.

## Nächste Sitzung

1. Bei neuer Storygrafik die Dateien in `print/assets/` ergänzen und den Generator erneut ausführen.
2. Nach jeder visuellen Änderung `python tools/validate_project.py` ausführen und alle geänderten PDF-Seiten rendern.
3. Die App bei Bedarf um vollständige digitale Handout-Ansichten erweitern. Der aktuelle IPA-Stand zeigt Handout-Titel, Format und Spoilerstatus, aber nicht die Druckgrafiken selbst.
