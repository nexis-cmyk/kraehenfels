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
                NavigationLink(destination: InventoryView()) {
                    Label("Gemeinsame Ausrüstung", systemImage: "shippingbox")
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
            Section("Gegenstandskarten") {
                Text("Diese Karten kannst du einzeln über WhatsApp verschicken oder in Dateien sichern.")
                    .font(.caption)
                    .foregroundStyle(FrostTheme.quiet)
                    .fixedSize(horizontal: false, vertical: true)
                ForEach(content.guideItems) { item in
                    NavigationLink(destination: ItemCardPreviewView(item: item)) {
                        HStack {
                            Image(systemName: item.weapon == nil ? "shippingbox.fill" : "scope")
                                .foregroundStyle(item.weapon == nil ? FrostTheme.cobalt : FrostTheme.warning)
                            VStack(alignment: .leading, spacing: 2) {
                                Text(item.title)
                                    .foregroundStyle(.white)
                                Text("Spielerkarte · \(item.initialUses) \(item.initialUses == 1 ? "Anwendung" : "Anwendungen")")
                                    .font(.caption)
                                    .foregroundStyle(FrostTheme.quiet)
                            }
                        }
                    }
                }
            }
            Section("Endkarten") {
                NavigationLink(destination: EndingCardsPreviewView()) {
                    HStack {
                        Image(systemName: "rectangle.stack.fill")
                            .foregroundStyle(FrostTheme.warning)
                        VStack(alignment: .leading, spacing: 2) {
                            Text("Entscheidungen an der Alten Eiche")
                                .foregroundStyle(.white)
                            Text("Erst im Finale zeigen")
                                .font(.caption)
                                .foregroundStyle(FrostTheme.warning)
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
    @Environment(\.dismiss) private var dismiss

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
                    if let previewAsset = handout.previewAsset {
                        FrostCard {
                            VStack(alignment: .leading, spacing: 10) {
                                HStack {
                                    Label("Spielerbild", systemImage: "photo")
                                        .font(.caption.weight(.semibold))
                                        .foregroundStyle(FrostTheme.cobalt)
                                    Spacer()
                                    Text("PNG")
                                        .font(.caption2.monospaced().weight(.bold))
                                        .foregroundStyle(FrostTheme.quiet)
                                }
                                MaterialImagePreview(
                                    resourceName: previewAsset,
                                    subdirectory: "Materials/Handouts",
                                    maxHeight: 540,
                                    accessibilityLabel: "Vorschau von \(handout.title)"
                                )
                                MaterialShareLink(
                                    resourceName: previewAsset,
                                    subdirectory: "Materials/Handouts",
                                    label: "Bild teilen / sichern"
                                )
                            }
                        }
                    }
                    if let asset = handout.asset {
                        FrostCard {
                            VStack(alignment: .leading, spacing: 6) {
                                Label("Druckdatei im Projekt", systemImage: "printer")
                                    .font(.caption.weight(.semibold))
                                    .foregroundStyle(FrostTheme.cobalt)
                                Text(asset)
                                    .font(.caption.monospaced())
                                    .foregroundStyle(FrostTheme.quiet)
                                Text("Die PNG-Vorschau oben ist für WhatsApp und zum Sichern gedacht.")
                                    .font(.caption)
                                    .foregroundStyle(FrostTheme.quiet)
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                        }
                    }
                    if !handout.linkedClueIds.isEmpty {
                        FrostCard {
                            VStack(alignment: .leading, spacing: 8) {
                                SectionLabel(title: "Verknüpfte Hinweise")
                                Text("Diese Einträge zeigen, welche Spur das Handout stützt.")
                                    .font(.caption)
                                    .foregroundStyle(FrostTheme.quiet)
                                    .fixedSize(horizontal: false, vertical: true)
                                ForEach(handout.linkedClueIds, id: \.self) { clueID in
                                    if let clue = content.manifest.clues.first(where: { $0.id == clueID }) {
                                        NavigationLink(destination: ClueDetailView(clueID: clue.id)) {
                                            VStack(alignment: .leading, spacing: 4) {
                                                HStack(alignment: .firstTextBaseline, spacing: 6) {
                                                    Text("\(clue.id) · \(clue.title)")
                                                        .font(.subheadline.weight(.semibold))
                                                        .foregroundStyle(.white)
                                                    if clue.handoutId == handout.id {
                                                        Text("PRIMÄR")
                                                            .font(.system(size: 9, weight: .bold, design: .monospaced))
                                                            .foregroundStyle(FrostTheme.cobalt)
                                                    } else {
                                                        Text("ZUSATZBELEG")
                                                            .font(.system(size: 9, weight: .bold, design: .monospaced))
                                                            .foregroundStyle(FrostTheme.quiet)
                                                    }
                                                }
                                                Text(clue.details)
                                                    .font(.caption)
                                                    .foregroundStyle(FrostTheme.quiet)
                                                    .fixedSize(horizontal: false, vertical: true)
                                            }
                                            .frame(maxWidth: .infinity, alignment: .leading)
                                        }
                                        .buttonStyle(.plain)
                                        if clueID != (handout.linkedClueIds.last ?? "") {
                                            Divider().overlay(FrostTheme.quiet.opacity(0.25))
                                        }
                                    }
                                }
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
        .toolbar {
            ToolbarItem(placement: .topBarLeading) {
                Button("Zurück", systemImage: "chevron.left") { dismiss() }
            }
        }
    }
}

struct ItemCardPreviewView: View {
    let item: AdventureItem
    @EnvironmentObject private var content: ContentStore
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                FrostCard {
                    VStack(alignment: .leading, spacing: 8) {
                        SectionLabel(title: "SPIELERKARTE")
                        Text(item.title)
                            .font(.title2.weight(.bold))
                            .foregroundStyle(FrostTheme.frost)
                        Text("Fundort · \(locationTitle)")
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(item.weapon == nil ? FrostTheme.cobalt : FrostTheme.warning)
                    }
                }
                if let asset = item.playerCardAsset {
                    FrostCard {
                        VStack(alignment: .leading, spacing: 10) {
                            MaterialImagePreview(
                                resourceName: asset,
                                subdirectory: "Materials/Items",
                                maxHeight: 540,
                                accessibilityLabel: "Spielerkarte für \(item.title)"
                            )
                            MaterialShareLink(
                                resourceName: asset,
                                subdirectory: "Materials/Items",
                                label: "Karte teilen / sichern"
                            )
                        }
                    }
                }
                FrostCard {
                    VStack(alignment: .leading, spacing: 8) {
                        SectionLabel(title: "Text für die Spieler")
                        Text(item.playerCardDetail ?? item.detail)
                            .font(.body)
                            .foregroundStyle(.white.opacity(0.9))
                            .fixedSize(horizontal: false, vertical: true)
                        ForEach(item.playerCardUses, id: \.self) { use in
                            Label(use, systemImage: "checkmark.circle")
                                .font(.caption)
                                .foregroundStyle(FrostTheme.quiet)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                }
            }
            .padding(20)
        }
        .background(FrostTheme.ink.ignoresSafeArea())
        .navigationTitle(item.title)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarLeading) {
                Button("Zurück", systemImage: "chevron.left") { dismiss() }
            }
        }
    }

    private var locationTitle: String {
        content.itemFindLocations.first(where: { $0.id == item.locationID })?.title ?? item.locationID
    }
}

struct EndingCardsPreviewView: View {
    @Environment(\.dismiss) private var dismiss
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                FrostCard {
                    VStack(alignment: .leading, spacing: 8) {
                        SectionLabel(title: "FINALE")
                        Text("Entscheidungen an der Alten Eiche")
                            .font(.title2.weight(.bold))
                            .foregroundStyle(FrostTheme.frost)
                        Text("Zeige die drei Karten erst, wenn Gastrecht, Erinnerung und Feuer verstanden wurden.")
                            .font(.subheadline)
                            .foregroundStyle(FrostTheme.quiet)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
                FrostCard {
                    VStack(alignment: .leading, spacing: 10) {
                        MaterialImagePreview(
                            resourceName: "ending-cards.png",
                            subdirectory: "Materials/Endings",
                            maxHeight: 620,
                            accessibilityLabel: "Die drei Endkarten für die Alte Eiche"
                        )
                        MaterialShareLink(
                            resourceName: "ending-cards.png",
                            subdirectory: "Materials/Endings",
                            label: "Karten teilen / sichern"
                        )
                    }
                }
            }
            .padding(20)
        }
        .background(FrostTheme.ink.ignoresSafeArea())
        .navigationTitle("Endkarten")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarLeading) {
                Button("Zurück", systemImage: "chevron.left") { dismiss() }
            }
        }
    }
}

struct NPCDossierView: View {
    let npcID: String
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var session: SessionStore
    @Environment(\.dismiss) private var dismiss
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
                            SectionLabel(title: "Auftrittsfolge")
                            ForEach(npc.appearances) { appearance in
                                VStack(alignment: .leading, spacing: 5) {
                                    Text("\(appearance.sceneId) · \(sceneTitle(for: appearance.sceneId))")
                                        .font(.caption.weight(.bold))
                                        .foregroundStyle(FrostTheme.cobalt)
                                    NPCDirectionView(
                                        npc: npc,
                                        appearance: appearance,
                                        sceneID: appearance.sceneId,
                                        showAllReactions: true,
                                        showAllDirections: true
                                    )
                                }
                                if appearance.id != npc.appearances.last?.id {
                                    Divider().overlay(FrostTheme.quiet.opacity(0.25))
                                }
                            }
                            if npc.appearances.isEmpty {
                                Text(npc.prompts.first ?? "Lass die Figur auf die Fragen der Gruppe reagieren.")
                                    .font(.body)
                                    .foregroundStyle(.white.opacity(0.9))
                                    .fixedSize(horizontal: false, vertical: true)
                            }
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
        .toolbar {
            ToolbarItem(placement: .topBarLeading) {
                Button("Zurück", systemImage: "chevron.left") { dismiss() }
            }
        }
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

    private func sceneTitle(for sceneID: String) -> String {
        content.manifest.scenes.first(where: { $0.id == sceneID })?.shortTitle ?? sceneID
    }
}
