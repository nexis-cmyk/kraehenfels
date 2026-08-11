# Handoff 13: AltStore-Feed mit Buildnummer

## Ursache und Korrektur

AltStore prüft bei einer Quelle sowohl `CFBundleShortVersionString` als auch `CFBundleVersion`. Der Feed enthielt zuvor keine explizite `buildVersion`. `tools/update_altstore_feed.py` liest ab jetzt beide Werte direkt aus der gebauten IPA, setzt sie im Feed und bricht ab, wenn die sichtbare IPA-Version nicht zum Release-Tag passt.

## Geprüftes Release

`v2.0.4` wurde vor Veröffentlichung heruntergeladen und verifiziert:

- Kurzversion: `2.0.4`
- Buildnummer: `1`
- Bundle-ID: `de.kraehenfels.spielleitung`
- SHA-256: `bc2e81aacac9824df800c0fc00ffe7218826fd274dc2f17b4a194026a47d94ae`

Der Feed unter `altstore/source.json` verwendet dieselben Werte. Bei AltStore muss der Nutzer die vorhandene Quelle entfernen und erneut mit der bekannten Feed-URL hinzufügen, damit der Cache sicher verworfen wird.
