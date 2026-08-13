# Krähenfels

`Krähenfels: Die letzte Kutsche` ist ein deutschsprachiges Folk-Horror-Abenteuer für drei Spieler und eine erstmalige Spielleitung. Es verwendet das Regelwerk How to be a Hero und spielt im Schwarzwald des Jahres 1890. Die Geschichte dreht sich um eine manipulierte Kutschfahrt, ein verdrehtes Gastrecht und einen Waldpakt an der Alten Eiche.

Das Repository enthält:

- das vollständige Abenteuer mit SL-Schnellreferenz
- eine spoilerfreie Dorfkarte, eine markierte SL-Karte und drei Detailkarten
- Handouts, drei sofort spielbare Schnellstartfiguren und optionale Bögen für eigene Figuren
- 20 technisch geprüfte Atmosphären, Musik-Layer und Soundeffekte. Zwölf problematische Cues liegen als V6-Ersatzfassungen vor
- eine native iOS-Begleitapp ab iOS 17 mit geführtem Spielleiter-Modus, Nachtstand, NPCs, Pflichtspuren, Vorlesetexten, Würfelhelfer, Tischnotizen und Audio-Selbsttest
- GitHub Actions für Tests, IPA-Build und AltStore-Feed
- eine offlinefähige Web-Testversion für Leitstand und Soundboard

## iPhone-Build und AltStore

Der aktuelle native Release-Kandidat ist `v3.3.0-rc3` (App-Version `3.3.0`, Build `4`). Den IPA-Build erzeugt macOS oder GitHub Actions; die IPA bleibt unsigniert und wird erst durch AltStore mit deinem Apple-Account signiert.

