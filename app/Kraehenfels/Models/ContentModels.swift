import Foundation

struct ContentManifest: Codable {
    let meta: ContentMeta
    let scenes: [SceneEntry]
    let handouts: [HandoutEntry]
    let audioCues: [AudioCue]

    static let empty = ContentManifest(
        meta: ContentMeta(title: "Die Weiße Frau schweigt", appTitle: "Krähenfels", subtitle: "SL-Begleiter", system: "How to be a Hero", setting: "Schwarzwald, November 1890", language: "de", version: "1.0.0", minimumIOS: "17.0"),
        scenes: [], handouts: [], audioCues: []
    )
}

struct ContentMeta: Codable {
    let title: String
    let appTitle: String
    let subtitle: String
    let system: String
    let setting: String
    let language: String
    let version: String
    let minimumIOS: String
}

struct SceneEntry: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let shortTitle: String
    let duration: String
    let goal: String
    let handoutIds: [String]
    let audioCueIds: [String]
    let nextSceneIds: [String]
}

struct HandoutEntry: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let format: String
    let spoiler: Bool
    let fallback: String
}

struct AudioCue: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let scene: String
    let category: String
    let file: String
    let mode: String
    let gain: Double
    let fadeMs: Int
    let isClue: Bool
    let printFallbackId: String?

    var categoryLabel: String {
        switch category {
        case "ambient": return "Atmosphäre"
        case "music": return "Musik"
        default: return "Effekt"
        }
    }

    var iconName: String {
        switch category {
        case "ambient": return "wind"
        case "music": return "music.note"
        default: return "sparkles"
        }
    }
}
