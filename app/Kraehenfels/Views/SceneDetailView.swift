import SwiftUI

struct SceneDetailView: View {
    let scene: SceneEntry
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var audio: AudioEngine
    @EnvironmentObject private var session: SessionStore
    @Environment(\.dismiss) private var dismiss
    @State private var showSpoilers = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                SceneArtView(resourceName: scene.art, height: 205, shareLabel: "Szenenbild teilen / sichern")
                sceneHeader
                escalationCard
                readAloudCard
                goalCard
                recommendationCard
                gmNotesCard
                sessionNoteCard
                cluePanel
                npcPanel
                audioPanel
                handoutPanel
                stuckPanel
                checklistPanel
                finishButton
            }
            .padding(20)
        }
        .background(FrostTheme.ink.ignoresSafeArea())
        .navigationTitle(scene.shortTitle)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarLeading) {
                Button("Zurück", systemImage: "chevron.left") { dismiss() }
            }
        }
    }

    private var sceneHeader: some View {
        VStack(alignment: .leading, spacing: 9) {
            HStack {
                Text(scene.id)
                    .font(.caption.monospaced().weight(.bold))
                    .foregroundStyle(FrostTheme.cobalt)
                Spacer()
                Text(scene.soundPreset ?? "Freies Spiel")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(FrostTheme.warning)
            }
            Text(scene.title)
                .font(.system(size: 31, weight: .bold, design: .rounded))
                .foregroundStyle(FrostTheme.frost)
            Label(scene.duration, systemImage: "clock")
                .font(.subheadline)
                .foregroundStyle(FrostTheme.quiet)
        }
    }

    private var escalationCard: some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    SectionLabel(title: "Dorfspannung")
                    Spacer()
                    Text("Stufe \(session.threatLevel)/5")
                        .font(.caption.weight(.bold))
                        .foregroundStyle(session.threatLevel >= 4 ? FrostTheme.warning : FrostTheme.frost)
                }
                HStack(spacing: 7) {
                    ForEach(0..<6, id: \.self) { index in
                        Capsule()
                            .fill(index <= session.threatLevel ? (index >= 4 ? FrostTheme.warning : FrostTheme.cobalt) : FrostTheme.panelRaised)
                            .frame(height: 7)
                    }
                }
                Stepper("Manuell setzen", value: Binding(get: { session.threatLevel }, set: { session.setThreatLevel($0) }), in: 0...5)
                    .font(.caption)
                    .foregroundStyle(FrostTheme.quiet)
            }
        }
    }

    private var recommendationCard: some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    SectionLabel(title: "Nächster sinnvoller Schritt")
                    Spacer()
                    Image(systemName: "lightbulb.fill")
                        .foregroundStyle(FrostTheme.warning)
                }
                Text(scene.recommendation.isEmpty ? "Lass die Gruppe frei handeln und reagiere auf ihre Fragen." : scene.recommendation)
                    .font(.subheadline)
                    .foregroundStyle(.white.opacity(0.9))
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    private var readAloudCard: some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    SectionLabel(title: "Vorlesen")
                    Spacer()
                    Image(systemName: "quote.opening")
                        .foregroundStyle(FrostTheme.cobalt)
                }
                Text(scene.readAloud.isEmpty ? "Kein Vorleseimpuls hinterlegt." : scene.readAloud)
                    .font(.body.italic())
                    .foregroundStyle(.white.opacity(0.92))
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    private var goalCard: some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 8) {
                SectionLabel(title: "Ziel der Szene")
                Text(scene.goal)
                    .font(.body)
                    .foregroundStyle(.white.opacity(0.92))
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    private var gmNotesCard: some View {
        DisclosureGroup(isExpanded: $showSpoilers) {
            VStack(alignment: .leading, spacing: 8) {
                ForEach(Array(scene.gmNotes.enumerated()), id: \.offset) { _, note in
                    Label(note, systemImage: "eye.slash")
                        .font(.subheadline)
                        .foregroundStyle(.white.opacity(0.88))
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
            .padding(.top, 8)
        } label: {
            HStack {
                SectionLabel(title: "SL-Notizen")
                Spacer()
                Text(showSpoilers ? "offen" : "Spoiler")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(FrostTheme.warning)
            }
        }
        .tint(FrostTheme.frost)
        .padding(16)
        .background(FrostTheme.panel, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    private var cluePanel: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                SectionLabel(title: "Hinweise verfolgen")
                Spacer()
                Text("\(checkedClueCount)/\(scene.clueIds.count)")
                    .font(.caption.monospaced().weight(.bold))
                    .foregroundStyle(FrostTheme.cobalt)
            }
            if scene.clueIds.isEmpty {
                Text("Keine Pflicht-Hinweise in dieser Szene.")
                    .font(.subheadline)
                    .foregroundStyle(FrostTheme.quiet)
            } else {
                ForEach(scene.clueIds, id: \.self) { id in
                    if let clue = content.manifest.clues.first(where: { $0.id == id }) {
                        clueRow(clue)
                    }
                }
            }
        }
    }

    private var sessionNoteCard: some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    SectionLabel(title: "Deine Tischnotiz")
                    Spacer()
                    Text("speichert lokal")
                        .font(.caption)
                        .foregroundStyle(FrostTheme.quiet)
                }
                ZStack(alignment: .topLeading) {
                    if session.sceneNoteBinding(for: scene.id).wrappedValue.isEmpty {
                        Text("Was ist gerade passiert? Wer weiß schon zu viel? Was bleibt offen?")
                            .font(.subheadline)
                            .foregroundStyle(FrostTheme.quiet)
                            .padding(.top, 8)
                            .padding(.leading, 5)
                            .allowsHitTesting(false)
                    }
                    TextEditor(text: session.sceneNoteBinding(for: scene.id))
                        .font(.subheadline)
                        .foregroundStyle(.white)
                        .scrollContentBackground(.hidden)
                        .frame(minHeight: 108)
                        .accessibilityLabel("Tischnotiz zu \(scene.title)")
                }
            }
        }
    }

    private func clueRow(_ clue: ClueEntry) -> some View {
        Button { toggleClue(clue.id) } label: {
            HStack(alignment: .top, spacing: 12) {
                Image(systemName: session.checkedClueIDs.contains(clue.id) ? "checkmark.circle.fill" : "circle")
                    .foregroundStyle(session.checkedClueIDs.contains(clue.id) ? FrostTheme.cobalt : FrostTheme.quiet)
                VStack(alignment: .leading, spacing: 3) {
                    HStack(spacing: 5) {
                        Text(clue.title)
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(.white)
                        if clue.required {
                            Text("PFLICHT")
                                .font(.system(size: 9, weight: .bold, design: .monospaced))
                                .foregroundStyle(FrostTheme.warning)
                        }
                    }
                    Text(clue.details)
                        .font(.caption)
                        .foregroundStyle(FrostTheme.quiet)
                        .fixedSize(horizontal: false, vertical: true)
                }
                Spacer()
            }
            .padding(13)
            .background(FrostTheme.panel, in: RoundedRectangle(cornerRadius: 13, style: .continuous))
        }
        .buttonStyle(.plain)
    }

    private var npcPanel: some View {
        VStack(alignment: .leading, spacing: 10) {
            SectionLabel(title: "NPCs in dieser Szene")
            if scene.npcIds.isEmpty {
                Text("Keine festen NPCs. Die Erscheinung reagiert auf die Gruppe.")
                    .font(.subheadline)
                    .foregroundStyle(FrostTheme.quiet)
            }
            ForEach(scene.npcIds, id: \.self) { id in
                if let npc = content.manifest.npcs.first(where: { $0.id == id }) {
                    npcCard(npc)
                }
            }
        }
    }

    private func npcCard(_ npc: NPCEntry) -> some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 8) {
                HStack(alignment: .firstTextBaseline) {
                    Text(npc.name)
                        .font(.headline)
                        .foregroundStyle(.white)
                    Spacer()
                    Text(npc.role)
                        .font(.caption)
                        .foregroundStyle(FrostTheme.cobalt)
                }
                Text(npc.description)
                    .font(.subheadline)
                    .foregroundStyle(FrostTheme.quiet)
                if let appearance = npc.appearances.first(where: { $0.sceneId == scene.id }) {
                    VStack(alignment: .leading, spacing: 7) {
                        bulletList(title: "Auftritt", items: [appearance.when], icon: "clock")
                        bulletList(title: "So spielen", items: [appearance.playAs], icon: "theatermasks")
                        VStack(alignment: .leading, spacing: 3) {
                            Text("ERSTER SATZ")
                                .font(.system(size: 9, weight: .bold, design: .monospaced))
                                .foregroundStyle(FrostTheme.quiet)
                            Text("„\(appearance.openingLine)“")
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(FrostTheme.warning)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        bulletList(title: "Danach", items: [appearance.turn], icon: "arrow.turn.down.right")
                    }
                    .padding(.vertical, 4)
                }
                if showSpoilers {
                    if !npc.knows.isEmpty {
                        bulletList(title: "Weiß", items: npc.knows, icon: "checkmark.seal")
                    }
                    if !npc.hides.isEmpty {
                        bulletList(title: "Verschweigt", items: npc.hides, icon: "lock")
                    }
                    if !npc.givesHandoutIds.isEmpty {
                        Label("Kann geben: \(npc.givesHandoutIds.joined(separator: ", "))", systemImage: "doc.badge.plus")
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(FrostTheme.cobalt)
                    }
                    if !npc.states.isEmpty {
                        Picker("Haltung", selection: Binding(get: { session.npcStates[npc.id, default: 0] }, set: { session.setNPCState(npc.id, state: $0) })) {
                            ForEach(Array(npc.states.enumerated()), id: \.offset) { index, state in
                                Text(state.capitalized).tag(index)
                            }
                        }
                        .pickerStyle(.segmented)
                        .accessibilityLabel("Haltung von \(npc.name)")
                    }
                }
                if npc.appearances.first(where: { $0.sceneId == scene.id }) == nil {
                    Label("Kein geplanter Auftritt in dieser Szene. NPC nicht automatisch einsetzen.", systemImage: "exclamationmark.triangle")
                        .font(.caption)
                        .foregroundStyle(FrostTheme.warning)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
        }
    }

    private func bulletList(title: String, items: [String], icon: String) -> some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(title.uppercased())
                .font(.system(size: 9, weight: .bold, design: .monospaced))
                .foregroundStyle(FrostTheme.quiet)
            ForEach(items, id: \.self) { item in
                Label(item, systemImage: icon)
                    .font(.caption)
                    .foregroundStyle(.white.opacity(0.82))
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    private var audioPanel: some View {
        VStack(alignment: .leading, spacing: 11) {
            HStack {
                SectionLabel(title: "Sound-Regie")
                Spacer()
                Button {
                    audio.playPreset(content.cues(for: scene))
                } label: {
                    Label("Atmosphäre", systemImage: "wind")
                        .font(.caption.weight(.bold))
                        .foregroundStyle(FrostTheme.frost)
                }
                .buttonStyle(.borderedProminent)
                .tint(FrostTheme.cobalt.opacity(0.8))
            }
            HStack(spacing: 7) {
                Circle()
                    .fill(audio.activeCueIDs.isEmpty ? FrostTheme.quiet : FrostTheme.accent)
                    .frame(width: 7, height: 7)
                Text(audio.activeLayerSummary)
                    .font(.caption)
                    .foregroundStyle(FrostTheme.quiet)
            }
            if scene.audioPlan.isEmpty {
                Label("Für diese Szene ist bewusst kein Cue vorgesehen.", systemImage: "speaker.slash.fill")
                    .font(.subheadline)
                    .foregroundStyle(FrostTheme.quiet)
            } else {
                ForEach(Array(scene.audioPlan.enumerated()), id: \.element.id) { index, plan in
                    if let cue = content.cue(for: plan.cueId) {
                        CueRow(cue: cue, plan: plan, index: index + 1)
                    }
                }
            }
            if let error = audio.lastError {
                Label(error, systemImage: "exclamationmark.triangle.fill")
                    .font(.caption)
                    .foregroundStyle(FrostTheme.warning)
                    .fixedSize(horizontal: false, vertical: true)
            } else if let event = audio.lastEvent {
                Label(event, systemImage: "checkmark.circle")
                    .font(.caption)
                    .foregroundStyle(FrostTheme.cobalt)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    private var handoutPanel: some View {
        VStack(alignment: .leading, spacing: 10) {
            SectionLabel(title: "Handouts")
            ForEach(scene.handoutIds, id: \.self) { id in
                if let handout = content.handout(for: id) {
                    if showSpoilers || !handout.spoiler {
                        NavigationLink(destination: HandoutPreviewView(handoutID: handout.id)) {
                            HStack(spacing: 12) {
                                Image(systemName: handout.spoiler ? "lock.open.fill" : "doc.text")
                                    .foregroundStyle(handout.spoiler ? FrostTheme.warning : FrostTheme.cobalt)
                                VStack(alignment: .leading, spacing: 3) {
                                    Text("\(handout.id) · \(handout.title)")
                                        .font(.subheadline.weight(.medium))
                                        .foregroundStyle(.white)
                                    Text(handout.spoiler ? "SL-Spoiler · \(handout.format)" : "Spielerhinweis · \(handout.format)")
                                        .font(.caption)
                                        .foregroundStyle(handout.spoiler ? FrostTheme.warning : FrostTheme.quiet)
                                }
                                Spacer()
                                Image(systemName: "chevron.right")
                                    .font(.caption.weight(.bold))
                                    .foregroundStyle(FrostTheme.quiet)
                            }
                        }
                        .padding(.vertical, 5)
                    } else {
                        HStack(spacing: 12) {
                            Image(systemName: "lock.fill")
                                .foregroundStyle(FrostTheme.warning)
                            VStack(alignment: .leading, spacing: 3) {
                                Text("\(handout.id) · \(handout.title)")
                                    .font(.subheadline.weight(.medium))
                                    .foregroundStyle(.white)
                                Text("Spoiler · Schalter oben öffnen")
                                    .font(.caption)
                                    .foregroundStyle(FrostTheme.warning)
                            }
                            Spacer()
                            Image(systemName: "lock.fill")
                                .font(.caption.weight(.bold))
                                .foregroundStyle(FrostTheme.quiet)
                        }
                        .padding(.vertical, 5)
                    }
                }
            }
        }
    }

    private var stuckPanel: some View {
        DisclosureGroup {
            VStack(alignment: .leading, spacing: 8) {
                ForEach(scene.stuckPrompts, id: \.self) { prompt in
                    Label(prompt, systemImage: "lifepreserver")
                        .font(.subheadline)
                        .foregroundStyle(.white.opacity(0.88))
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
            .padding(.top, 8)
        } label: {
            SectionLabel(title: "Wenn die Gruppe feststeckt")
        }
        .tint(FrostTheme.frost)
        .padding(16)
        .background(FrostTheme.panel, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    private var checklistPanel: some View {
        VStack(alignment: .leading, spacing: 9) {
            HStack {
                SectionLabel(title: "Abschluss-Checkliste")
                Spacer()
                Text("\(completedChecklistCount)/\(scene.checklist.count)")
                    .font(.caption.monospaced().weight(.bold))
                    .foregroundStyle(FrostTheme.cobalt)
            }
            ForEach(Array(scene.checklist.enumerated()), id: \.offset) { index, item in
                let id = "\(scene.id)-\(index)"
                Button { toggleChecklist(id) } label: {
                    HStack(spacing: 10) {
                        Image(systemName: session.completedChecklistIDs.contains(id) ? "checkmark.square.fill" : "square")
                            .foregroundStyle(session.completedChecklistIDs.contains(id) ? FrostTheme.cobalt : FrostTheme.quiet)
                        Text(item)
                            .font(.subheadline)
                            .foregroundStyle(.white.opacity(0.88))
                        Spacer()
                    }
                }
                .buttonStyle(.plain)
            }
        }
    }

    private var finishButton: some View {
        Button {
            session.currentSceneID = scene.nextSceneIds.first ?? scene.id
            session.completedSceneIDs.insert(scene.id)
        } label: {
            Text(scene.nextSceneIds.isEmpty ? "Szene abschließen" : "Szene abschließen und weiter")
                .font(.headline)
                .foregroundStyle(FrostTheme.ink)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 15)
                .background(FrostTheme.frost, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
        }
        .accessibilityHint("Markiert diese Szene als abgeschlossen")
    }

    private var checkedClueCount: Int {
        scene.clueIds.filter { session.checkedClueIDs.contains($0) }.count
    }

    private var completedChecklistCount: Int {
        scene.checklist.indices.filter { session.completedChecklistIDs.contains("\(scene.id)-\($0)") }.count
    }

    private func toggleClue(_ id: String) {
        session.toggleClue(id)
    }

    private func toggleChecklist(_ id: String) {
        session.toggleChecklist(id)
    }
}

private struct CueRow: View {
    let cue: AudioCue
    let plan: AudioPlanEntry
    let index: Int
    @EnvironmentObject private var audio: AudioEngine

    var body: some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 10) {
                HStack(spacing: 12) {
                    Text("\(index)")
                        .font(.caption.monospaced().weight(.bold))
                        .foregroundStyle(FrostTheme.ink)
                        .frame(width: 25, height: 25)
                        .background(FrostTheme.cobalt, in: Circle())
                Image(systemName: audio.isPlaying(cue) ? "pause.fill" : cue.iconName)
                    .foregroundStyle(audio.isPlaying(cue) ? FrostTheme.frost : FrostTheme.cobalt)
                    .frame(width: 25)
                VStack(alignment: .leading, spacing: 3) {
                        HStack(spacing: 6) {
                            Text(cue.title)
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(.white)
                            if plan.optional {
                                Text("OPTIONAL")
                                    .font(.system(size: 9, weight: .bold, design: .monospaced))
                                    .foregroundStyle(FrostTheme.warning)
                            }
                        }
                        Text("\(cue.id) · \(cue.categoryLabel)\(cue.isClue ? " · Hinweis" : "")")
                        .font(.caption)
                        .foregroundStyle(cue.isClue ? FrostTheme.warning : FrostTheme.quiet)
                }
                Spacer()
                    Button { audio.toggle(cue) } label: {
                        Image(systemName: audio.isPlaying(cue) && cue.mode == "loop" ? "pause.fill" : "play.fill")
                            .font(.body.weight(.bold))
                            .foregroundStyle(FrostTheme.ink)
                            .frame(width: 44, height: 44)
                            .background(FrostTheme.frost, in: Circle())
                    }
                    .accessibilityLabel("\(cue.title) abspielen")
                }
                VStack(alignment: .leading, spacing: 5) {
                    Label(plan.playWhen, systemImage: "clock.badge.checkmark")
                        .foregroundStyle(.white.opacity(0.92))
                    Label(plan.gmInstruction, systemImage: "person.wave.2")
                        .foregroundStyle(FrostTheme.cobalt)
                    if cue.mode == "loop" {
                        Label(plan.stopWhen, systemImage: "stop.circle")
                            .foregroundStyle(FrostTheme.quiet)
                    }
                }
                .font(.caption)
                .fixedSize(horizontal: false, vertical: true)
            }
        }
        .accessibilityLabel("\(cue.title), \(cue.categoryLabel)")
        .accessibilityValue(audio.isPlaying(cue) ? "Läuft" : "Gestoppt")
    }
}
