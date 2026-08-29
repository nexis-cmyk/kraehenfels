import SwiftUI

struct CaseFileView: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var session: SessionStore
    @State private var showSpoilers = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                intro
                players
                facts
                clueChain
                maps
                endings
            }
            .padding(20)
        }
        .background(FrostTheme.ink.ignoresSafeArea())
        .navigationTitle("Akte")
        .navigationBarTitleDisplayMode(.inline)
    }

    private var intro: some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 8) {
                SectionLabel(title: "Die letzte Kutsche")
                Text("Der Fall bleibt offen, bis du ihn am Tisch schließt.")
                    .font(.title3.weight(.semibold))
                    .foregroundStyle(FrostTheme.frost)
                Text("Markiere nur, was die Gruppe wirklich herausgefunden hat. Die Empfehlungen verändern keine Szene automatisch.")
                    .font(.subheadline)
                    .foregroundStyle(FrostTheme.quiet)
            }
        }
    }

    private var players: some View {
        VStack(alignment: .leading, spacing: 10) {
            SectionLabel(title: "Eigene Figuren")
            Text("Die drei Figuren bringen ihre eigenen Werte, Berufe und Geschichten mit. Die Akte speichert hier nur die Namen.")
                .font(.caption)
                .foregroundStyle(FrostTheme.quiet)
                .fixedSize(horizontal: false, vertical: true)
            ForEach(0..<3, id: \.self) { index in
                HStack(spacing: 10) {
                    Image(systemName: "person.fill")
                        .foregroundStyle(FrostTheme.cobalt)
                    Text(playerName(at: index))
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(.white)
                    Spacer()
                }
                .frame(minHeight: 44)
            }
        }
        .padding(13)
        .background(FrostTheme.panel, in: RoundedRectangle(cornerRadius: 13, style: .continuous))
    }

    private func playerName(at index: Int) -> String {
        guard session.playerNames.indices.contains(index) else { return "Figur \(index + 1)" }
        let name = session.playerNames[index].trimmingCharacters(in: .whitespacesAndNewlines)
        return name.isEmpty ? "Figur \(index + 1)" : name
    }

    private var facts: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                SectionLabel(title: "Schlussfolgerungen")
                Spacer()
                Text("\(completedFacts.count)/\(content.manifest.facts.count)")
                    .font(.caption.monospaced().weight(.bold))
                    .foregroundStyle(FrostTheme.cobalt)
            }
            ForEach(content.manifest.facts) { fact in
                let found = completedFacts.contains(fact.id)
                HStack(alignment: .top, spacing: 11) {
                    Image(systemName: found ? "checkmark.seal.fill" : "circle.dotted")
                        .foregroundStyle(found ? FrostTheme.cobalt : FrostTheme.quiet)
                    VStack(alignment: .leading, spacing: 4) {
                        Text(fact.title)
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(.white)
                        Text(found ? fact.details : "Noch nicht bestätigt")
                            .font(.caption)
                            .foregroundStyle(found ? FrostTheme.quiet : FrostTheme.quiet.opacity(0.7))
                    }
                    Spacer()
                }
                .padding(13)
                .background(FrostTheme.panel, in: RoundedRectangle(cornerRadius: 13, style: .continuous))
            }
        }
    }

    private var maps: some View {
        VStack(alignment: .leading, spacing: 10) {
            SectionLabel(title: "Karten")
            ForEach(content.manifest.maps) { map in
                NavigationLink(destination: MapDetailView(map: map, showSpoilers: showSpoilers)) {
                    HStack(spacing: 12) {
                        Image(systemName: "map.fill")
                            .foregroundStyle(FrostTheme.cobalt)
                            .frame(width: 28)
                        VStack(alignment: .leading, spacing: 3) {
                            Text(map.title)
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(.white)
                            Text("Spielerkarte und SL-Overlay")
                                .font(.caption)
                                .foregroundStyle(FrostTheme.quiet)
                        }
                        Spacer()
                        Image(systemName: "chevron.right")
                            .foregroundStyle(FrostTheme.quiet)
                    }
                    .padding(.vertical, 6)
                }
                .buttonStyle(.plain)
            }
        }
    }

    private var endings: some View {
        DisclosureGroup(isExpanded: $showSpoilers) {
            VStack(alignment: .leading, spacing: 12) {
                ForEach(content.manifest.endings) { ending in
                    VStack(alignment: .leading, spacing: 4) {
                        Text(ending.title)
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(.white)
                        Text(ending.summary)
                            .font(.caption)
                            .foregroundStyle(FrostTheme.quiet)
                        Text("Preis: \(ending.cost)")
                            .font(.caption)
                            .foregroundStyle(FrostTheme.warning)
                    }
                }
            }
            .padding(.top, 10)
        } label: {
            HStack {
                SectionLabel(title: "Finale und Spoiler")
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

    private var completedFacts: Set<String> {
        Set(content.completedFacts(for: session.checkedClueIDs).map(\.id))
    }

    private var clueChain: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                SectionLabel(title: "Hinweiskette")
                Spacer()
                Text("\(session.checkedClueIDs.intersection(Set(content.manifest.clues.map(\.id))).count)/\(content.manifest.clues.count)")
                    .font(.caption.monospaced().weight(.bold))
                    .foregroundStyle(FrostTheme.cobalt)
            }
            Text("Jeder Hinweis bleibt einzeln auffindbar. Öffne den Eintrag für Fundort, Handout und die Schlussfolgerung, zu der er beiträgt.")
                .font(.caption)
                .foregroundStyle(FrostTheme.quiet)
                .fixedSize(horizontal: false, vertical: true)
            ForEach(content.manifest.clues) { clue in
                NavigationLink(destination: ClueDetailView(clueID: clue.id)) {
                    HStack(alignment: .top, spacing: 10) {
                        Image(systemName: session.checkedClueIDs.contains(clue.id) ? "checkmark.circle.fill" : "circle")
                            .foregroundStyle(session.checkedClueIDs.contains(clue.id) ? FrostTheme.accent : FrostTheme.quiet)
                        VStack(alignment: .leading, spacing: 3) {
                            Text("\(clue.id) · \(clue.title)")
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(.white)
                            Text(clue.details)
                                .font(.caption)
                                .foregroundStyle(FrostTheme.quiet)
                                .fixedSize(horizontal: false, vertical: true)
                            Text("Fundort: \(locationTitle(for: clue.locationId)) · \(clue.handoutId ?? "kein Handout")")
                                .font(.caption2)
                                .foregroundStyle(FrostTheme.cobalt)
                        }
                        Spacer(minLength: 0)
                        Image(systemName: "chevron.right")
                            .font(.caption.weight(.bold))
                            .foregroundStyle(FrostTheme.quiet)
                    }
                    .padding(12)
                    .background(FrostTheme.panel, in: RoundedRectangle(cornerRadius: 13, style: .continuous))
                }
                .buttonStyle(.plain)
            }
        }
    }

    private func locationTitle(for id: String?) -> String {
        guard let id else { return "unbekannt" }
        return content.manifest.locations.first(where: { $0.id == id })?.title ?? id
    }
}

