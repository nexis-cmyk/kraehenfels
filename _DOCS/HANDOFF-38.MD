# Handoff 38

Datum: 2026-08-26  
Release: `v4.1.2`, Build `8`  
Release-Commit auf `main`: `78b51f7`

## Erledigt

- `adventure/guide.json` kennt für alle sieben Würfelproben eindeutige `failureConsequences` mit kurzer deutscher Spielleiteranweisung, optionaler Endzuordnung sowie den erlaubten Effekten `threatDelta` und `minimumThreat`.
- Ein Erfolg wird direkt übernommen. Ein Fehlschlag bleibt offen, bis eine Folge gewählt und bewusst bestätigt wurde. Eine feste kanonische Folge zeigt nur eine Option, benötigt aber ebenfalls die Bestätigung.
- Kritische Misserfolge zeigen zusätzlich die kritische Komplikation und verwenden denselben Auswahl- und Bestätigungsweg. Pflicht-Hinweise bleiben unabhängig vom Wurf erhalten.
- Auswirkungen werden erst beim Bestätigen angewandt. Schließen, Korrigieren und erneutes Auswerten verändern keinen Spielstand.
- Native V5-Sitzungen speichern strukturierte Würfelergebnisse mit gewählter Folge. Alte V5-Snapshots ohne das neue Feld bleiben lesbar. Zurücksetzen, Pfadwechsel und ein Wechsel des Finale-Endes entfernen abhängige Würfe.
- Das Finale verlangt zwei Erfolge vor zwei Fehlschlägen. Ein kritischer Misserfolg zählt doppelt und beendet die Gefahrenszene mit zwei Fehlschlägen.
- Web-Vorschau und SwiftUI-App verwenden denselben Storyablauf. Die Würfelsession zeigt das letzte Ergebnis und die gewählte Folge.
- Touch-Flächen im relevanten Ablauf sind mindestens 44 Pixel beziehungsweise 44 Punkte hoch. Der Web-Inhalt lässt sich bis zum unteren Ende scrollen und berücksichtigt den unteren Abstand.
- Die drei Inhaltsmanifeste wurden aus der gemeinsamen Storyquelle neu gebaut.

## Prüfung

- `python tools/build_content_v5.py`: PASS.
- `python tools/validate_guided_flow.py`: PASS, 41 Schritte, 8 Szenen, 7 Ziele.
- `node --check web/js/app.js` und `node --check web/js/guided-flow.js`: PASS.
- Python-Syntaxprüfung für Content-Build und Guided-Flow-Validator: PASS.
- Die drei Manifeste sind bytegleich.
- Live-Webprüfung auf localhost: S01- und S02-Fehlschlag mit Auswahl und Effekt, S07-kritischer Fehlschlag, Auswahl für alle drei Enden, Finale-Fortschritt, Pfadwechsel mit Löschung abhängiger Würfe sowie Scroll- und Touch-Maße geprüft.
- GitHub Actions iOS-Run `32966458958`: SUCCESS. XcodeGen, Simulator-Build, Appetize-Paket und Swift-Tests liefen erfolgreich.
- GitHub Actions Release-Run `32966881331`: SUCCESS. IPA und generierter AltStore-Feed wurden veröffentlicht.
- Der vollständige lokale Projektvalidator stoppt auf Windows an einem vorhandenen ignorierten Build-Artefakt: `audio/generated/V6_A01_Kutschenstrasse.m4a` fehlt. Die gebündelte App-Ressource ist vorhanden; der macOS-Release-Workflow war trotzdem erfolgreich.

## AltStore

Direkter, unveränderlicher Release-Feed:

`https://github.com/nexis-cmyk/kraehenfels/releases/download/v4.1.2/source.generated.json`

IPA:

`https://github.com/nexis-cmyk/kraehenfels/releases/download/v4.1.2/Kraehenfels.ipa`

Dauerhafter Feed im Repository:

`https://github.com/nexis-cmyk/kraehenfels/raw/refs/heads/main/altstore/source.json`

Der Feed enthält Version `4.1.2`, Build `8`, die IPA-Größe `82487980` Bytes und SHA-256 `e9da919ecd0d12be18ebfd411fcba9984c9ac870fb5f3e25883af4aa16ed463c`.

Die IPA ist unsigniert. AltStore signiert sie beim Installieren mit dem eigenen Apple-Account.

## Übergabe

In AltStore unter `Sources` den direkten Release-Feed hinzufügen. Falls noch der alte Feed mit `v4.1.1` eingetragen ist, diesen entfernen oder aktualisieren und anschließend `v4.1.2` installieren.
