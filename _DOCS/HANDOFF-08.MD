# Handoff 08: Audio-Neuerzeugung vorbereiten

## Stand

Der Nutzer moechte die aktuellen Sounds komplett neu erstellen lassen, weil die prozedural erzeugten Platzhalter zu flach und kuenstlich klingen.

Neu angelegt:

- `_DOCS/AUDIO-REBUILD-MASTER-PROMPT.md`: ein einzelner kopierbarer Gesamtprompt fuer eine externe Audio-KI oder einen Sound-Designer.
- `tools/import_audio_replacements.py`: Import-Skript fuer neue Audio-Dateien mit stabilen Dateinamen.

Der bestehende Detailkatalog bleibt in `_DOCS/SOUND-PROMPTS.md`.

## Import-Ablauf

Neue Audios in einen eigenen Ordner legen. Die Dateinamen muessen exakt wie im Manifest heissen. Falls der Generator nur WAV ausgibt, reicht der gleiche Basisname.

```powershell
python tools/import_audio_replacements.py "C:\Pfad\zu\neuen-sounds" --sync-web
python tools/build_web_preview.py
python tools/validate_project.py
```

Das Skript liest `content/manifest.json`, findet alle 46 Cue-Dateien, normalisiert mit FFmpeg, schreibt nach `audio/generated/`, kopiert nach `app/Kraehenfels/Resources/Audio/` und mit `--sync-web` nach `web/assets/audio/`.

## Hinweise

- Keine neuen Dateinamen einfuehren, ausser Manifest, App und Webversion werden bewusst angepasst.
- Loops auf Klicks pruefen.
- SFX06 bleibt technisch besser als App-Funktion. Die stille WAV bleibt nur Kompatibilitaet.
- Nach erfolgreichem Import muss eine neue Web-Testversion und danach eine neue iPhone-IPA gebaut werden.