struct ClueDetailView: View {
    let clueID: String
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var session: SessionStore
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ScrollView {
            if let clue = content.manifest.clues.first(where: { $0.id == clueID }) {
                VStack(alignment: .leading, spacing: 16) {
                    FrostCard {
                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                SectionLabel(title: "HINWEIS")
                                Spacer()
                                Text(clue.required ? "PFLICHT" : "OPTIONAL")
                                    .font(.caption2.weight(.bold))
                                    .foregroundStyle(clue.required ? FrostTheme.warning : FrostTheme.cobalt)
                            }
                            Text("\(clue.id) · \(clue.title)")
                                .font(.title2.weight(.bold))
                                .foregroundStyle(FrostTheme.frost)
                            Text(clue.details)
                                .font(.body)
                                .foregroundStyle(.white.opacity(0.92))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                    FrostCard {
                        VStack(alignment: .leading, spacing: 8) {
                            Label(session.checkedClueIDs.contains(clue.id) ? "In der Akte bestätigt" : "Noch nicht bestätigt", systemImage: session.checkedClueIDs.contains(clue.id) ? "checkmark.circle.fill" : "circle")
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(session.checkedClueIDs.contains(clue.id) ? FrostTheme.accent : FrostTheme.quiet)
                            Button(session.checkedClueIDs.contains(clue.id) ? "Als offen markieren" : "Als gefunden markieren") {
                                session.toggleClue(clue.id)
                            }
                            .buttonStyle(.borderedProminent)
                            .tint(FrostTheme.accent)
                            if let locationID = clue.locationId {
                                Label("Fundort: \(locationTitle(for: locationID))", systemImage: "location.fill")
                                    .font(.caption)
                                    .foregroundStyle(FrostTheme.quiet)
                            }
                            let linkedHandouts = content.manifest.handouts.filter { handout in
                                handout.linkedClueIds.contains(clue.id)
                            }
                            if !linkedHandouts.isEmpty {
                                VStack(alignment: .leading, spacing: 8) {
                                    SectionLabel(title: "Verknüpfte Handouts")
                                    ForEach(linkedHandouts) { handout in
                                        NavigationLink(destination: HandoutPreviewView(handoutID: handout.id)) {
                                            HStack {
                                                Label("\(handout.id) · \(handout.title)", systemImage: "doc.text")
                                                Spacer()
                                                if handout.id == clue.handoutId {
                                                    Text("primär")
                                                        .font(.caption2.weight(.semibold))
                                                        .foregroundStyle(FrostTheme.cobalt)
                                                } else {
                                                    Text("Zusatzbeleg")
                                                        .font(.caption2.weight(.semibold))
                                                        .foregroundStyle(FrostTheme.quiet)
                                                }
                                            }
                                        }
                                        .buttonStyle(.bordered)
                                    }
                                }
                            }
                            if let factID = clue.factId,
                               let fact = content.manifest.facts.first(where: { $0.id == factID }) {
                                Label("Trägt zu \(fact.id) · \(fact.title) bei", systemImage: "link")
                                    .font(.caption)
                                    .foregroundStyle(FrostTheme.cobalt)
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                        }
                    }
                }
                .padding(20)
            } else {
                Text("Dieser Hinweis ist im aktuellen Inhalt nicht vorhanden.")
                    .foregroundStyle(FrostTheme.warning)
                    .padding(20)
            }
        }
        .background(FrostTheme.ink.ignoresSafeArea())
        .navigationTitle(clueID)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarLeading) {
                Button("Zurück", systemImage: "chevron.left") { dismiss() }
            }
        }
    }

    private func locationTitle(for id: String) -> String {
        content.manifest.locations.first(where: { $0.id == id })?.title ?? id
    }
}

