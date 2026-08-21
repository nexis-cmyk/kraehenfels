import SwiftUI

struct AudioTransportBar: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var audio: AudioEngine
    @State private var expanded = false

    var body: some View {
        VStack(spacing: 0) {
            if expanded {
                expandedControls
            }
            HStack(spacing: 8) {
                if let music = content.musicBed {
                    Button {
                        audio.toggle(music)
                    } label: {
                        transportItem(
                            title: audio.isPlaying(music) ? "Motiv läuft" : "Motiv",
                            icon: audio.isPlaying(music) ? "pause.fill" : "play.fill",
                            active: audio.isPlaying(music)
                        )
                    }
                    .accessibilityHint("Startet oder pausiert das dauerhafte Krähenfels-Motiv")
                }

                Button {
                    audio.toggleReadAloudDuck()
                } label: {
                    transportItem(
                        title: "Vorlesen",
                        icon: audio.readAloudDuck ? "quote.bubble.fill" : "quote.bubble",
                        active: audio.readAloudDuck
                    )
                }
                .accessibilityHint("Senkt die Musik ab, damit dein Vorlesetext verständlich bleibt")

                Button {
                    withAnimation(.easeInOut(duration: 0.2)) { expanded.toggle() }
                } label: {
                    transportItem(title: expanded ? "Schließen" : "Soundplan", icon: expanded ? "chevron.down" : "chevron.up", active: expanded)
                }

                Spacer(minLength: 2)

                Button(role: .destructive) {
                    audio.stopAll()
                } label: {
                    Label("STOP", systemImage: "stop.fill")
                        .font(.caption.weight(.heavy))
                        .foregroundStyle(.white)
                        .padding(.horizontal, 12)
                        .frame(minHeight: 44)
                        .background(FrostTheme.warning, in: Capsule())
                }
                .accessibilityLabel("Alle Sounds sofort stoppen")
            }
            .buttonStyle(.plain)
            .padding(.horizontal, 12)
            .padding(.vertical, 7)
        }
        .background(.ultraThinMaterial)
        .overlay(alignment: .top) { Divider().overlay(FrostTheme.line) }
    }

    private var expandedControls: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                SectionLabel(title: "Soundplan")
                Spacer()
                Text(audio.activeLayerSummary)
                    .font(.caption)
                    .foregroundStyle(FrostTheme.quiet)
                    .lineLimit(1)
            }
            Text("Cues startest du bewusst im aktuellen Szenenschritt. Das dauerhafte Motiv bleibt unabhängig davon aktiv.")
                .font(.caption)
                .foregroundStyle(FrostTheme.quiet)
            HStack(spacing: 12) {
                volume("Gesamt", value: $audio.masterVolume)
                volume("Atmosphäre", value: $audio.ambientVolume)
                volume("Musik", value: $audio.musicVolume)
                volume("Effekte", value: $audio.effectsVolume)
            }
        }
        .padding(.horizontal, 16)
        .padding(.top, 12)
        .padding(.bottom, 4)
        .frame(maxWidth: 1040, alignment: .leading)
    }

    private func volume(_ title: String, value: Binding<Double>) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption2)
                .foregroundStyle(FrostTheme.quiet)
            Slider(value: value, in: 0...1)
                .tint(FrostTheme.cobalt)
                .frame(minWidth: 110)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private func transportItem(title: String, icon: String, active: Bool) -> some View {
        VStack(spacing: 3) {
            Image(systemName: icon)
                .font(.body.weight(.semibold))
            Text(title)
                .font(.caption2.weight(.semibold))
                .lineLimit(1)
        }
        .foregroundStyle(active ? FrostTheme.frost : FrostTheme.quiet)
        .frame(minWidth: 68, minHeight: 44)
        .background(active ? FrostTheme.cobalt.opacity(0.22) : Color.clear, in: Capsule())
    }
}
