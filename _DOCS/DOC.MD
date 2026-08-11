# Projektdokumentation

## Ziel

`Krähenfels: Die letzte Kutsche` ist ein vollständiges, offlinefähiges Spielpaket für drei Spieler und eine Spielleitung. Das Abenteuer nutzt How to be a Hero mit W100 und W10 und ist auf einen ersten Leitungsabend von etwa vier bis fünf Stunden ausgelegt. Die Geschichte ersetzt die frühere Glocken-, Gruben- und Weiße-Frau-Fassung vollständig.

## Kanonische Quelle

Die verbindliche Quelle liegt in [`adventure/canon.json`](../adventure/canon.json). Sie enthält Phasen, Figuren-Verbindungen (technisch weiterhin `travelHooks`), Eskalation, Fakten, drei Enden, Orte, Szenen, NPCs, Hinweise, Handouts und Audio-Cues. Die Dateien unter `content/`, in `app/.../Resources/` und unter `web/data/` werden mit `python tools/build_content_v3.py` daraus erzeugt. Ortsakten, Beweismatrix und Run-Sheet liegen in `adventure/locations/`, `adventure/evidence/`, `adventure/indexes/` und `adventure/session/`.

## Geschichte

Die drei Reisenden stranden nach einer manipulierten Kutschenpanne im Schwarzwald. Bürgermeister Konrad Gruber nimmt sie im Gasthaus Zum schwarzen Keiler auf und verdreht das alte Gastrecht: Schutz bis zum Morgen wird zu einer Opferung an der Alten Eiche. Gästebuch, Kirchenbuch, Winterbuchhaltung, Schmiedezeichnung und Kinderzeichnung ergeben gemeinsam die Wahrheit. Der gebundene Waldgeist erscheint als Knochenhirsch. Im Finale entscheidet die Gruppe zwischen öffentlichem Widerruf, erneuertem Gastrecht und Feuer.

## Architektur

- `adventure/`: autorenfreundliche V3-Quelle und Spielleiterstruktur
- `content/`: erzeugtes Manifest und längere Spieltexte
- `app/`: SwiftUI-Leitstand für iOS 17 oder neuer
- `web/`: offlinefähige PWA für den Test vor dem Sideload
- `print/`: Rastergrafiken und Druckvorlagen
- `audio/`: erzeugte V3-Audios und Quellenhinweise
- `tools/`: reproduzierbare Build- und Validierungsskripte
- `outputs/`: finale PDFs, ZIP-Archive und Einladung

Die App bleibt frei navigierbar. Sie zeigt Vorlesetext, SL-Notizen, NPC-Zustände, Pflichtspuren, Fakten, Figuren-Verbindungen, Karten, Sound-Presets und Stillstandshilfen. Sie entscheidet keine Handlung automatisch. Hinweise werden nie durch einen einzelnen misslungenen Wurf blockiert.

## Audio

Der aktive Satz besteht aus 18 unterscheidbaren Dateien: sechs Atmosphären, zwei Musikflächen und zehn One-Shots. Die aktuelle Produktionsfassung steht in [`SOUND-PROMPTS-V4.md`](SOUND-PROMPTS-V4.md). `tools/import_audio_replacements.py` schreibt die normalisierten Dateien synchron nach `audio/generated/`, in das iOS-Bundle und in die Web-App. Der Audio-Selbsttest bleibt in SwiftUI und Web-Leitstand sichtbar.

## Druckpaket

`tools/build_print_pack_v3.py` ruft den V3-Generator auf. Die Handouts tragen IDs, eigene Requisitenlayouts und eine gestrichelte Außenlinie mit Ausschneidehinweis. Das Spielerpaket enthält keine H09-Ritualspoiler. Die Kartensätze sind in Spieler- und SL-Ansicht getrennt. Die textfreien GPT-Bildplatten werden erst im Build mit Titeln, Hinweis-IDs und Spoilerrahmen versehen. Gasthaus, Kirche, Schmiede, Rathausarchiv und Alte Eiche liegen zusätzlich als Detailkarten bei.

Geliefert werden:

- `00_Spielstart.pdf`
- `Einladung_Kraehenfels.pdf` und `Einladung_Kraehenfels.png`
- `01_Karte_Spieler.pdf`, `01_Karte_SL.pdf`, `01_Karten_Detail.pdf`
- `02_Handouts.pdf`, `03_Figurenbau.pdf`
- `10_SL_Abenteuer.pdf`, `11_SL_Schnellreferenz.pdf`, `12_SL_Am_Tisch.pdf`
- `13_SL_Spoiler-Handouts.pdf`, `14_Soundboard-Cues.pdf`

## Reproduzierbarer Build

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

`tools/validate_project.py` prüft IDs und Querverweise, Manifest-Synchronität, Szene- und Kartenbilder, alle 18 Audio-Dateien, Duplikate innerhalb einer Szene, PDF-Lesbarkeit und die Spoilertrennung der Spielerunterlagen. Der Kartensatz umfasst MAP01 bis MAP06.

## Qualitätsregeln

- Pflichtspuren besitzen einen gedruckten oder beschreibbaren Fallback.
- Kein Kernfakt hängt an einem gelungenen Würfelwurf.
- Spielerunterlagen enthalten keine Ritualspoiler.
- App, Web-Version und Druckpaket verwenden dieselben IDs.
- Audio-Presets, Einzel-Cues und Stop-All bleiben getrennt bedienbar.
- Jede finale PDF wird gerendert und auf Lesbarkeit sowie Textüberlauf geprüft.
