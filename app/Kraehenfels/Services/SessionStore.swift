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
    }

    private let storageKey = "kraehenfels.sessionJournal.v6"
    private let legacyStorageKey = "kraehenfels.sessionJournal.v5"
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
        let loadedData = defaults.data(forKey: storageKey)
            ?? defaults.data(forKey: legacyStorageKey)
            ?? defaults.data(forKey: legacyV4StorageKey)
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
        }

        if defaults.data(forKey: storageKey) == nil, loadedData != nil {
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

    func clearJournal() {
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
    }

    func finishGuidedSession() {
        completedSceneIDs.insert(currentSceneID)
        hasStartedSession = false
    }

    func advanceGuideStep(in sceneID: String, stepID: String, stepCount: Int) {
        guideHistory.append(GuidePosition(sceneID: sceneID, stepIndex: guidedStepIndex))
        completedGuideStepIDs.insert(stepID)
        if guidedStepIndex + 1 < stepCount {
            guidedStepIndex += 1
        } else {
            completedSceneIDs.insert(sceneID)
        }
    }

    func advanceToScene(_ sceneID: String, from currentID: String? = nil) {
        if let currentID {
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
        let sceneOrder = ["S01", "S02", "S03", "S04", "S05", "S06", "S07", "S08"]
        guard let index = sceneOrder.firstIndex(of: sceneID) else { return }
        let dependentScenes = Set(sceneOrder.dropFirst(index + 1))
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
        if index < (sceneOrder.firstIndex(of: "S07") ?? sceneOrder.count) {
            selectedEndingID = nil
            resetFinaleProgress()
        }
    }

    func isRecommendedScene(_ sceneID: String) -> Bool {
        if sceneID == currentSceneID { return true }
        switch sceneID {
        case "S01": return true
        case "S02": return completedSceneIDs.contains("S01")
        case "S03", "S04", "S05": return completedSceneIDs.contains("S02")
        case "S06":
            return Set(["S03", "S04", "S05"]).intersection(completedSceneIDs).count >= 2
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
        finaleMode = "guided"
    }

    func setFinaleMode(_ mode: String) {
        finaleMode = mode == "combat" ? "combat" : "guided"
        clearFinaleRolls()
        resetFinaleProgress()
    }

    func setThreatLevel(_ level: Int) {
        threatLevel = Self.normalizedThreat(level)
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
            itemUseRecords: itemUseRecords
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
}
