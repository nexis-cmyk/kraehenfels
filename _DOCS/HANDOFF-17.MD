# Handoff 17 – Nachtstand 2.0.7

## Änderung

Der Leitstand besitzt jetzt einen manuell steuerbaren Nachtstand. Er führt fünf dramaturgische Momente:

1. Ankunft
2. Dunkelheit
3. Warnung
4. Mitternacht
5. Tauwetter

Die Spielleitung setzt ihn bewusst selbst. Der Stand startet keine Szenen, verändert keine Hinweise und ersetzt keinen Countdown. Er schafft lediglich Tempo- und Situationsüberblick.

## Umsetzung

- `SessionStore` speichert den Nachtstand zusammen mit Namen und Tischnotizen lokal in `UserDefaults`; vorhandene ältere Snapshots bleiben lesbar.
- `SessionView` bietet einen nativen Picker mit kurzer Erklärung je Phase.
- Die iPhone-Startseite zeigt eine kompakte Karte mit dem aktuellen Nachtstand.
- Der Web-Leitstand speichert denselben Wert in `localStorage`, zeigt ihn in der Szenen-Kopfzeile und bietet Zurück-, Auswahl- und Weiter-Steuerung.
- `content/manifest.json` und die iOS-Kopie tragen Version `2.0.7`.

## Prüfung und Release

`python tools/build_web_preview.py`, `python tools/validate_project.py` und `node --check web/js/app.js` sind erfolgreich. Vor dem Tag `v2.0.7` muss der iOS-Compile-Check auf GitHub erfolgreich sein; danach die erzeugte IPA herunterladen und `altstore/source.json` mit realer Größe und SHA-256 aktualisieren.
