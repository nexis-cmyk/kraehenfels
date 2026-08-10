# iPhone-App

Die App ist ein offline-first SwiftUI-Begleiter für die Spielleitung. Szenen, Hinweise, Regeln und Audio-Cues liegen im Bundle. Es gibt keine Anmeldung und keine Netzwerkabhängigkeit während der Runde.

## Build auf macOS

```bash
brew install xcodegen
cd app
xcodegen generate
xcodebuild -project Kraehenfels.xcodeproj -scheme Kraehenfels \
  -destination 'generic/platform=iOS Simulator' test
```

Für ein eigenes Gerät in Xcode das Team im Target eintragen und den Bundle-Identifier bei Bedarf ändern. Für den GitHub-Release wird absichtlich eine unsignierte IPA gebaut. Diese muss vor der Installation mit AltStore, SideStore oder einem vergleichbaren Signierweg mit dem eigenen Apple-Account signiert werden.

## Audio

Atmosphäre und Musik laufen als Schleife. Effekte sind One-Shots. Die Lautstärke bleibt in der App getrennt regelbar über Master und Sicherheitsmodus. Alle Hinweis-Cues besitzen ein gedrucktes Fallback im Spielpaket.
