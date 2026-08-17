# Handoff 33 – Branch- und AltStore-Synchronisierung

## Ursache des alten Stands

Der iOS-Release wurde auf `master` gebaut, während GitHub/AltStore standardmäßig noch `main` auslieferten. Dadurch konnten Webansicht, dauerhafte Feed-URL und IPA auseinanderlaufen.

## Korrektur

- `master` wurde nach erfolgreicher Prüfung nach `main` synchronisiert (`3c2cd7d`).
- Die dauerhafte Feed-Datei enthält jetzt Version `3.3.1`, die geprüfte Größe und SHA-256-Prüfsumme.
- Der Feed zeigt direkt auf das GitHub-Release-Asset, statt auf einen verzögerten Pages-Mirror.
- Der Release-Workflow erzeugt künftige Feeds ebenfalls mit dem direkten GitHub-Release-Downloadziel.

## Verifizierte Links

- IPA: `https://github.com/nexis-cmyk/kraehenfels/releases/download/v3.3.1/Kraehenfels.ipa`
- Dauerhafte AltStore-Quelle: `https://github.com/nexis-cmyk/kraehenfels/raw/refs/heads/main/altstore/source.json`