- [GitHub-Repository](https://github.com/nexis-cmyk/kraehenfels)
- [Release-Übersicht](https://github.com/nexis-cmyk/kraehenfels/releases)
- [AltStore-Feed für den letzten veröffentlichten Build](https://github.com/nexis-cmyk/kraehenfels/releases/latest)
- [Dauerhafter AltStore-Feed](https://github.com/nexis-cmyk/kraehenfels/raw/refs/heads/main/altstore/source.json)

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

Die native Fassung wird unter Windows so erzeugt:

```powershell
python tools/build_content_v5.py
python tools/process_audio_v5.py
python tools/generate_audio_v6.py
python tools/validate_audio_v6.py
python tools/build_print_pack_v3.py
python tools/build_archives_v3.py
python tools/validate_project.py
python tools/validate_guided_flow.py
```

`process_audio_v5.py` baut die acht bereits abgenommenen V5-Cues. `generate_audio_v6.py` ersetzt die zwölf markierten Problem-Cues reproduzierbar und kopiert sie in das native Bundle. Danach liegen PDFs unter `outputs/` und alle Audio-Dateien unter `audio/generated/`. Die Web-App bleibt absichtlich auf 3.1.0 und wird von diesen Befehlen nicht verändert. Das iOS-Projekt wird auf macOS mit XcodeGen erzeugt:

```bash
brew install xcodegen
cd app
xcodegen generate
xcodebuild -project Kraehenfels.xcodeproj -scheme Kraehenfels \
  -destination 'generic/platform=iOS Simulator' test
```

Ein Tag wie `v3.0.0` oder der Button **Run workflow** mit einer Versionsnummer startet `.github/workflows/release.yml`. Der Workflow erzeugt eine unsignierte `Kraehenfels.ipa` und zusätzlich einen ausgefüllten `altstore/source.generated.json` als Release-Asset. Für die aktuelle Installation ist der unveränderliche Release-Feed am zuverlässigsten; die dauerhaft gepflegte Feed-URL zeigt auf `https://github.com/nexis-cmyk/kraehenfels/raw/refs/heads/main/altstore/source.json`.

## Druckpaket

Die Unterlagen haben eine gemeinsame 1890er-Schwarzwald-Optik: kaltes Nachtblau, Rostrot, Schnee, Tannen und klare Beweisstück-Rahmen. Die Kartenplatten wurden mit GPT-Bildgenerierung als textfreie, realistische Top-down-Illustrationen angelegt. Die exakten Titel, Hinweis-IDs und SL-Markierungen liegen als sauber gesetzte Typografie darüber. Jede Spielerinformation ist als eigenes ausschneidbares Beweisstück gestaltet und trägt ihre Ausgabe-ID.

- `00_Spielstart.pdf`: kurze Vorbereitung für die erste Spielleitung
- `Einladung_Kraehenfels.pdf` und `Einladung_Kraehenfels.png`: druckbare Spieleinladung mit Abenteuerteaser und Charaktervorbereitung
- `01_Karte_Spieler.pdf`: spoilerfreie Tischkarte
- `01_Karte_SL.pdf`: geheime Karte mit Routen, Eichenplatz und Prozessionsspur
- `01_Karten_Detail.pdf`: Gasthaus, Kirche, Schmiede, Rathausarchiv und Alte Eiche als separate Tischkarten
- `02_Handouts.pdf`: nur spielersichere, ausschneidbare Hinweise mit Kennung, Schnittlinie und Ausgabezeitpunkt
- `03_Figurenbau.pdf`: optionale ausfüllbare Reiseakte für eigene Figuren; für den direkten Einstieg nutzt du Clara, Otto und Jakob aus dem Spielleiter-Modus
- `10_SL_Abenteuer.pdf`: vorlesbare Szenen, NPCs und Enden
- `11_SL_Schnellreferenz.pdf`: Wahrheit, Pflichtspuren und Improvisationshilfe
- `12_SL_Am_Tisch.pdf`: einseitiger Ablaufzettel mit Hinweisen, Sounds und Eskalation pro Szene
- `13_SL_Spoiler-Handouts.pdf`: H09, das Ritualfragment, getrennt für die Spielleitung
- `14_Soundboard-Cues.pdf`: konkrete Cue-Momente mit Papier-Fallbacks

Für die direkte Weitergabe liegen zusätzlich `outputs/Kraehenfels-Druckpaket.zip` und `outputs/Kraehenfels-Audio.zip` bereit.

## Web-Testversion

Die Browser-Version bleibt als eingefrorener Teststand 3.1.0 erhalten. Audio V5 und der neue vierkanalige Player erscheinen nur in der nativen iPhone-App. Die lokale Startanleitung steht in [`web/README.md`](web/README.md).

Nach einem Push auf `main` veröffentlicht GitHub Actions sie außerdem unter `https://nexis-cmyk.github.io/kraehenfels/`. Dafür muss Pages einmal im Repository freigeschaltet werden: **Settings → Pages → Build and deployment → Source: GitHub Actions → Save**. Danach kannst du sie unterwegs als Web-App ausprobieren.

## Audio

Audio V6 umfasst acht Ortsatmosphären, ein durchgehendes Krähenfels-Motiv, einen zusätzlichen Prozessions-Layer und zehn One-Shots. Die acht im Hörtest passenden V5-Dateien bleiben unverändert. Die zwölf Ersatzdateien werden lokal aus vorhandenen Quellen und Filtern zusammengesetzt, auf 48 kHz normalisiert und auf Dubletten geprüft. Der technische Bericht steht in [`_DOCS/AUDIO-V6-QA.md`](_DOCS/AUDIO-V6-QA.md), die Zuordnung und Prompttexte in [`_DOCS/AUDIO-SOURCES-V6.md`](_DOCS/AUDIO-SOURCES-V6.md).

Die App behandelt Grundmusik, Prozessionsmusik, Atmosphäre und Effekte unabhängig. Ein Szenen-Preset tauscht deshalb nur die Atmosphäre aus. M01 läuft auf Wunsch durch den ganzen Abend, die Vorlesen-Taste senkt Musik ab, und STOP beendet alle Ebenen sofort. Unter Einstellungen gibt es einen Hörtest, mit dem jeder Cue auf iPhone und Bluetooth-Box als passend oder falsch markiert werden kann.

```powershell
python tools/process_audio_v5.py
python tools/generate_audio_v6.py
python tools/validate_audio_v6.py
python tools/validate_project.py
```

## Lizenzhinweise

Die Abenteuertexte und Medien dieses Projekts sind eigenständig erstellt. How to be a Hero ist ein separates Regelwerk. Die Kurzregeln im Spielpaket fassen nur die am Tisch benötigten Mechaniken zusammen und verweisen auf das offizielle Regelwerk.
