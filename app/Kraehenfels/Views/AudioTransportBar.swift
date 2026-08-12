import SwiftUI

struct AudioTransportBar: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var audio: AudioEngine

    var body: some View {
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
        .padding(.vertical, 8)
        .background(.ultraThinMaterial)
        .overlay(alignment: .top) { Divider().overlay(FrostTheme.frost.opacity(0.2)) }
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
