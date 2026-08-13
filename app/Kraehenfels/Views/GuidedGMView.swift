import SwiftUI

struct GMStartView: View {
    @EnvironmentObject private var session: SessionStore
    @EnvironmentObject private var audio: AudioEngine
    @EnvironmentObject private var content: ContentStore
    @State private var startSession = false

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
            .safeAreaPadding(.bottom, 88)
        }
        .background(FrostTheme.ink.ignoresSafeArea())
        .navigationTitle("Spiel starten")
        .navigationBarTitleDisplayMode(.inline)
        .navigationDestination(isPresented: $startSession) {
            GuidedGMView()
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
                Text("\(session.setupChecks.count)/\(GuidedFlowCatalog.setupItems.count)")
                    .font(.caption.monospaced().weight(.bold))
                    .foregroundStyle(FrostTheme.cobalt)
            }
            ForEach(GuidedFlowCatalog.setupItems, id: \.id) { item in
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
            SectionLabel(title: "Die drei Reisenden")
            Text("Diese Figuren sind sofort spielbereit. Lies nur den kurzen Hook vor; die übrigen Informationen bleiben bei dir.")
                .font(.subheadline)
                .foregroundStyle(FrostTheme.quiet)
            ForEach(GuidedFlowCatalog.characters) { character in
                FrostCard {
                    HStack(alignment: .top, spacing: 12) {
                        Text(String(character.name.prefix(1)))
                            .font(.title2.weight(.bold))
                            .foregroundStyle(FrostTheme.ink)
                            .frame(width: 42, height: 42)
                            .background(FrostTheme.frost, in: Circle())
                        VStack(alignment: .leading, spacing: 4) {
                            Text(character.name)
                                .font(.headline)
                                .foregroundStyle(.white)
                            Text(character.role)
                                .font(.caption.weight(.semibold))
                                .foregroundStyle(FrostTheme.cobalt)
                            Text(character.hook)
                                .font(.caption)
                                .foregroundStyle(FrostTheme.quiet)
                                .fixedSize(horizontal: false, vertical: true)
                            Text(character.skills.joined(separator: " · "))
                                .font(.caption2.monospaced())
                                .foregroundStyle(FrostTheme.frost.opacity(0.82))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        Spacer()
                    }
                }
            }
        }
    }

    private var tableBriefing: some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 8) {
                Label("Was du den Spielern sagst", systemImage: "person.3.fill")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(FrostTheme.frost)
                Text("Ihr seid Reisende im Schwarzwald des Jahres 1890. Eine Kutschenpanne zwingt euch nach Krähenfels. Ihr wisst noch nichts von einem Pakt. Ihr dürft jederzeit Fragen stellen, Orte wählen und eigene Lösungen versuchen.")
                    .font(.subheadline)
                    .foregroundStyle(.white.opacity(0.9))
                    .fixedSize(horizontal: false, vertical: true)
                Label("Nicht verraten: Knochenhirsch, Opferbuch, verdrehter Pakt und die drei Enden.", systemImage: "eye.slash.fill")
                    .font(.caption)
                    .foregroundStyle(FrostTheme.warning)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    private var startButton: some View {
        VStack(spacing: 9) {
            Button {
                session.playerNames = GuidedFlowCatalog.characters.map(\.name)
                session.beginGuidedSession()
                if let music = content.musicBed, !audio.isPlaying(music) {
                    audio.play(music)
                }
                startSession = true
            } label: {
                Label("Spielleiter-Modus starten", systemImage: "play.fill")
                    .font(.headline)
                    .foregroundStyle(FrostTheme.ink)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 15)
                    .background(FrostTheme.frost, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
            }
            Text("Du kannst die Vorbereitung auch später nachholen.")
                .font(.caption)
                .foregroundStyle(FrostTheme.quiet)
        }
    }
}

