# Handoff 34: iPad-V4-Redesign

## Umgesetzt

- Native App auf iPad-only (`TARGETED_DEVICE_FAMILY: 2`) mit Querformat als bevorzugter Arbeitsfläche. Hochformat und Split View bleiben möglich.
- `NavigationSplitView` mit Szenen-Navigation links, Leitstand in der Mitte und Schritt-Kontext rechts.
- Lokaler V4-Spielstand mit `hasStartedSession`; beim ersten V4-Start wird nicht der alte V3-Schlüssel übernommen.
- Audio-Regieleiste ist einklappbar und zeigt im geöffneten Zustand die vier Lautstärkeebenen. STOP bleibt jederzeit sichtbar.
- Google-Login, Supabase-SPM, Auth-Gate, Cloudkonto und Web-Live-Sync aus Krähenfels entfernt.
- Neue dunkelgrüne Waldpalette und neues Rabe-Waldweg-Icon in App, AltStore und Web-Vorschau.
- AltStore-Metadaten und CI auf V4.0.0 / Build 5 sowie iPad-Simulator aktualisiert.

## Verifikation

- `node --check web/js/app.js` bestanden.
- `python tools/validate_guided_flow.py` bestanden.
- `python tools/validate_project.py` bestanden, inklusive PDF-, Audio-, Map- und Manifest-Prüfung.
- Native Xcode-/Swift-Buildprüfung ist auf Windows nicht ausführbar; der aktualisierte GitHub-Workflow baut und testet auf macOS mit einem 11-Zoll-iPad-Simulator.

## Release abgeschlossen

- GitHub-Workflow `iPad release IPA` mit Tag `v4.0.0` erfolgreich.
- IPA: `https://github.com/nexis-cmyk/kraehenfels/releases/download/v4.0.0/Kraehenfels.ipa`
- Größe: `82,404,155` Bytes.
- SHA-256: `dd3a68985388ee311d22cffbdbc814c1dafb6cb2a2095cbda5b7fa855a85fe2b`.
- IPA geprüft: Version `4.0.0`, Build `5`, `UIDeviceFamily [2]`, Manifest vorhanden, 22 Audio-Dateien und 21 Art-Dateien.
- Dauerhafte AltStore-Quelle und Release-Feed enthalten nun dieselben Größe-/Hashwerte.
