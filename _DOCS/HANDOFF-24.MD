# Übergabe 24: geführter Leitstand und Audio V6

Stand: 12. August 2026.

## Erledigt

- Der native Inhalt steht auf `3.3.0-rc1`.
- `GMStartView` führt durch Vorbereitung, Materialtrennung, Sicherheitscheck und drei sofort spielbare Reisende.
- `GuidedGMView` zeigt pro Schritt die Rollen `JETZT VORLESEN`, `NUR FÜR DIE SPIELLEITUNG`, `DIE SPIELER KÖNNEN JETZT`, `WENN DAS PASSIERT`, `WÜRFELPROBE`, `HINWEIS ODER GEGENSTAND`, `ENTSCHEIDUNG` und `NÄCHSTER SCHRITT`.
- Die Ermittlungsorte Kirche, Schmiede und Waldspur bleiben frei wählbar. Das Archiv erscheint erst nach zwei besuchten Ermittlungsorten.
- Der Gästezimmer-Zustand ist explizit und wird mit dem Riegel-Cue bedient. Finale und Würfelproben werden im Sitzungsjournal gespeichert.
- Materialien, Handouts, Karten, NPC-Dossiers, Fakten und Regeln sind aus dem Leitstand direkt erreichbar.
- Die Audio-Engine zeigt geladene Datei, letzten Status, Fehler und einen Testton. Die Grundmusik kann über den ganzen Abend laufen.
- V6 ersetzt zwölf markierte Cues. Die acht im Hörtest passenden V5-Cues bleiben unverändert.
- Das Druckpaket ist auf denselben Ablauf synchronisiert: vorbereitete Schnellstart-Figuren, M01 als Einstiegsmusik und A01 erst beim Aufbruch; leere Figurenbögen sind ausdrücklich optional.

## Prüfungen

Ausgeführt und erfolgreich:

```powershell
python tools/generate_audio_v6.py
python tools/validate_audio_v6.py
python tools/build_content_v5.py
python tools/validate_project.py
python -m compileall tools -q
```

Der aktuelle Audio-Bericht meldet 20 Dateien, keine Dublette und keine Ähnlichkeitswarnung: [`AUDIO-V6-QA.md`](AUDIO-V6-QA.md).

Swift konnte auf diesem Windows-Rechner nicht kompiliert werden, weil `xcodebuild`, XcodeGen und `swiftc` fehlen. Die neuen Swift-Dateien liegen unter `app/Kraehenfels/`. Der native Build muss auf macOS oder in GitHub Actions laufen.

## macOS-Abnahme

```bash
cd app
xcodegen generate
xcodebuild -project Kraehenfels.xcodeproj -scheme Kraehenfels \
  -destination 'generic/platform=iOS Simulator' test
xcodebuild -project Kraehenfels.xcodeproj -scheme Kraehenfels \
  -destination 'generic/platform=iOS' -allowProvisioningUpdates archive
```

Danach die IPA in AltStore installieren und in der App zuerst den Audio-Selbsttest, danach den geführten Start bis S02 prüfen. Auf dem iPhone außerdem die untere Scrollkante im Hauptmenü und die Audio-Ausgabe über Bluetooth testen.

## Bekannte Grenzen

- Für einen echten IPA-Build und den Sideload wird weiterhin macOS oder GitHub Actions benötigt.
- Der Würfelhelfer wertet den physischen W100 aus. Die Zielwerte stehen auf den Schnellstart-Figurenblättern und werden nicht automatisch aus einem Charakterbogen gelesen.
- Die V6-Dateien sind technisch geprüft. Die letzte kreative Abnahme erfolgt mit `Passt` oder `Falsch` im Audio-Check über die tatsächliche Box.
