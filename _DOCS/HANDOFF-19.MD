# Handoff 19 · Krähenfels V3

## Stand

Krähenfels wurde auf `3.0.0` und die neue Geschichte `Die letzte Kutsche` umgestellt. Die kanonische Quelle ist `adventure/canon.json`. Die aktive Geschichte handelt von der manipulierten Kutschenfahrt, Gruber, dem verdrehten Gastrecht und dem Knochenhirsch an der Alten Eiche. Die frühere Weiße-Frau- und Grubenhandlung ist nicht mehr Teil des aktiven Manifests.

## Erzeugte Artefakte

- 8 Szenen, 10 Handouts, 6 NPCs, 11 Hinweise, 5 Fakten und 3 Enden
- 4 Karten mit Spieler- und SL-Assets plus 3 Detailkarten
- 18 V3-Audio-Cues
- 11 Spielleiter- und Spieler-PDFs plus Einladung
- SwiftUI-Casefile mit Reisehaken, Fakten, Karten, Spoiler-Schalter, NPC-Zuständen und Eskalationsstufe
- Web-Leitstand mit denselben Daten, lokalen Notizen, Audio-Selbsttest und Soundboard

## Verifikation

Ausgeführt und erfolgreich:

```powershell
python tools/build_content_v3.py
python tools/build_visual_assets_v3.py
python tools/build_audio_v3.py
python tools/build_print_pack.py
python tools/build_invitation.py
python tools/build_web_preview.py
python tools/build_archives_v3.py
python tools/validate_project.py
node --check web/js/app.js
```

Die PDF-Stichproben `00_Spielstart.pdf`, `01_Karte_Spieler.pdf`, `02_Handouts.pdf` und `10_SL_Abenteuer.pdf` wurden mit Poppler gerendert und visuell geprüft. Die Handouts verwenden gestrichelte Außenlinien und eigene layoutspezifische Beweisstücke.

## Release-Abschluss

Der Tag `v3.0.0` wurde veröffentlicht. Der macOS-GitHub-Workflow hat die unsignierte `Kraehenfels.ipa` und `source.generated.json` erzeugt; die IPA ist 108140877 Bytes groß und hat SHA-256 `c30c4b5019570f1a50e37b8837afdb1d721f0acd5d9922c88a463d4e1e176907`. GitHub Pages ist auf GitHub Actions gestellt und der öffentliche Web-Leitstand unter `https://nexis-cmyk.github.io/kraehenfels/` erreichbar. Vor dem Sideload den Release-Feed in AltStore aktualisieren.
