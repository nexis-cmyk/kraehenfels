import SwiftUI

struct MaterialsView: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var session: SessionStore
    @State private var showSpoilers = false

    var body: some View {
        List {
            Section {
                VStack(alignment: .leading, spacing: 6) {
                    Text("SL-MATERIALIEN")
                        .font(.caption.weight(.bold))
                        .tracking(1.5)
                        .foregroundStyle(FrostTheme.cobalt)
                    Text("Alles, was du am Tisch zeigen, wissen oder nachschlagen kannst.")
                        .font(.headline)
                        .foregroundStyle(FrostTheme.frost)
                    Text("Spieler sehen weiterhin nur die gedruckten Handouts. Diese Ansicht ist vollständig für die Spielleitung.")
                        .font(.caption)
                        .foregroundStyle(FrostTheme.quiet)
                }
                .padding(.vertical, 8)
                .listRowBackground(Color.clear)
            }
            Section("Aktueller Abschnitt") {
                if let scene = content.scene(for: session.currentSceneID) {
                    NavigationLink(destination: GuidedGMView()) {
                        Label(scene.title == "Das schwarze Keiler" ? "Der Schwarze Keiler" : scene.title, systemImage: "location.fill")
                    }
                }
                NavigationLink(destination: CaseFileView()) {
                    Label("Fakten und Hinweiskette", systemImage: "magnifyingglass")
                }
            }
            Section("Karten und Räume") {
                ForEach(content.manifest.maps) { map in
                    NavigationLink(destination: MapDetailView(map: map, showSpoilers: true)) {
                        Label(map.title, systemImage: "map.fill")
                    }
                }
            }
            Section("Handouts") {
                Toggle("SL-Spoilerblätter anzeigen", isOn: $showSpoilers)
                    .tint(FrostTheme.cobalt)
                ForEach(content.manifest.handouts.filter { showSpoilers || !$0.spoiler }) { handout in
                    NavigationLink(destination: HandoutPreviewView(handoutID: handout.id)) {
                        HStack {
                            Image(systemName: handout.spoiler ? "lock.fill" : "doc.text")
                                .foregroundStyle(handout.spoiler ? FrostTheme.warning : FrostTheme.cobalt)
                            VStack(alignment: .leading, spacing: 2) {
                                Text("\(handout.id) · \(handout.title)")
                                    .foregroundStyle(.white)
                                Text(handout.format)
                                    .font(.caption)
                                    .foregroundStyle(FrostTheme.quiet)
                            }
                        }
                    }
                }
            }
            Section("NPC-Dossiers") {
                ForEach(content.manifest.npcs) { npc in
                    NavigationLink(destination: NPCDossierView(npcID: npc.id)) {
                        Label(npc.name, systemImage: "person.crop.circle")
                    }
                }
            }
            Section("Regeln und Audio") {
                NavigationLink(destination: RulesView()) {
                    Label("HTBAH-Kurzregeln", systemImage: "dice")
                }
                NavigationLink(destination: AudioCheckView()) {
                    Label("Audio-Check", systemImage: "waveform")
                }
            }
        }
        .scrollContentBackground(.hidden)
        .background(FrostTheme.ink)
        .navigationTitle("Materialien")
        .navigationBarTitleDisplayMode(.inline)
        .tint(FrostTheme.cobalt)
    }
}

struct HandoutPreviewView: View {
    let handoutID: String
    @EnvironmentObject private var content: ContentStore

