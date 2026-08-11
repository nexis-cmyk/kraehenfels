# Handoff 07: Sound-Ersatzkatalog

## Stand

Die 46 vorhandenen Audio-Dateien sind technisch gueltig, aber prozedural erzeugt. Sie bestehen aus einfachen Wellenformen, Rauschen, Glockenhuellen und FFmpeg-Exporten. Das ist der Grund, warum mehrere Cues eher wie kurze "Bumm, Tsch"-Platzhalter wirken und nicht wie echte Szenengeraeusche.

Der neue Produktionskatalog liegt in `_DOCS/SOUND-PROMPTS.md`. Er enthaelt fuer jede Soundboard-Datei:

- exakte Cue-ID
- exakten Dateinamen
- kurzen Zielklang
- kopierbaren Prompt fuer Audio-Generatoren
- Loop- oder One-shot-Hinweis

## Naechster Arbeitsschritt

Die beste Route ist, neue Quellen mit den vorhandenen Dateinamen zu erzeugen oder aus lizenzierten/CC0-Quellen zu schneiden. Danach die Dateien in `audio/generated/` und `web/assets/audio/` ersetzen, die Web-Testversion neu bauen und auf iPhone-Audio testen.

Empfohlene Reihenfolge:

1. Ambiences A01, A03 bis A10 ersetzen.
2. Musik M01 bis M06 ersetzen.
3. Zuerst die wichtigsten SFX ersetzen: SFX01, SFX02, SFX07, SFX08, SFX09, SFX12, SFX13, SFX14, SFX15, SFX20, SFX31.
4. `python tools/build_web_preview.py` und `python tools/validate_project.py` ausfuehren.
5. Browser-Test und iPhone-Test mit aktivem Audio-Testbutton machen.

## Hinweis

`SFX06_Stille.wav` sollte spaeter als App-Funktion geloest werden: laufende Atmosphaere kurz ausblenden, echte Stille halten, dann kontrolliert zurueck. Eine stille WAV-Datei ist fuer diesen Effekt weniger zuverlaessig.
