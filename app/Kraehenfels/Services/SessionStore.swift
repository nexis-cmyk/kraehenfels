import SwiftUI

@MainActor
final class SessionStore: ObservableObject {
    enum FinaleRollState: Equatable {
        case ongoing(successes: Int, failures: Int)
        case resolved(success: Bool)

        var isResolved: Bool {
            if case .resolved = self { return true }
            return false
        }
    }

    struct GuidePosition: Codable, Equatable, Hashable {
        let sceneID: String
        let stepIndex: Int
    }

    private static let nightPhaseCount = 5

    private struct Snapshot: Codable {
        var playerNames: [String]
        var sessionNote: String
        var sceneNotes: [String: String]
        var nightPhaseIndex: Int?
        var currentSceneID: String
        var completedSceneIDs: [String]
        var checkedClueIDs: [String]
        var completedChecklistIDs: [String]
        var npcStates: [String: Int]
        var threatLevel: Int
        var selectedHooks: [String: String]
        var audioRatings: [String: Int]?
        var guidedStepIndex: Int?
        var completedGuideStepIDs: [String]?
        var setupChecks: [String]?
        var doorStates: [String: Bool]?
        var rollHistory: [String: String]?
        var rollResolutions: [RollResolutionRecord]?
        var selectedEndingID: String?
        var finaleMode: String?
        var finaleSuccesses: Int?
        var finaleFailures: Int?
        var finaleOutcome: String?
        var hasStartedSession: Bool?
        var guideHistory: [GuidePosition]?
        var discoveredItemIDs: [String]?
        var itemOwners: [String: Int]?
        var itemUseRecords: [ItemUseRecord]?
        var time: Int?
        var warmth: Int?
        var trust: Int?
        var injuries: Int?
        var combatState: CombatState?
    }

    private let storageKey = "kraehenfels.sessionJournal.v7"
    private let legacyV6StorageKey = "kraehenfels.sessionJournal.v6"
    private let legacyV5StorageKey = "kraehenfels.sessionJournal.v5"
    private let legacyV4StorageKey = "kraehenfels.sessionJournal.v4"
    private let defaults: UserDefaults
    private var shouldMigrateLegacyInventory = false

    @Published var playerNames: [String] {
        didSet { persist() }
    }

    @Published var sessionNote: String {
        didSet { persist() }
    }

    @Published private var sceneNotes: [String: String] {
        didSet { persist() }
    }

    @Published var nightPhaseIndex: Int {
        didSet { persist() }
    }

    @Published var currentSceneID: String {
        didSet { persist() }
    }

    @Published var completedSceneIDs: Set<String> {
        didSet { persist() }
    }

    @Published var checkedClueIDs: Set<String> {
        didSet { persist() }
    }

    @Published var completedChecklistIDs: Set<String> {
        didSet { persist() }
    }

    @Published var npcStates: [String: Int] {
        didSet { persist() }
    }

    @Published var threatLevel: Int {
        didSet { persist() }
    }

    @Published var selectedHooks: [String: String] {
        didSet { persist() }
    }

    @Published var audioRatings: [String: Int] {
        didSet { persist() }
    }

    @Published var guidedStepIndex: Int {
        didSet { persist() }
    }

    @Published private(set) var hasStartedSession: Bool {
        didSet { persist() }
    }

    @Published var completedGuideStepIDs: Set<String> {
        didSet { persist() }
    }

    @Published private(set) var guideHistory: [GuidePosition] {
        didSet { persist() }
    }

    @Published var setupChecks: Set<String> {
        didSet { persist() }
    }

    @Published var doorStates: [String: Bool] {
        didSet { persist() }
    }

    @Published var rollHistory: [String: String] {
        didSet { persist() }
    }

    @Published private(set) var rollResolutions: [RollResolutionRecord] {
        didSet { persist() }
    }

    @Published private(set) var discoveredItemIDs: Set<String> {
        didSet { persist() }
    }

    @Published var itemOwners: [String: Int] {
        didSet { persist() }
    }

    @Published private(set) var itemUseRecords: [ItemUseRecord] {
        didSet { persist() }
    }

