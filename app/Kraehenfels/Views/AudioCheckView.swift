import SwiftUI

struct AudioCheckView: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var audio: AudioEngine
    @EnvironmentObject private var session: SessionStore

    var body: some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 14) {
                intro
                ForEach(content.manifest.audioCues) { cue in
                    cueCard(cue)
                }
                Button("Bewertungen zurücksetzen") { session.clearAudioRatings() }
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(FrostTheme.warning)
                    .frame(maxWidth: .infinity, minHeight: 44)
            }
            .padding(20)
            .safeAreaPadding(.bottom, 88)
        }
        .background(FrostTheme.ink.ignoresSafeArea())
        .navigationTitle("Audio-Check")
        .navigationBarTitleDisplayMode(.inline)
        .onDisappear { audio.stopAll() }
    }

    private var intro: some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    SectionLabel(title: "Hörprobe vor dem Abend")
                    Spacer()
                    Text("\(ratedCount)/\(content.manifest.audioCues.count)")
                        .font(.caption.monospaced().weight(.bold))
                        .foregroundStyle(FrostTheme.cobalt)
                }
                Text("Hör jeden Cue einmal über die Box und einmal über das iPhone. Markiere nur, ob Klang und Beschreibung wirklich zusammenpassen.")
                    .font(.subheadline)
                    .foregroundStyle(.white.opacity(0.9))
                Button {
                    audio.runSelfTest()
                } label: {
                    Label("Testton abspielen", systemImage: "speaker.wave.3.fill")
                        .font(.subheadline.weight(.semibold))
                }
                .buttonStyle(.bordered)
                if let loaded = audio.lastLoadedResource {
                    Text("Zuletzt geladen: \(loaded)")
                        .font(.caption.monospaced())
                        .foregroundStyle(FrostTheme.quiet)
                }
                if let event = audio.lastEvent {
                    Text(event)
                        .font(.caption)
                        .foregroundStyle(FrostTheme.cobalt)
                }
                if let error = audio.lastError {
                    Label(error, systemImage: "exclamationmark.triangle.fill")
                        .font(.caption)
                        .foregroundStyle(FrostTheme.warning)
                        .fixedSize(horizontal: false, vertical: true)
                }
                ProgressView(value: Double(ratedCount), total: Double(max(content.manifest.audioCues.count, 1)))
                    .tint(ratedCount == content.manifest.audioCues.count ? .green : FrostTheme.cobalt)
                Text(audio.sessionStatus)
                    .font(.caption)
                    .foregroundStyle(FrostTheme.quiet)
            }
        }
    }

    private func cueCard(_ cue: AudioCue) -> some View {
        let rating = session.audioRatings[cue.id]
        return FrostCard {
            VStack(alignment: .leading, spacing: 11) {
                HStack(alignment: .top, spacing: 12) {
                    Button { audio.toggle(cue) } label: {
                        Image(systemName: audio.isPlaying(cue) && cue.mode == "loop" ? "pause.fill" : "play.fill")
                            .font(.headline)
                            .foregroundStyle(FrostTheme.ink)
                            .frame(width: 48, height: 48)
                            .background(FrostTheme.frost, in: Circle())
                    }
                    .accessibilityLabel("\(cue.title) abspielen")
                    VStack(alignment: .leading, spacing: 3) {
                        HStack(spacing: 7) {
                            Text(cue.id)
                                .font(.caption.monospaced().weight(.bold))
                                .foregroundStyle(FrostTheme.cobalt)
                            Text(cue.categoryLabel)
                                .font(.caption2.weight(.bold))
                                .foregroundStyle(FrostTheme.quiet)
                            if cue.file.hasPrefix("V6_") {
                                Text("V6")
                                    .font(.caption2.monospaced().weight(.bold))
                                    .foregroundStyle(FrostTheme.warning)
                            }
                        }
                        Text(cue.title)
                            .font(.headline)
                            .foregroundStyle(.white)
                        Text(cue.file)
                            .font(.caption2.monospaced())
                            .foregroundStyle(FrostTheme.quiet)
                    }
                    Spacer()
                    if let rating {
                        Image(systemName: rating > 0 ? "checkmark.seal.fill" : "xmark.octagon.fill")
                            .foregroundStyle(rating > 0 ? .green : FrostTheme.warning)
                    }
                }

                VStack(alignment: .leading, spacing: 5) {
                    Text("SOLL KLINGEN WIE")
                        .font(.caption2.weight(.bold))
                        .tracking(1.1)
                        .foregroundStyle(FrostTheme.quiet)
                    Text(cue.description)
                        .font(.subheadline)
                        .foregroundStyle(.white.opacity(0.9))
                    Text("Im Spiel: \(cue.playWhen)")
                        .font(.caption)
                        .foregroundStyle(FrostTheme.cobalt)
                }

                HStack(spacing: 10) {
                    ratingButton("Passt", icon: "checkmark", selected: rating == 1, color: .green) {
                        session.setAudioRating(cue.id, rating: 1)
                    }
                    ratingButton("Falsch", icon: "xmark", selected: rating == -1, color: FrostTheme.warning) {
                        session.setAudioRating(cue.id, rating: -1)
                    }
                }
            }
        }
    }

    private func ratingButton(_ title: String, icon: String, selected: Bool, color: Color, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Label(title, systemImage: icon)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(selected ? FrostTheme.ink : color)
                .frame(maxWidth: .infinity, minHeight: 44)
                .background(selected ? color : color.opacity(0.12), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
        }
        .buttonStyle(.plain)
    }

    private var ratedCount: Int {
        content.manifest.audioCues.reduce(0) { result, cue in
            result + (session.audioRatings[cue.id] == nil ? 0 : 1)
        }
    }
}
