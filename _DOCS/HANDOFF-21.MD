# Handoff 21 · Audio V4

## Stand

Die alten, ähnlich klingenden Mixkit-Cues wurden ersetzt. ElevenLabs lieferte sechs 8-Sekunden-Atmosphären, zwei 10-Sekunden-Musikflächen und zehn 4-Sekunden-One-Shots. Die Zielnamen im Bundle bleiben `V3_*`, damit Manifest, App und Web-Version rückwärtskompatibel bleiben.

## Technischer Import

`tools/import_audio_replacements.py` wandelt die WAV-Quellen auf 48 kHz Stereo um. Atmosphären und Musik werden als AAC-M4A abgelegt. One-Shots bleiben PCM-WAV. Die Normalisierung nutzt für Atmosphären und Musik einen Zielpegel von ungefähr -22 LUFS und für Effekte ungefähr -18 LUFS.

## Prüfung

```powershell
python tools/import_audio_replacements.py _TMP/elevenlabs_v4/import --sync-web
python tools/build_web_preview.py
python tools/validate_project.py
```

Alle 18 Cue-Dateien haben eindeutige SHA-256-Fingerprints, 48 kHz und zwei Kanäle. Die Dauern betragen 8 Sekunden für Atmosphären, 10 Sekunden für Musik und 4 Sekunden für One-Shots. Die ausführlichen Produktionsprompts stehen in `SOUND-PROMPTS-V4.md`.