    var body: some View {
        ScrollView {
            if let handout = content.handout(for: handoutID) {
                VStack(alignment: .leading, spacing: 16) {
                    FrostCard {
                        VStack(alignment: .leading, spacing: 9) {
                            HStack {
                                Text(handout.id)
                                    .font(.caption.monospaced().weight(.bold))
                                    .foregroundStyle(FrostTheme.cobalt)
                                Spacer()
                                Text(handout.spoiler ? "SL-SPOILER" : "SPIELERHANDOUT")
                                    .font(.caption.weight(.bold))
                                    .foregroundStyle(handout.spoiler ? FrostTheme.warning : FrostTheme.frost)
                            }
                            Text(handout.title)
                                .font(.title2.weight(.bold))
                                .foregroundStyle(FrostTheme.frost)
                            Text(handout.format)
                                .font(.subheadline)
                                .foregroundStyle(FrostTheme.quiet)
                        }
                    }
                    if let asset = handout.asset {
                        FrostCard {
                            VStack(alignment: .leading, spacing: 6) {
                                Label("Druckstück im Paket", systemImage: "printer")
                                    .font(.caption.weight(.semibold))
                                    .foregroundStyle(FrostTheme.cobalt)
                                Text(asset)
                                    .font(.caption.monospaced())
                                    .foregroundStyle(FrostTheme.quiet)
                                Text("Wenn du das Papierstück gerade nicht zur Hand hast, nutze den darunterstehenden Fallback. Die App behauptet nicht, eine fehlende PDF-Datei öffnen zu können.")
                                    .font(.caption)
                                    .foregroundStyle(FrostTheme.quiet)
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                        }
                    }
                    if let clue = content.manifest.clues.first(where: { $0.handoutId == handout.id }) {
                        FrostCard {
                            VStack(alignment: .leading, spacing: 8) {
                                SectionLabel(title: "Was die Spieler daraus erfahren")
                                Text(clue.title)
                                    .font(.headline)
                                    .foregroundStyle(.white)
                                Text(clue.details)
                                    .font(.body)
                                    .foregroundStyle(FrostTheme.quiet)
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                        }
                    }
                    FrostCard {
                        VStack(alignment: .leading, spacing: 8) {
                            SectionLabel(title: "Papier-Fallback")
                            Text(handout.fallback)
                                .font(.body)
                                .foregroundStyle(.white.opacity(0.9))
                                .fixedSize(horizontal: false, vertical: true)
                            Text("Wenn das gedruckte Stück fehlt, beschreibe genau diese Information – nicht mehr.")
                                .font(.caption)
                                .foregroundStyle(FrostTheme.warning)
                        }
                    }
                }
                .padding(20)
            }
        }
        .background(FrostTheme.ink.ignoresSafeArea())
        .navigationTitle(handoutID)
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct NPCDossierView: View {
    let npcID: String
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var session: SessionStore
    @State private var showSpoilers = false

    var body: some View {
        ScrollView {
            if let npc = content.manifest.npcs.first(where: { $0.id == npcID }) {
                VStack(alignment: .leading, spacing: 16) {
                    FrostCard {
                        VStack(alignment: .leading, spacing: 7) {
                            SectionLabel(title: "NPC-DOSSIER")
                            Text(npc.name)
                                .font(.title2.weight(.bold))
                                .foregroundStyle(FrostTheme.frost)
                            Text(npc.role)
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(FrostTheme.cobalt)
                            Text(npc.description)
                                .font(.body)
                                .foregroundStyle(.white.opacity(0.9))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                    FrostCard {
                        VStack(alignment: .leading, spacing: 8) {
                            SectionLabel(title: "Am Tisch")
                            Text(npc.prompts.first ?? "Lass die Figur auf die Fragen der Gruppe reagieren.")
                                .font(.body)
                                .foregroundStyle(.white.opacity(0.9))
                                .fixedSize(horizontal: false, vertical: true)
                            Picker("Haltung", selection: Binding(get: { session.npcStates[npc.id, default: 0] }, set: { session.setNPCState(npc.id, state: $0) })) {
                                ForEach(Array(npc.states.enumerated()), id: \.offset) { index, state in
                                    Text(state.capitalized).tag(index)
                                }
                            }
                            .pickerStyle(.segmented)
                        }
                    }
                    DisclosureGroup(isExpanded: $showSpoilers) {
                        VStack(alignment: .leading, spacing: 10) {
                            dossierList(title: "Weiß", items: npc.knows, icon: "checkmark.seal")
                            dossierList(title: "Verschweigt", items: npc.hides, icon: "lock")
                            if !npc.givesHandoutIds.isEmpty {
                                Label("Kann bei passenden Fragen verknüpfen: \(npc.givesHandoutIds.joined(separator: ", "))", systemImage: "doc.badge.plus")
                                    .font(.caption)
                                    .foregroundStyle(FrostTheme.cobalt)
                            }
                        }
                        .padding(.top, 10)
                    } label: {
                        HStack {
                            SectionLabel(title: "SL-Information")
                            Spacer()
                            Text(showSpoilers ? "offen" : "geschlossen")
                                .font(.caption.weight(.semibold))
                                .foregroundStyle(FrostTheme.warning)
                        }
                    }
                    .tint(FrostTheme.frost)
                    .padding(16)
                    .background(FrostTheme.panel, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                }
                .padding(20)
            }
        }
        .background(FrostTheme.ink.ignoresSafeArea())
        .navigationTitle("NPC")
        .navigationBarTitleDisplayMode(.inline)
    }

    private func dossierList(title: String, items: [String], icon: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title.uppercased())
                .font(.caption.weight(.bold))
                .foregroundStyle(FrostTheme.quiet)
            ForEach(items, id: \.self) { item in
                Label(item, systemImage: icon)
                    .font(.caption)
                    .foregroundStyle(.white.opacity(0.85))
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }
}