struct MapDetailView: View {
    let map: MapEntry
    let showSpoilers: Bool
    @Environment(\.dismiss) private var dismiss
    @State private var gmOverlay = false

    var body: some View {
        ScrollView([.vertical, .horizontal], showsIndicators: false) {
            VStack(alignment: .leading, spacing: 14) {
                SceneArtView(
                    resourceName: gmOverlay ? map.gmAsset : map.playerAsset,
                    height: 330,
                    shareLabel: gmOverlay ? "SL-Karte teilen / sichern" : "Spielerkarte teilen / sichern"
                )
                    .frame(minWidth: 560)
                Toggle("SL-Overlay", isOn: $gmOverlay)
                    .toggleStyle(.switch)
                    .tint(FrostTheme.cobalt)
                    .disabled(!showSpoilers)
                    .foregroundStyle(FrostTheme.frost)
                if !showSpoilers {
                    Text("Spoiler-Schalter in der Akte öffnen, um die SL-Karte zu sehen.")
                        .font(.caption)
                        .foregroundStyle(FrostTheme.quiet)
                }
            }
            .padding(20)
        }
        .background(FrostTheme.ink.ignoresSafeArea())
        .navigationTitle(map.title)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarLeading) {
                Button("Zurück", systemImage: "chevron.left") { dismiss() }
            }
        }
    }
}
