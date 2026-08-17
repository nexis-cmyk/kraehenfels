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

    struct NightPhase: Identifiable, Equatable {
        let id: Int
        let title: String
        let detail: String
        let symbol: String
    }

    static let nightPhases = [
        NightPhase(id: 0, title: "Der Bruch", detail: "Manipulierte Kutsche, Schnee und der erste falsche Schutz.", symbol: "car.side.fill"),
        NightPhase(id: 1, title: "Das Dorf", detail: "Gasthaus, Kirche und Schmiede öffnen ihre Widersprüche.", symbol: "house.lodge.fill"),
        NightPhase(id: 2, title: "Die Spur", detail: "Namen, Buchseiten und der Weg zur Alten Eiche.", symbol: "magnifyingglass"),
        NightPhase(id: 3, title: "Der Ruf", detail: "Die Glocke schlägt. Das Dorf muss sich entscheiden.", symbol: "bell.and.waves.left.and.right.fill"),
        NightPhase(id: 4, title: "Der Morgen", detail: "Drei mögliche Enden und die Rechnung des Waldes.", symbol: "sunrise.fill"),
    ]

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
        var selectedEndingID: String?
        var finaleMode: String?
        var finaleSuccesses: Int?
        var finaleFailures: Int?
        var finaleOutcome: String?
    }

    private let storageKey = "kraehenfels.sessionJournal.v3"
    private let defaults: UserDefaults

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

    @Published var completedGuideStepIDs: Set<String> {
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
        if let data = defaults.data(forKey: storageKey),
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
            completedGuideStepIDs = Set(snapshot.completedGuideStepIDs ?? [])
            setupChecks = Set(snapshot.setupChecks ?? [])
            doorStates = snapshot.doorStates ?? [:]
            rollHistory = snapshot.rollHistory ?? [:]
            selectedEndingID = snapshot.selectedEndingID
            finaleMode = snapshot.finaleMode ?? "guided"
            finaleSuccesses = min(max(snapshot.finaleSuccesses ?? 0, 0), 2)
            finaleFailures = min(max(snapshot.finaleFailures ?? 0, 0), 2)
            finaleOutcome = snapshot.finaleOutcome
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
            completedGuideStepIDs = []
            setupChecks = []
            doorStates = [:]
            rollHistory = [:]
            selectedEndingID = nil
            finaleMode = "guided"
            finaleSuccesses = 0
            finaleFailures = 0
            finaleOutcome = nil
        }
    }

    var currentNightPhase: NightPhase {
        Self.nightPhases[Self.normalizedNightPhase(nightPhaseIndex)]
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
        setupChecks = []
        doorStates = [:]
        rollHistory = [:]
        selectedEndingID = nil
        finaleMode = "guided"
        finaleSuccesses = 0
        finaleFailures = 0
        finaleOutcome = nil
    }

    func beginGuidedSession() {
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
        finaleSuccesses = 0
        finaleFailures = 0
        finaleOutcome = nil
        doorStates = ["inn.guestroom": true]
        completedGuideStepIDs = []
        nightPhaseIndex = 0
    }

    func advanceGuideStep(in sceneID: String, stepID: String, stepCount: Int) {
        completedGuideStepIDs.insert(stepID)
        if guidedStepIndex + 1 < stepCount {
            guidedStepIndex += 1
        } else {
            completedSceneIDs.insert(sceneID)
        }
    }

    func advanceToScene(_ sceneID: String, from currentID: String? = nil) {
        if let currentID {
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

    func recordRoll(stepID: String, result: RollEvaluator.Result) {
        rollHistory[stepID] = String(result.roll) + " / " + String(result.target) + " · " + result.label
    }

    @discardableResult
    func recordFinaleRoll(_ result: RollEvaluator.Result) -> FinaleRollState {
        recordRoll(stepID: "S07_DANGER", result: result)
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
        resetFinaleProgress()
        finaleMode = "guided"
    }

    func setFinaleMode(_ mode: String) {
        finaleMode = mode == "combat" ? "combat" : "guided"
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
            selectedEndingID: selectedEndingID,
            finaleMode: finaleMode,
            finaleSuccesses: finaleSuccesses,
            finaleFailures: finaleFailures,
            finaleOutcome: finaleOutcome
        )
        guard let data = try? JSONEncoder().encode(snapshot) else { return }
        defaults.set(data, forKey: storageKey)
    }

    private static func normalizedNames(_ names: [String]) -> [String] {
        Array((names + Array(repeating: "", count: 3)).prefix(3))
    }

    private static func normalizedNightPhase(_ index: Int) -> Int {
        min(max(index, 0), nightPhases.count - 1)
    }

    private static func normalizedThreat(_ level: Int) -> Int {
        min(max(level, 0), 5)
    }
}
