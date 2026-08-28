import SwiftUI

struct GMStartView: View {
    @EnvironmentObject private var session: SessionStore
    @EnvironmentObject private var audio: AudioEngine
    @EnvironmentObject private var content: ContentStore
    @State private var startSession = false
    let onStart: (() -> Void)?
    let onExit: (() -> Void)?

    init(onStart: (() -> Void)? = nil, onExit: (() -> Void)? = nil) {
        self.onStart = onStart
        self.onExit = onExit
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                intro
                setupChecklist
                characterTable
                tableBriefing
                startButton
            }
            .padding(20)
        }
        .background(FrostTheme.ink.ignoresSafeArea())
        .navigationTitle("Spiel starten")
        .navigationBarTitleDisplayMode(.inline)
        .navigationDestination(isPresented: $startSession) {
            GuidedGMView(onExit: {
                if let onExit {
                    onExit()
                } else {
                    startSession = false
                }
            })
        }
    }

    private var intro: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("SPIELLEITER-MODUS")
                .font(.caption.weight(.bold))
                .tracking(1.6)
                .foregroundStyle(FrostTheme.cobalt)
            Text("Heute Abend musst du nichts auswendig können.")
                .font(.system(size: 30, weight: .bold, design: .rounded))
                .foregroundStyle(FrostTheme.frost)
            Text("Dieser Assistent zeigt dir immer genau, was du vorliest, was nur du wissen darfst, was die Spieler tun können und wann ein W100 sinnvoll ist.")
                .font(.body)
                .foregroundStyle(FrostTheme.quiet)
                .fixedSize(horizontal: false, vertical: true)
        }
    }

    private var setupChecklist: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                SectionLabel(title: "Vorbereitung")
                Spacer()
                Text("\(session.setupChecks.count)/\(content.setupItems.count)")
                    .font(.caption.monospaced().weight(.bold))
                    .foregroundStyle(FrostTheme.cobalt)
            }
            ForEach(content.setupItems, id: \.id) { item in
                Button { session.toggleSetup(item.id) } label: {
                    HStack(alignment: .top, spacing: 12) {
                        Image(systemName: session.setupChecks.contains(item.id) ? "checkmark.circle.fill" : "circle")
                            .foregroundStyle(session.setupChecks.contains(item.id) ? FrostTheme.cobalt : FrostTheme.quiet)
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
                        Spacer()
                    }
                    .padding(.vertical, 8)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(16)
        .background(FrostTheme.panel, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    private var characterTable: some View {
        VStack(alignment: .leading, spacing: 10) {
            SectionLabel(title: "Drei eigene Figuren")
            Text("Jede Person bringt ihren eigenen Charakter mit. Trage nur die Namen ein; Werte, Beruf und Geschichte bleiben auf euren eigenen Figurenbögen.")
                .font(.subheadline)
                .foregroundStyle(FrostTheme.quiet)
            ForEach(0..<3, id: \.self) { index in
                HStack(spacing: 12) {
                    Text("\(index + 1)")
                        .font(.headline.monospaced().weight(.bold))
                        .foregroundStyle(FrostTheme.ink)
                        .frame(width: 34, height: 34)
                        .background(FrostTheme.frost, in: Circle())
                    TextField("Name der Figur", text: session.playerNameBinding(at: index))
                        .textInputAutocapitalization(.words)
                        .autocorrectionDisabled()
                        .textFieldStyle(.roundedBorder)
                        .frame(minHeight: 44)
                }
            }
        }
        .padding(16)
        .background(FrostTheme.panel, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    private var tableBriefing: some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 8) {
                Label("Was du den Spielern sagst", systemImage: "person.3.fill")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(FrostTheme.frost)
                Text(content.manifest.guide.playerBriefing)
                    .font(.subheadline)
                    .foregroundStyle(.white.opacity(0.9))
                    .fixedSize(horizontal: false, vertical: true)
                Label("Nicht verraten: \(content.manifest.guide.hiddenFromPlayers)", systemImage: "eye.slash.fill")
                    .font(.caption)
                    .foregroundStyle(FrostTheme.warning)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    private var startButton: some View {
        VStack(spacing: 9) {
            Button {
                session.beginGuidedSession()
                if let music = content.musicBed, !audio.isPlaying(music) {
                    audio.play(music)
                }
                if let onStart {
                    onStart()
                } else {
                    startSession = true
                }
            } label: {
                Label("Spielleiter-Modus starten", systemImage: "play.fill")
                    .font(.headline)
                    .foregroundStyle(FrostTheme.ink)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 15)
                    .background(FrostTheme.frost, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
            }
            .disabled(!hasThreePlayerNames)
            .opacity(hasThreePlayerNames ? 1 : 0.45)
            Text("Du kannst die Vorbereitung auch später nachholen.")
                .font(.caption)
                .foregroundStyle(FrostTheme.quiet)
            if !hasThreePlayerNames {
                Text("Bitte alle drei eigenen Figuren benennen, bevor die Runde startet.")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(FrostTheme.warning)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    private var hasThreePlayerNames: Bool {
        session.playerNames.count == 3
            && session.playerNames.allSatisfy { !$0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }
    }
}

struct GuidedGMView: View {
    let onExit: (() -> Void)?
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var audio: AudioEngine
    @EnvironmentObject private var session: SessionStore
    @Environment(\.dismiss) private var dismiss
    @State private var rollStep: GuideStep?
    @State private var readAloudStep: GuideStep?
    @State private var showMaterials = false
    @State private var showRules = false
    @State private var showCombat = false
    @State private var showAudioPlan = false
    @State private var showContext = false
    @State private var showInventory = false
    @State private var pendingDestination: String?
    @State private var showBranchChangeConfirmation = false

    init(onExit: (() -> Void)? = nil) {
        self.onExit = onExit
    }

    private var steps: [GuideStep] {
        let base = content.steps(for: session.currentSceneID)
        guard session.currentSceneID == "S07" else { return base }
        if session.finaleMode == "combat" {
            return base.filter { $0.id != "S07_DANGER" }
        }
        return base.filter { $0.id != "S07_COMBAT" }
    }

    private var currentStep: GuideStep? {
        guard steps.indices.contains(session.guidedStepIndex) else { return steps.last }
        return steps[session.guidedStepIndex]
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                progressHeader
                if let scene = content.scene(for: session.currentSceneID) {
                    SceneArtView(resourceName: scene.art, height: 168)
                    sceneContext(scene)
                    audioPlanPanel(scene)
                }
                if let step = currentStep {
                    stepCard(step)
                    if !step.options.isEmpty {
                        optionsPanel(step)
                    }
                } else {
                    emptyFlow
                }
                quickAccess
                sessionNote
            }
            .padding(20)
        }
        .safeAreaInset(edge: .bottom, spacing: 0) {
            guideFooter
        }
        .background(FrostTheme.ink.ignoresSafeArea())
        .navigationTitle(content.scene(for: session.currentSceneID)?.shortTitle ?? "Spielleitung")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            session.migrateLegacyInventoryIfNeeded(itemIDs: content.guideItems.map(\.id))
        }
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Menu {
                    Button("Materialien öffnen", systemImage: "folder") { showMaterials = true }
                    Button("Ausrüstung öffnen", systemImage: "shippingbox") { showInventory = true }
                    Button("Regeln öffnen", systemImage: "dice") { showRules = true }
                    Button("Kontext anzeigen", systemImage: "sidebar.right") { showContext = true }
                } label: {
                    Image(systemName: "ellipsis.circle")
                        .foregroundStyle(FrostTheme.frost)
                }
                .accessibilityLabel("Spielleiter-Werkzeuge")
            }
        }
        .sheet(item: $rollStep) { step in
            RollHelperView(step: step, selectedEndingID: session.selectedEndingID) { result, consequence, itemSelections in
                let itemUseRecords = itemSelections.compactMap { selection -> ItemUseRecord? in
                    guard let item = content.item(for: selection.itemID) else { return nil }
                    return session.useItem(
                        itemID: selection.itemID,
                        effectID: selection.effectID,
                        sceneID: step.sceneID,
                        stepID: step.id,
                        maximumUses: item.initialUses
                    )
                }
                guard itemUseRecords.count == itemSelections.count else {
                    itemUseRecords.forEach { session.undoItemUse($0.id) }
                    return
                }
                let itemUseIDs = itemUseRecords.map { $0.id.uuidString }
                if step.id == "S07_DANGER" {
                    let state = session.recordFinaleRoll(result, consequence: consequence, itemUseIDs: itemUseIDs)
                    if state.isResolved {
                        advance(step)
                    }
                    return
                }
                session.recordRoll(stepID: step.id, result: result, consequence: consequence, itemUseIDs: itemUseIDs)
                advance(step)
            }
        }
        .sheet(item: $readAloudStep) { step in
            ReadAloudCueSheet(step: step, cue: step.audioCueID.flatMap(content.cue)) { mode in
                if mode == .start {
                    audio.startReadAloud(cue: step.audioCueID.flatMap(content.cue))
                } else if mode == .complete {
                    audio.finishReadAloud()
                    advance(step)
                } else {
                    audio.finishReadAloud()
                }
            }
        }
        .sheet(isPresented: $showCombat) {
            CombatReferenceView()
        }
        .sheet(isPresented: $showContext) {
            NavigationStack {
                WorkspaceContextView(sceneID: session.currentSceneID)
            }
            .presentationDetents([.medium, .large])
        }
        .alert("Diesen Pfad neu wählen?", isPresented: $showBranchChangeConfirmation) {
            Button("Abbrechen", role: .cancel) {
                pendingDestination = nil
            }
            Button("Pfad neu setzen", role: .destructive) {
                if let pendingDestination {
                    move(to: pendingDestination, resettingDependentPath: true)
                }
            }
        } message: {
            Text("Gefundene Hinweise und Tischnotizen bleiben erhalten. Spätere Szenen werden ab dem neuen Ziel zurückgesetzt.")
        }
        .navigationDestination(isPresented: $showMaterials) { MaterialsView() }
        .navigationDestination(isPresented: $showInventory) { InventoryView() }
        .navigationDestination(isPresented: $showRules) { RulesView() }
    }

    private var guideFooter: some View {
        VStack(spacing: 8) {
            HStack(spacing: 10) {
                Button {
                    if !session.stepBack() {
                        if let onExit {
                            onExit()
                        } else {
                            dismiss()
                        }
                    }
                } label: {
                    Label(session.guideHistory.isEmpty ? "Übersicht" : "Zurück", systemImage: "chevron.left")
                        .font(.subheadline.weight(.semibold))
                        .frame(minWidth: 106, minHeight: 48)
                }
                .buttonStyle(.bordered)
                .tint(FrostTheme.accent)
                .accessibilityHint("Geht zum vorherigen Spielleiterschritt zurück. Gefundene Hinweise bleiben erhalten.")

                if let step = currentStep, step.options.isEmpty {
                    Button {
                        primaryAction(for: step)
                    } label: {
                        Label(primaryActionTitle(for: step), systemImage: primaryActionSymbol(for: step))
                            .font(.headline)
                            .foregroundStyle(FrostTheme.ink)
                            .frame(maxWidth: .infinity, minHeight: 48)
                            .background(FrostTheme.frost, in: RoundedRectangle(cornerRadius: 13, style: .continuous))
                    }
                    .buttonStyle(.plain)
                    .disabled(!canAdvance(step))
                    .opacity(canAdvance(step) ? 1 : 0.45)
                } else {
                    Text("Wähle den nächsten Schritt oben")
                        .font(.caption)
                        .foregroundStyle(FrostTheme.quiet)
                        .frame(maxWidth: .infinity, minHeight: 48)
                }
            }

            if let step = currentStep, step.options.isEmpty, let roll = step.roll, !roll.required {
                Button("Ohne Probe weiter") {
                    advance(step)
                }
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(FrostTheme.quiet)
                .frame(maxWidth: .infinity, minHeight: 44)
            }
        }
        .padding(.horizontal, 16)
        .padding(.top, 10)
        .padding(.bottom, 8)
        .background(.ultraThinMaterial)
        .overlay(alignment: .top) {
            Divider().overlay(FrostTheme.line)
        }
    }

    private func primaryActionTitle(for step: GuideStep) -> String {
        if step.roll != nil { return "Würfelhelfer öffnen" }
        if step.kind == .readAloud { return "Sound vorbereiten und vorlesen" }
        return step.actionLabel
    }

    private func primaryActionSymbol(for step: GuideStep) -> String {
        if step.roll != nil { return "dice.fill" }
        if step.kind == .readAloud { return "quote.bubble.fill" }
        return "arrow.right"
    }

    private func primaryAction(for step: GuideStep) {
        if step.roll != nil {
            rollStep = step
        } else if step.kind == .readAloud {
            readAloudStep = step
        } else if canAdvance(step) {
            advance(step)
        }
    }

    private func canAdvance(_ step: GuideStep) -> Bool {
        if step.id == "S01_DISTRIBUTE" {
            return session.isItemDistributionComplete(for: content.guideItems.map(\.id))
        }
        return true
    }

    private var progressHeader: some View {
        let count = max(steps.count, 1)
        return VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text("SCHRITT \(min(session.guidedStepIndex + 1, count)) VON \(count)")
                    .font(.caption.monospaced().weight(.bold))
                    .foregroundStyle(FrostTheme.cobalt)
                Spacer()
                Text("Stufe \(session.threatLevel)/5")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(session.threatLevel >= 4 ? FrostTheme.warning : FrostTheme.quiet)
            }
            ProgressView(value: Double(min(session.guidedStepIndex + 1, count)), total: Double(count))
                .tint(FrostTheme.cobalt)
        }
    }

    private func sceneContext(_ scene: SceneEntry) -> some View {
        HStack(alignment: .top, spacing: 11) {
            Image(systemName: "location.fill")
                .foregroundStyle(FrostTheme.cobalt)
                .frame(width: 24)
            VStack(alignment: .leading, spacing: 3) {
                Text(scene.title == "Das schwarze Keiler" ? "Der Schwarze Keiler" : scene.title)
                    .font(.headline)
                    .foregroundStyle(.white)
                Text(scene.goal)
                    .font(.caption)
                    .foregroundStyle(FrostTheme.quiet)
                    .fixedSize(horizontal: false, vertical: true)
            }
            Spacer()
        }
    }

    private func audioPlanPanel(_ scene: SceneEntry) -> some View {
        let plans = content.plannedCues(for: scene)
        return FrostCard {
            DisclosureGroup(isExpanded: $showAudioPlan) {
                VStack(alignment: .leading, spacing: 10) {
                    ForEach(Array(plans.enumerated()), id: \.offset) { index, entry in
                        let plan = entry.0
                        let cue = entry.1
                        HStack(alignment: .top, spacing: 10) {
                            Image(systemName: cue.iconName)
                                .foregroundStyle(cue.layer == "sfx" ? FrostTheme.warning : FrostTheme.cobalt)
                                .frame(width: 20)
                            VStack(alignment: .leading, spacing: 3) {
                                HStack(spacing: 6) {
                                    Text(cue.title)
                                        .font(.subheadline.weight(.semibold))
                                        .foregroundStyle(.white)
                                    Text(cue.mode == "loop" ? "LOOP" : "EINMAL")
                                        .font(.caption2.monospaced().weight(.bold))
                                        .foregroundStyle(FrostTheme.quiet)
                                }
                                Text("Jetzt: \(plan.playWhen)")
                                    .font(.caption)
                                    .foregroundStyle(FrostTheme.cobalt)
                                Text("Stop: \(plan.stopWhen)")
                                    .font(.caption)
                                    .foregroundStyle(FrostTheme.quiet)
                                Text(plan.gmInstruction)
                                    .font(.caption)
                                    .foregroundStyle(.white.opacity(0.8))
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                            Spacer(minLength: 4)
                            Button {
                                audio.toggle(cue)
                            } label: {
                                Image(systemName: audio.isPlaying(cue) && cue.mode == "loop" ? "pause.fill" : "play.fill")
                                    .frame(width: 44, height: 44)
                            }
                            .buttonStyle(.bordered)
                            .accessibilityLabel("\(cue.title) abspielen")
                        }
                        if index < plans.count - 1 {
                            Divider().overlay(FrostTheme.quiet.opacity(0.25))
                        }
                    }
                }
                .padding(.top, 10)
            } label: {
                HStack {
                    Label("Soundplan für diesen Abschnitt", systemImage: "waveform")
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(FrostTheme.frost)
                    Spacer()
                    Text("\(scene.audioCueIds.count) Cues")
                        .font(.caption.monospaced().weight(.bold))
                        .foregroundStyle(FrostTheme.cobalt)
                }
            }
            .tint(FrostTheme.frost)
        }
    }

    private func stepCard(_ step: GuideStep) -> some View {
        VStack(alignment: .leading, spacing: 11) {
            HStack(alignment: .firstTextBaseline) {
                Label(step.kind.label, systemImage: step.kind.symbol)
                    .font(.caption.weight(.bold))
                    .foregroundStyle(stepColor(step.kind))
                Spacer()
                if session.completedGuideStepIDs.contains(step.id) {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundStyle(FrostTheme.accent)
                }
            }
            Text(step.title)
                .font(.title2.weight(.bold))
                .foregroundStyle(FrostTheme.frost)
            Text(step.body)
                .font(step.kind == .readAloud ? .body.italic() : .body)
                .foregroundStyle(.white.opacity(0.92))
                .fixedSize(horizontal: false, vertical: true)
            if let roll = step.roll {
                rollSessionPanel(step, roll)
            } else {
                noRollSummary(step)
            }
            if step.kind == .itemSearch {
                ItemFindingsPanel(locations: content.itemFindLocations, items: content.guideItems)
            }
            if step.kind == .itemDistribution {
                ItemDistributionPanel()
            }
            if step.id == "S07_GM" {
                finaleModePicker
            }
            if step.id == "S07_DANGER" {
                finaleProgressCard
            }
            if step.id == "S07_COMBAT" {
                Button {
                    showCombat = true
                } label: {
                    Label("Kampf-Kurzreferenz öffnen", systemImage: "shield.lefthalf.filled")
                }
                .buttonStyle(.bordered)
                .tint(FrostTheme.warning)
            }
            if ["S02_GM", "S02_CLUE", "S02_ROLL"].contains(step.id) {
                doorStateControl
            }
            materialLinks(for: step)
        }
        .padding(17)
        .background(stepBackground(step.kind), in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(stepColor(step.kind).opacity(0.36), lineWidth: 1))
    }

    private var finaleProgressCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Label("Zwei Erfolge vor zwei Fehlschlägen", systemImage: "chart.bar.fill")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(FrostTheme.frost)
                Spacer()
                Text("\(session.finaleSuccesses) : \(session.finaleFailures)")
                    .font(.headline.monospaced().weight(.bold))
                    .foregroundStyle(session.finaleOutcome == "failure" ? FrostTheme.warning : FrostTheme.cobalt)
            }
            ProgressView(value: Double(session.finaleSuccesses), total: 2)
                .tint(FrostTheme.accent)
            Text(session.finaleOutcome == "success"
                 ? "Die Gefahrenszene ist zugunsten der Gruppe entschieden."
                 : session.finaleOutcome == "failure"
                    ? "Zwei Fehlschläge: Die Szene kostet Wärme und Vertrauen, danach geht es trotzdem weiter."
                    : "Ein kritischer Misserfolg zählt als zwei Fehlschläge. Bei einem Zwischenstand bleibt derselbe Schritt geöffnet.")
                .font(.caption)
                .foregroundStyle(FrostTheme.quiet)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(12)
        .background(FrostTheme.ink.opacity(0.42), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
    }

    private func rollSessionPanel(_ step: GuideStep, _ roll: RollSpec) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .firstTextBaseline) {
                Label("Würfelsession", systemImage: "dice.fill")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(FrostTheme.frost)
                Spacer()
                Text(roll.required ? "PFLICHT" : "OPTIONAL")
                    .font(.caption2.monospaced().weight(.bold))
                    .foregroundStyle(roll.required ? FrostTheme.warning : FrostTheme.accent)
            }
            Label("Wer: \(roll.actor)", systemImage: "person.fill")
            Label("\(roll.die) auf \(roll.ability)", systemImage: "dice")
            Label("Ziel: \(roll.target)", systemImage: "scope")
            Label(roll.modifier, systemImage: "plusminus")
            Text(roll.required ? "Diese Probe gehört zum aktuellen Schritt." : "Würfle nur, wenn die Gruppe die riskante Handlung tatsächlich versucht.")
                .font(.caption)
                .foregroundStyle(FrostTheme.quiet)
                .fixedSize(horizontal: false, vertical: true)
            if roll.guaranteedClue {
                Label("Pflicht-Hinweis bleibt unabhängig vom Ergebnis erhalten.", systemImage: "lock.open.fill")
            }
            if let previous = session.rollHistory[step.id] {
                Label("Letztes Ergebnis: \(previous)", systemImage: "clock.arrow.circlepath")
                    .foregroundStyle(FrostTheme.accent)
            }
            if let previous = session.latestRollResolution(for: step.id),
               let consequenceTitle = previous.consequenceTitle {
                Label("Gewählte Folge: \(consequenceTitle)", systemImage: "arrow.triangle.branch")
                    .foregroundStyle(FrostTheme.warning)
                    .fixedSize(horizontal: false, vertical: true)
            }
            if let previous = session.latestRollResolution(for: step.id), !previous.itemUseIDs.isEmpty {
                let usedItems = previous.itemUseIDs.compactMap { UUID(uuidString: $0) }.compactMap { recordID in
                    session.itemUseRecords.first(where: { $0.id == recordID }).flatMap { content.item(for: $0.itemID)?.title }
                }
                if !usedItems.isEmpty {
                    Label("Eingesetzte Ausrüstung: \(usedItems.joined(separator: ", "))", systemImage: "shippingbox.fill")
                        .foregroundStyle(FrostTheme.accent)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
            Button {
                rollStep = step
            } label: {
                Label("Würfelhelfer öffnen", systemImage: "dice.fill")
                    .frame(maxWidth: .infinity, minHeight: 44)
            }
            .buttonStyle(.borderedProminent)
            .tint(FrostTheme.accent)
        }
        .font(.caption)
        .foregroundStyle(.white.opacity(0.82))
        .fixedSize(horizontal: false, vertical: true)
        .padding(12)
        .background(FrostTheme.ink.opacity(0.42), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
    }

    private func noRollSummary(_ step: GuideStep) -> some View {
        let message: String
        switch step.kind {
        case .readAloud:
            message = "Keine Probe. Sound bestätigen, Text vorlesen und erst danach weitergehen."
        case .gmInfo:
            message = "Keine Probe. Nur für dich lesen und nicht an die Spieler weitergeben."
        case .playerAction:
            message = "Keine Pflichtprobe. Würfle nur, wenn eine riskante Handlung wirklich etwas verändern kann."
        case .trigger:
            message = "Keine Probe. Warte auf den beschriebenen Auslöser und spiele dann den Schritt aus."
        case .clue:
            message = "Keine Probe. Den Hinweis zeigen oder den angegebenen Fallback vorlesen."
        case .choice, .next:
            message = "Keine Probe. Die Gruppe entscheidet. Wähle danach den passenden nächsten Schritt."
        case .roll:
            message = "Würfelprobe ist im Schritt angegeben."
        case .itemSearch:
            message = "Keine Probe. Alle sechs Gegenstände aus der Kutsche werden automatisch sichtbar."
        case .itemDistribution:
            message = "Keine Probe. Verteile die Gegenstände und gib jeder Figur mindestens einen."
        }
        return FrostCard {
            Label("WÜRFELSTATUS", systemImage: "dice")
                .font(.caption.weight(.bold))
                .foregroundStyle(FrostTheme.quiet)
            Text(message)
                .font(.caption)
                .foregroundStyle(.white.opacity(0.82))
                .fixedSize(horizontal: false, vertical: true)
        }
    }

    @ViewBuilder
    private func materialLinks(for step: GuideStep) -> some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(([step.handoutID].compactMap { $0 } + step.handoutIDs), id: \.self) { handoutID in
                    NavigationLink(destination: HandoutPreviewView(handoutID: handoutID)) {
                        Label(handoutID, systemImage: "doc.text")
                    }
                    .buttonStyle(.bordered)
                }
                if let scene = content.scene(for: step.sceneID) {
                    ForEach(content.maps(for: scene)) { map in
                        NavigationLink(destination: MapDetailView(map: map, showSpoilers: true)) {
                            Label("Karte", systemImage: "map")
                        }
                        .buttonStyle(.bordered)
                    }
                }
                ForEach(([step.npcID].compactMap { $0 } + step.npcIDs), id: \.self) { npcID in
                    NavigationLink(destination: NPCDossierView(npcID: npcID)) {
                        Label(content.manifest.npcs.first(where: { $0.id == npcID })?.name ?? "NPC", systemImage: "person.crop.circle")
                    }
                    .buttonStyle(.bordered)
                }
                if let cueID = step.audioCueID,
                   !(cueID == "SFX09" && session.selectedEndingID != "E03"),
                   let cue = content.cue(for: cueID) {
                    Button {
                        audio.play(cue)
                    } label: {
                        Label("Sound", systemImage: "speaker.wave.2")
                    }
                    .buttonStyle(.bordered)
                }
            }
            .tint(FrostTheme.cobalt)
        }
    }

    private var finaleModePicker: some View {
        VStack(alignment: .leading, spacing: 8) {
            SectionLabel(title: "Finale-Modus")
            Picker("Finale-Modus", selection: Binding(
                get: { session.finaleMode },
                set: { session.setFinaleMode($0) }
            )) {
                Text("Geführt").tag("guided")
                Text("Voller Kampf").tag("combat")
            }
            .pickerStyle(.segmented)
            Text(session.finaleMode == "combat"
                 ? "Danach nutzt du Initiative, Angriff, Parade und Schaden nach den HTBAH-Kurzregeln."
                 : "Die App führt dich durch wenige Proben. Es gibt keine Gegner-Tabelle und keinen Zwangskampf.")
                .font(.caption)
                .foregroundStyle(FrostTheme.quiet)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(12)
        .background(FrostTheme.ink.opacity(0.36), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
    }

    private var doorStateControl: some View {
        let isOpen = session.doorStates["inn.guestroom"] ?? true
        return HStack(alignment: .center, spacing: 10) {
            Image(systemName: isOpen ? "door.left.hand.open" : "door.left.hand.closed")
                .foregroundStyle(isOpen ? FrostTheme.cobalt : FrostTheme.warning)
            VStack(alignment: .leading, spacing: 2) {
                Text(isOpen ? "Gästezimmer: offen" : "Gästezimmer: von außen verriegelt")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.white)
                Text(isOpen ? "Beim Schlafengehen schließen und SFX03 einmal spielen." : "Alternativen bleiben offen: Fenster, Elara oder Werkzeug.")
                    .font(.caption)
                    .foregroundStyle(FrostTheme.quiet)
                    .fixedSize(horizontal: false, vertical: true)
            }
            Spacer()
            Button(isOpen ? "Schließen" : "Öffnen") {
                session.setDoor("inn.guestroom", isOpen: !isOpen)
                if isOpen, let cue = content.cue(for: "SFX03") {
                    audio.play(cue)
                }
            }
            .buttonStyle(.bordered)
        }
        .padding(12)
        .background(FrostTheme.ink.opacity(0.36), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
    }

    private func optionsPanel(_ step: GuideStep) -> some View {
        VStack(alignment: .leading, spacing: 9) {
            SectionLabel(title: step.kind == .choice ? "Wähle nach der Spielerentscheidung" : "Weiter")
            ForEach(availableOptions(for: step)) { option in
                Button { choose(option, from: step) } label: {
                    HStack(alignment: .top, spacing: 11) {
                        Image(systemName: "arrow.right.circle.fill")
                            .foregroundStyle(FrostTheme.cobalt)
                        VStack(alignment: .leading, spacing: 3) {
                            Text(option.title)
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(.white)
                            Text(option.detail)
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
        }
    }

    private func availableOptions(for step: GuideStep) -> [GuideOption] {
        guard ["S03", "S04", "S05"].contains(step.sceneID) else { return step.options }
        let visited = session.completedSceneIDs.union(Set([session.currentSceneID]))
        let investigativeVisits = visited.intersection(Set(["S03", "S04", "S05"])).count
        return step.options.filter { option in
            option.destinationSceneID != "S06" || investigativeVisits >= 2
        }
    }

    private var quickAccess: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 10) {
                NavigationLink(destination: MaterialsView()) {
                    Label("Materialien", systemImage: "folder")
                }
                .buttonStyle(.bordered)
                NavigationLink(destination: InventoryView()) {
                    Label("Ausrüstung", systemImage: "shippingbox")
                }
                .buttonStyle(.bordered)
                NavigationLink(destination: CaseFileView()) {
                    Label("Fakten", systemImage: "magnifyingglass")
                }
                .buttonStyle(.bordered)
                NavigationLink(destination: RulesView()) {
                    Label("Regeln", systemImage: "dice")
                }
                .buttonStyle(.bordered)
            }
        }
        .tint(FrostTheme.cobalt)
    }

    private var sessionNote: some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 8) {
                SectionLabel(title: "Tischnotiz")
                TextEditor(text: session.sceneNoteBinding(for: session.currentSceneID))
                    .font(.subheadline)
                    .foregroundStyle(.white)
                    .scrollContentBackground(.hidden)
                    .frame(minHeight: 90)
                    .overlay(alignment: .topLeading) {
                        if session.sceneNoteBinding(for: session.currentSceneID).wrappedValue.isEmpty {
                            Text("Was ist gerade passiert? Was bleibt offen?")
                                .font(.subheadline)
                                .foregroundStyle(FrostTheme.quiet)
                                .padding(.top, 8)
                                .allowsHitTesting(false)
                        }
                    }
            }
        }
    }

    private var emptyFlow: some View {
        FrostCard {
            Label("Für diesen Abschnitt gibt es keinen weiteren Schritt.", systemImage: "checkmark.seal")
                .foregroundStyle(FrostTheme.frost)
        }
    }

    private func choose(_ option: GuideOption, from step: GuideStep) {
        if let endingID = option.endingID {
            session.setSelectedEnding(endingID)
            advance(step)
        } else if let destination = option.destinationSceneID {
            let needsConfirmation = session.completedSceneIDs.contains(destination)
            if needsConfirmation {
                pendingDestination = destination
                showBranchChangeConfirmation = true
            } else {
                move(to: destination, resettingDependentPath: false)
            }
        }
    }

    private func move(to destination: String, resettingDependentPath: Bool) {
        audio.stopLayer("ambient", fadeMilliseconds: 600)
        if let step = currentStep,
           let cueID = step.audioCueID,
           let cue = content.cue(for: cueID),
           cue.mode == "loop" {
            audio.play(cue)
        }
        if resettingDependentPath {
            session.advanceToScene(destination, from: session.currentSceneID)
            session.resetDependentPath(from: destination)
        } else {
            session.advanceToScene(destination, from: session.currentSceneID)
        }
        pendingDestination = nil
    }

    private func advance(_ step: GuideStep) {
        guard canAdvance(step) else { return }
        if step.id == "S08_NEXT" {
            session.finishGuidedSession()
            if let onExit {
                onExit()
            } else {
                dismiss()
            }
            return
        }
        if step.id == "S01_ITEMS" {
            session.discoverItems(content.guideItems.map(\.id))
        }
        let guaranteedClues: [String: Set<String>] = [
            "S01_CLUE": ["C01", "C02"],
            "S02_CLUE": ["C03", "C04"],
            "S03_CLUE": ["C05"],
            "S04_CLUE": ["C07"],
            "S05_CLUE": ["C08", "C09", "C11"],
            "S06_CLUE": ["C06", "C10"]
        ]
        if let clues = guaranteedClues[step.id] {
            session.checkedClueIDs.formUnion(clues)
        } else if let clueID = step.clueID {
            session.checkedClueIDs.insert(clueID)
        }
        let count = steps.count
        session.advanceGuideStep(in: session.currentSceneID, stepID: step.id, stepCount: count)
    }

    private func stepColor(_ kind: GuideStepKind) -> Color {
        switch kind {
        case .readAloud: return FrostTheme.frost
        case .gmInfo: return FrostTheme.warning
        case .playerAction: return FrostTheme.cobalt
        case .trigger, .roll, .clue, .choice, .next, .itemSearch, .itemDistribution: return FrostTheme.accent
        }
    }

    private func stepBackground(_ kind: GuideStepKind) -> Color {
        switch kind {
        case .readAloud: return FrostTheme.panelRaised
        case .gmInfo: return FrostTheme.warning.opacity(0.12)
        case .roll: return FrostTheme.accent.opacity(0.14)
        default: return FrostTheme.panel
        }
    }
}

