# Handoff 25

## Aktueller Stand

Krähenfels steht auf dem Arbeitsstand `bb2f86f` auf `master` und `main`. Die Story bleibt die manipulierte Kutschfahrt, das Gasthaus Zum Schwarzen Keiler, Kirche, Schmiede, Waldspur, Rathausarchiv, Alte Eiche und drei Enden. Die native App richtet sich an drei Spieler und eine neue Spielleitung.

## Umgesetzte Leitstand-Funktionen

1. `GMStartView` führt durch Vorbereitung, Materialtrennung, Sicherheitscheck, Schnellstartfiguren und Start der Runde.
2. `GuidedGMView` zeigt 41 Schritte in 8 Szenen. Die Kategorien sind Vorlesen, Spielleiter-Info, Spieleraktion, Auslöser, Hinweis, Würfelprobe, Entscheidung und nächster Schritt.
3. Pro Szene ist der vollständige Audio-Plan mit Start, Stop, Anweisung und Einzelabspielknopf sichtbar.
4. Ein bestätigter Vorlese-Dialog startet den Cue erst nach Tastendruck. Der Text bleibt bis zum Weiterklick sichtbar; danach wird die Musik wieder normal gemischt.
5. Das Finale speichert Erfolge und Fehlschläge. Zwei Erfolge oder zwei Fehlschläge entscheiden die Gefahrenszene.
6. Schritte ohne Probe zeigen einen eigenen Würfelstatus. Der W100-Helfer validiert Werte zwischen 1 und 100 und erklärt kritische Folgen.
7. Karten, Handouts, NPCs, Regeln und Sound sind aus dem aktuellen Schritt erreichbar. Die zentrale Materialansicht bleibt zusätzlich verfügbar.

## Prüfungen

```powershell
python tools/validate_project.py
python tools/validate_audio_v6.py
python tools/validate_guided_flow.py
python -m compileall -q tools
git diff --check
```

Alle lokalen Prüfungen bestanden. GitHub Actions baut den Swift-Code auf macOS; die CI enthält einen Compilerfehler-Reporter, weil Xcode auf Windows nicht verfügbar ist.

## Release-Hinweise

- AltStore-Feed: `https://github.com/nexis-cmyk/kraehenfels/raw/refs/heads/main/altstore/source.json`
- IPA-Mirror: `https://nexis-cmyk.github.io/kraehenfels/Kraehenfels.ipa`
- Aktuelle veröffentlichte Feed-Version: `3.3.0`, SHA-256 `2edba11f0b96867b1521185d69aeb3aff9496c18b64748f52b3bb455c92cde9e`.
- Nach einer neuen Release-IPA muss zuerst der Release-Workflow laufen, danach der Pages-Workflow, damit der Mirror und der Feed zusammenpassen.

## Nächster sinnvoller Schritt

Auf dem iPhone den Audio-Check über Lautsprecher und Box durchführen, die Vorlese-Bestätigung in S01 und S02 testen und anschließend eine komplette Runde mit drei Spielern probespielen. Erst danach sollte ein neuer Release-Tag erstellt werden.
