# Übergabe 03: Requisiten- und Kartenüberarbeitung

## Stand

Das Druckpaket wurde auf eine deutlich stärkere Requisitenoptik umgebaut. Die Spielerkarte ist nun eine beschriftete Luftansicht von Krähenfels mit verschneiten Tannen, Bach, Brücke, Kirche, Gasthaus, Schmiede und Grube. Die SL-Fassung legt den geheimen Weg als rote, gestrichelte Ebene darüber.

`02_Handouts.pdf` verwendet für jedes Handout eine eigene Gestaltung: Kutschschein, Zeitungsseite mit Holzstich und Spalten, Kirchenregister, Kabinettfoto, Liedblatt, Stellmacher-Werkbuch, gefaltete Flurkarte, Zeugenaussage, persönlicher Brief und dunkle Ritualkarte.

## Neue Assets

- `print/assets/kraehenfels-aerial-map.png`
- `print/assets/wochenblatt-woodcut.png`
- `print/assets/stallmacherei-technical-etching.png`

## Erzeugen und prüfen

```powershell
python -m py_compile tools/build_print_pack.py
python tools/build_print_pack.py
python tools/validate_project.py
```

Zusätzlich wurden die Spielerkarte sowie alle fünf Handout-Seiten per Poppler als PNG gerendert und visuell geprüft. Temporäre Raster liegen nur unter `_TMP/handout-final-qa/`.