    /// Accumulated time cost from failed actions. The value is deliberately
    /// bounded so a long table session remains readable at a glance.
    @Published private(set) var time: Int {
        didSet { persist() }
    }

    /// Remaining warmth on the shared track (0 means the group is freezing).
    @Published private(set) var warmth: Int {
        didSet { persist() }
    }

    /// Shared trust in the group's plan (0 means the plan is fractured).
    @Published private(set) var trust: Int {
        didSet { persist() }
    }

    /// Small injuries recorded by consequences. This is not a replacement for
    /// the character sheets; it is a reminder for the table.
    @Published private(set) var injuries: Int {
        didSet { persist() }
    }

    @Published private(set) var combatState: CombatState? {
        didSet { persist() }
    }

    @Published var selectedEndingID: String? {
        didSet { persist() }
    }

    @Published var finaleMode: String {
        didSet { persist() }
    }

    @Published private(set) var finaleSuccesses: Int {
        didSet { persist() }
    }

    @Published private(set) var finaleFailures: Int {
        didSet { persist() }
    }

    @Published private(set) var finaleOutcome: String? {
        didSet { persist() }
    }

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
        var storedSnapshot: (data: Data, key: String)?
        for key in [storageKey, legacyV6StorageKey, legacyV5StorageKey, legacyV4StorageKey] {
            if let data = defaults.data(forKey: key) {
                storedSnapshot = (data, key)
                break
            }
        }
        let loadedData = storedSnapshot?.data
        let loadedKey = storedSnapshot?.key
        if let data = loadedData,
           let snapshot = try? JSONDecoder().decode(Snapshot.self, from: data) {
            playerNames = Self.normalizedNames(snapshot.playerNames)
            sessionNote = snapshot.sessionNote
            sceneNotes = snapshot.sceneNotes
            nightPhaseIndex = Self.normalizedNightPhase(snapshot.nightPhaseIndex ?? 0)
            currentSceneID = snapshot.currentSceneID
            completedSceneIDs = Set(snapshot.completedSceneIDs)
            checkedClueIDs = Set(snapshot.checkedClueIDs)
            completedChecklistIDs = Set(snapshot.completedChecklistIDs)
            npcStates = snapshot.npcStates
            threatLevel = Self.normalizedThreat(snapshot.threatLevel)
            selectedHooks = snapshot.selectedHooks
            audioRatings = snapshot.audioRatings ?? [:]
            guidedStepIndex = max(0, snapshot.guidedStepIndex ?? 0)
            hasStartedSession = snapshot.hasStartedSession ?? false
            completedGuideStepIDs = Set(snapshot.completedGuideStepIDs ?? [])
            setupChecks = Set(snapshot.setupChecks ?? [])
            doorStates = snapshot.doorStates ?? [:]
            rollHistory = snapshot.rollHistory ?? [:]
            rollResolutions = snapshot.rollResolutions ?? []
            selectedEndingID = snapshot.selectedEndingID
            finaleMode = snapshot.finaleMode ?? "guided"
            finaleSuccesses = min(max(snapshot.finaleSuccesses ?? 0, 0), 2)
            finaleFailures = min(max(snapshot.finaleFailures ?? 0, 0), 2)
            finaleOutcome = snapshot.finaleOutcome
            guideHistory = snapshot.guideHistory ?? []
            discoveredItemIDs = Set(snapshot.discoveredItemIDs ?? [])
            itemOwners = snapshot.itemOwners ?? [:]
            itemUseRecords = snapshot.itemUseRecords ?? []
            time = Self.normalizedTime(snapshot.time ?? 0)
            warmth = Self.normalizedResource(snapshot.warmth ?? 3)
            trust = Self.normalizedResource(snapshot.trust ?? 3)
            injuries = Self.normalizedInjuries(snapshot.injuries ?? 0)
            combatState = snapshot.combatState
            shouldMigrateLegacyInventory = snapshot.hasStartedSession == true
                && snapshot.discoveredItemIDs == nil
                && snapshot.itemOwners == nil
                && snapshot.itemUseRecords == nil
        } else {
            playerNames = ["", "", ""]
            sessionNote = ""
            sceneNotes = [:]
            nightPhaseIndex = 0
            currentSceneID = "S01"
            completedSceneIDs = []
            checkedClueIDs = []
            completedChecklistIDs = []
            npcStates = [:]
            threatLevel = 0
            selectedHooks = [:]
            audioRatings = [:]
            guidedStepIndex = 0
            hasStartedSession = false
            completedGuideStepIDs = []
            setupChecks = []
            doorStates = [:]
            rollHistory = [:]
            rollResolutions = []
            selectedEndingID = nil
            finaleMode = "guided"
            finaleSuccesses = 0
            finaleFailures = 0
            finaleOutcome = nil
            guideHistory = []
            discoveredItemIDs = []
            itemOwners = [:]
            itemUseRecords = []
            time = 0
            warmth = 3
            trust = 3
            injuries = 0
            combatState = nil
        }