struct GuidedGMView: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var audio: AudioEngine
    @EnvironmentObject private var session: SessionStore
    @State private var rollStep: GuideStep?
    @State private var readAloudStep: GuideStep?
    @State private var showMaterials = false
    @State private var showRules = false
    @State private var showCombat = false
    @State private var showAudioPlan = false

    private var steps: [GuideStep] {
        let base = GuidedFlowCatalog.steps(for: session.currentSceneID)
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
                    } else {
                        actionButton(step)
                    }
                } else {
                    emptyFlow
                }
                quickAccess
                sessionNote
            }
            .padding(20)
            .safeAreaPadding(.bottom, 88)
        }
        .background(FrostTheme.ink.ignoresSafeArea())
        .navigationTitle(content.scene(for: session.currentSceneID)?.shortTitle ?? "Spielleitung")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Menu {
                    Button("Materialien öffnen", systemImage: "folder") { showMaterials = true }
                    Button("Regeln öffnen", systemImage: "dice") { showRules = true }
                    Button("Schritt zurück", systemImage: "arrow.left") { stepBack() }
                } label: {
                    Image(systemName: "ellipsis.circle")
                        .foregroundStyle(FrostTheme.frost)
                }
                .accessibilityLabel("Spielleiter-Werkzeuge")
            }
        }
        .sheet(item: $rollStep) { step in
            RollHelperView(step: step) { result in
                if step.id == "S07_DANGER" {
                    let state = session.recordFinaleRoll(result)
                    if state.isResolved {
                        advance(step)
                    }
                    return
                }
                session.recordRoll(stepID: step.id, result: result)
                if step.id == "S02_ROLL", !result.isSuccess {
                    session.setThreatLevel(session.threatLevel + 1)
                }
                if step.id == "S06_ROLL", !result.isSuccess {
                    session.setThreatLevel(4)
                }
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
        .navigationDestination(isPresented: $showMaterials) { MaterialsView() }
        .navigationDestination(isPresented: $showRules) { RulesView() }
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
                                    .frame(width: 34, height: 34)
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
                        .foregroundStyle(.green)
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
                rollSummary(roll)
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
                .tint(.green)
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

    private func rollSummary(_ roll: RollSpec) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Label("Wer: \(roll.actor)", systemImage: "person.fill")
            Label("\(roll.die) auf \(roll.ability)", systemImage: "dice.fill")
            Label("Ziel: \(roll.target)", systemImage: "scope")
            Label("Erfolg: \(roll.success)", systemImage: "checkmark.circle")
            Label("Misserfolg: \(roll.failure)", systemImage: "xmark.circle")
            Label(roll.modifier, systemImage: "plusminus")
            Label(roll.required ? "Diese Probe ist für den Schritt vorgesehen." : "Optional: nur bei einer riskanten Handlung würfeln.", systemImage: roll.required ? "exclamationmark.circle" : "questionmark.circle")
            if roll.guaranteedClue {
                Label("Pflicht-Hinweis bleibt unabhängig vom Ergebnis erhalten.", systemImage: "lock.open.fill")
            }
        }
        .font(.caption)
        .foregroundStyle(.white.opacity(0.82))
        .fixedSize(horizontal: false, vertical: true)
        .padding(12)
        .background(FrostTheme.ink.opacity(0.42), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
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

    private func actionButton(_ step: GuideStep) -> some View {
        VStack(spacing: 8) {
            Button {
                if step.kind == .readAloud {
                    readAloudStep = step
                } else if step.kind == .roll, step.roll != nil {
                    rollStep = step
                } else {
                    advance(step)
                }
            } label: {
                let title = step.kind == .readAloud
                    ? "Sound vorbereiten und vorlesen"
                    : step.kind == .roll ? "Würfelhelfer öffnen" : step.actionLabel
                let icon = step.kind == .readAloud
                    ? "quote.bubble.fill"
                    : step.kind == .roll ? "dice.fill" : "arrow.right"
                Label(title, systemImage: icon)
                    .font(.headline)
                    .foregroundStyle(FrostTheme.ink)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 14)
                    .background(FrostTheme.frost, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
            }
            if step.kind == .roll, step.roll?.required == false {
                Button("Ohne Probe weiter") { advance(step) }
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(FrostTheme.quiet)
                    .frame(maxWidth: .infinity, minHeight: 40)
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
        HStack(spacing: 10) {
            NavigationLink(destination: MaterialsView()) {
                Label("Materialien", systemImage: "folder")
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
            audio.stopLayer("ambient", fadeMilliseconds: 600)
            if let cueID = step.audioCueID,
               let cue = content.cue(for: cueID),
               cue.mode == "loop" {
                audio.play(cue)
            }
            session.advanceToScene(destination, from: session.currentSceneID)
        }
    }

    private func advance(_ step: GuideStep) {
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

    private func stepBack() {
        guard session.guidedStepIndex > 0 else { return }
        session.guidedStepIndex -= 1
    }

    private func stepColor(_ kind: GuideStepKind) -> Color {
        switch kind {
        case .readAloud: return FrostTheme.frost
        case .gmInfo: return FrostTheme.warning
        case .playerAction: return FrostTheme.cobalt
        case .trigger: return .orange
        case .roll: return .mint
        case .clue: return .cyan
        case .choice: return .purple
        case .next: return .green
        }
    }

    private func stepBackground(_ kind: GuideStepKind) -> Color {
        switch kind {
        case .readAloud: return FrostTheme.panelRaised
        case .gmInfo: return FrostTheme.warning.opacity(0.12)
        case .roll: return Color.blue.opacity(0.16)
        default: return FrostTheme.panel
        }
    }
}

struct RollHelperView: View {
    let step: GuideStep
    let onResult: (RollEvaluator.Result) -> Void
    @Environment(\.dismiss) private var dismiss
    @State private var targetText = "50"
    @State private var rollText = ""
    @State private var result: RollEvaluator.Result?
    @State private var validationMessage: String?

    private var roll: RollSpec? { step.roll }

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
                        input("Zielwert", text: $targetText, prompt: "z. B. 60")
                        input("Gewürfeltes Ergebnis", text: $rollText, prompt: "1 bis 100")
                        Text("Trage den Wert bereits inklusive eines passenden Modifikators ein. Die App würfelt nicht selbst.")
                            .font(.caption)
                            .foregroundStyle(FrostTheme.quiet)
                            .fixedSize(horizontal: false, vertical: true)
                        if let validationMessage {
                            Label(validationMessage, systemImage: "exclamationmark.triangle.fill")
                                .font(.caption)
                                .foregroundStyle(FrostTheme.warning)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        Button("Ergebnis auswerten") { evaluate(roll) }
                            .buttonStyle(.borderedProminent)
                            .tint(FrostTheme.cobalt)
                        if let result {
                            resultCard(result, spec: roll)
                        }
                    }
                }
                .padding(20)
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
        }
    }

    private func evaluate(_ spec: RollSpec) {
        guard let target = Int(targetText), let rolled = Int(rollText) else {
            validationMessage = "Bitte Zielwert und Würfelergebnis als ganze Zahlen eintragen."
            result = nil
            return
        }
        guard (1...100).contains(target), (1...100).contains(rolled) else {
            validationMessage = "Beide Werte müssen zwischen 1 und 100 liegen."
            result = nil
            return
        }
        validationMessage = nil
        result = RollEvaluator.evaluate(roll: rolled, target: target, begabung: spec.begabung)
    }

    private func resultCard(_ result: RollEvaluator.Result, spec: RollSpec) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Label(result.label, systemImage: result.isSuccess ? "checkmark.circle.fill" : "xmark.circle.fill")
                .font(.headline)
                .foregroundStyle(result.isSuccess ? .green : FrostTheme.warning)
            Text("\(result.roll) gegen \(result.target)")
                .font(.subheadline)
                .foregroundStyle(.white)
            Text(result.isCriticalSuccess ? spec.critical : (result.isSuccess ? spec.success : spec.failure))
                .font(.subheadline)
                .foregroundStyle(FrostTheme.quiet)
                .fixedSize(horizontal: false, vertical: true)
            Text(spec.reroll)
                .font(.caption)
                .foregroundStyle(FrostTheme.cobalt)
            Button("Ergebnis übernehmen") {
                onResult(result)
                dismiss()
            }
            .buttonStyle(.borderedProminent)
            .tint(result.isSuccess ? .green : FrostTheme.warning)
        }
        .padding(15)
        .background(FrostTheme.panel, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
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
                            onComplete(.complete)
                            dismiss()
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
                        onComplete(.complete)
                        dismiss()
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
                        onComplete(.cancel)
                        dismiss()
                    }
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
                    combatRule("1 · Reihenfolge", "Alle würfeln W10 + Handeln. Die höchste Zahl handelt zuerst. Bei Überraschung setzt die betroffene Figur die erste Runde aus.")
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
