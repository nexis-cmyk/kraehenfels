# Projektdokumentation

## Ziel

Das Projekt liefert ein vollständiges Spielpaket für `Die Weiße Frau schweigt`. Alle Spielerunterlagen sind deutsch, druckbar und spoilerfrei getrennt. Die iOS-App dient ausschließlich der Spielleitung.

## Verbindliche Entscheidungen

- System: How to be a Hero, 400 Fähigkeitspunkte, W100 und W10
- Gruppe: drei frei erstellte Figuren mit lockeren Rollenimpulsen
- Ton: klassischer Horror ab etwa 16 Jahren mit trockenem Humor
- Schauplatz: Krähenfels im Schwarzwald, November 1890
- Kernmotiv: eine seit Jahrzehnten stumme Glocke und ein Wesen, das Stimmen kopiert
- Weiße Frau: Elisabeth Abele, verkannte Retterin und stumme Wächterin
- Zeitdruck: Der neue Pfarrer will die Glocke um Mitternacht weihen
- App: SwiftUI, iPhone, Hochformat, iOS 17 oder neuer, offline
- Verteilung: unsigned IPA über GitHub Releases, zusätzlicher AltStore-Classic-Feed

## Architektur

`content/manifest.json` ist die maschinenlesbare Quelle für Szenen, Handouts, Cues und Verknüpfungen. Lange Spieltexte liegen daneben in klar getrennten Inhaltsdateien. Der PDF-Generator und die SwiftUI-App prüfen dieselben IDs gegen das Manifest.

Die Audioerzeugung ist deterministisch. Python und NumPy erzeugen die Rohsignale, FFmpeg normalisiert und exportiert die Dateien. Es werden keine fremden Samples eingebunden.

Die Druckunterlagen entstehen mit ReportLab. `print/assets/` enthält eigens erzeugte Rasterbilder: das Titelmotiv, eine beschriftete Luftansicht des Dorfes, Elisabeth Abeles Kabinettfoto, eine Glockenradierung, einen Holzstich für das Wochenblatt, eine technische Stellmacher-Zeichnung und einen gefalteten Vermessungsplan der Grube. Der Generator bettet sie gezielt in Titel, Karte und Handouts ein. Die PDFs werden mit `pypdf` und per Poppler-Render geprüft.

## Gelieferte Artefakte

- `outputs/01_Karte_Spieler.pdf` und `outputs/01_Karte_SL.pdf`
- `outputs/01_Grubenplan_H08.pdf` und `outputs/01_Grubenplan_SL.pdf`
- `outputs/02_Handouts.pdf`, `outputs/03_Figurenbau.pdf`, `outputs/10_SL_Abenteuer.pdf`, `outputs/11_SL_Schnellreferenz.pdf`
- `outputs/14_Soundboard-Cues.pdf`
- sieben Druckgrafiken in `print/assets/`
- 35 originale Audios in `audio/generated/` und im iOS-Bundle
- SwiftUI-App mit Offline-Content, Cue-Steuerung, Regeln, Settings und GitHub-Release-Workflow

## Qualitätsregeln

- Kein Pflichtfortschritt hängt von einem gelungenen Würfelwurf ab.
- Jede Kernschlussfolgerung hat mindestens drei Hinweise.
- Jeder Audiohinweis besitzt eine gedruckte Entsprechung.
- Spielerdateien enthalten keine Spoiler in Inhalt, Dateinamen, Metadaten oder Lesezeichen.
- Code, Buildskripte und Daten bleiben modular und erhalten automatisierte Prüfungen.
- Jede finale PDF-Seite wird vor der Weitergabe als Raster gerendert und visuell auf Textüberlauf, leere Seiten und Lesbarkeit geprüft.
- Handouts erscheinen als eigenständige Requisiten und verwenden keine wiederholte Karten-Schablone.
