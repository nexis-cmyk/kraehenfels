# Handoff 10: echte Soundquellen eingebaut

## Ergebnis

Die prozeduralen Platzhalter wurden für den Spielabend durch echte, lokal gespeicherte Mixkit-Quellen ersetzt. Der Nutzer muss nichts bei ElevenLabs herunterladen.

## Neuer Ablauf

1. Rohdateien liegen lokal unter `_TMP/mixkit_audio/`.
2. `python tools/build_mixkit_simple_pack.py` erzeugt 18 tischrelevante Quellen in `audio/mixkit_simple_pack/`.
3. `python tools/import_audio_replacements.py audio/mixkit_simple_pack --simple-pack --sync-web` verteilt sie auf die 46 App- und Web-Cues.
4. `python tools/build_web_preview.py` synchronisiert die Testversion.
5. `python tools/validate_project.py` prüft Manifest, Druckunterlagen und Audiozuordnung.

## Prüfung

Der Import meldet `Imported 46 of 46 manifest target files from the simple pack`. Der Validator meldet 9 Szenen, 11 Handouts, 5 NPCs, 11 Hinweise und 46 Audio-Cues ohne Fehler.

## Wichtige Dateien

- `tools/build_mixkit_simple_pack.py`
- `audio/mixkit_simple_pack/`
- `_DOCS/AUDIO-SOURCES.md`
- `tools/import_audio_replacements.py`

Die Rohquellen in `_TMP/` sind absichtlich nicht Teil der normalen Projektstruktur. Die im Bundle verwendeten, daraus erzeugten Dateien liegen unter `audio/generated/`, `app/Kraehenfels/Resources/Audio/` und `web/assets/audio/`.
