import SwiftUI

/// Compact, dialogue-free direction for one NPC in one scene.
/// The same component is used by the guided flow, scene details and dossiers
/// so the GM never has to translate between three different NPC vocabularies.
struct NPCDirectionView: View {
    let npc: NPCEntry
    let appearance: NPCAppearance
    let sceneID: String
    let focusClueIDs: Set<String>
    let showAllReactions: Bool
    let showAllDirections: Bool

    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var session: SessionStore

    init(
        npc: NPCEntry,
        appearance: NPCAppearance,
        sceneID: String,
        focusClueIDs: Set<String> = [],
        showAllReactions: Bool = false,
        showAllDirections: Bool = false
    ) {
        self.npc = npc
        self.appearance = appearance
        self.sceneID = sceneID
        self.focusClueIDs = focusClueIDs
        self.showAllReactions = showAllReactions
        self.showAllDirections = showAllDirections
    }

    private var currentStateIndex: Int {
        session.npcStates[npc.id, default: 0]
    }

    private var presenceSatisfied: Bool {
        appearance.presence.isSatisfied(
            checkedClueIDs: session.checkedClueIDs.union(focusClueIDs),
            npcStateIndex: currentStateIndex,
            selectedEndingID: session.selectedEndingID,
            completedGuideStepIDs: session.completedGuideStepIDs
        )
    }

    private var isPresent: Bool {
        showAllDirections || presenceSatisfied
    }

    private var presenceLabel: String {
        if !presenceSatisfied { return showAllDirections ? "Vorschau · nicht einsetzen" : "nicht einsetzen" }
        return isContextual ? "situationsabhängig" : "einsetzen"
    }

    private var isContextual: Bool {
        ["conditional", "contextual", "manual"].contains(appearance.presence.mode)
    }

