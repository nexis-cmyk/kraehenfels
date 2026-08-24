# Handoff 35

## Stand

- Datum: 2026-08-24
- Branch: `codex/ipad-gm-redesign`
- Ausgangsbasis: Remote `main`, Release 4.0.0
- Ziel: iPad-Leitstand für den Guided Flow überarbeiten

## Umgesetzt

- `adventure/guide.json` ist die gemeinsame Quelle für Vorbereitung, drei Schnellstartfiguren, Spielerbriefing und 41 Spielleiterschritte.
- `adventure/rules.json` ist die gemeinsame Quelle für die Kurzregeln.
- `tools/build_content_v5.py` schreibt daraus identische Manifeste für Content, native App und Web-Teststand.
- Die native App nutzt eine zweispaltige `NavigationSplitView`: Szenen links, aktueller Spielleiterschritt rechts. Der frühere permanente dritte Kontextbereich ist entfernt.
- Der Kontext öffnet sich bei Bedarf als Sheet. Das Audio-Dock liegt über `safeAreaInset` am unteren sicheren Rand.
- Guided Flow und Startassistent haben eine sichtbare Zurück-Taste. Der Spielstand speichert dafür einen V5-Verlauf und migriert ältere V4-Journale.
- Zurückgehen stellt die vorige Position wieder her und behält Hinweise sowie Tischnotizen. Ein Wechsel in einen begonnenen anderen Pfad verlangt Bestätigung und setzt nur abhängige spätere Szenen zurück.
- Die Webansicht nutzt dieselben Guided-Daten, hat ebenfalls sichtbare Zurück-Navigation, Pfadbestätigung, sicheren Scrollraum und die Waldnacht-Farbwelt.
- Die Web-Dateien tragen den Cache-Suffix `v4.1.2`.

## Prüfungen

Erfolgreich:

- `python tools/validate_guided_flow.py`
- `node --check web/js/app.js`
- `node --check web/js/guided-flow.js`
- Manifest-Synchronität für alle drei Laufzeitdateien
- `python -m py_compile tools/build_content_v5.py tools/validate_guided_flow.py`
- `git diff --check`
- Live-Test im Browser bei 834 x 1194 und 1194 x 834

Bekannt offen:

- `python tools/validate_project.py` stoppt wegen der bereits fehlenden generierten Datei `audio/generated/V6_A01_Kutschenstrasse.m4a`.
- `python tools/validate_audio_v6.py` kann in der Windows-Umgebung `ffmpeg` nicht starten.
- Ein nativer Xcode-Build war in der Windows-Umgebung nicht möglich, da `swiftc`, `xcodebuild` und `xcodegen` fehlen.

## Nächster Schritt

Auf macOS mit Xcode Projekt generieren, native Unit-Tests und Build ausführen, anschließend den Branch committen und pushen.
