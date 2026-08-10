import SwiftUI

struct SettingsView: View {
    @EnvironmentObject private var audio: AudioEngine

    var body: some View {
        Form {
            Section("Audio") {
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Label("Master", systemImage: "speaker.wave.2")
                        Spacer()
                        Text("\(Int(audio.masterVolume * 100)) %")
                            .foregroundStyle(.secondary)
                    }
                    Slider(value: $audio.masterVolume, in: 0...1)
                        .accessibilityLabel("Masterlautstärke")
                }
                Toggle("Sicherheitslautstärke", isOn: $audio.safetyMode)
                Text("Reduziert alle Sounds und ist für empfindliche Ohren gedacht.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Section("Session") {
                Button("Alle Sounds stoppen") { audio.stopAll() }
                    .foregroundStyle(FrostTheme.warning)
                Text("Die App spielt keine Sprache ab. Alle Hinweise bleiben zusätzlich auf Papier vorhanden.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .scrollContentBackground(.hidden)
        .background(FrostTheme.ink.ignoresSafeArea())
        .navigationTitle("Einstellungen")
        .navigationBarTitleDisplayMode(.inline)
    }
}
