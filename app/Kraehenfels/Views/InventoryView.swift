import SwiftUI

struct InventoryView: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var session: SessionStore

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                FrostCard {
                    VStack(alignment: .leading, spacing: 8) {
                        SectionLabel(title: "GEMEINSAME AUSRÜSTUNG")
                        Text("Sechs Funde aus der Kutsche")
                            .font(.title2.weight(.bold))
                            .foregroundStyle(FrostTheme.frost)
                        Text("Die Gegenstände gehören der Gruppe. Ihr könnt sie jederzeit weitergeben. Verbrauch wird erst nach einer bestätigten Verwendung abgezogen.")
                            .font(.subheadline)
                            .foregroundStyle(FrostTheme.quiet)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }

                playerSummary

                if content.guideItems.isEmpty {
                    FrostCard {
                        Label("Keine Gegenstände geladen", systemImage: "shippingbox")
                            .foregroundStyle(FrostTheme.warning)
                    }
                } else {
                    SectionLabel(title: "GEGENSTÄNDE UND BESITZ")
                    ForEach(content.guideItems) { item in
                        itemCard(item)
                    }
                }
            }
            .padding(20)
            .safeAreaPadding(.bottom, 24)
        }
        .background(FrostTheme.ink.ignoresSafeArea())
        .navigationTitle("Ausrüstung")
        .navigationBarTitleDisplayMode(.inline)
    }

    private var playerSummary: some View {
        VStack(alignment: .leading, spacing: 9) {
            HStack {
                SectionLabel(title: "VERTEILUNG")
                Spacer()
                Text(session.isItemDistributionComplete(for: content.guideItems.map(\.id)) ? "vollständig" : "offen")
                    .font(.caption.weight(.bold))
                    .foregroundStyle(session.isItemDistributionComplete(for: content.guideItems.map(\.id)) ? FrostTheme.accent : FrostTheme.warning)
            }
            ForEach(0..<3, id: \.self) { index in
                HStack(spacing: 10) {
                    Image(systemName: "person.fill")
                        .foregroundStyle(FrostTheme.cobalt)
                        .frame(width: 22)
                    Text(playerName(at: index))
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(.white)
                    Spacer()
                    Text("\(session.items(forPlayerAt: index, from: content.guideItems).count) Gegenstände")
                        .font(.caption)
                        .foregroundStyle(FrostTheme.quiet)
                }
                .frame(minHeight: 44)
            }
            if !session.isItemDistributionComplete(for: content.guideItems.map(\.id)) {
                Text("Für den Start braucht jede der drei Figuren mindestens einen Gegenstand.")
                    .font(.caption)
                    .foregroundStyle(FrostTheme.warning)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(14)
        .background(FrostTheme.panel, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
    }

    private func itemCard(_ item: AdventureItem) -> some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 8) {
                HStack(alignment: .firstTextBaseline, spacing: 8) {
                    Image(systemName: item.weapon == nil ? "shippingbox.fill" : "scope")
                        .foregroundStyle(item.weapon == nil ? FrostTheme.cobalt : FrostTheme.warning)
                    Text(item.title)
                        .font(.headline)
                        .foregroundStyle(.white)
                    Spacer(minLength: 4)
                    Text("\(session.remainingUses(for: item))/\(item.initialUses)")
                        .font(.caption.monospaced().weight(.bold))
                        .foregroundStyle(session.remainingUses(for: item) > 0 ? FrostTheme.accent : FrostTheme.warning)
                }
                Text(item.detail)
                    .font(.caption)
                    .foregroundStyle(FrostTheme.quiet)
                    .fixedSize(horizontal: false, vertical: true)
                Text("Fundort: \(locationTitle(for: item.locationID))")
                    .font(.caption2.weight(.semibold))
                    .foregroundStyle(FrostTheme.cobalt)
                if let weapon = item.weapon {
                    Text("\(weapon.skill) · Schaden \(weapon.damageDice) · nicht parierbar")
                        .font(.caption2.monospaced())
                        .foregroundStyle(FrostTheme.warning)
                        .fixedSize(horizontal: false, vertical: true)
                }
                if !item.effects.isEmpty {
                    VStack(alignment: .leading, spacing: 4) {
                        ForEach(item.effects) { effect in
                            Text("• \(effect.title): \(effect.detail)")
                                .font(.caption2)
                                .foregroundStyle(FrostTheme.frost.opacity(0.84))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                }
                ownerMenu(for: item)
            }
        }
    }

    private func ownerMenu(for item: AdventureItem) -> some View {
        Menu {
            Button("Gemeinsamer Vorrat", systemImage: "person.3") {
                session.unassignItem(item.id)
            }
            ForEach(0..<3, id: \.self) { index in
                Button(playerName(at: index), systemImage: session.ownerIndex(for: item.id) == index ? "checkmark" : "person.fill") {
                    session.transferItem(item.id, toPlayerAt: index)
                }
            }
        } label: {
            HStack {
                Label("Besitz: \(ownerName(for: item))", systemImage: "arrow.left.arrow.right")
                    .font(.subheadline.weight(.semibold))
                Spacer()
                Image(systemName: "chevron.up.chevron.down")
            }
            .foregroundStyle(FrostTheme.frost)
            .frame(maxWidth: .infinity, minHeight: 44, alignment: .leading)
            .padding(.horizontal, 11)
            .background(FrostTheme.ink.opacity(0.42), in: RoundedRectangle(cornerRadius: 10, style: .continuous))
        }
        .tint(FrostTheme.cobalt)
    }

    private func playerName(at index: Int) -> String {
        guard session.playerNames.indices.contains(index) else { return "Figur \(index + 1)" }
        let name = session.playerNames[index].trimmingCharacters(in: .whitespacesAndNewlines)
        return name.isEmpty ? "Figur \(index + 1)" : name
    }

    private func ownerName(for item: AdventureItem) -> String {
        guard let index = session.ownerIndex(for: item.id) else { return "Gemeinsamer Vorrat" }
        return playerName(at: index)
    }

    private func locationTitle(for locationID: String) -> String {
        content.itemFindLocations.first(where: { $0.id == locationID })?.title ?? locationID
    }
}

struct ItemFindingsPanel: View {
    let locations: [ItemFindLocation]
    let items: [AdventureItem]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            SectionLabel(title: "DREI FUNDORTE · KEINE PROBE")
            Text("Alle sechs Gegenstände werden gefunden.")
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(FrostTheme.frost)
            ForEach(locations) { location in
                VStack(alignment: .leading, spacing: 6) {
                    Text(location.title)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(.white)
                    Text(location.detail)
                        .font(.caption)
                        .foregroundStyle(FrostTheme.quiet)
                        .fixedSize(horizontal: false, vertical: true)
                    ForEach(location.itemIDs, id: \.self) { itemID in
                        if let item = items.first(where: { $0.id == itemID }) {
                            Label(item.title, systemImage: item.weapon == nil ? "shippingbox" : "scope")
                                .font(.caption.weight(.semibold))
                                .foregroundStyle(item.weapon == nil ? FrostTheme.cobalt : FrostTheme.warning)
                        }
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(11)
                .background(FrostTheme.ink.opacity(0.42), in: RoundedRectangle(cornerRadius: 10, style: .continuous))
            }
        }
        .padding(12)
        .background(FrostTheme.ink.opacity(0.35), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
    }
}

struct ItemDistributionPanel: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var session: SessionStore

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                SectionLabel(title: "SECHS GEGENSTÄNDE")
                Spacer()
                Text("\(session.itemOwners.count)/\(content.guideItems.count) verteilt")
                    .font(.caption.monospaced().weight(.bold))
                    .foregroundStyle(FrostTheme.cobalt)
            }
            ForEach(content.guideItems) { item in
                HStack(alignment: .top, spacing: 9) {
                    Image(systemName: session.ownerIndex(for: item.id) == nil ? "circle" : "checkmark.circle.fill")
                        .foregroundStyle(session.ownerIndex(for: item.id) == nil ? FrostTheme.quiet : FrostTheme.accent)
                        .font(.title3)
                    VStack(alignment: .leading, spacing: 3) {
                        Text(item.title)
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(.white)
                        Text(item.detail)
                            .font(.caption)
                            .foregroundStyle(FrostTheme.quiet)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    Spacer(minLength: 4)
                    ownerMenu(for: item)
                }
                .padding(.vertical, 7)
            }
            Label(
                session.isItemDistributionComplete(for: content.guideItems.map(\.id))
                    ? "Alle Figuren haben mindestens einen Gegenstand."
                    : "Verteile alle Gegenstände und gib jeder Figur mindestens einen.",
                systemImage: session.isItemDistributionComplete(for: content.guideItems.map(\.id)) ? "checkmark.seal.fill" : "exclamationmark.triangle.fill"
            )
            .font(.caption.weight(.semibold))
            .foregroundStyle(session.isItemDistributionComplete(for: content.guideItems.map(\.id)) ? FrostTheme.accent : FrostTheme.warning)
            .fixedSize(horizontal: false, vertical: true)
        }
        .padding(12)
        .background(FrostTheme.ink.opacity(0.35), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
    }

    private func ownerMenu(for item: AdventureItem) -> some View {
        Menu {
            Button("Noch nicht verteilt", systemImage: "person.3") {
                session.unassignItem(item.id)
            }
            ForEach(0..<3, id: \.self) { index in
                Button(playerName(at: index), systemImage: session.ownerIndex(for: item.id) == index ? "checkmark" : "person.fill") {
                    session.assignItem(item.id, toPlayerAt: index)
                }
            }
        } label: {
            Text(ownerName(for: item))
                .font(.caption.weight(.semibold))
                .foregroundStyle(FrostTheme.frost)
                .lineLimit(2)
                .frame(minWidth: 92, minHeight: 44)
                .padding(.horizontal, 7)
                .background(FrostTheme.panelRaised, in: RoundedRectangle(cornerRadius: 9, style: .continuous))
        }
        .tint(FrostTheme.cobalt)
    }

    private func playerName(at index: Int) -> String {
        guard session.playerNames.indices.contains(index) else { return "Figur \(index + 1)" }
        let name = session.playerNames[index].trimmingCharacters(in: .whitespacesAndNewlines)
        return name.isEmpty ? "Figur \(index + 1)" : name
    }

    private func ownerName(for item: AdventureItem) -> String {
        guard let index = session.ownerIndex(for: item.id) else { return "Offen" }
        return playerName(at: index)
    }
}
