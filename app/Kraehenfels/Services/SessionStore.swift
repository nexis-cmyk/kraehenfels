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
        NightPhase(id: 0, title: "Ankunft", detail: "Kutschenpanne und erster Weg ins Dorf.", symbol: "car.side.fill"),
        NightPhase(id: 1, title: "Dunkelheit", detail: "Dorf, Kirche, Schmiede und Grube stehen offen.", symbol: "moon.stars.fill"),
        NightPhase(id: 2, title: "Warnung", detail: "Die Weiße Frau und die Wahrheit vor Mitternacht.", symbol: "exclamationmark.triangle.fill"),
        NightPhase(id: 3, title: "Mitternacht", detail: "Das Finale beginnt. Jetzt zählt jede Entscheidung.", symbol: "bell.and.waves.left.and.right.fill"),
        NightPhase(id: 4, title: "Tauwetter", detail: "Stille nach dem Finale und persönlicher Epilog.", symbol: "drop.fill"),
    ]

    private struct Snapshot: Codable {
        var playerNames: [String]
        var sessionNote: String
        var sceneNotes: [String: String]
        var nightPhaseIndex: Int?
    }

    private let storageKey = "kraehenfels.sessionJournal.v1"

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

    init(defaults: UserDefaults = .standard) {
        if let data = defaults.data(forKey: storageKey),
           let snapshot = try? JSONDecoder().decode(Snapshot.self, from: data) {
            playerNames = Self.normalizedNames(snapshot.playerNames)
            sessionNote = snapshot.sessionNote
            sceneNotes = snapshot.sceneNotes
            nightPhaseIndex = Self.normalizedNightPhase(snapshot.nightPhaseIndex ?? 0)
        } else {
            playerNames = ["", "", ""]
            sessionNote = ""
            sceneNotes = [:]
            nightPhaseIndex = 0
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
    }

    private func persist() {
        let snapshot = Snapshot(
            playerNames: Self.normalizedNames(playerNames),
            sessionNote: sessionNote,
            sceneNotes: sceneNotes,
            nightPhaseIndex: Self.normalizedNightPhase(nightPhaseIndex)
        )
        guard let data = try? JSONEncoder().encode(snapshot) else { return }
        UserDefaults.standard.set(data, forKey: storageKey)
    }

    private static func normalizedNames(_ names: [String]) -> [String] {
        Array((names + Array(repeating: "", count: 3)).prefix(3))
    }

    private static func normalizedNightPhase(_ index: Int) -> Int {
        min(max(index, 0), nightPhases.count - 1)
    }
}