struct RollHelperView: View {
    private struct ItemEffectOption: Identifiable {
        let item: AdventureItem
        let effect: ItemEffect

        var id: String { "\(item.id):\(effect.id)" }
    }

    let step: GuideStep
    let selectedEndingID: String?
    let onResult: (RollEvaluator.Result, RollConsequence?, [ItemUseSelection]) -> Void
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var session: SessionStore
    @Environment(\.dismiss) private var dismiss
    @State private var targetText = "50"
    @State private var rollText = ""
    @State private var result: RollEvaluator.Result?
    @State private var selectedConsequenceID: String?
    @State private var selectedItemEffectIDs: [String: String] = [:]
    @State private var validationMessage: String?

    private var roll: RollSpec? { step.roll }

    private func consequences(for spec: RollSpec) -> [RollConsequence] {
        let available = spec.failureConsequences.filter { $0.isAvailable(for: selectedEndingID) }
        return available.isEmpty ? spec.failureConsequences : available
    }

    private func itemEffects(timing: ItemEffectTiming, consequenceID: String? = nil) -> [ItemEffectOption] {
        content.guideItems.flatMap { item in
            guard session.ownerIndex(for: item.id) != nil, session.remainingUses(for: item) > 0 else { return [ItemEffectOption]() }
            return item.effects.compactMap { effect in
                guard effect.timing == timing,
                      effect.isAvailable(for: step.id, endingID: selectedEndingID),
                      effect.consequenceIDs.isEmpty || (consequenceID.map(effect.consequenceIDs.contains) ?? false) else { return nil }
                return ItemEffectOption(item: item, effect: effect)
            }
        }
    }

