# Krähenfels

`Die Weiße Frau schweigt` ist ein deutschsprachiges Folk-Horror-Abenteuer für drei Spieler und eine erstmalige Spielleitung. Es verwendet das Regelwerk How to be a Hero und spielt im Schwarzwald des Jahres 1890.

Das Repository enthält:

- das vollständige Abenteuer mit SL-Schnellreferenz
- eine spoilerfreie Dorfkarte und eine markierte SL-Karte
- Handouts und einen geführten Charakterbau
- selbst erzeugte Musik, Atmosphären und Soundeffekte
- eine native iOS-Begleitapp ab iOS 17
- GitHub Actions für Tests, IPA-Build und AltStore-Feed

## Projektstruktur

- `content/`: verbindliche Geschichte, Szenen, Hinweise und Cue-IDs
- `print/`: Quellen und Generator für die Druckunterlagen
- `audio/`: prozedurale Audioerzeugung und Metadaten
- `app/`: SwiftUI-App und Tests
- `altstore/`: Vorlage für den AltStore-Feed
- `_DOCS/`: Architektur und Übergabenotizen
- `_TMP/`: lokale Prüfskripte und temporäre Dateien

## Lokaler Build

Die Drucksachen und Audios lassen sich unter Windows erzeugen:

```powershell
python tools/build_print_pack.py
python audio/generate_audio.py
```

Danach liegen die PDFs unter `outputs/` und die Audio-Dateien unter `audio/generated/`. Für die App werden die erzeugten Audios nach `app/Kraehenfels/Resources/Audio/` kopiert. Das Projekt wird auf macOS mit XcodeGen erzeugt:

```bash
brew install xcodegen
cd app
xcodegen generate
xcodebuild -project Kraehenfels.xcodeproj -scheme Kraehenfels \
  -destination 'generic/platform=iOS Simulator' test
```

Ein Tag wie `v1.0.0` oder der Button **Run workflow** mit einer Versionsnummer startet `.github/workflows/release.yml`. Der Workflow erzeugt eine unsignierte `Kraehenfels.ipa` und zusätzlich einen ausgefüllten `altstore/source.generated.json` als Release-Asset. Für eine dauerhafte Feed-URL kannst du diese erzeugte JSON-Datei in dein Repository oder GitHub Pages übernehmen.

## Druckpaket

- `00_Spielstart.pdf`: kurze Vorbereitung für die erste Spielleitung
- `01_Karte_Spieler.pdf`: spoilerfreie Tischkarte
- `01_Karte_SL.pdf`: geheime Karte mit Flutstollen, Kammer und Wahrheit
- `01_Grubenplan_H08.pdf` und `01_Grubenplan_SL.pdf`: unvollständiger Plan mit optionalem SL-Overlay
- `02_Handouts.pdf`: Kutschschein, Zeitung, Kirchenbuch, Liedblatt, Brief und weitere Spuren
- `03_Figurenbau.pdf`: drei Begabungen, 400 Punkte und HTBAH-Schnellregeln
- `10_SL_Abenteuer.pdf`: vorlesbare Szenen, NPCs und Enden
- `11_SL_Schnellreferenz.pdf`: Wahrheit, Pflichtspuren und Improvisationshilfe
- `14_Soundboard-Cues.pdf`: konkrete Cue-Momente mit Papier-Fallbacks

Für die direkte Weitergabe liegen zusätzlich `outputs/Kraehenfels-Druckpaket.zip` und `outputs/Kraehenfels-Audio.zip` bereit.

## Lizenzhinweise

Die Abenteuertexte und Medien dieses Projekts sind eigenständig erstellt. How to be a Hero ist ein separates Regelwerk. Die Kurzregeln im Spielpaket fassen nur die am Tisch benötigten Mechaniken zusammen und verweisen auf das offizielle Regelwerk.
