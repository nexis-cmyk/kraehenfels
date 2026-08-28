import SwiftUI

enum WorkspaceDestination: Hashable {
    case home
    case preparation
    case scene(String)
    case materials
    case inventory
    case rules
    case session
    case audioCheck
    case dossier
    case settings
}

struct RootView: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var session: SessionStore
    @State private var selection: WorkspaceDestination?
    @State private var columnVisibility: NavigationSplitViewVisibility = .all

    var body: some View {
        NavigationSplitView(columnVisibility: $columnVisibility) {
            sidebar
        } detail: {
            centerContent
                .safeAreaInset(edge: .bottom, spacing: 0) {
                    AudioTransportBar()
                }
        }
        .navigationSplitViewStyle(.balanced)
        .tint(FrostTheme.accent)
        .background(FrostTheme.ink.ignoresSafeArea())
        .onAppear {
            if selection == nil {
                selection = session.hasStartedSession ? .scene(session.currentSceneID) : .home
            }
        }
        .onChange(of: selection) { _, destination in
            guard case let .scene(sceneID) = destination else { return }
            guard session.currentSceneID != sceneID else { return }
            session.currentSceneID = sceneID
            session.guidedStepIndex = 0
        }
    }

    private var sidebar: some View {
        List(selection: $selection) {
            Section {
                NavigationLink(value: WorkspaceDestination.home) {
                    Label("Übersicht", systemImage: "square.grid.2x2")
                }
                NavigationLink(value: WorkspaceDestination.preparation) {
                    Label(session.hasStartedSession ? "Neue Runde vorbereiten" : "Spiel starten", systemImage: "play.circle.fill")
                }
            }

            Section("Szenen") {
                ForEach(content.manifest.scenes) { scene in
                    NavigationLink(value: WorkspaceDestination.scene(scene.id)) {
                        HStack(spacing: 10) {
                            Text(scene.id)
                                .font(.caption.monospaced().weight(.bold))
                                .foregroundStyle(session.completedSceneIDs.contains(scene.id) ? FrostTheme.accent : FrostTheme.quiet)
                                .frame(width: 30, alignment: .leading)
                            VStack(alignment: .leading, spacing: 2) {
                                Text(scene.shortTitle)
                                    .font(.subheadline.weight(.medium))
                                Text(session.isRecommendedScene(scene.id) ? "empfohlen · \(scene.duration)" : scene.duration)
                                    .font(.caption)
                                    .foregroundStyle(session.isRecommendedScene(scene.id) ? FrostTheme.accent : FrostTheme.quiet)
                            }
                            Spacer(minLength: 0)
                            if session.completedSceneIDs.contains(scene.id) {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundStyle(FrostTheme.accent)
                            }
                        }
                        .frame(minHeight: 44)
                    }
                }
            }

            Section("Werkzeuge") {
                NavigationLink(value: WorkspaceDestination.materials) { Label("Materialien", systemImage: "folder") }
                NavigationLink(value: WorkspaceDestination.inventory) { Label("Ausrüstung", systemImage: "shippingbox") }
                NavigationLink(value: WorkspaceDestination.rules) { Label("Regeln", systemImage: "dice") }
                NavigationLink(value: WorkspaceDestination.session) { Label("Am Tisch", systemImage: "person.3") }
                NavigationLink(value: WorkspaceDestination.audioCheck) { Label("Audio-Check", systemImage: "waveform") }
                NavigationLink(value: WorkspaceDestination.dossier) { Label("Akte", systemImage: "magnifyingglass") }
                NavigationLink(value: WorkspaceDestination.settings) { Label("Einstellungen", systemImage: "gearshape") }
            }
        }
        .listStyle(.sidebar)
        .scrollContentBackground(.hidden)
        .background(FrostTheme.panel)
        .navigationTitle("Krähenfels")
        .safeAreaPadding(.top, 8)
        .navigationSplitViewColumnWidth(min: 250, ideal: 282, max: 330)
    }

    @ViewBuilder
    private var centerContent: some View {
        switch selection ?? .home {
        case .home:
            WorkspaceHomeView(selection: $selection)
        case .preparation:
            GMStartView(
                onStart: { selection = .scene(session.currentSceneID) },
                onExit: { selection = .home }
            )
        case .scene(_):
            GuidedGMView(onExit: { selection = .home })
        case .materials:
            MaterialsView()
        case .inventory:
            InventoryView()
        case .rules:
            RulesView()
        case .session:
            SessionView()
        case .audioCheck:
            AudioCheckView()
        case .dossier:
            CaseFileView()
        case .settings:
            SettingsView()
        }
    }
}

