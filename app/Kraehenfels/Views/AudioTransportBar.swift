import SwiftUI

struct AudioTransportBar: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var audio: AudioEngine
    @State private var showMixer = false

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

            Button {
                showMixer = true
            } label: {
                transportItem(title: "Soundplan", icon: "slider.horizontal.3", active: showMixer)
            }
            .accessibilityHint("Öffnet die Lautstärkeeinstellungen")

            Spacer(minLength: 2)

            Button(role: .destructive) {
                audio.stopAll()
            } label: {
                Label("STOP", systemImage: "stop.fill")
                    .font(.caption.weight(.heavy))
                    .foregroundStyle(FrostTheme.frost)
                    .padding(.horizontal, 12)
                    .frame(minHeight: 44)
                    .background(FrostTheme.warning, in: Capsule())
            }
            .accessibilityLabel("Alle Sounds sofort stoppen")
        }
        .buttonStyle(.plain)
        .padding(.horizontal, 12)
        .frame(maxWidth: 1080, minHeight: 60, maxHeight: 60)
        .frame(maxWidth: .infinity)
        .background(.ultraThinMaterial)
        .overlay(alignment: .top) { Divider().overlay(FrostTheme.line) }
        .popover(isPresented: $showMixer, attachmentAnchor: .rect(.bounds), arrowEdge: .bottom) {
            AudioMixerPopover()
                .environmentObject(audio)
                .presentationCompactAdaptation(.sheet)
        }
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
        .background(active ? FrostTheme.accent.opacity(0.22) : Color.clear, in: Capsule())
    }
}

private struct AudioMixerPopover: View {
    @EnvironmentObject private var audio: AudioEngine

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                VStack(alignment: .leading, spacing: 3) {
                    Text("Soundplan")
                        .font(.headline)
                    Text(audio.activeLayerSummary)
                        .font(.caption)
                        .foregroundStyle(FrostTheme.quiet)
                        .lineLimit(1)
                }
                Spacer()
                Image(systemName: "waveform")
                    .foregroundStyle(FrostTheme.accent)
            }
            Text("Cues startest du bewusst im aktuellen Szenenschritt. Das dauerhafte Motiv bleibt unabhängig davon aktiv.")
                .font(.caption)
                .foregroundStyle(FrostTheme.quiet)
                .fixedSize(horizontal: false, vertical: true)
            volume("Gesamt", value: $audio.masterVolume)
            volume("Atmosphäre", value: $audio.ambientVolume)
            volume("Musik", value: $audio.musicVolume)
            volume("Effekte", value: $audio.effectsVolume)
        }
        .padding(20)
        .frame(width: 360, alignment: .leading)
        .presentationBackground(FrostTheme.panel)
    }

    private func volume(_ title: String, value: Binding<Double>) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(title)
                    .font(.caption.weight(.semibold))
                Spacer()
                Text("\(Int(value.wrappedValue * 100)) %")
                    .font(.caption.monospaced())
                    .foregroundStyle(FrostTheme.quiet)
            }
            Slider(value: value, in: 0...1)
                .tint(FrostTheme.accent)
        }
    }
}
