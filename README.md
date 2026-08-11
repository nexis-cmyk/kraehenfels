# Krähenfels

`Krähenfels: Die letzte Kutsche` ist ein deutschsprachiges Folk-Horror-Abenteuer für drei Spieler und eine erstmalige Spielleitung. Es verwendet das Regelwerk How to be a Hero und spielt im Schwarzwald des Jahres 1890. Die Geschichte dreht sich um eine manipulierte Kutschfahrt, ein verdrehtes Gastrecht und einen Waldpakt an der Alten Eiche.

Das Repository enthält:

- das vollständige Abenteuer mit SL-Schnellreferenz
- eine spoilerfreie Dorfkarte, eine markierte SL-Karte und drei Detailkarten
- Handouts und einen geführten Charakterbau
- einsatzfertige Atmosphären, Musik und Soundeffekte aus dokumentierten Mixkit-Quellen
- eine native iOS-Begleitapp ab iOS 17 mit Szenenleitstand, Nachtstand, NPCs, Pflichtspuren, Vorlesetexten, Tischnotizen und Audio-Selbsttest
- GitHub Actions für Tests, IPA-Build und AltStore-Feed
- eine offlinefähige Web-Testversion für Leitstand und Soundboard

## iPhone-Build und AltStore

Die V3-Projektdatei und der AltStore-Feed sind vorbereitet. Der IPA-Build läuft auf macOS über den GitHub-Workflow; bis dieser abgeschlossen ist, bleibt der letzte öffentliche IPA-Release `v2.0.7`.

