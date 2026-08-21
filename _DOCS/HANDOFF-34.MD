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

## Offener Release-Schritt

Nach dem Push muss der Workflow mit Tag `v4.0.0` laufen. Erst danach werden die echte IPA, `source.generated.json`, Größe und SHA-256 in der dauerhaften AltStore-Quelle ersetzt. Die derzeitige `altstore/source.json` ist die V4-Metadatenvorlage und enthält noch keine Release-Prüfsumme.
