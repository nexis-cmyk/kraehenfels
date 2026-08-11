# Handoff 12: AltStore-Version korrigiert

## Ursache

Der Release-Workflow hat zuvor keine `MARKETING_VERSION` an `xcodebuild` übergeben. Dadurch enthielt die IPA intern `1.0`, während der AltStore-Feed `2.0.2` ankündigte. AltStore verweigert solche Pakete korrekt.

## Korrektur

- `app/project.yml` enthält eine Standardversion und Buildnummer.
- `.github/workflows/release.yml` extrahiert die Versionsnummer aus dem Tag und übergibt sie als `MARKETING_VERSION` an den iOS-Build.
- `v2.0.3` wurde heruntergeladen und geprüft: `CFBundleShortVersionString=2.0.3`, `CFBundleVersion=1`, Bundle-ID `de.kraehenfels.spielleitung`.
- `altstore/source.json` verweist auf dieselbe Version, Größe und SHA-256.

## Nutzerhinweis

In AltStore die Krähenfels-Quelle aktualisieren. Falls noch `2.0.2` angezeigt wird, die Quelle einmal entfernen und dieselbe Feed-URL erneut hinzufügen. Danach `Krähenfels 2.0.3` installieren.
