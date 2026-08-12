import SwiftUI

@MainActor
final class SessionStore: ObservableObject {
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
            audioRatings: audioRatings
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
