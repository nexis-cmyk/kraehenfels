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

## Simulator-Vorschau am Windows-PC

Der iOS-Workflow erzeugt bei jedem Push nach `main` zusätzlich das Artefakt
`kraehenfels-ios-simulator-app`. Es enthält `Kraehenfels-simulator.zip` mit der
echten iOS-Simulator-App (`.app`) und ist direkt für Appetize geeignet.

1. In GitHub zu **Actions → iOS build → letzter erfolgreicher Lauf** gehen.
2. Unter **Artifacts** `kraehenfels-ios-simulator-app` herunterladen und entpacken.
3. [Appetize Upload](https://appetize.io/upload) öffnen, die enthaltene
   `Kraehenfels-simulator.zip` hochladen und anschließend ein iPhone-Modell wählen.

Die Vorschau ist die native SwiftUI-App – nicht die separate Browser-Vorschau.
