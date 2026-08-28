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
}

struct MapDetailView: View {
    let map: MapEntry
    let showSpoilers: Bool
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
    }
}
