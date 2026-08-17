# Handoff 32 – Google-Login IPA Release

## Ergebnis

- Die Google-Login-Sperre ist im aktuellen iOS-Code enthalten (`AuthGateView`, `SupabaseManager` und `SupabaseConfig`).
- Der Versionsfehler im XcodeGen-Projekt wurde behoben: `CFBundleShortVersionString` und `CFBundleVersion` verwenden jetzt die Build-Einstellungen `MARKETING_VERSION` und `CURRENT_PROJECT_VERSION`.
- Commit: `6d2743f` (`fix ipa release version metadata`), auf `master` gepusht.
- GitHub Actions Release-Lauf `32035274601` ist erfolgreich durchgelaufen.
- Release: `v3.3.1`.
- Assets: `Kraehenfels.ipa` und `source.generated.json`.

## Übergabe

- IPA-Download: `https://github.com/nexis-cmyk/kraehenfels/releases/download/v3.3.1/Kraehenfels.ipa`
- AltStore-Feed als Release-Asset: `https://github.com/nexis-cmyk/kraehenfels/releases/download/v3.3.1/source.generated.json`
- Der Feed-Schritt validiert die IPA-Bundle-Version vor dem Veröffentlichen; der Build ist dadurch gegen den zuvor aufgetretenen `IPA version 1.0`-Fehler abgesichert.

## Nächster Test

1. In AltStore die vorhandene Quelle aktualisieren oder `source.generated.json` als Quelle hinzufügen.
2. `Krähenfels` aus dem Release `v3.3.1` installieren/aktualisieren.
3. Beim Start den Google-Login testen und anschließend im Audio-Check eine Bewertung speichern.