- [GitHub-Repository](https://github.com/nexis-cmyk/kraehenfels)
- [Release-Übersicht](https://github.com/nexis-cmyk/kraehenfels/releases)
- [AltStore-Feed](https://raw.githubusercontent.com/nexis-cmyk/kraehenfels/main/altstore/source.json)

Die IPA ist unsigniert und wird beim Installieren von AltStore mit deinem Apple-Account signiert. Eine kurze Windows-Anleitung steht in [`altstore/README.md`](altstore/README.md).

## Projektstruktur

- `adventure/`: kanonische V3-Quelle, Ortsakten, Beweismatrix und Run-Sheet
- `content/`: aus dem Kanon erzeugte Geschichte, Szenen, Hinweise und Cue-IDs
- `print/`: Quellen und Generator für die Druckunterlagen
- `audio/`: prozedurale Audioerzeugung und Metadaten
- `app/`: SwiftUI-App und Tests
- `web/`: offlinefähige Browser-Testversion und lokale Startanleitung
- `altstore/`: Vorlage für den AltStore-Feed
- `_DOCS/`: Architektur und Übergabenotizen
- `_TMP/`: lokale Prüfskripte und temporäre Dateien

## Lokaler Build

Die komplette V3-Ausgabe lässt sich unter Windows erzeugen:

```powershell
python tools/build_content_v3.py
python tools/build_visual_assets_v3.py
python tools/build_audio_v3.py
python tools/build_print_pack.py
python tools/build_invitation.py
python tools/build_web_preview.py
python tools/build_archives_v3.py
python tools/validate_project.py
```

Danach liegen die PDFs unter `outputs/` und die Audio-Dateien unter `audio/generated/`. Für die App werden die erzeugten Audios nach `app/Kraehenfels/Resources/Audio/` kopiert. Das Projekt wird auf macOS mit XcodeGen erzeugt:

```bash
brew install xcodegen
cd app
xcodegen generate
xcodebuild -project Kraehenfels.xcodeproj -scheme Kraehenfels \
  -destination 'generic/platform=iOS Simulator' test
```

Ein Tag wie `v2.0.0` oder der Button **Run workflow** mit einer Versionsnummer startet `.github/workflows/release.yml`. Der Workflow erzeugt eine unsignierte `Kraehenfels.ipa` und zusätzlich einen ausgefüllten `altstore/source.generated.json` als Release-Asset. Die aktuell gepflegte dauerhafte Feed-URL ist `https://raw.githubusercontent.com/nexis-cmyk/kraehenfels/main/altstore/source.json`.

## Druckpaket

Die Unterlagen haben eine gemeinsame 1890er-Schwarzwald-Optik: kaltes Nachtblau, Rostrot, Schnee, Tannen und klare Beweisstück-Rahmen. Die Dorfkarte ist eine realistische Luftansicht mit sichtbarem Gelände, Bach, Gebäuden und Prozessionsweg. Jede Spielerinformation ist als eigenes ausschneidbares Beweisstück gestaltet und trägt ihre Ausgabe-ID.

- `00_Spielstart.pdf`: kurze Vorbereitung für die erste Spielleitung
- `Einladung_Kraehenfels.pdf` und `Einladung_Kraehenfels.png`: druckbare Spieleinladung mit Abenteuerteaser und Charaktervorbereitung
- `01_Karte_Spieler.pdf`: spoilerfreie Tischkarte
- `01_Karte_SL.pdf`: geheime Karte mit Routen, Eichenplatz und Prozessionsspur
- `01_Karten_Detail.pdf`: Gasthaus, Kirche und Alte Eiche als separate Tischkarten
- `02_Handouts.pdf`: nur spielersichere, ausschneidbare Hinweise mit Kennung, Schnittlinie und Ausgabezeitpunkt
- `03_Figurenbau.pdf`: ausfüllbare Reiseakte mit Porträtfeld, Passdaten, Rollenfragen, drei Begabungen, 400 Punkten und HTBAH-Schnellregeln (Spielerseite dreimal drucken)
- `10_SL_Abenteuer.pdf`: vorlesbare Szenen, NPCs und Enden
- `11_SL_Schnellreferenz.pdf`: Wahrheit, Pflichtspuren und Improvisationshilfe
- `12_SL_Am_Tisch.pdf`: einseitiger Ablaufzettel mit Hinweisen, Sounds und Eskalation pro Szene
- `13_SL_Spoiler-Handouts.pdf`: H09, das Ritualfragment, getrennt für die Spielleitung
- `14_Soundboard-Cues.pdf`: konkrete Cue-Momente mit Papier-Fallbacks

Für die direkte Weitergabe liegen zusätzlich `outputs/Kraehenfels-Druckpaket.zip` und `outputs/Kraehenfels-Audio.zip` bereit.

## Web-Testversion

Die Browser-Version lässt sich vor dem Sideloaden lokal testen. Sie verwendet dieselben Szenen, NPCs, Handouts und Audiodateien wie die iPhone-App. Die genaue Startanleitung steht in [`web/README.md`](web/README.md).

Nach einem Push auf `main` veröffentlicht GitHub Actions sie außerdem unter `https://nexis-cmyk.github.io/kraehenfels/`. Dafür muss Pages einmal im Repository freigeschaltet werden: **Settings → Pages → Build and deployment → Source: GitHub Actions → Save**. Danach kannst du sie unterwegs als Web-App ausprobieren.

## Audio

Das Soundboard nutzt ein bewusst kleines, unterscheidbares Set aus sechs Atmosphären, zwei Musikflächen und zehn One-Shots. Die V3-Dateien tragen sprechende Namen wie `V3_A02_Dorf_Nacht.m4a` und werden automatisch in App, Web-Version und Soundboard-PDF synchronisiert. Die Prompt- und Quellenabsicht steht in [`_DOCS/SOUND-PROMPTS-V3.md`](_DOCS/SOUND-PROMPTS-V3.md).

Wenn du später eigene oder KI-generierte Dateien einsetzen möchtest, ersetzt du nur die V3-Datei mit demselben Namen und startest anschließend den Audio- und Web-Build erneut.

```powershell
python tools/import_audio_replacements.py "C:\Pfad\zu\neuen-sounds" --sync-web
python tools/build_web_preview.py
python tools/validate_project.py
```

Das Skript schreibt nach `audio/generated/`, `app/Kraehenfels/Resources/Audio/` und mit `--sync-web` auch nach `web/assets/audio/`.

Simple-Pack-Import:

```powershell
python tools/build_mixkit_simple_pack.py
python tools/import_audio_replacements.py "C:\Pfad\zu\simple-sounds" --simple-pack --sync-web
python tools/build_web_preview.py
python tools/validate_project.py
```

## Lizenzhinweise

Die Abenteuertexte und Medien dieses Projekts sind eigenständig erstellt. How to be a Hero ist ein separates Regelwerk. Die Kurzregeln im Spielpaket fassen nur die am Tisch benötigten Mechaniken zusammen und verweisen auf das offizielle Regelwerk.
