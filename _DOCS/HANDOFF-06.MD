# Handoff 06: Browser-Test und Spoiler-Schnitt

## Stand

Die Browser-Testversion liegt unter `web/`. Sie ist eine statische PWA ohne Framework und verwendet die gleiche `content/manifest.json`-Quelle wie die iPhone-App. `tools/build_web_preview.py` kopiert die aktuelle Quelle nach `web/data/manifest.json` sowie Icon, sieben Szenenbilder und alle 46 Audios in die zugehörigen Web-Ordner.

Zum lokalen Testen:

```powershell
python tools/build_web_preview.py
python -m http.server 4173 --directory web
```

Dann `http://localhost:4173` öffnen. Die Testversion hat Szenenführung, Vorlesebereich, Spoiler-Schalter, Hinweise, NPCs mit Handout-Zuordnung, Checklisten, getrennte Lautstärke, Szenen-Presets, Einzel-Cues, Stopp und Audio-Selbsttest. Fortschritt bleibt ausschließlich im lokalen Browser gespeichert.

## Druckpaket

`02_Handouts.pdf` enthält nur Spielermaterial: H01, H03 bis H09. Jeder Bogen hat die ID, den Ausgabemoment, Schnittmarken und die mittige Scherenlinie. H10 und H11 liegen getrennt in `13_SL_Spoiler-Handouts.pdf`. H10 wird bei S07 und H11 im Finale ausgegeben. Diese Trennung wird durch `tools/validate_project.py` geprüft.

Die Spielerkarte ist sichtbar als H02 markiert. H05 ist ein A5-Foto, nicht mehr ein nicht vorhandenes doppelseitiges A6-Handout. Text im Szenario, in der Handout-Quelle und im grafischen Foto stimmen überein.

## Konsistenz

Martin Hoch ist durchgehend Pfarrer. Jakob Rieger ist durchgehend der Kutscher und erscheint in Dorf und Grube. Beim nächsten Inhaltswechsel immer ausführen:

```powershell
python tools/build_print_pack.py
python tools/build_web_preview.py
python tools/validate_project.py
```

## Noch ausstehend

- ZIP-Druckpaket aktualisieren und die bestehende Drive-Datei ersetzen.
- Änderungen committen, eine v2.0.1-IPA veröffentlichen und den AltStore-Feed mit deren Größe und SHA-256 aktualisieren.
- Release-IPA auf Manifest, Art und Audio prüfen.