    private var beforeRollEffects: [ItemEffectOption] {
        itemEffects(timing: .beforeRoll)
    }

    private var activeModifier: Int {
        beforeRollEffects.reduce(0) { total, option in
            selectedItemEffectIDs[option.item.id] == option.effect.id ? total + (option.effect.modifier ?? 0) : total
        }
    }

    private func toggleItemEffect(_ option: ItemEffectOption) {
        if selectedItemEffectIDs[option.item.id] == option.effect.id {
            selectedItemEffectIDs.removeValue(forKey: option.item.id)
        } else {
            selectedItemEffectIDs[option.item.id] = option.effect.id
        }
        if option.effect.timing == .beforeRoll {
            result = nil
            selectedConsequenceID = nil
        }
        validationMessage = nil
    }

    private func selectedItemUses(for consequence: RollConsequence?) -> [ItemUseSelection] {
        let options = itemEffects(timing: .beforeRoll) + itemEffects(timing: .afterFailure, consequenceID: consequence?.id)
        return options.compactMap { option in
            guard selectedItemEffectIDs[option.item.id] == option.effect.id else { return nil }
            return ItemUseSelection(itemID: option.item.id, effectID: option.effect.id)
        }
    }

    private func ownerName(for item: AdventureItem) -> String {
        guard let index = session.ownerIndex(for: item.id), session.playerNames.indices.contains(index) else { return "Gruppe" }
        let name = session.playerNames[index].trimmingCharacters(in: .whitespacesAndNewlines)
        return name.isEmpty ? "Figur \(index + 1)" : name
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    if let roll {
                        FrostCard {
                            VStack(alignment: .leading, spacing: 8) {
                                SectionLabel(title: "W100-PROBE")
                                Text(roll.ability)
                                    .font(.title2.weight(.bold))
                                    .foregroundStyle(FrostTheme.frost)
                                Text("\(roll.actor) würfelt \(roll.die). \(roll.target)")
                                    .font(.subheadline)
                                    .foregroundStyle(FrostTheme.quiet)
                                    .fixedSize(horizontal: false, vertical: true)
                                Text(roll.modifier)
                                    .font(.caption)
                                    .foregroundStyle(FrostTheme.warning)
                            }
                        }
                        input("Basis-Zielwert", text: $targetText, prompt: "z. B. 60")
                        input("Gewürfeltes Ergebnis", text: $rollText, prompt: "1 bis 100")
                        Text("Trage den normalen Fähigkeitswert ein. Die App würfelt nicht selbst.")
                            .font(.caption)
                            .foregroundStyle(FrostTheme.quiet)
                            .fixedSize(horizontal: false, vertical: true)
                        if !beforeRollEffects.isEmpty {
                            itemEffectSelection(title: "AUSRÜSTUNG VOR DER PROBE", options: beforeRollEffects)
                        }
                        if activeModifier > 0 {
                            Label("Effektiver Zielwert: Basis +\(activeModifier) = maximal 100", systemImage: "plus.circle.fill")
                                .font(.caption.weight(.semibold))
                                .foregroundStyle(FrostTheme.accent)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        if let validationMessage {
                            Label(validationMessage, systemImage: "exclamationmark.triangle.fill")
                                .font(.caption)
                                .foregroundStyle(FrostTheme.warning)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        Button("Ergebnis auswerten") { evaluate(roll) }
                            .buttonStyle(.borderedProminent)
                            .tint(FrostTheme.cobalt)
                            .frame(maxWidth: .infinity, minHeight: 44)
                        if let result {
                            resultCard(result, spec: roll)
                        }
                    }
                }
                .padding(20)
                .safeAreaPadding(.bottom, 24)
            }
            .background(FrostTheme.ink.ignoresSafeArea())
            .navigationTitle("Würfelhelfer")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Fertig") { dismiss() }
                }
            }
        }
        .preferredColorScheme(.dark)
    }

    private func input(_ title: String, text: Binding<String>, prompt: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            SectionLabel(title: title)
            TextField(prompt, text: text)
                .keyboardType(.numberPad)
                .textFieldStyle(.roundedBorder)
                .frame(minHeight: 44)
        }
    }

    private func itemEffectSelection(title: String, options: [ItemEffectOption]) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            SectionLabel(title: title)
            Text("Nur der besitzende Spieler kann den Einsatz ansagen. Die Anwendung wird erst beim Übernehmen verbraucht.")
                .font(.caption)
                .foregroundStyle(FrostTheme.quiet)
                .fixedSize(horizontal: false, vertical: true)
            ForEach(options) { option in
                let selected = selectedItemEffectIDs[option.item.id] == option.effect.id
                Button {
                    toggleItemEffect(option)
                } label: {
                    HStack(alignment: .top, spacing: 9) {
                        Image(systemName: selected ? "checkmark.circle.fill" : "circle")
                            .foregroundStyle(selected ? FrostTheme.accent : FrostTheme.quiet)
                            .font(.title3)
                        VStack(alignment: .leading, spacing: 3) {
                            Text("\(option.item.title) · \(option.effect.title)")
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(.white)
                            Text("Besitz: \(ownerName(for: option.item)) · noch \(session.remainingUses(for: option.item)) Anwendung(en)")
                                .font(.caption2)
                                .foregroundStyle(FrostTheme.cobalt)
                            Text(option.effect.detail)
                                .font(.caption)
                                .foregroundStyle(FrostTheme.quiet)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        Spacer(minLength: 0)
                    }
                    .frame(maxWidth: .infinity, minHeight: 44, alignment: .leading)
                    .padding(10)
                    .background(selected ? FrostTheme.accent.opacity(0.18) : FrostTheme.ink.opacity(0.42), in: RoundedRectangle(cornerRadius: 11, style: .continuous))
                    .overlay(RoundedRectangle(cornerRadius: 11, style: .continuous).stroke(selected ? FrostTheme.accent : FrostTheme.line, lineWidth: 1))
                }
                .buttonStyle(.plain)
                .accessibilityAddTraits(selected ? .isSelected : [])
            }
        }
        .padding(10)
        .background(FrostTheme.ink.opacity(0.32), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
    }

    private func evaluate(_ spec: RollSpec) {
        guard let baseTarget = Int(targetText), let rolled = Int(rollText) else {
            validationMessage = "Bitte Zielwert und Würfelergebnis als ganze Zahlen eintragen."
            result = nil
            return
        }
        guard (1...100).contains(baseTarget), (1...100).contains(rolled) else {
            validationMessage = "Beide Werte müssen zwischen 1 und 100 liegen."
            result = nil
            return
        }
        validationMessage = nil
        let target = min(100, baseTarget + activeModifier)
        let evaluated = RollEvaluator.evaluate(roll: rolled, target: target, begabung: spec.begabung)
        result = evaluated
        let availableConsequences = evaluated.isSuccess ? [] : consequences(for: spec)
        selectedConsequenceID = availableConsequences.count == 1 ? availableConsequences.first?.id : nil
    }

    private func resultCard(_ result: RollEvaluator.Result, spec: RollSpec) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Label(result.label, systemImage: result.isSuccess ? "checkmark.circle.fill" : "xmark.circle.fill")
                .font(.headline)
                .foregroundStyle(result.isSuccess ? FrostTheme.accent : FrostTheme.warning)
            Text("\(result.roll) gegen \(result.target)")
                .font(.subheadline)
                .foregroundStyle(.white)
            Text(result.isCriticalFailure ? spec.criticalFailure : (result.isCriticalSuccess ? spec.critical : (result.isSuccess ? spec.success : spec.failure)))
                .font(.subheadline)
                .foregroundStyle(FrostTheme.quiet)
                .fixedSize(horizontal: false, vertical: true)
            if !result.isSuccess {
                let availableConsequences = consequences(for: spec)
                if availableConsequences.isEmpty {
                    Label("Folge: \(spec.failure)", systemImage: "arrow.triangle.branch")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(FrostTheme.warning)
                        .fixedSize(horizontal: false, vertical: true)
                } else {
                    VStack(alignment: .leading, spacing: 8) {
                        SectionLabel(title: availableConsequences.count == 1 ? "FOLGE BESTÄTIGEN" : "WAS PASSIERT JETZT?")
                        Text(availableConsequences.count == 1 ? "Bestätige die Folge für die Runde." : "Wähle die Folge, die du am Tisch ausspielst.")
                            .font(.caption)
                            .foregroundStyle(FrostTheme.quiet)
                            .fixedSize(horizontal: false, vertical: true)
                        ForEach(availableConsequences) { consequence in
                            let isSelected = selectedConsequenceID == consequence.id
                            Button {
                                selectedConsequenceID = consequence.id
                            } label: {
                                HStack(alignment: .top, spacing: 10) {
                                    Image(systemName: isSelected ? "checkmark.circle.fill" : "circle")
                                        .foregroundStyle(isSelected ? FrostTheme.accent : FrostTheme.quiet)
                                        .font(.title3)
                                    VStack(alignment: .leading, spacing: 3) {
                                        Text(consequence.title)
                                            .font(.subheadline.weight(.semibold))
                                            .foregroundStyle(.white)
                                        Text(consequence.detail)
                                            .font(.caption)
                                            .foregroundStyle(FrostTheme.quiet)
                                            .fixedSize(horizontal: false, vertical: true)
                                        if let effectText = effectText(for: consequence.effect) {
                                            Text(effectText)
                                                .font(.caption2.weight(.semibold))
                                                .foregroundStyle(FrostTheme.warning)
                                        }
                                    }
                                    Spacer(minLength: 0)
                                }
                                .frame(maxWidth: .infinity, minHeight: 44, alignment: .leading)
                                .padding(10)
                                .background(isSelected ? FrostTheme.accent.opacity(0.18) : FrostTheme.ink.opacity(0.42), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
                                .overlay(RoundedRectangle(cornerRadius: 12, style: .continuous).stroke(isSelected ? FrostTheme.accent : FrostTheme.line, lineWidth: 1))
                            }
                            .buttonStyle(.plain)
                            .accessibilityAddTraits(isSelected ? .isSelected : [])
                        }
                        if let selectedConsequence = availableConsequences.first(where: { $0.id == selectedConsequenceID }) {
                            let protectionOptions = itemEffects(timing: .afterFailure, consequenceID: selectedConsequence.id)
                            if !protectionOptions.isEmpty {
                                itemEffectSelection(title: "AUSRÜSTUNG FÜR DIE FOLGE", options: protectionOptions)
                            }
                        }
                    }
                    .padding(.top, 4)
                }
            }
            Text(spec.reroll)
                .font(.caption)
                .foregroundStyle(FrostTheme.cobalt)
            let availableConsequences = result.isSuccess ? [] : consequences(for: spec)
            let selectedConsequence = availableConsequences.first { $0.id == selectedConsequenceID }
            Button(result.isSuccess ? "Ergebnis übernehmen" : availableConsequences.isEmpty ? "Ergebnis übernehmen" : "Konsequenz übernehmen") {
                guard result.isSuccess || availableConsequences.isEmpty || selectedConsequence != nil else { return }
                onResult(result, selectedConsequence, selectedItemUses(for: selectedConsequence))
                dismiss()
            }
            .buttonStyle(.borderedProminent)
            .tint(result.isSuccess ? FrostTheme.accent : FrostTheme.warning)
            .frame(maxWidth: .infinity, minHeight: 44)
            .disabled(!result.isSuccess && !availableConsequences.isEmpty && selectedConsequence == nil)
        }
        .padding(15)
        .background(FrostTheme.panel, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
    }

    private func effectText(for effect: RollConsequenceEffect?) -> String? {
        if let threatDelta = effect?.threatDelta {
            return "Dorfspannung \(threatDelta >= 0 ? "+" : "")\(threatDelta)"
        }
        if let minimumThreat = effect?.minimumThreat {
            return "Dorfspannung mindestens \(minimumThreat)"
        }
        return nil
    }
}

