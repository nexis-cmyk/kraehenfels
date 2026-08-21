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
                volumeSlider(title: "Atmosphäre", icon: "wind", value: $audio.ambientVolume)
                volumeSlider(title: "Musik", icon: "music.note", value: $audio.musicVolume)
                volumeSlider(title: "Effekte", icon: "sparkles", value: $audio.effectsVolume)
                Toggle("Sicherheitslautstärke", isOn: $audio.safetyMode)
                Text("Reduziert alle Sounds und ist für empfindliche Ohren gedacht.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Section("Session") {
                NavigationLink {
                    AudioCheckView()
                } label: {
                    Label("Alle 20 Cues prüfen", systemImage: "checklist.checked")
                }
                Button {
                    audio.runSelfTest()
                } label: {
                    Label("Audio-Selbsttest starten", systemImage: "waveform.and.mic")
                }
                Text(audio.sessionStatus)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                if let error = audio.lastError {
                    Label(error, systemImage: "exclamationmark.triangle.fill")
                        .font(.caption)
                        .foregroundStyle(FrostTheme.warning)
                        .fixedSize(horizontal: false, vertical: true)
                } else if let event = audio.lastEvent {
                    Label(event, systemImage: "checkmark.circle")
                        .font(.caption)
                        .foregroundStyle(FrostTheme.cobalt)
                }
                Button("Alle Sounds stoppen") { audio.stopAll() }
                    .foregroundStyle(FrostTheme.warning)
                Text(audio.activeLayerSummary)
                    .font(.caption)
                    .foregroundStyle(FrostTheme.cobalt)
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

    private func volumeSlider(title: String, icon: String, value: Binding<Double>) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Label(title, systemImage: icon)
                Spacer()
                Text("\(Int(value.wrappedValue * 100)) %")
                    .foregroundStyle(.secondary)
            }
            Slider(value: value, in: 0...1)
                .accessibilityLabel("\(title) Lautstärke")
        }
    }
}
