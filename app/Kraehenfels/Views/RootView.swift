import SwiftUI

struct RootView: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var audio: AudioEngine
    @EnvironmentObject private var session: SessionStore

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 22) {
                    header
                    tableStatus
                    nightStatus
                    threatStatus
                    currentSceneCard
                    sceneList
                    quickActions
                }
                .padding(20)
            }
            .background(FrostTheme.ink.ignoresSafeArea())
            .navigationTitle("Krähenfels")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Menu {
                        NavigationLink("Regeln", destination: RulesView())
                        NavigationLink("Am Tisch", destination: SessionView())
                        NavigationLink("Einstellungen", destination: SettingsView())
                    } label: {
                        Image(systemName: "ellipsis.circle")
                            .foregroundStyle(FrostTheme.frost)
                    }
                    .accessibilityLabel("Weitere Bereiche")
                }
            }
        }
        .tint(FrostTheme.cobalt)
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("KRÄHENFELS · DIE LETZTE KUTSCHE")
                .font(.caption.weight(.semibold))
                .tracking(1.6)
                .foregroundStyle(FrostTheme.cobalt)
            Text("Die Nacht läuft.")
                .font(.system(size: 35, weight: .bold, design: .rounded))
                .foregroundStyle(FrostTheme.frost)
            Text("Spielleitung für drei Reisende · Schwarzwald, November 1890")
                .font(.subheadline)
                .foregroundStyle(FrostTheme.quiet)
        }
    }

    private var currentSceneCard: some View {
        Group {
            if let scene = content.scene(for: session.currentSceneID) {
                NavigationLink(destination: SceneDetailView(scene: scene)) {
                    FrostCard {
                        VStack(alignment: .leading, spacing: 13) {
                            HStack {
                                SectionLabel(title: "Aktuelle Szene")
                                Spacer()
                                Text("\(session.completedSceneIDs.count)/\(content.manifest.scenes.count) abgeschlossen")
                                    .font(.caption.monospaced())
                                    .foregroundStyle(FrostTheme.quiet)
                            }
                            HStack(alignment: .top, spacing: 14) {
                                Image(systemName: scene.escalation >= 4 ? "exclamationmark.triangle.fill" : "circle.dotted.circle")
                                    .font(.title2)
                                    .foregroundStyle(scene.escalation >= 4 ? FrostTheme.warning : FrostTheme.frost)
                                    .frame(width: 28)
                                VStack(alignment: .leading, spacing: 5) {
                                    Text(scene.title)
                                        .font(.title3.weight(.semibold))
                                        .foregroundStyle(.white)
                                    Text(scene.duration)
                                        .font(.caption)
                                        .foregroundStyle(FrostTheme.quiet)
                                }
                                Spacer()
                                Image(systemName: "arrow.up.right")
                                    .foregroundStyle(FrostTheme.cobalt)
                            }
                            ProgressView(value: Double(session.completedSceneIDs.count), total: Double(max(content.manifest.scenes.count, 1)))
                                .tint(FrostTheme.cobalt)
                        }
                    }
                }
                .buttonStyle(.plain)
            }
        }
    }

    private var tableStatus: some View {
        FrostCard {
            HStack(alignment: .center, spacing: 12) {
                Image(systemName: "person.3.fill")
                    .font(.title3)
                    .foregroundStyle(FrostTheme.cobalt)
                    .frame(width: 28)
                VStack(alignment: .leading, spacing: 3) {
                    SectionLabel(title: "Am Tisch")
                    if session.savedNames().isEmpty {
                        Text("Drei Reisende noch benennen")
                            .font(.subheadline)
                            .foregroundStyle(FrostTheme.quiet)
                    } else {
                        Text(session.savedNames().joined(separator: " · "))
                            .font(.subheadline.weight(.medium))
                            .foregroundStyle(.white)
                            .lineLimit(2)
                    }
                }
                Spacer()
                NavigationLink(destination: SessionView()) {
                    Image(systemName: "pencil")
                        .foregroundStyle(FrostTheme.cobalt)
                        .frame(minWidth: 44, minHeight: 44)
                }
                .accessibilityLabel("Tischdaten bearbeiten")
            }
        }
    }

    private var nightStatus: some View {
        FrostCard {
            HStack(alignment: .center, spacing: 12) {
                Image(systemName: session.currentNightPhase.symbol)
                    .font(.title3)
                    .foregroundStyle(session.currentNightPhase.id >= 2 ? FrostTheme.warning : FrostTheme.cobalt)
                    .frame(width: 28)
                VStack(alignment: .leading, spacing: 3) {
                    SectionLabel(title: "Nachtstand")
                    Text(session.currentNightPhase.title)
                        .font(.subheadline.weight(.medium))
                        .foregroundStyle(.white)
                    Text(session.currentNightPhase.detail)
                        .font(.caption)
                        .foregroundStyle(FrostTheme.quiet)
                }
                Spacer()
                NavigationLink(destination: SessionView()) {
                    Image(systemName: "chevron.right")
                        .foregroundStyle(FrostTheme.cobalt)
                        .frame(minWidth: 44, minHeight: 44)
                }
                .accessibilityLabel("Nachtstand ändern")
            }
        }
    }

    private var threatStatus: some View {
        FrostCard {
            HStack(spacing: 12) {
                Image(systemName: session.threatLevel >= 4 ? "eye.trianglebadge.exclamationmark" : "tree.fill")
                    .foregroundStyle(session.threatLevel >= 4 ? FrostTheme.warning : FrostTheme.cobalt)
                    .frame(width: 28)
                VStack(alignment: .leading, spacing: 3) {
                    SectionLabel(title: "Dorfspannung")
                    if let level = content.manifest.threatLevels.first(where: { $0.level == session.threatLevel }) {
                        Text("Stufe \(session.threatLevel): \(level.title)")
                            .font(.subheadline.weight(.medium))
                            .foregroundStyle(.white)
                        Text(level.detail)
                            .font(.caption)
                            .foregroundStyle(FrostTheme.quiet)
                    } else {
                        Text("Stufe \(session.threatLevel) von 5")
                            .font(.subheadline.weight(.medium))
                            .foregroundStyle(.white)
                    }
                }
                Spacer()
                Stepper("", value: Binding(get: { session.threatLevel }, set: { session.setThreatLevel($0) }), in: 0...5)
                    .labelsHidden()
                    .accessibilityLabel("Dorfspannung")
            }
        }
    }

    private var sceneList: some View {
        VStack(alignment: .leading, spacing: 12) {
            SectionLabel(title: "Szenen")
            ForEach(content.manifest.scenes) { scene in
                    NavigationLink(destination: SceneDetailView(scene: scene)) {
                    sceneRow(scene)
                }
                .buttonStyle(.plain)
            }
        }
    }

    private func sceneRow(_ scene: SceneEntry) -> some View {
        let completed = session.completedSceneIDs.contains(scene.id)
        return HStack(spacing: 13) {
            Text(scene.id)
                .font(.caption.monospaced().weight(.bold))
                .foregroundStyle(completed ? FrostTheme.cobalt : FrostTheme.quiet)
                .frame(width: 32)
            VStack(alignment: .leading, spacing: 3) {
                Text(scene.title)
                    .font(.body.weight(.medium))
                    .foregroundStyle(.white)
                Text(scene.duration)
                    .font(.caption)
                    .foregroundStyle(FrostTheme.quiet)
            }
            Spacer()
            Image(systemName: completed ? "checkmark.circle.fill" : "chevron.right")
                .foregroundStyle(completed ? FrostTheme.cobalt : FrostTheme.quiet)
        }
        .padding(.vertical, 8)
        .contentShape(Rectangle())
    }

    private var quickActions: some View {
        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
            NavigationLink(destination: RulesView()) {
                FrostCard {
                    Label("Regeln", systemImage: "dice")
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(FrostTheme.frost)
                }
            }
            .buttonStyle(.plain)
            NavigationLink(destination: SettingsView()) {
                FrostCard {
                    Label("Audio", systemImage: "speaker.wave.2")
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(FrostTheme.frost)
                }
            }
            .buttonStyle(.plain)
            NavigationLink(destination: SessionView()) {
                FrostCard {
                    Label("Am Tisch", systemImage: "person.3")
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(FrostTheme.frost)
                }
            }
            .buttonStyle(.plain)
            NavigationLink(destination: CaseFileView()) {
                FrostCard {
                    Label("Akte", systemImage: "folder")
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(FrostTheme.frost)
                }
            }
            .buttonStyle(.plain)
        }
    }

}