enum ReadAloudMode: Equatable {
    case start
    case complete
    case cancel
}

struct ReadAloudCueSheet: View {
    let step: GuideStep
    let cue: AudioCue?
    let onComplete: (ReadAloudMode) -> Void
    @Environment(\.dismiss) private var dismiss
    @State private var hasStarted = false
    @State private var didClose = false

    private func close(mode: ReadAloudMode) {
        guard !didClose else { return }
        didClose = true
        onComplete(mode)
        dismiss()
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    FrostCard {
                        VStack(alignment: .leading, spacing: 9) {
                            SectionLabel(title: "JETZT VORLESEN")
                            Text(step.title)
                                .font(.title2.weight(.bold))
                                .foregroundStyle(FrostTheme.frost)
                            Text("Lies den Text erst vor, wenn die Gruppe aufmerksam ist. Der Leitstand senkt die Musik ab und startet den bestätigten Cue.")
                                .font(.subheadline)
                                .foregroundStyle(FrostTheme.quiet)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }

                    FrostCard {
                        VStack(alignment: .leading, spacing: 10) {
                            Text(step.body)
                                .font(.body.italic())
                                .foregroundStyle(.white.opacity(0.94))
                                .fixedSize(horizontal: false, vertical: true)
                            if let cue {
                                Divider().overlay(FrostTheme.quiet.opacity(0.25))
                                Label("Sound: \(cue.title)", systemImage: cue.iconName)
                                    .font(.subheadline.weight(.semibold))
                                    .foregroundStyle(FrostTheme.cobalt)
                                Text(cue.playWhen)
                                    .font(.caption)
                                    .foregroundStyle(FrostTheme.quiet)
                            } else {
                                Label("Kein eigener Cue – nur die Grundmusik weiterlaufen lassen.", systemImage: "music.note")
                                    .font(.caption)
                                    .foregroundStyle(FrostTheme.quiet)
                            }
                        }
                    }

                    Button {
                        if hasStarted {
                            close(mode: .complete)
                        } else {
                            onComplete(.start)
                            hasStarted = true
                        }
                    } label: {
                        Label(hasStarted ? "Vorgelesen – weiter" : "Sound starten und vorlesen", systemImage: hasStarted ? "checkmark.circle.fill" : "play.fill")
                            .font(.headline)
                            .foregroundStyle(FrostTheme.ink)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                            .background(FrostTheme.frost, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
                    }

                    Button {
                        close(mode: .complete)
                    } label: {
                        Text(hasStarted ? "Ohne weiteren Sound weiter" : "Nur als vorgelesen markieren")
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(FrostTheme.quiet)
                            .frame(maxWidth: .infinity, minHeight: 44)
                    }
                }
                .padding(20)
                .safeAreaPadding(.bottom, 24)
            }
            .background(FrostTheme.ink.ignoresSafeArea())
            .navigationTitle("Vorlese-Moment")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Abbrechen") {
                        close(mode: .cancel)
                    }
                }
            }
            .onDisappear {
                // Covers swipe-to-dismiss and the interactive back gesture.
                if !didClose {
                    didClose = true
                    onComplete(.cancel)
                }
            }
        }
        .preferredColorScheme(.dark)
    }
}

