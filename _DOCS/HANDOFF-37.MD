# Handoff 37

Datum: 2026-08-24
Branch: `codex/ipad-gm-redesign`
Commit: `c0906d3` plus the feed documentation update after release
Release: `v4.1.1`, Build `7`

## Erledigt

- Der Button `Spielleiter-Modus starten` navigiert im nativen `NavigationSplitView` direkt zur ersten Guided-Szene. Der lokale Fallback für andere Aufrufer bleibt erhalten.
- Jeder Guided-Schritt mit `roll` zeigt eine sichtbare Würfelsession. Das gilt auch für optionale Proben in `playerAction`-Schritten. Die native Ansicht zeigt zusätzlich Pflichtstatus, Zielwert, Modifikator, letztes Ergebnis und den 44-Punkt-Button zum Würfelhelfer.
- `adventure/rules.json` ist die Regelquelle für W100, Erfolgsprüfung, kritische Ergebnisse, Begabungsproben, Standardwürfel und Initiative. Die drei Manifest-Kopien wurden mit `tools/build_content_v5.py` neu erzeugt.
- Kritische Ergebnisse verwenden im nativen und Web-Evaluator die exakten 10-Prozent-Grenzen. Begabungsproben können kritische Erfolge erzeugen.
- Die Web-Vorschau zeigt die Würfelsession auch für Schritte mit einer Probe und besitzt eine eigene Regelansicht.
- Die Kampf-Kurzreferenz nennt ausdrücklich `1W10 plus den Begabungswert Handeln`.

## Prüfung

- `python tools/validate_guided_flow.py`: PASS, 41 Schritte, 8 Szenen.
- `node --check web/js/app.js`: PASS.
- `node --check web/js/guided-flow.js`: PASS.
- `git diff --check`: PASS.
- Live-Test der Web-Vorschau auf localhost: Guided-Start, erster Rollenschritt, Würfelsession, kritischer Erfolg und Regelansicht geprüft.
- GitHub Actions Release-Run `32774580748`: SUCCESS. XcodeGen, native macOS-Kompilierung, IPA-Paketierung und AltStore-Feed waren erfolgreich.
- `tools/validate_project.py` konnte auf Windows nicht starten, weil das lokale Python-Umfeld `pypdf` nicht installiert hat.

## AltStore

Direkter Feed für den neuen Release:

`https://github.com/nexis-cmyk/kraehenfels/releases/download/v4.1.1/source.generated.json`

IPA:

`https://github.com/nexis-cmyk/kraehenfels/releases/download/v4.1.1/Kraehenfels.ipa`

Der veröffentlichte Feed enthält Version `4.1.1`, Build `7`, die IPA-Größe `82445965` Bytes und SHA-256 `07081a517851c01755cbee51520c73a5f3f5f72ae011918f658c49c1da23b4df`.

## Nächster sinnvoller Schritt

Auf dem iPad in AltStore die neue Feed-URL hinzufügen oder den bisherigen Release-Feed aktualisieren, dann Krähenfels installieren. Die IPA ist unsigniert und muss wie gewohnt durch AltStore mit dem eigenen Apple-Account signiert werden.
