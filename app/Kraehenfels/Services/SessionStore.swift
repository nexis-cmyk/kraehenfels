import SwiftUI

@MainActor
final class SessionStore: ObservableObject {
    private struct Snapshot: Codable {
        var playerNames: [String]
        var sessionNote: String
        var sceneNotes: [String: String]
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

    init(defaults: UserDefaults = .standard) {
        if let data = defaults.data(forKey: storageKey),
           let snapshot = try? JSONDecoder().decode(Snapshot.self, from: data) {
            playerNames = Self.normalizedNames(snapshot.playerNames)
            sessionNote = snapshot.sessionNote
            sceneNotes = snapshot.sceneNotes
        } else {
            playerNames = ["", "", ""]
            sessionNote = ""
            sceneNotes = [:]
        }
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
            sceneNotes: sceneNotes
        )
        guard let data = try? JSONEncoder().encode(snapshot) else { return }
        UserDefaults.standard.set(data, forKey: storageKey)
    }

    private static func normalizedNames(_ names: [String]) -> [String] {
        Array((names + Array(repeating: "", count: 3)).prefix(3))
    }
}