struct CombatReferenceView: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    FrostCard {
                        VStack(alignment: .leading, spacing: 8) {
                            SectionLabel(title: "OPTIONALER KAMPF")
                            Text("Kampf am Tisch")
                                .font(.title2.weight(.bold))
                                .foregroundStyle(FrostTheme.frost)
                            Text("Nutze diese Kurzreferenz nur, wenn die Gruppe den finalen Konflikt wirklich ausspielen möchte. Für ein schnelleres Finale wechselst du zurück in die geführte Gefahrenszene.")
                                .font(.subheadline)
                                .foregroundStyle(FrostTheme.quiet)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                    combatRule("1 · Reihenfolge", "Alle würfeln 1W10 plus den Begabungswert Handeln. Die höchste Zahl handelt zuerst. Bei Überraschung setzt die betroffene Figur die erste Runde aus.")
                    combatRule("2 · Angriff", "Angreifer würfelt eine passende Fertigkeitsprobe mit W100. Bei Erfolg trifft der Angriff; bei Misserfolg entsteht kein Schaden.")
                    combatRule("3 · Parade", "Eine Figur darf einmal pro Runde mit Handeln parieren. Kritische Angriffe und Schusswaffen sind nicht parierbar.")
                    combatRule("4 · Schaden", "Würfle die zur Waffe passende Anzahl W10. Kritische Angriffe verdoppeln den Schaden. Ziehe die Summe von den LP ab.")
                    combatRule("5 · LP-Zustände", "Unter 10 LP ist eine Figur bewusstlos, bei 0 LP tot. Mehr als 60 Schaden in einem einzelnen Treffer macht ebenfalls bewusstlos.")
                    combatRule("6 · Ende", "Der Knochenhirsch flieht, sobald die Bindung bricht. Spiele SFX09 nur bei E03 und öffne danach den Epilog.")
                    FrostCard {
                        Label("Keine Gegnerwerte im Kanon", systemImage: "info.circle")
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(FrostTheme.warning)
                        Text("Für dieses Abenteuer sind keine festen Knochenhirsch-Werte definiert. Entscheide Trefferpunkte und Fertigkeitswerte passend zur Gruppe oder nutze den geführten Modus.")
                            .font(.caption)
                            .foregroundStyle(FrostTheme.quiet)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
                .padding(20)
                .safeAreaPadding(.bottom, 24)
            }
            .background(FrostTheme.ink.ignoresSafeArea())
            .navigationTitle("Kampf-Kurzreferenz")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Fertig") { dismiss() }
                }
            }
        }
        .preferredColorScheme(.dark)
    }

    private func combatRule(_ title: String, _ body: String) -> some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 6) {
                SectionLabel(title: title)
                Text(body)
                    .font(.body)
                    .foregroundStyle(.white.opacity(0.9))
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }
}