private struct WorkspaceHomeView: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var session: SessionStore
    @Binding var selection: WorkspaceDestination?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                header
                resumePanel
                nightPanel
                materialPanel
            }
            .frame(maxWidth: 800, alignment: .leading)
            .padding(28)
        }
        .background(FrostTheme.ink.ignoresSafeArea())
        .navigationTitle("Leitstand")
        .navigationBarTitleDisplayMode(.inline)
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 7) {
            Text("KRÄHNFELS · DIE LETZTE KUTSCHE")
                .font(.caption.weight(.semibold))
                .foregroundStyle(FrostTheme.accent)
            Text("Dein Leitstand für die Nacht.")
                .font(.system(size: 38, weight: .bold, design: .rounded))
                .foregroundStyle(FrostTheme.frost)
            Text("Drei Reisende · Schwarzwald · November 1890")
                .font(.title3)
                .foregroundStyle(FrostTheme.quiet)
        }
    }

    private var resumePanel: some View {
        FrostCard {
            HStack(alignment: .top, spacing: 16) {
                Image(systemName: session.hasStartedSession ? "arrow.clockwise.circle.fill" : "play.circle.fill")
                    .font(.system(size: 36))
                    .foregroundStyle(FrostTheme.accent)
                VStack(alignment: .leading, spacing: 6) {
                    Text(session.hasStartedSession ? "Runde fortsetzen" : "Spielleiter-Modus starten")
                        .font(.title3.weight(.semibold))
                        .foregroundStyle(FrostTheme.frost)
                    Text(session.hasStartedSession ? "Weiter bei \(content.scene(for: session.currentSceneID)?.shortTitle ?? "der aktuellen Szene")" : "Vorbereitung, Figuren und Schritt-für-Schritt-Führung")
                        .font(.body)
                        .foregroundStyle(FrostTheme.quiet)
                }
                Spacer()
                Button {
                    selection = session.hasStartedSession ? .scene(session.currentSceneID) : .preparation
                } label: {
                    Image(systemName: "chevron.right")
                        .frame(width: 44, height: 44)
                        .background(FrostTheme.accent.opacity(0.16), in: Circle())
                }
                .buttonStyle(.plain)
                .foregroundStyle(FrostTheme.accent)
                .accessibilityLabel(session.hasStartedSession ? "Runde fortsetzen" : "Spielleiter-Modus starten")
            }
        }
    }

    private var nightPanel: some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    SectionLabel(title: "Nachtstand")
                    Spacer()
                    Text("Stufe \(session.threatLevel)/5")
                        .font(.caption.weight(.bold))
                        .foregroundStyle(session.threatLevel >= 4 ? FrostTheme.warning : FrostTheme.accent)
                }
                HStack(spacing: 7) {
                    ForEach(0..<6, id: \.self) { index in
                        Capsule()
                            .fill(index <= session.threatLevel ? (index >= 4 ? FrostTheme.warning : FrostTheme.accent) : FrostTheme.panelRaised)
                            .frame(height: 7)
                    }
                }
                Text(content.phase(at: session.nightPhaseIndex)?.detail ?? "")
                    .font(.subheadline)
                    .foregroundStyle(FrostTheme.quiet)
                Stepper("Dorfspannung manuell setzen", value: Binding(get: { session.threatLevel }, set: { session.setThreatLevel($0) }), in: 0...5)
                    .font(.subheadline)
            }
        }
    }

    private var materialPanel: some View {
        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
            homeAction("Materialien", "folder", .materials)
            homeAction("Ausrüstung", "shippingbox", .inventory)
            homeAction("Regeln", "dice", .rules)
            homeAction("Audio-Check", "waveform", .audioCheck)
            homeAction("Akte", "magnifyingglass", .dossier)
        }
        .buttonStyle(.plain)
    }

    private func homeAction(_ title: String, _ symbol: String, _ destination: WorkspaceDestination) -> some View {
        Button { selection = destination } label: {
            FrostCard {
                Label(title, systemImage: symbol)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(FrostTheme.frost)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
    }
}

struct WorkspaceContextView: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var session: SessionStore
    let sceneID: String

    private var step: GuideStep? {
        let steps = content.steps(for: sceneID)
        guard steps.indices.contains(session.guidedStepIndex) else { return steps.last }
        return steps[session.guidedStepIndex]
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                SectionLabel(title: "Jetzt relevant")
                if let step {
                    Label(step.kind.label, systemImage: step.kind.symbol)
                        .font(.headline)
                        .foregroundStyle(FrostTheme.accent)
                    Text(step.title)
                        .font(.title3.weight(.semibold))
                        .foregroundStyle(FrostTheme.frost)
                    Divider().overlay(FrostTheme.line)
                    contextRow("Sound", value: step.audioCueID.flatMap { content.cue(for: $0)?.title } ?? "Kein Sound vorgeschlagen", symbol: "waveform")
                    contextRow("Hinweis", value: step.clueID ?? step.handoutID ?? "Keine Ausgabe", symbol: "doc.text")
                    contextRow("NPC", value: step.npcID ?? step.npcIDs.first ?? "Keiner", symbol: "person")
                    if let roll = step.roll {
                        FrostCard {
                            VStack(alignment: .leading, spacing: 5) {
                                Label("Würfelprobe", systemImage: "dice")
                                    .font(.subheadline.weight(.semibold))
                                    .foregroundStyle(FrostTheme.accent)
                                Text("\(roll.actor) · \(roll.ability)")
                                    .font(.subheadline)
                                Text("Ziel: \(roll.target)")
                                    .font(.caption)
                                    .foregroundStyle(FrostTheme.quiet)
                            }
                        }
                    }
                } else {
                    Text("Wähle eine Szene, um ihren aktuellen Kontext zu sehen.")
                        .foregroundStyle(FrostTheme.quiet)
                }
            }
            .padding(20)
        }
        .background(FrostTheme.panel.opacity(0.82).ignoresSafeArea())
        .navigationTitle("Kontext")
        .navigationBarTitleDisplayMode(.inline)
    }

    private func contextRow(_ title: String, value: String, symbol: String) -> some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: symbol)
                .foregroundStyle(FrostTheme.accent)
                .frame(width: 22)
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(FrostTheme.quiet)
                Text(value)
                    .font(.subheadline)
                    .foregroundStyle(FrostTheme.frost)
            }
        }
    }
}
