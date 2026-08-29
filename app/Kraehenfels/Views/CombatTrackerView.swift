import SwiftUI

/// A persistent, table-friendly tracker for the optional S07 combat path.
/// The tracker deliberately records values instead of trying to automate the
/// HTBAH rules: the GM still decides what happens, while the app keeps the
/// order, LP, ammunition, geistesblitze and outcome visible.
struct CombatTrackerView: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var session: SessionStore
    @Environment(\.dismiss) private var dismiss
    @State private var logEntry = ""

    private var combat: CombatState? { session.combatState }
    private var config: CombatConfig? { content.manifest.guide.combat }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    header
                    if let combat {
                        turnBar(combat)
                        participantList(combat)
                        combatLog(combat)
                        outcomePanel(combat)
                    } else {
                        FrostCard {
                            Label("Kampf noch nicht gestartet", systemImage: "shield.slash")
                                .foregroundStyle(FrostTheme.warning)
                            Text("Schließe diese Ansicht und öffne den Tracker erneut aus dem Schritt „Optional: Kampf am Tisch“.")
                                .font(.caption)
                                .foregroundStyle(FrostTheme.quiet)
                        }
                    }
                    rules
                }
                .padding(20)
                .safeAreaPadding(.bottom, 24)
            }
            .background(FrostTheme.ink.ignoresSafeArea())
            .navigationTitle("Kampf-Tracker")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Zurück") { dismiss() }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Fertig") { dismiss() }
                }
            }
        }
        .preferredColorScheme(.dark)
    }

    private var header: some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 8) {
                HStack(alignment: .firstTextBaseline) {
                    SectionLabel(title: "OPTIONALER KAMPF")
                    Spacer()
                    Text(combat.map { "Runde \($0.round)" } ?? "Bereit")
                        .font(.caption.monospaced().weight(.bold))
                        .foregroundStyle(FrostTheme.cobalt)
                }
                Text(config?.enemy.name ?? "Knochenhirsch")
                    .font(.title2.weight(.bold))
                    .foregroundStyle(FrostTheme.frost)
                if let enemy = config?.enemy {
                    Text("\(enemy.maxLP) LP · Initiative \(enemy.initiative) · Angriff \(enemy.attackSkill) · Schaden \(enemy.damageDice) · \(enemy.parryable ? "parierbar" : "nicht parierbar")")
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(FrostTheme.warning)
                    Text(enemy.notes)
                        .font(.caption)
                        .foregroundStyle(FrostTheme.quiet)
                        .fixedSize(horizontal: false, vertical: true)
                }
                Text("Die App hält den Tischzustand fest. Würfe, Schaden und erzählte Folgen entscheidest du nach den Kurzregeln.")
                    .font(.caption)
                    .foregroundStyle(.white.opacity(0.84))
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    private func turnBar(_ combat: CombatState) -> some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    Label("Zugsteuerung", systemImage: "arrow.triangle.2.circlepath")
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(FrostTheme.frost)
                    Spacer()
                    Text("Runde \(combat.round)")
                        .font(.caption.monospaced().weight(.bold))
                        .foregroundStyle(FrostTheme.cobalt)
                }
                if let current = combat.currentParticipant {
                    HStack(alignment: .firstTextBaseline, spacing: 8) {
                        Image(systemName: current.kind == .enemy ? "pawprint.fill" : "person.fill")
                            .foregroundStyle(current.kind == .enemy ? FrostTheme.warning : FrostTheme.cobalt)
                        Text("Am Zug: \(current.name)")
                            .font(.headline)
                            .foregroundStyle(.white)
                        if current.hasActed {
                            Text("hat gehandelt")
                                .font(.caption)
                                .foregroundStyle(FrostTheme.quiet)
                        }
                    }
                }
                HStack(spacing: 8) {
                    Button {
                        session.sortCombatByInitiative()
                    } label: {
                        Label("Initiative sortieren", systemImage: "arrow.up.arrow.down")
                    }
                    .buttonStyle(.bordered)
                    .tint(FrostTheme.cobalt)
                    Button {
                        session.nextCombatTurn()
                    } label: {
                        Label("Nächster Zug", systemImage: "arrow.right")
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(FrostTheme.accent)
                    .disabled(!combat.isActive)
                }
            }
        }
    }

    private func participantList(_ combat: CombatState) -> some View {
        VStack(alignment: .leading, spacing: 9) {
            SectionLabel(title: "Teilnehmer")
            ForEach(combat.participants) { participant in
                participantCard(participant, isCurrent: combat.currentParticipant?.id == participant.id)
            }
        }
    }

    private func participantCard(_ participant: CombatParticipant, isCurrent: Bool) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .firstTextBaseline) {
                Image(systemName: participant.kind == .enemy ? "pawprint.fill" : "person.crop.circle.fill")
                    .foregroundStyle(participant.kind == .enemy ? FrostTheme.warning : FrostTheme.cobalt)
                Text(participant.name)
                    .font(.headline)
                    .foregroundStyle(.white)
                if isCurrent {
                    Text("AM ZUG")
                        .font(.caption2.monospaced().weight(.bold))
                        .foregroundStyle(FrostTheme.accent)
                }
                Spacer()
                Text(participant.statusLabel.capitalized)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(participant.isDefeated ? FrostTheme.warning : FrostTheme.quiet)
            }

            HStack(spacing: 8) {
                TextField("Name", text: Binding(
                    get: { participant.name },
                    set: { session.setCombatParticipantName(participant.id, value: $0) }
                ))
                .textFieldStyle(.roundedBorder)
                .frame(maxWidth: 220)
                Text("LP")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(FrostTheme.quiet)
                TextField("LP", value: Binding(
                    get: { participant.currentLP },
                    set: { session.setCombatLP(participant.id, value: $0) }
                ), format: .number)
                .textFieldStyle(.roundedBorder)
                .keyboardType(.numberPad)
                .frame(width: 68)
                Stepper(value: Binding(
                    get: { participant.currentLP },
                    set: { session.setCombatLP(participant.id, value: $0) }
                ), in: 0...participant.maxLP) {
                    EmptyView()
                }
                .labelsHidden()
            }

            HStack(spacing: 12) {
                compactStepper("Initiative", value: participant.initiative, range: 0...30, symbol: "bolt") {
                    session.setCombatInitiative(participant.id, value: $0)
                }
                compactStepper("Geistesblitze", value: participant.geistesblitze, range: 0...9, symbol: "lightbulb") {
                    session.setCombatGeistesblitze(participant.id, value: $0)
                }
                if participant.kind == .player {
                    compactStepper("Patronen", value: participant.ammunition, range: 0...12, symbol: "circle.grid.3x3") {
                        session.setCombatAmmunition(participant.id, value: $0)
                    }
                }
            }

            HStack(spacing: 8) {
                Button {
                    session.logCombat("\(participant.name) greift an · \(participant.attackSkill) · Schaden \(participant.damageDice)")
                } label: {
                    Label("Angriff notieren", systemImage: "scope")
                }
                .buttonStyle(.bordered)
                .tint(participant.kind == .enemy ? FrostTheme.warning : FrostTheme.cobalt)
                if participant.parryable {
                    Button {
                        session.logCombat("\(participant.name) pariert mit Handeln.")
                    } label: {
                        Label("Parade", systemImage: "shield")
                    }
                    .buttonStyle(.bordered)
                    .tint(FrostTheme.cobalt)
                }
                if participant.kind == .player, participant.ammunition > 0 {
                    Button {
                        if session.useCombatAmmunition(participant.id) {
                            session.logCombat("\(participant.name) verwendet eine Revolverpatrone.")
                        }
                    } label: {
                        Label("Schuss", systemImage: "flame")
                    }
                    .buttonStyle(.bordered)
                    .tint(FrostTheme.warning)
                }
            }
            .font(.caption.weight(.semibold))
        }
        .padding(12)
        .background((isCurrent ? FrostTheme.cobalt.opacity(0.16) : FrostTheme.ink.opacity(0.38)), in: RoundedRectangle(cornerRadius: 13, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 13, style: .continuous).stroke(isCurrent ? FrostTheme.cobalt.opacity(0.6) : FrostTheme.line, lineWidth: 1))
    }

    private func compactStepper(_ title: String, value: Int, range: ClosedRange<Int>, symbol: String, set: @escaping (Int) -> Void) -> some View {
        Stepper(value: Binding(get: { value }, set: set), in: range) {
            Label {
                VStack(alignment: .leading, spacing: 1) {
                    Text(title)
                        .font(.caption2.weight(.semibold))
                    Text("\(value)")
                        .font(.caption.monospaced())
                        .foregroundStyle(FrostTheme.frost)
                }
            } icon: {
                Image(systemName: symbol)
                    .foregroundStyle(FrostTheme.cobalt)
            }
        }
        .font(.caption)
        .frame(maxWidth: .infinity, minHeight: 44, alignment: .leading)
    }

    private func combatLog(_ combat: CombatState) -> some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 9) {
                HStack {
                    SectionLabel(title: "Kampflog")
                    Spacer()
                    Text("\(combat.log.count) Einträge")
                        .font(.caption.monospaced())
                        .foregroundStyle(FrostTheme.quiet)
                }
                HStack(spacing: 8) {
                    TextField("Ereignis notieren …", text: $logEntry)
                        .textFieldStyle(.roundedBorder)
                    Button("Eintragen") {
                        let message = logEntry.trimmingCharacters(in: .whitespacesAndNewlines)
                        guard !message.isEmpty else { return }
                        session.logCombat(message)
                        logEntry = ""
                    }
                    .buttonStyle(.bordered)
                    .tint(FrostTheme.cobalt)
                }
                ForEach(Array(combat.log.suffix(12).reversed().enumerated()), id: \.offset) { _, entry in
                    Text(entry)
                        .font(.caption)
                        .foregroundStyle(.white.opacity(0.86))
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
        }
    }

    @ViewBuilder
    private func outcomePanel(_ combat: CombatState) -> some View {
        if let outcome = combat.outcome {
            FrostCard {
                VStack(alignment: .leading, spacing: 8) {
                    Label(outcome == "victory" ? "Sieg bestätigt" : "Niederlage bestätigt", systemImage: outcome == "victory" ? "checkmark.seal.fill" : "xmark.seal.fill")
                        .font(.headline.weight(.bold))
                        .foregroundStyle(outcome == "victory" ? FrostTheme.accent : FrostTheme.warning)
                    if let endingID = combat.endingID,
                       let text = config?.victoryByEnding[endingID] {
                        Text(text)
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(FrostTheme.frost)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    Text("Schließe den Tracker und bestätige danach im Guided Flow den Schritt „Zum Nachhall weiter“.")
                        .font(.caption)
                        .foregroundStyle(FrostTheme.quiet)
                }
            }
        } else {
            HStack(spacing: 10) {
                Button {
                    session.finishCombat(outcome: "victory")
                } label: {
                    Label("Sieg bestätigen", systemImage: "checkmark.circle.fill")
                        .frame(maxWidth: .infinity, minHeight: 48)
                }
                .buttonStyle(.borderedProminent)
                .tint(FrostTheme.accent)
                Button {
                    session.finishCombat(outcome: "defeat")
                } label: {
                    Label("Niederlage", systemImage: "xmark.circle")
                        .frame(maxWidth: .infinity, minHeight: 48)
                }
                .buttonStyle(.bordered)
                .tint(FrostTheme.warning)
            }
        }
    }

    private var rules: some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 6) {
                SectionLabel(title: "Kurzregeln")
                Text("Initiative: 1W10 + Handeln. Angriff: passende W100-Probe. Parade einmal pro Runde; Schusswaffen und kritische Angriffe sind nicht parierbar. Schaden mit den Waffenwürfeln auswürfeln und von den LP abziehen. Unter 10 LP bewusstlos, bei 0 LP ausgeschaltet.")
                    .font(.caption)
                    .foregroundStyle(FrostTheme.quiet)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }
}