        if loadedKey != nil, loadedKey != storageKey, hasStartedSession {
            migrateActiveLegacySession()
        } else if defaults.data(forKey: storageKey) == nil, loadedData != nil {
            persist()
        }
    }

    func setNightPhase(_ index: Int) {
        nightPhaseIndex = Self.normalizedNightPhase(index)
    }

    func playerNameBinding(at index: Int) -> Binding<String> {
        Binding(
            get: { self.playerNames.indices.contains(index) ? self.playerNames[index] : "" },
            set: { value in
                guard self.playerNames.indices.contains(index) else { return }
                self.playerNames[index] = value
            }
        )
    }

    func sceneNoteBinding(for sceneID: String) -> Binding<String> {
        Binding(
            get: { self.sceneNotes[sceneID, default: ""] },
            set: { value in self.sceneNotes[sceneID] = value }
        )
    }

    func savedNames() -> [String] {
        playerNames.filter { !$0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }
    }

    /// Removes only player names and table notes. Story progress, clues and
    /// audio ratings remain untouched so a mid-session cleanup cannot destroy
    /// the investigation.
    func clearTableData() {
        playerNames = ["", "", ""]
        sessionNote = ""
        sceneNotes = [:]
    }

    /// Starts with a completely empty round while keeping audio preferences.
    /// This is intentionally separate from `clearTableData()` so the UI can
    /// describe the affected data accurately before confirming.
    func resetRound() {
        clearTableData()
        resetStoryState()
    }

    /// Backwards-compatible name used by older screens and integrations.
    func clearJournal() {
        resetRound()
    }

    private func resetStoryState() {
        nightPhaseIndex = 0
        currentSceneID = "S01"
        completedSceneIDs = []
        checkedClueIDs = []
        completedChecklistIDs = []
        npcStates = [:]
        threatLevel = 0
        selectedHooks = [:]
        guidedStepIndex = 0
        completedGuideStepIDs = []
        guideHistory = []
        setupChecks = []
        doorStates = [:]
        rollHistory = [:]
        rollResolutions = []
        discoveredItemIDs = []
        itemOwners = [:]
        itemUseRecords = []
        selectedEndingID = nil
        finaleMode = "guided"
        finaleSuccesses = 0
        finaleFailures = 0
        finaleOutcome = nil
        hasStartedSession = false
        time = 0
        warmth = 3
        trust = 3
        injuries = 0
        combatState = nil
    }

    func beginGuidedSession() {
        hasStartedSession = true
        sessionNote = ""
        sceneNotes = [:]
        currentSceneID = "S01"
        guidedStepIndex = 0
        completedSceneIDs = []
        checkedClueIDs = []
        completedChecklistIDs = []
        npcStates = [:]
        threatLevel = 0
        selectedEndingID = nil
        finaleMode = "guided"
        rollHistory = [:]
        rollResolutions = []
        discoveredItemIDs = []
        itemOwners = [:]
        itemUseRecords = []
        finaleSuccesses = 0
        finaleFailures = 0
        finaleOutcome = nil
        doorStates = ["inn.guestroom": true]
        completedGuideStepIDs = []
        guideHistory = []
        nightPhaseIndex = 0
        time = 0
        warmth = 3
        trust = 3
        injuries = 0
        combatState = nil
    }

    /// Migrates an interrupted pre-5.0 round to the new, deterministic
    /// starting point. Names and both note stores are intentionally retained;
    /// all generated story state is reset so the revised S06 gate is respected.
    private func migrateActiveLegacySession() {
        let preservedNames = playerNames
        let preservedSessionNote = sessionNote
        let preservedSceneNotes = sceneNotes

        hasStartedSession = true
        playerNames = preservedNames
        sessionNote = preservedSessionNote
        sceneNotes = preservedSceneNotes
        currentSceneID = "S06"
        guidedStepIndex = 0
        completedSceneIDs = ["S01", "S02", "S03", "S04", "S05"]
        checkedClueIDs = []
        completedChecklistIDs = []
        completedGuideStepIDs = []
        guideHistory = []
        npcStates = [:]
        threatLevel = 0
        selectedHooks = [:]
        setupChecks = []
        doorStates = ["inn.guestroom": true]
        rollHistory = [:]
        rollResolutions = []
        selectedEndingID = nil
        finaleMode = "guided"
        finaleSuccesses = 0
        finaleFailures = 0
        finaleOutcome = nil
        discoveredItemIDs = []
        itemOwners = [:]
        itemUseRecords = []
        time = 0
        warmth = 3
        trust = 3
        injuries = 0
        combatState = nil
        shouldMigrateLegacyInventory = false
        persist()
    }

    func finishGuidedSession() {
        completedSceneIDs.insert(currentSceneID)
        hasStartedSession = false
    }

    func advanceGuideStep(in sceneID: String, stepID: String, stepCount: Int) {
        completedGuideStepIDs.insert(stepID)
        let nextIndex = min(guidedStepIndex + 1, max(0, stepCount - 1))
        if nextIndex != guidedStepIndex {
            guideHistory.append(GuidePosition(sceneID: sceneID, stepIndex: guidedStepIndex))
            guidedStepIndex = nextIndex
        } else {
            completedSceneIDs.insert(sceneID)
        }
    }

    func advanceToScene(_ sceneID: String, from currentID: String? = nil) {
        if let currentID, currentID != sceneID {
            guideHistory.append(GuidePosition(sceneID: currentID, stepIndex: guidedStepIndex))
            completedSceneIDs.insert(currentID)
        }
        currentSceneID = sceneID
        guidedStepIndex = 0
        switch sceneID {
        case "S02": nightPhaseIndex = 0
        case "S03", "S04", "S05": nightPhaseIndex = 1
        case "S06": nightPhaseIndex = 2
        case "S07": nightPhaseIndex = 3
        case "S08": nightPhaseIndex = 4
        default: break
        }
    }

    @discardableResult
    func stepBack() -> Bool {
        guard let previous = guideHistory.popLast() else { return false }
        currentSceneID = previous.sceneID
        guidedStepIndex = max(0, previous.stepIndex)
        return true
    }

    func resetDependentPath(from sceneID: String) {
        // S03, S04 and S05 are parallel investigations. Resetting one of
        // them must never erase the evidence already completed in a sibling.
        let dependentScenes: Set<String>
        switch sceneID {
        case "S01": dependentScenes = ["S02", "S03", "S04", "S05", "S06", "S07", "S08"]
        case "S02": dependentScenes = ["S03", "S04", "S05", "S06", "S07", "S08"]
        case "S03", "S04", "S05": dependentScenes = ["S06", "S07", "S08"]
        case "S06": dependentScenes = ["S07", "S08"]
        case "S07": dependentScenes = ["S08"]
        default: dependentScenes = []
        }
        guard !dependentScenes.isEmpty else { return }
        completedSceneIDs.subtract(dependentScenes)
        completedGuideStepIDs = completedGuideStepIDs.filter { stepID in
            !dependentScenes.contains(String(stepID.prefix(3)))
        }
        rollHistory = rollHistory.filter { stepID, _ in
            !dependentScenes.contains(String(stepID.prefix(3)))
        }
        rollResolutions = rollResolutions.filter { resolution in
            !dependentScenes.contains(String(resolution.stepID.prefix(3)))
        }
        itemUseRecords = itemUseRecords.filter { !dependentScenes.contains($0.sceneID) }
        guideHistory = guideHistory.filter { !dependentScenes.contains($0.sceneID) }
        if dependentScenes.contains("S07") {
            selectedEndingID = nil
            resetFinaleProgress()
        }
        if dependentScenes.contains("S07") {
            combatState = nil
            finaleMode = "guided"
        }
    }

    func canEnterScene(_ sceneID: String) -> Bool {
        if sceneID == currentSceneID || completedSceneIDs.contains(sceneID) { return true }
        switch sceneID {
        case "S01": return true
        case "S02": return completedSceneIDs.contains("S01")
        case "S03", "S04", "S05": return completedSceneIDs.contains("S02")
        case "S06": return ["S03", "S04", "S05"].allSatisfy(completedSceneIDs.contains)
        case "S07": return completedSceneIDs.contains("S06")
        case "S08": return completedSceneIDs.contains("S07")
        default: return false
        }
    }

    func isRecommendedScene(_ sceneID: String) -> Bool {
        if sceneID == currentSceneID { return true }
        switch sceneID {
        case "S01": return true
        case "S02": return completedSceneIDs.contains("S01")
        case "S03", "S04", "S05": return completedSceneIDs.contains("S02")
        case "S06":
            return ["S03", "S04", "S05"].allSatisfy(completedSceneIDs.contains)
        case "S07": return completedSceneIDs.contains("S06")
        case "S08": return completedSceneIDs.contains("S07")
        default: return false
        }
    }

    func toggleSetup(_ id: String) {
        if setupChecks.contains(id) {
            setupChecks.remove(id)
        } else {
            setupChecks.insert(id)
        }
    }

    func setDoor(_ id: String, isOpen: Bool) {
        doorStates[id] = isOpen
    }

    func migrateLegacyInventoryIfNeeded(itemIDs: [String]) {
        guard shouldMigrateLegacyInventory else { return }
        discoveredItemIDs = Set(itemIDs)
        shouldMigrateLegacyInventory = false
    }

    func discoverItems(_ itemIDs: [String]) {
        discoveredItemIDs.formUnion(itemIDs)
    }

    func assignItem(_ itemID: String, toPlayerAt index: Int) {
        guard discoveredItemIDs.contains(itemID), (0..<3).contains(index) else { return }
        itemOwners[itemID] = index
    }

    func transferItem(_ itemID: String, toPlayerAt index: Int) {
        assignItem(itemID, toPlayerAt: index)
    }

    func unassignItem(_ itemID: String) {
        itemOwners.removeValue(forKey: itemID)
    }

    func isItemDistributionComplete(for itemIDs: [String]) -> Bool {
        let expected = Set(itemIDs)
        guard expected.count == itemIDs.count,
              Set(itemOwners.keys) == expected,
              expected.isSubset(of: discoveredItemIDs) else { return false }
        return Set(itemOwners.values) == Set(0..<3)
    }

    func items(forPlayerAt index: Int, from items: [AdventureItem]) -> [AdventureItem] {
        items.filter { itemOwners[$0.id] == index }
    }

    func ownerIndex(for itemID: String) -> Int? {
        itemOwners[itemID]
    }

    func remainingUses(for item: AdventureItem) -> Int {
        max(0, item.initialUses - itemUseRecords.filter { $0.itemID == item.id }.count)
    }

    @discardableResult
    func useItem(itemID: String, effectID: String, sceneID: String, stepID: String, maximumUses: Int) -> ItemUseRecord? {
        guard discoveredItemIDs.contains(itemID), itemOwners[itemID] != nil,
              itemUseRecords.filter({ $0.itemID == itemID }).count < max(0, maximumUses) else { return nil }
        let record = ItemUseRecord(itemID: itemID, effectID: effectID, sceneID: sceneID, stepID: stepID)
        itemUseRecords.append(record)
        return record
    }

    func undoItemUse(_ recordID: UUID) {
        itemUseRecords.removeAll { $0.id == recordID }
    }

    func recordRoll(stepID: String, result: RollEvaluator.Result, consequence: RollConsequence? = nil, itemUseIDs: [String] = []) {
        rollHistory[stepID] = String(result.roll) + " / " + String(result.target) + " · " + result.label
        rollResolutions.append(RollResolutionRecord(stepID: stepID, result: result, consequence: consequence, itemUseIDs: itemUseIDs))
        if !result.isSuccess {
            apply(consequence?.effect)
        }
    }

    func latestRollResolution(for stepID: String) -> RollResolutionRecord? {
        rollResolutions.last(where: { $0.stepID == stepID })
    }

    @discardableResult
    func recordFinaleRoll(_ result: RollEvaluator.Result, consequence: RollConsequence? = nil, itemUseIDs: [String] = []) -> FinaleRollState {
        recordRoll(stepID: "S07_DANGER", result: result, consequence: consequence, itemUseIDs: itemUseIDs)
        if result.isCriticalFailure {
            finaleFailures = min(2, finaleFailures + 2)
        } else if result.isSuccess {
            finaleSuccesses = min(2, finaleSuccesses + 1)
        } else {
            finaleFailures = min(2, finaleFailures + 1)
        }

        if finaleSuccesses >= 2 {
            finaleOutcome = "success"
            return .resolved(success: true)
        }
        if finaleFailures >= 2 {
            finaleOutcome = "failure"
            threatLevel = min(5, threatLevel + 1)
            return .resolved(success: false)
        }
        return .ongoing(successes: finaleSuccesses, failures: finaleFailures)
    }

    func resetFinaleProgress() {
        finaleSuccesses = 0
        finaleFailures = 0
        finaleOutcome = nil
    }

    func setSelectedEnding(_ endingID: String) {
        selectedEndingID = endingID
        clearFinaleRolls()
        resetFinaleProgress()
        // Choosing another ending must not silently switch the mode the GM
        // selected. A stale combat tracker, however, cannot be reused for a
        // different ending because its victory text and log would be wrong.
        if finaleMode == "combat", combatState?.endingID != endingID {
            combatState = nil
        }
        finaleMode = finaleMode == "combat" ? "combat" : "guided"
    }

    func setFinaleMode(_ mode: String) {
        finaleMode = mode == "combat" ? "combat" : "guided"
        clearFinaleRolls()
        resetFinaleProgress()
        if finaleMode != "combat" {
            combatState = nil
        }
    }

    func startCombat(using config: CombatConfig, endingID: String?) {
        let playerParticipants = playerNames.enumerated().map { index, rawName in
            let spentShots = itemUseRecords.filter { $0.itemID == "item-revolver" }.count
            let ammunition = itemOwners["item-revolver"] == index ? max(0, 3 - spentShots) : 0
            return CombatParticipant(
                id: "player-\(index)",
                name: rawName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? "Figur \(index + 1)" : rawName,
                kind: .player,
                maxLP: 100,
                initiative: 0,
                attackSkill: 50,
                damageDice: "1W10",
                ammunition: ammunition,
                geistesblitze: 0,
                parryable: true
            )
        }
        let enemy = CombatParticipant(
            id: config.enemy.id,
            name: config.enemy.name,
            kind: .enemy,
            maxLP: config.enemy.maxLP,
            initiative: config.enemy.initiative,
            attackSkill: config.enemy.attackSkill,
            damageDice: config.enemy.damageDice,
            ammunition: 0,
            geistesblitze: 0,
            parryable: config.enemy.parryable
        )
        combatState = CombatState(
            isActive: true,
            round: 1,
            turnIndex: 0,
            endingID: endingID,
            participants: playerParticipants + [enemy],
            log: ["Kampf gestartet · \(enemy.name) · Ziel: \(endingID ?? "unbekanntes Ende")"],
            outcome: nil
        )
        finaleMode = "combat"
    }

    func ensureCombat(using config: CombatConfig, endingID: String?) {
        guard combatState == nil || combatState?.endingID != endingID else { return }
        startCombat(using: config, endingID: endingID)
    }

    func updateCombatParticipant(_ id: String, _ update: (inout CombatParticipant) -> Void) {
        guard var state = combatState,
              let index = state.participants.firstIndex(where: { $0.id == id }) else { return }
        var participant = state.participants[index]
        update(&participant)
        participant.currentLP = min(max(participant.currentLP, 0), participant.maxLP)
        participant.initiative = max(0, participant.initiative)
        participant.attackSkill = min(max(participant.attackSkill, 1), 100)
        participant.ammunition = max(0, participant.ammunition)
        participant.geistesblitze = max(0, participant.geistesblitze)
        state.participants[index] = participant
        combatState = state
    }

    func setCombatLP(_ id: String, value: Int) {
        updateCombatParticipant(id) { $0.currentLP = value }
    }

    func adjustCombatLP(_ id: String, by delta: Int) {
        updateCombatParticipant(id) { $0.currentLP += delta }
    }

    func setCombatInitiative(_ id: String, value: Int) {
        updateCombatParticipant(id) { $0.initiative = value }
    }

    func setCombatGeistesblitze(_ id: String, value: Int) {
        updateCombatParticipant(id) { $0.geistesblitze = value }
    }

    func setCombatAmmunition(_ id: String, value: Int) {
        updateCombatParticipant(id) { $0.ammunition = value }
    }

    func setCombatParticipantName(_ id: String, value: String) {
        let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        updateCombatParticipant(id) { $0.name = trimmed }
        if let index = Int(id.replacingOccurrences(of: "player-", with: "")), playerNames.indices.contains(index) {
            playerNames[index] = trimmed
        }
    }

    func spendCombatGeistesblitz(_ id: String) {
        updateCombatParticipant(id) { $0.geistesblitze = max(0, $0.geistesblitze - 1) }
    }

    func useCombatAmmunition(_ id: String) -> Bool {
        guard let participant = combatState?.participants.first(where: { $0.id == id }), participant.ammunition > 0 else { return false }
        updateCombatParticipant(id) { $0.ammunition -= 1 }
        return true
    }

    func sortCombatByInitiative() {
        guard var state = combatState else { return }
        state.participants.sort {
            if $0.initiative == $1.initiative { return $0.kind == .player && $1.kind == .enemy }
            return $0.initiative > $1.initiative
        }
        state.turnIndex = 0
        state.participants.indices.forEach { state.participants[$0].hasActed = false }
        combatState = state
        logCombat("Initiative sortiert")
    }

    func nextCombatTurn() {
        guard var state = combatState, state.isActive, !state.participants.isEmpty else { return }
        guard state.participants.indices.contains(state.turnIndex) else {
            state.turnIndex = state.participants.firstIndex(where: { !$0.isDefeated }) ?? 0
            combatState = state
            return
        }
        state.participants[state.turnIndex].hasActed = true
        let nextIndex = state.participants.indices.first(where: {
            $0 > state.turnIndex && !state.participants[$0].isDefeated
        })
        if let nextIndex {
            state.turnIndex = nextIndex
        } else {
            state.round += 1
            state.turnIndex = state.participants.firstIndex(where: { !$0.isDefeated }) ?? 0
            state.participants.indices.forEach { state.participants[$0].hasActed = false }
            state.log.append("Runde \(state.round) beginnt")
        }
        combatState = state
    }

    func logCombat(_ message: String) {
        guard var state = combatState else { return }
        state.log.append(message)
        state.log = Array(state.log.suffix(100))
        combatState = state
    }

    func finishCombat(outcome: String) {
        guard var state = combatState else { return }
        guard state.outcome == nil else { return }
        state.isActive = false
        state.outcome = outcome
        state.log.append("Kampf beendet · \(outcome)")
        combatState = state
    }

    func setThreatLevel(_ level: Int) {
        threatLevel = Self.normalizedThreat(level)
    }

    func applyStateDelta(time: Int = 0, warmth: Int = 0, trust: Int = 0, injuries: Int = 0) {
        self.time = Self.normalizedTime(self.time + time)
        self.warmth = Self.normalizedResource(self.warmth + warmth)
        self.trust = Self.normalizedResource(self.trust + trust)
        self.injuries = Self.normalizedInjuries(self.injuries + injuries)
    }

    func setTime(_ value: Int) {
        time = Self.normalizedTime(value)
    }

    func setWarmth(_ value: Int) {
        warmth = Self.normalizedResource(value)
    }

    func setTrust(_ value: Int) {
        trust = Self.normalizedResource(value)
    }

    func setInjuries(_ value: Int) {
        injuries = Self.normalizedInjuries(value)
    }

    func toggleClue(_ clueID: String) {
        if checkedClueIDs.contains(clueID) {
            checkedClueIDs.remove(clueID)
        } else {
            checkedClueIDs.insert(clueID)
        }
    }

    func toggleChecklist(_ checklistID: String) {
        if completedChecklistIDs.contains(checklistID) {
            completedChecklistIDs.remove(checklistID)
        } else {
            completedChecklistIDs.insert(checklistID)
        }
    }

    func setNPCState(_ npcID: String, state: Int) {
        npcStates[npcID] = min(max(state, 0), 2)
    }

    func setAudioRating(_ cueID: String, rating: Int) {
        audioRatings[cueID] = min(max(rating, -1), 1)
    }

    func mergeAudioRatings(_ incoming: [String: Int]) {
        guard !incoming.isEmpty else { return }
        audioRatings.merge(incoming) { _, remote in min(max(remote, -1), 1) }
    }

    func clearAudioRatings() {
        audioRatings = [:]
    }

    private func apply(_ effect: RollConsequenceEffect?) {
        if let threatDelta = effect?.threatDelta {
            setThreatLevel(threatLevel + threatDelta)
        }
        if let minimumThreat = effect?.minimumThreat {
            setThreatLevel(max(threatLevel, minimumThreat))
        }
        applyStateDelta(
            time: effect?.timeDelta ?? 0,
            warmth: effect?.warmthDelta ?? 0,
            trust: effect?.trustDelta ?? 0,
            injuries: effect?.injuryDelta ?? 0
        )
    }

    private func clearFinaleRolls() {
        rollHistory = rollHistory.filter { stepID, _ in stepID != "S07_DANGER" }
        rollResolutions.removeAll { $0.stepID == "S07_DANGER" }
        itemUseRecords.removeAll { $0.stepID == "S07_DANGER" }
    }

    private func persist() {
        let snapshot = Snapshot(
            playerNames: Self.normalizedNames(playerNames),
            sessionNote: sessionNote,
            sceneNotes: sceneNotes,
            nightPhaseIndex: Self.normalizedNightPhase(nightPhaseIndex),
            currentSceneID: currentSceneID,
            completedSceneIDs: Array(completedSceneIDs).sorted(),
            checkedClueIDs: Array(checkedClueIDs).sorted(),
            completedChecklistIDs: Array(completedChecklistIDs).sorted(),
            npcStates: npcStates,
            threatLevel: Self.normalizedThreat(threatLevel),
            selectedHooks: selectedHooks,
            audioRatings: audioRatings,
            guidedStepIndex: guidedStepIndex,
            completedGuideStepIDs: Array(completedGuideStepIDs).sorted(),
            setupChecks: Array(setupChecks).sorted(),
            doorStates: doorStates,
            rollHistory: rollHistory,
            rollResolutions: rollResolutions,
            selectedEndingID: selectedEndingID,
            finaleMode: finaleMode,
            finaleSuccesses: finaleSuccesses,
            finaleFailures: finaleFailures,
            finaleOutcome: finaleOutcome,
            hasStartedSession: hasStartedSession,
            guideHistory: guideHistory,
            discoveredItemIDs: Array(discoveredItemIDs).sorted(),
            itemOwners: itemOwners,
            itemUseRecords: itemUseRecords,
            time: time,
            warmth: warmth,
            trust: trust,
            injuries: injuries,
            combatState: combatState
        )
        guard let data = try? JSONEncoder().encode(snapshot) else { return }
        defaults.set(data, forKey: storageKey)
    }

    private static func normalizedNames(_ names: [String]) -> [String] {
        Array((names + Array(repeating: "", count: 3)).prefix(3))
    }

    private static func normalizedNightPhase(_ index: Int) -> Int {
        min(max(index, 0), nightPhaseCount - 1)
    }

    private static func normalizedThreat(_ level: Int) -> Int {
        min(max(level, 0), 5)
    }

    private static func normalizedTime(_ value: Int) -> Int {
        min(max(value, 0), 5)
    }

    private static func normalizedResource(_ value: Int) -> Int {
        min(max(value, 0), 5)
    }

    private static func normalizedInjuries(_ value: Int) -> Int {
        min(max(value, 0), 3)
    }
}