    private var reactions: [NPCClueReaction] {
        if showAllReactions {
            return appearance.clueReactions
        }
        let relevantClues = focusClueIDs.union(session.checkedClueIDs)
        return appearance.clueReactions.filter { relevantClues.contains($0.clueID) }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            presenceHeader
            if isPresent {
                directionFields
                statePicker
                if !reactions.isEmpty {
                    reactionsPanel
                }
            } else {
                Label(appearance.presence.absentInstruction.isEmpty
                      ? "Noch nicht einsetzen."
                      : appearance.presence.absentInstruction,
                      systemImage: "pause.circle")
                    .font(.caption)
                    .foregroundStyle(FrostTheme.warning)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(12)
        .background(FrostTheme.ink.opacity(0.38), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
    }

    private var presenceHeader: some View {
        HStack(alignment: .firstTextBaseline, spacing: 8) {
            Image(systemName: presenceSatisfied ? "person.crop.circle.fill" : "person.crop.circle.badge.xmark")
                .foregroundStyle(presenceSatisfied ? FrostTheme.accent : FrostTheme.warning)
            VStack(alignment: .leading, spacing: 2) {
                Text(npc.name)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.white)
                Text(npc.role)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(FrostTheme.quiet)
            }
            Spacer(minLength: 4)
            Text(presenceLabel)
                .font(.caption2.weight(.bold))
                .foregroundStyle(presenceSatisfied ? FrostTheme.accent : FrostTheme.warning)
        }
    }

    private var directionFields: some View {
        VStack(alignment: .leading, spacing: 8) {
            directionRow("Warum hier", appearance.reason, "mappin.and.ellipse")
            directionRow("Laune", appearance.mood, "face.smiling")
            directionRow("Ziel", appearance.goal, "scope")
            directionRow("Verhalten", appearance.behavior, "person.wave.2")
            directionRow("Nächste Handlung", appearance.nextAction, "arrow.turn.down.right")
            if !appearance.presence.instruction.isEmpty {
                directionRow("Einsetzen", appearance.presence.instruction, "clock.badge.checkmark")
            }
        }
    }

    private func directionRow(_ title: String, _ text: String, _ symbol: String) -> some View {
        HStack(alignment: .top, spacing: 8) {
            Image(systemName: symbol)
                .foregroundStyle(FrostTheme.cobalt)
                .frame(width: 18)
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.caption.weight(.bold))
                    .foregroundStyle(FrostTheme.quiet)
                Text(text)
                    .font(.caption)
                    .foregroundStyle(.white.opacity(0.88))
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    private var statePicker: some View {
        Picker("Haltung von \(npc.name)", selection: Binding(
            get: { session.npcStates[npc.id, default: 0] },
            set: { session.setNPCState(npc.id, state: $0) }
        )) {
            ForEach(Array(npc.states.enumerated()), id: \.offset) { index, state in
                Text(state.capitalized).tag(index)
            }
        }
        .pickerStyle(.segmented)
        .accessibilityLabel("Aktuelle Haltung von \(npc.name)")
    }

    private var reactionsPanel: some View {
        VStack(alignment: .leading, spacing: 9) {
            Divider().overlay(FrostTheme.quiet.opacity(0.25))
            SectionLabel(title: "Reaktion auf Hinweise")
            Text("Wähle, wer den Hinweis hält. Danach bestätigst du die ausgespielte Reaktion.")
                .font(.caption)
                .foregroundStyle(FrostTheme.quiet)
                .fixedSize(horizontal: false, vertical: true)
            ForEach(reactions) { reaction in
                reactionRow(reaction)
            }
        }
    }

    private func reactionRow(_ reaction: NPCClueReaction) -> some View {
        let presenterIndex = session.cluePresenterIndex(for: reaction.clueID)
        let presenterName = presenterIndex.flatMap { index in
            session.playerNames.indices.contains(index)
                ? (session.playerNames[index].trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                   ? "Figur \(index + 1)"
                   : session.playerNames[index])
                : nil
        } ?? "die Gruppe"
        let targetStateIndex = npc.states.firstIndex {
            $0.trimmingCharacters(in: .whitespacesAndNewlines).caseInsensitiveCompare(reaction.targetState ?? "") == .orderedSame
        }
        let isConfirmed = session.isNPCReactionConfirmed(npcID: npc.id, sceneID: sceneID, clueID: reaction.clueID)
        let clueIsAvailable = session.checkedClueIDs.contains(reaction.clueID) || focusClueIDs.contains(reaction.clueID)
        let clueTitle = content.manifest.clues.first(where: { $0.id == reaction.clueID })?.title ?? reaction.clueID

        return VStack(alignment: .leading, spacing: 7) {
            HStack(alignment: .firstTextBaseline, spacing: 6) {
                Text("\(reaction.clueID) · \(clueTitle)")
                    .font(.caption.weight(.bold))
                    .foregroundStyle(FrostTheme.cobalt)
                if session.checkedClueIDs.contains(reaction.clueID) {
                    Text("bestätigt")
                        .font(.caption2.weight(.bold))
                        .foregroundStyle(FrostTheme.accent)
                } else {
                    Text("nach Ausgabe")
                        .font(.caption2.weight(.bold))
                        .foregroundStyle(FrostTheme.quiet)
                }
            }
            Picker("Wer hält \(reaction.clueID)?", selection: Binding(
                get: { session.cluePresenterIndex(for: reaction.clueID) ?? -1 },
                set: { session.setCluePresenter(reaction.clueID, index: $0 == -1 ? nil : $0) }
            )) {
                Text("Gruppe").tag(-1)
                ForEach(session.playerNames.indices, id: \.self) { index in
                    Text(session.playerNames[index].trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                         ? "Figur \(index + 1)"
                         : session.playerNames[index]).tag(index)
                }
            }
            .pickerStyle(.menu)
            .accessibilityLabel("Figur für \(reaction.clueID) auswählen")
            directionRow("Wenn \(presenterName) den Hinweis zeigt", reaction.reaction, "person.crop.circle")
            directionRow("Was klar wird", reaction.reveals, "lightbulb")
            directionRow("Danach", reaction.nextAction, "arrow.right")
            if isConfirmed {
                Label("Reaktion bestätigt\(reaction.targetState.map { " · Haltung: \($0)" } ?? "")", systemImage: "checkmark.circle.fill")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(FrostTheme.accent)
                Button("Bestätigung zurücknehmen") {
                    session.clearNPCReaction(npcID: npc.id, sceneID: sceneID, clueID: reaction.clueID)
                }
                .font(.caption)
                .foregroundStyle(FrostTheme.quiet)
            } else {
                Button("Reaktion bestätigen") {
                    session.confirmNPCReaction(
                        npcID: npc.id,
                        sceneID: sceneID,
                        clueID: reaction.clueID,
                        targetStateIndex: targetStateIndex
                    )
                }
                .buttonStyle(.bordered)
                .tint(FrostTheme.accent)
                .frame(minHeight: 44)
                .disabled(!clueIsAvailable)
                Text(clueIsAvailable ? "Nach dem Ausspielen bestätigen." : "Wird nach der Hinweis-Ausgabe freigeschaltet.")
                    .font(.caption2)
                    .foregroundStyle(FrostTheme.quiet)
            }
        }
        .padding(10)
        .background(FrostTheme.panelRaised.opacity(0.72), in: RoundedRectangle(cornerRadius: 10, style: .continuous))
    }
}
