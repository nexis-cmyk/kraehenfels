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

`content/manifest.json` ist die maschinenlesbare Quelle für Szenen, Handouts, Cues, NPCs, Pflichtspuren und Verknüpfungen. Lange Spieltexte liegen daneben in klar getrennten Inhaltsdateien. Der PDF-Generator, die SwiftUI-App und die Web-Testversion prüfen dieselben IDs gegen das Manifest.

Die Audioerzeugung ist deterministisch. Python und NumPy erzeugen die Rohsignale, FFmpeg normalisiert und exportiert die Dateien. Es werden keine fremden Samples eingebunden.

Die aktuellen Audios sind damit als technische Platzhalter zu behandeln. Fuer den finalen Spieltisch brauchen Ambiences, Musik und wichtige Effekte echte Foley- oder AI-generierte Quellen. Der komplette Ersatzkatalog steht in `_DOCS/SOUND-PROMPTS.md` und listet alle 46 Soundboard-Dateien mit Zielklang und Prompt. `_DOCS/AUDIO-REBUILD-MASTER-PROMPT.md` ist der kopierbare Gesamtprompt fuer eine externe Audio-KI oder Soundproduktion. `_DOCS/AUDIO-SIMPLE-PACK.md` ist die reduzierte Spielabend-Variante mit 5 Loops, 1 Hintergrundthema und 12 Effektknoepfen. Die Dateinamen sollen beim Austausch gleich bleiben, damit Manifest, App und Web-Testversion unveraendert weiter funktionieren. `tools/import_audio_replacements.py` importiert neu erzeugte Dateien, wandelt sie bei Bedarf mit FFmpeg in die erwarteten Formate und kopiert sie in App- und Web-Zielordner. Mit `--simple-pack` verteilt es das reduzierte Set auf alle 46 technischen App-Dateien und legt unnoetige Cues still.

Die Druckunterlagen entstehen mit ReportLab. `print/assets/` enthält eigens erzeugte Rasterbilder: das Titelmotiv, eine beschriftete Luftansicht des Dorfes, Elisabeth Abeles Kabinettfoto, eine Glockenradierung, einen Holzstich für das Wochenblatt, eine technische Stellmacher-Zeichnung, einen gefalteten Vermessungsplan der Grube und sieben Graphic-Novel-Szenenbilder. Die Handouts haben voneinander abweichende Requisitenformen: Ticket, Zeitung, Kirchenregister, Foto, Liedblatt, Werkbuch, Feldnotiz, handschriftliche Aussage, Brief und Ritualkarte. Der Generator bettet sie gezielt in Titel, Karte, Handouts und die SL-Bildstrecke ein. Spielerhinweise und H10/H11 sind nun in getrennten PDFs, damit das Spielpaket keine Spoiler mitliefert. Jede Druckseite führt Handout-ID, Ausgabehinweis, Schnittmarken und eine Scherenlinie. Die PDFs werden mit `pypdf` und per Poppler-Render geprüft.

`web/` ist eine statische, lokal gestartete PWA für den Test vor dem Sideload. `tools/build_web_preview.py` synchronisiert Manifest, sieben Szenenbilder, Icon und alle 46 Audio-Dateien aus den App-Ressourcen. Die Browser-Oberfläche speichert Fortschritt und Häkchen im lokalen Browser, hat einen Audio-Selbsttest, getrennte Lautstärken, Szenen-Presets, einzelne Effekte und einen globalen Stopp. Der Validator erzwingt, dass Manifest, Szenenbilder und Audiodateien in SwiftUI-App und Web-Testversion übereinstimmen.

## Gelieferte Artefakte

- `outputs/01_Karte_Spieler.pdf` und `outputs/01_Karte_SL.pdf`
- `outputs/01_Grubenplan_H08.pdf` und `outputs/01_Grubenplan_SL.pdf`
- `outputs/02_Handouts.pdf`, `outputs/03_Figurenbau.pdf`, `outputs/10_SL_Abenteuer.pdf`, `outputs/11_SL_Schnellreferenz.pdf`, `outputs/12_SL_Am_Tisch.pdf`, `outputs/13_SL_Spoiler-Handouts.pdf`
- `outputs/14_Soundboard-Cues.pdf`
- vierzehn Druckgrafiken in `print/assets/`
- 46 originale Audios in `audio/generated/` und im iOS-Bundle
- SwiftUI-Leitstand mit Offline-Content, Szenenbildern, Vorlesetext, NPCs, Pflichtspuren, Cue-Steuerung, Audio-Selbsttest, Regeln, Settings und GitHub-Release-Workflow

## Qualitätsregeln

- Kein Pflichtfortschritt hängt von einem gelungenen Würfelwurf ab.
- Jede Kernschlussfolgerung hat mindestens drei Hinweise.
- Jeder Audiohinweis besitzt eine gedruckte Entsprechung.
- Spielerdateien enthalten keine Spoiler in Inhalt, Dateinamen, Metadaten oder Lesezeichen.
- Code, Buildskripte und Daten bleiben modular und erhalten automatisierte Prüfungen.
- Jede finale PDF-Seite wird vor der Weitergabe als Raster gerendert und visuell auf Textüberlauf, leere Seiten und Lesbarkeit geprüft.
- Handouts erscheinen als eigenständige Requisiten und verwenden keine wiederholte Karten-Schablone.
