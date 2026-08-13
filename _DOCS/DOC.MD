# Projektdokumentation

## Ziel

`Krähenfels: Die letzte Kutsche` ist ein vollständiges, offlinefähiges Spielpaket für drei Spieler und eine Spielleitung. Das Abenteuer nutzt How to be a Hero mit W100 und W10 und ist auf einen ersten Leitungsabend von etwa vier bis fünf Stunden ausgelegt. Die Geschichte ersetzt die frühere Glocken-, Gruben- und Weiße-Frau-Fassung vollständig.

## Kanonische Quelle

Die verbindliche Quelle liegt in [`adventure/canon.json`](../adventure/canon.json). Sie enthält Phasen, Figuren-Verbindungen (technisch weiterhin `travelHooks`), Eskalation, Fakten, drei Enden, Orte, Szenen, NPCs, Hinweise, Handouts und Audio-Cues. `python tools/build_content_v5.py` schreibt den Kanon in `content/` und in das native App-Bundle. `web/data/manifest.json` bleibt für den eingefrorenen Web-Teststand 3.1.0 unverändert. Ortsakten, Beweismatrix und Run-Sheet liegen in `adventure/locations/`, `adventure/evidence/`, `adventure/indexes/` und `adventure/session/`.

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

Die App bleibt frei navigierbar. Der Einstieg über `GMStartView` führt zuerst durch Vorbereitung, Materialtrennung, Sicherheitscheck und die drei Schnellstartfiguren. `GuidedGMView` zeigt danach pro Szene klar getrennte Karten für Vorlesen, SL-Information, Spieleraktion, Auslöser, Hinweis, Würfelprobe und nächsten Schritt. Materialien, Karten, NPC-Dossiers, Fakten und Regeln bleiben direkt aus dem aktuellen Schritt erreichbar. Der Ablauf entscheidet keine Handlung automatisch. Hinweise werden nie durch einen einzelnen misslungenen Wurf blockiert.

Der Leitstand führt die kanonischen Wege aus dem Gasthaus getrennt: Kirche, Schmiede und Waldspur sind in beliebiger Reihenfolge möglich. Das Archiv wird erst nach zwei besuchten Ermittlungsorten angeboten. Im Finale kann die Spielleitung zwischen der geführten Gefahrenszene und einem vollständigen HTBAH-Kampf umschalten. Der Türzustand des Gästezimmers und die Würfelhistorie werden im Sitzungsjournal gespeichert.

## Audio

Der native Satz besteht aus 20 unterscheidbaren Dateien: acht Atmosphären, einem dauerhaften Musikbett, einem Prozessions-Layer und zehn One-Shots. `tools/process_audio_v5.py` baut die acht abgenommenen V5-Dateien. `tools/generate_audio_v6.py` ersetzt die zwölf markierten Problem-Cues mit reproduzierbaren lokalen Assemblies und schreibt die V6-Metadaten. `tools/validate_audio_v6.py` prüft Dauer, 48-kHz-Stereoformat, Lautheit, True Peak, Loop-Naht, Dateihashes und akustische Fingerprints. Der aktuelle Lauf meldet 20 gültige Dateien und keine Dublette. Ein separater Hörtest in der App bleibt vor dem finalen Release Pflicht.

Der Player hält vier Ebenen getrennt. Ein Szenen-Preset wechselt nur die Ortsatmosphäre. M01 bleibt über Szenenwechsel hinweg aktiv, M02 kann im letzten Drittel daruntergelegt werden, und One-Shots überlappen die laufenden Flächen. Beim Vorlesen öffnet sich zuerst ein bestätigter Moment: Der Cue startet, die Musik wird abgesenkt, der Text bleibt sichtbar und erst nach "Vorgelesen, weiter" geht der Leitstand zum nächsten Schritt. STOP beendet alles. Die genaue Fassung steht in [`AUDIO-V5-PLAN.md`](AUDIO-V5-PLAN.md), die V6-Zuordnung in [`AUDIO-SOURCES-V6.md`](AUDIO-SOURCES-V6.md) und der Prüfbericht in [`AUDIO-V6-QA.md`](AUDIO-V6-QA.md).

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
python tools/build_content_v5.py
python tools/process_audio_v5.py
python tools/generate_audio_v6.py
python tools/validate_audio_v6.py
python tools/build_print_pack_v3.py
python tools/validate_project.py
python tools/validate_guided_flow.py
```

`tools/validate_project.py` prüft IDs und Querverweise, die native Manifest-Synchronität, den eingefrorenen Web-Stand, Szene- und Kartenbilder, exakt die 21 erwarteten nativen Audio-Dateien (20 Cues plus Selbsttest), unreferenzierte Audio-/Art-Dateien, Dubletten im gesamten nativen Paket, Cue-Zeitpunkte, kritische Szenenzuordnungen, PDF-Lesbarkeit und die Spoilertrennung der Spielerunterlagen. Der Kartensatz umfasst MAP01 bis MAP06.

## Qualitätsregeln

- Pflichtspuren besitzen einen gedruckten oder beschreibbaren Fallback.
- Kein Kernfakt hängt an einem gelungenen Würfelwurf.
- Spielerunterlagen enthalten keine Ritualspoiler.
- App, Web-Version und Druckpaket verwenden dieselben IDs.
- Audio-Presets, Einzel-Cues und Stop-All bleiben getrennt bedienbar.
- Jeder geführte Schritt zeigt ausdrücklich, ob eine Probe vorgesehen ist, und ein kritischer Misserfolg hat eine sichtbare Folge.
- Jede finale PDF wird gerendert und auf Lesbarkeit sowie Textüberlauf geprüft.
- Der Vorlese-Dialog hat eine explizite Bestätigung; STOP und interaktives Schließen lösen die Musik-Absenkung zuverlässig auf.
