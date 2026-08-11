# Handoff 09: Simple Sound Pack

## Stand

Der Nutzer ist mit dem 46er-Soundpaket ueberfordert und moechte eine einfache kostenlose Loesung fuer einen privaten Spielabend.

Neu angelegt:

- `_DOCS/AUDIO-SIMPLE-PACK.md`: reduzierte Soundplanung mit 5 Loops, 1 Hintergrundthema und 12 Effektknoepfen.
- `tools/import_audio_replacements.py` hat jetzt `--simple-pack`.

## Simple-Pack-Dateien

Der Nutzer muss nur diese 18 Dateien erzeugen oder herunterladen:

```text
LOOP01_Winterdorf_Wald.m4a
LOOP02_Wirtsstube.m4a
LOOP03_Kapelle_Glockenturm.m4a
LOOP04_Grube_Flutstollen.m4a
LOOP05_Finale_Froststurm.m4a
MUSIC01_Dunkles_Grundthema.m4a
SFX01_Kutschenunfall.wav
SFX02_Fenster_Ast.wav
SFX03_Glocke_Normal.wav
SFX04_Glocke_Falsch.wav
SFX05_Metall_Kloeppel.wav
SFX06_Schritte_Schnee.wav
SFX07_Barfuss_Schritte.wav
SFX08_Stimmen_Berg.wav
SFX09_Klopfen_Boden.wav
SFX10_Atem_Nah.wav
SFX11_Weisse_Frau_Motiv.wav
SFX12_Eisbruch_Finale.wav
```

Import:

```powershell
python tools/import_audio_replacements.py "C:\Pfad\zu\simple-sounds" --simple-pack --sync-web
python tools/build_web_preview.py
python tools/validate_project.py
```

Der Modus verteilt diese 18 Quellen auf alle 46 technischen App-Dateien. `SFX05_Kraehen.wav`, `SFX06_Stille.wav` und `SFX09_Schmiede.wav` werden als stille Dateien erzeugt, damit alte Platzhalter verschwinden.

## Empfehlung

Fuer kostenlose Quellen:

- Loops zuerst bei Mixkit oder Pixabay suchen.
- Spezielle SFX mit Adobe Firefly Sound Effects erzeugen.
- Freesound nur mit CC0-Filter verwenden.
- BBC Sound Effects nur privat/educational nutzen und nicht in einen oeffentlichen Release packen.
