import SwiftUI

struct RootView: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var session: SessionStore
    @EnvironmentObject private var cloud: SupabaseManager

    var body: some View {
        Group {
            if cloud.status == .connected {
                leadstand
            } else {
                AuthGateView()
            }
        }
        .task {
            _ = await cloud.start()
        }
    }

    private var leadstand: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    header
                    startCard
                    currentSceneCard
                    tableStatus
                    progressSummary
                    sceneList
                    quickActions
                }
                .padding(20)
                .safeAreaPadding(.bottom, 96)
            }
            .background(FrostTheme.ink.ignoresSafeArea())
            .navigationTitle("Krähenfels")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Menu {
                        NavigationLink("Materialien", destination: MaterialsView())
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
        .safeAreaInset(edge: .bottom, spacing: 0) {
            AudioTransportBar()
        }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("KRÄHENFELS · DIE LETZTE KUTSCHE")
                .font(.caption.weight(.semibold))
                .tracking(1.6)
                .foregroundStyle(FrostTheme.cobalt)
            Text("Dein Leitstand für die Nacht.")
                .font(.system(size: 33, weight: .bold, design: .rounded))
                .foregroundStyle(FrostTheme.frost)
            Text("Drei Reisende · Schwarzwald · November 1890")
                .font(.subheadline)
                .foregroundStyle(FrostTheme.quiet)
        }
    }

    private var startCard: some View {
        NavigationLink(destination: GMStartView()) {
            HStack(alignment: .top, spacing: 13) {
                Image(systemName: "play.circle.fill")
                    .font(.system(size: 32))
                    .foregroundStyle(FrostTheme.frost)
                VStack(alignment: .leading, spacing: 5) {
                    Text("Spielleiter-Modus starten")
                        .font(.headline)
                        .foregroundStyle(.white)
                    Text("Vorbereitung, fertige Figuren und Schritt-für-Schritt-Führung")
                        .font(.subheadline)
                        .foregroundStyle(FrostTheme.quiet)
                        .fixedSize(horizontal: false, vertical: true)
                }
                Spacer()
                Image(systemName: "chevron.right")
                    .foregroundStyle(FrostTheme.cobalt)
            }
            .padding(17)
            .background(FrostTheme.cobalt.opacity(0.2), in: RoundedRectangle(cornerRadius: 18, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(FrostTheme.cobalt.opacity(0.5), lineWidth: 1))
        }
        .buttonStyle(.plain)
    }

    private var currentSceneCard: some View {
        Group {
            if let scene = content.scene(for: session.currentSceneID) {
                NavigationLink(destination: GuidedGMView()) {
                    FrostCard {
                        VStack(alignment: .leading, spacing: 12) {
                            HStack {
                                SectionLabel(title: "Jetzt weiterspielen")
                                Spacer()
                                Text("\(session.completedSceneIDs.count)/\(content.manifest.scenes.count)")
                                    .font(.caption.monospaced())
                                    .foregroundStyle(FrostTheme.quiet)
                            }
                            HStack(alignment: .top, spacing: 12) {
                                Image(systemName: "location.fill")
                                    .foregroundStyle(FrostTheme.cobalt)
                                    .frame(width: 25)
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(scene.title == "Das schwarze Keiler" ? "Der Schwarze Keiler" : scene.title)
                                        .font(.title3.weight(.semibold))
                                        .foregroundStyle(.white)
                                    Text("Schritt \(min(session.guidedStepIndex + 1, max(GuidedFlowCatalog.steps(for: scene.id).count, 1))) von \(GuidedFlowCatalog.steps(for: scene.id).count)")
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
                    Text(session.savedNames().isEmpty ? "Drei Reisende sind noch nicht zugewiesen" : session.savedNames().joined(separator: " · "))
                        .font(.subheadline.weight(.medium))
                        .foregroundStyle(.white)
                        .lineLimit(2)
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

    private var progressSummary: some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    SectionLabel(title: "Nachtstand")
                    Spacer()
                    Text("Stufe \(session.threatLevel)/5")
                        .font(.caption.weight(.bold))
                        .foregroundStyle(session.threatLevel >= 4 ? FrostTheme.warning : FrostTheme.cobalt)
                }
                HStack(spacing: 7) {
                    ForEach(0..<6, id: \.self) { index in
                        Capsule()
                            .fill(index <= session.threatLevel ? (index >= 4 ? FrostTheme.warning : FrostTheme.cobalt) : FrostTheme.panelRaised)
                            .frame(height: 7)
                    }
                }
                Text(session.currentNightPhase.detail)
                    .font(.caption)
                    .foregroundStyle(FrostTheme.quiet)
                Stepper("Dorfspannung manuell setzen", value: Binding(get: { session.threatLevel }, set: { session.setThreatLevel($0) }), in: 0...5)
                    .font(.caption)
                    .foregroundStyle(FrostTheme.quiet)
            }
        }
    }

    private var sceneList: some View {
        VStack(alignment: .leading, spacing: 10) {
            SectionLabel(title: "Szenen")
            ForEach(content.manifest.scenes) { scene in
                NavigationLink(destination: GuidedGMView().onAppear { session.currentSceneID = scene.id; session.guidedStepIndex = 0 }) {
                    HStack(spacing: 12) {
                        Text(scene.id)
                            .font(.caption.monospaced().weight(.bold))
                            .foregroundStyle(session.completedSceneIDs.contains(scene.id) ? FrostTheme.cobalt : FrostTheme.quiet)
                            .frame(width: 32)
                        VStack(alignment: .leading, spacing: 3) {
                            Text(scene.title == "Das schwarze Keiler" ? "Der Schwarze Keiler" : scene.title)
                                .font(.body.weight(.medium))
                                .foregroundStyle(.white)
                            Text("\(scene.duration) · \(session.isRecommendedScene(scene.id) ? "empfohlen" : "GM-Sprung")")
                                .font(.caption)
                                .foregroundStyle(session.isRecommendedScene(scene.id) ? FrostTheme.quiet : FrostTheme.warning)
                        }
                        Spacer()
                        Image(systemName: session.completedSceneIDs.contains(scene.id) ? "checkmark.circle.fill" : "chevron.right")
                            .foregroundStyle(session.completedSceneIDs.contains(scene.id) ? FrostTheme.cobalt : FrostTheme.quiet)
                    }
                    .padding(.vertical, 7)
                }
                .buttonStyle(.plain)
            }
        }
    }

    private var quickActions: some View {
        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 10) {
            NavigationLink(destination: MaterialsView()) { quickAction("Materialien", "folder") }
            NavigationLink(destination: RulesView()) { quickAction("Regeln", "dice") }
            NavigationLink(destination: AudioCheckView()) { quickAction("Audio-Check", "waveform") }
            NavigationLink(destination: CaseFileView()) { quickAction("Akte", "magnifyingglass") }
        }
        .buttonStyle(.plain)
    }

    private func quickAction(_ title: String, _ symbol: String) -> some View {
        FrostCard {
            Label(title, systemImage: symbol)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(FrostTheme.frost)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}
