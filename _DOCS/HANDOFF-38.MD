# Handoff 38

## Folgeänderung: eigene Figuren und Kutschenfunde

Stand dieses Entwicklungszweigs: `v4.2.0`, Build `9`.

Die frühere Annahme von drei festen Schnellstartfiguren ist entfernt. Vor dem Start trägt die Spielleitung drei eigene Figurennamen ein; Werte, Rollen und persönliche Hintergründe bleiben auf den mitgebrachten Bögen. In der Kutschenszene werden die sechs gemeinsamen Gegenstände an drei sichtbaren Fundorten ohne Würfelprobe aufgedeckt und anschließend so verteilt, dass jede Figur mindestens einen erhält. Besitzwechsel bleibt während der Runde möglich.

Die Gegenstände haben nur konkrete, storygerechte Anwendungen: Vor einer passenden Probe können sie einen situativen Bonus geben, nach einem Fehlschlag können passende Folgen geschützt werden. Einsätze werden erst bei der bestätigten Übernahme des Ergebnisses verbraucht. Abbrechen, neu auswerten, zurückgehen und Pfadwechsel lassen unbestätigte Einsätze unangetastet; gespeicherte Nutzungen werden mit Szene und Schritt zurückgesetzt.

Das gemeinsame Manifest enthält nun 43 Guided-Schritte, drei Fundorte und sechs Gegenstände. Native App, Web-Vorschau und `04_Gegenstandskarten.pdf` werden aus denselben Quellen gebaut.

Datum: 2026-08-28
Release: `v4.2.0`, Build `9`
Release-Commit auf `main`: `5c01cb5`
Feed-Commit auf `main`: `8a84170`

## Erledigt

- `adventure/guide.json` kennt für alle sieben Würfelproben eindeutige `failureConsequences` mit kurzer deutscher Spielleiteranweisung, optionaler Endzuordnung sowie den erlaubten Effekten `threatDelta` und `minimumThreat`.
- Ein Erfolg wird direkt übernommen. Ein Fehlschlag bleibt offen, bis eine Folge gewählt und bewusst bestätigt wurde. Eine feste kanonische Folge zeigt nur eine Option, benötigt aber ebenfalls die Bestätigung.
- Kritische Misserfolge zeigen zusätzlich die kritische Komplikation und verwenden denselben Auswahl- und Bestätigungsweg. Pflicht-Hinweise bleiben unabhängig vom Wurf erhalten.
- Auswirkungen werden erst beim Bestätigen angewandt. Schließen, Korrigieren und erneutes Auswerten verändern keinen Spielstand.
- Native Sitzungen speichern strukturierte Würfelergebnisse mit gewählter Folge und Gegenstandseinsätzen. Alte V5-Snapshots ohne die neuen Felder bleiben lesbar. Zurücksetzen, Pfadwechsel und ein Wechsel des Finale-Endes entfernen abhängige Würfe.
- Das Finale verlangt zwei Erfolge vor zwei Fehlschlägen. Ein kritischer Misserfolg zählt doppelt und beendet die Gefahrenszene mit zwei Fehlschlägen.
- Web-Vorschau und SwiftUI-App verwenden denselben Storyablauf. Die Würfelsession zeigt das letzte Ergebnis und die gewählte Folge.
- Touch-Flächen im relevanten Ablauf sind mindestens 44 Pixel beziehungsweise 44 Punkte hoch. Der Web-Inhalt lässt sich bis zum unteren Ende scrollen und berücksichtigt den unteren Abstand.
- Die drei Inhaltsmanifeste wurden aus der gemeinsamen Storyquelle neu gebaut.

## Prüfung

- `python tools/build_content_v5.py`: PASS.
- `python tools/validate_guided_flow.py`: PASS, 43 Schritte, 8 Szenen, 7 Ziele.
- `node --check web/js/app.js` und `node --check web/js/guided-flow.js`: PASS.
- Python-Syntaxprüfung für Content-Build, Print-Pack, Archive, Web-Build und Validatoren: PASS.
- Die drei Manifeste sind bytegleich.
- Live-Webprüfung auf localhost: eigene Figuren, alle sechs Kutschenfunde, Verteilung, Besitzwechsel, Gegenstandsverbrauch, S01- und S02-Fehlschlag mit Auswahl und Effekt, S07-Finale, Pfadwechsel, Reload, Scroll- und Touch-Maße sowie der komplette Weg bis zum Epilog geprüft.
- `python tools/validate_project.py`: PASS. 13 PDFs, Druck- und Audioarchiv, Manifeste, Audio- und Bildressourcen sind geprüft.
- GitHub Actions iOS-Run `33162003168`: SUCCESS. XcodeGen, Simulator-Build, Appetize-Paket und Swift-Tests liefen erfolgreich.
- GitHub Actions Release-Run `33162304071`: SUCCESS. IPA und generierter AltStore-Feed wurden veröffentlicht.
- GitHub Actions Pages-Run `33162527079`: SUCCESS. Die Web-Testversion ist live.

## AltStore

Direkter, unveränderlicher Release-Feed:

`https://github.com/nexis-cmyk/kraehenfels/releases/download/v4.2.0/source.generated.json`

IPA:

`https://github.com/nexis-cmyk/kraehenfels/releases/download/v4.2.0/Kraehenfels.ipa`

Dauerhafter Feed im Repository:

`https://github.com/nexis-cmyk/kraehenfels/raw/refs/heads/main/altstore/source.json`

Der Feed enthält Version `4.2.0`, Build `9`, die IPA-Größe `82603188` Bytes und SHA-256 `a7a362adef74b6490eaf0ef01ff2e5c74789dfd2dd5edfef9630e783f9fb3bff`.

Die IPA ist unsigniert. AltStore signiert sie beim Installieren mit dem eigenen Apple-Account.

## Übergabe

In AltStore unter `Sources` den direkten Release-Feed hinzufügen. Falls noch der alte Feed mit `v4.1.2` eingetragen ist, diesen entfernen oder aktualisieren und anschließend `v4.2.0` installieren.
