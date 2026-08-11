import Foundation

struct ContentManifest: Codable {
    let meta: ContentMeta
    let scenes: [SceneEntry]
    let handouts: [HandoutEntry]
    let audioCues: [AudioCue]
    let npcs: [NPCEntry]
    let clues: [ClueEntry]

    init(meta: ContentMeta, scenes: [SceneEntry], handouts: [HandoutEntry], audioCues: [AudioCue], npcs: [NPCEntry] = [], clues: [ClueEntry] = []) {
        self.meta = meta
        self.scenes = scenes
        self.handouts = handouts
        self.audioCues = audioCues
        self.npcs = npcs
        self.clues = clues
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        meta = try container.decode(ContentMeta.self, forKey: .meta)
        scenes = try container.decode([SceneEntry].self, forKey: .scenes)
        handouts = try container.decode([HandoutEntry].self, forKey: .handouts)
        audioCues = try container.decode([AudioCue].self, forKey: .audioCues)
        npcs = try container.decodeIfPresent([NPCEntry].self, forKey: .npcs) ?? []
        clues = try container.decodeIfPresent([ClueEntry].self, forKey: .clues) ?? []
    }

    static let empty = ContentManifest(
        meta: ContentMeta(title: "Die Weiße Frau schweigt", appTitle: "Krähenfels", subtitle: "SL-Begleiter", system: "How to be a Hero", setting: "Schwarzwald, November 1890", language: "de", version: "2.0.0", minimumIOS: "17.0"),
        scenes: [], handouts: [], audioCues: []
    )

    private enum CodingKeys: String, CodingKey {
        case meta, scenes, handouts, audioCues, npcs, clues
    }
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
    let readAloud: String
    let gmNotes: [String]
    let npcIds: [String]
    let clueIds: [String]
    let soundPreset: String?
    let stuckPrompts: [String]
    let escalation: Int
    let checklist: [String]
    let art: String?

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        title = try container.decode(String.self, forKey: .title)
        shortTitle = try container.decode(String.self, forKey: .shortTitle)
        duration = try container.decode(String.self, forKey: .duration)
        goal = try container.decode(String.self, forKey: .goal)
        handoutIds = try container.decodeIfPresent([String].self, forKey: .handoutIds) ?? []
        audioCueIds = try container.decodeIfPresent([String].self, forKey: .audioCueIds) ?? []
        nextSceneIds = try container.decodeIfPresent([String].self, forKey: .nextSceneIds) ?? []
        readAloud = try container.decodeIfPresent(String.self, forKey: .readAloud) ?? ""
        gmNotes = try container.decodeIfPresent([String].self, forKey: .gmNotes) ?? []
        npcIds = try container.decodeIfPresent([String].self, forKey: .npcIds) ?? []
        clueIds = try container.decodeIfPresent([String].self, forKey: .clueIds) ?? []
        soundPreset = try container.decodeIfPresent(String.self, forKey: .soundPreset)
        stuckPrompts = try container.decodeIfPresent([String].self, forKey: .stuckPrompts) ?? []
        escalation = try container.decodeIfPresent(Int.self, forKey: .escalation) ?? 0
        checklist = try container.decodeIfPresent([String].self, forKey: .checklist) ?? []
        art = try container.decodeIfPresent(String.self, forKey: .art)
    }

    private enum CodingKeys: String, CodingKey {
        case id, title, shortTitle, duration, goal, handoutIds, audioCueIds, nextSceneIds
        case readAloud, gmNotes, npcIds, clueIds, soundPreset, stuckPrompts, escalation, checklist, art
    }
}

struct NPCEntry: Codable, Identifiable, Hashable {
    let id: String
    let name: String
    let role: String
    let description: String
    let knows: [String]
    let hides: [String]
    let givesHandoutIds: [String]
    let prompts: [String]
    let cueIds: [String]

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        name = try container.decode(String.self, forKey: .name)
        role = try container.decode(String.self, forKey: .role)
        description = try container.decode(String.self, forKey: .description)
        knows = try container.decodeIfPresent([String].self, forKey: .knows) ?? []
        hides = try container.decodeIfPresent([String].self, forKey: .hides) ?? []
        givesHandoutIds = try container.decodeIfPresent([String].self, forKey: .givesHandoutIds) ?? []
        prompts = try container.decodeIfPresent([String].self, forKey: .prompts) ?? []
        cueIds = try container.decodeIfPresent([String].self, forKey: .cueIds) ?? []
    }

    private enum CodingKeys: String, CodingKey {
        case id, name, role, description, knows, hides, givesHandoutIds, prompts, cueIds
    }
}

struct ClueEntry: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let details: String
    let required: Bool
    let handoutId: String?

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        title = try container.decode(String.self, forKey: .title)
        details = try container.decode(String.self, forKey: .details)
        required = try container.decodeIfPresent(Bool.self, forKey: .required) ?? false
        handoutId = try container.decodeIfPresent(String.self, forKey: .handoutId)
    }

    private enum CodingKeys: String, CodingKey {
        case id, title, details, required, handoutId
    }
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
