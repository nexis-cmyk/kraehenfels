import SwiftUI

struct SceneDetailView: View {
    let scene: SceneEntry
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var audio: AudioEngine
    @AppStorage("currentSceneID") private var currentSceneID = "S01"
    @AppStorage("completedSceneIDs") private var completedSceneIDs = ""

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                sceneHeader
                goalCard
                audioPanel
                handoutPanel
                finishButton
            }
            .padding(20)
        }
        .background(FrostTheme.ink.ignoresSafeArea())
        .navigationTitle(scene.shortTitle)
        .navigationBarTitleDisplayMode(.inline)
    }

    private var sceneHeader: some View {
        VStack(alignment: .leading, spacing: 9) {
            Text(scene.id)
                .font(.caption.monospaced().weight(.bold))
                .foregroundStyle(FrostTheme.cobalt)
            Text(scene.title)
                .font(.system(size: 31, weight: .bold, design: .rounded))
                .foregroundStyle(FrostTheme.frost)
            Label(scene.duration, systemImage: "clock")
                .font(.subheadline)
                .foregroundStyle(FrostTheme.quiet)
        }
    }

    private var goalCard: some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 8) {
                SectionLabel(title: "Ziel der Szene")
                Text(scene.goal)
                    .font(.body)
                    .foregroundStyle(.white.opacity(0.92))
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    private var audioPanel: some View {
        VStack(alignment: .leading, spacing: 11) {
            SectionLabel(title: "Soundboard")
            ForEach(content.cues(for: scene)) { cue in
                CueRow(cue: cue)
            }
            Button {
                audio.stopAll()
            } label: {
                Label("Alle Sounds stoppen", systemImage: "stop.fill")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(FrostTheme.warning)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.vertical, 6)
            }
            .accessibilityHint("Stoppt Atmosphäre, Musik und Effekte")
        }
    }

    private var handoutPanel: some View {
        VStack(alignment: .leading, spacing: 10) {
            SectionLabel(title: "Hinweise")
            ForEach(scene.handoutIds, id: \.self) { id in
                if let handout = content.handout(for: id) {
                    HStack(spacing: 12) {
                        Image(systemName: handout.spoiler ? "lock.fill" : "doc.text")
                            .foregroundStyle(handout.spoiler ? FrostTheme.warning : FrostTheme.cobalt)
                        VStack(alignment: .leading, spacing: 3) {
                            Text("\(handout.id) · \(handout.title)")
                                .font(.subheadline.weight(.medium))
                                .foregroundStyle(.white)
                            Text(handout.spoiler ? "Spoiler · nur bei Bedarf" : "Spielerhinweis · \(handout.format)")
                                .font(.caption)
                                .foregroundStyle(FrostTheme.quiet)
                        }
                        Spacer()
                    }
                    .padding(.vertical, 5)
                }
            }
        }
    }

    private var finishButton: some View {
        Button {
            currentSceneID = scene.nextSceneIds.first ?? scene.id
            var ids = completedSceneIDs.split(separator: ",").map(String.init)
            if !ids.contains(scene.id) { ids.append(scene.id) }
            completedSceneIDs = ids.joined(separator: ",")
        } label: {
            Text(scene.nextSceneIds.isEmpty ? "Szene abschließen" : "Szene abschließen und weiter")
                .font(.headline)
                .foregroundStyle(FrostTheme.ink)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 15)
                .background(FrostTheme.frost, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
        }
        .accessibilityHint("Markiert diese Szene als abgeschlossen")
    }
}

private struct CueRow: View {
    let cue: AudioCue
    @EnvironmentObject private var audio: AudioEngine

    var body: some View {
        Button {
            audio.toggle(cue)
        } label: {
            HStack(spacing: 12) {
                Image(systemName: audio.isPlaying(cue) ? "pause.fill" : cue.iconName)
                    .foregroundStyle(audio.isPlaying(cue) ? FrostTheme.frost : FrostTheme.cobalt)
                    .frame(width: 25)
                VStack(alignment: .leading, spacing: 3) {
                    Text(cue.title)
                        .font(.subheadline.weight(.medium))
                        .foregroundStyle(.white)
                    Text("\(cue.id) · \(cue.categoryLabel)\(cue.isClue ? " · Hinweis" : "")")
                        .font(.caption)
                        .foregroundStyle(cue.isClue ? FrostTheme.warning : FrostTheme.quiet)
                }
                Spacer()
                Text(audio.isPlaying(cue) ? "Läuft" : "Start")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(audio.isPlaying(cue) ? FrostTheme.frost : FrostTheme.quiet)
            }
            .padding(13)
            .background(FrostTheme.panel, in: RoundedRectangle(cornerRadius: 13, style: .continuous))
        }
        .buttonStyle(.plain)
        .accessibilityLabel("\(cue.title), \(cue.categoryLabel)")
        .accessibilityValue(audio.isPlaying(cue) ? "Läuft" : "Gestoppt")
    }
}
