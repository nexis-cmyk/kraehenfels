import Foundation

struct ContentManifest: Codable {
    let meta: ContentMeta
    let phases: [PhaseEntry]
    let travelHooks: [TravelHook]
    let threatLevels: [ThreatLevel]
    let facts: [FactEntry]
    let endings: [EndingEntry]
    let maps: [MapEntry]
    let locations: [LocationEntry]
    let scenes: [SceneEntry]
    let handouts: [HandoutEntry]
    let audioCues: [AudioCue]
    let npcs: [NPCEntry]
    let clues: [ClueEntry]
    let guide: GuideContent
    let rules: [RuleEntry]

    init(meta: ContentMeta, phases: [PhaseEntry] = [], travelHooks: [TravelHook] = [], threatLevels: [ThreatLevel] = [], facts: [FactEntry] = [], endings: [EndingEntry] = [], maps: [MapEntry] = [], locations: [LocationEntry] = [], scenes: [SceneEntry], handouts: [HandoutEntry], audioCues: [AudioCue], npcs: [NPCEntry] = [], clues: [ClueEntry] = [], guide: GuideContent = .empty, rules: [RuleEntry] = []) {
        self.meta = meta
        self.phases = phases
        self.travelHooks = travelHooks
        self.threatLevels = threatLevels
        self.facts = facts
        self.endings = endings
        self.maps = maps
        self.locations = locations
        self.scenes = scenes
        self.handouts = handouts
        self.audioCues = audioCues
        self.npcs = npcs
        self.clues = clues
        self.guide = guide
        self.rules = rules
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        meta = try container.decode(ContentMeta.self, forKey: .meta)
        phases = try container.decodeIfPresent([PhaseEntry].self, forKey: .phases) ?? []
        travelHooks = try container.decodeIfPresent([TravelHook].self, forKey: .travelHooks) ?? []
        threatLevels = try container.decodeIfPresent([ThreatLevel].self, forKey: .threatLevels) ?? []
        facts = try container.decodeIfPresent([FactEntry].self, forKey: .facts) ?? []
        endings = try container.decodeIfPresent([EndingEntry].self, forKey: .endings) ?? []
        maps = try container.decodeIfPresent([MapEntry].self, forKey: .maps) ?? []
        locations = try container.decodeIfPresent([LocationEntry].self, forKey: .locations) ?? []
        scenes = try container.decode([SceneEntry].self, forKey: .scenes)
        handouts = try container.decode([HandoutEntry].self, forKey: .handouts)
        audioCues = try container.decode([AudioCue].self, forKey: .audioCues)
        npcs = try container.decodeIfPresent([NPCEntry].self, forKey: .npcs) ?? []
        clues = try container.decodeIfPresent([ClueEntry].self, forKey: .clues) ?? []
        guide = try container.decodeIfPresent(GuideContent.self, forKey: .guide) ?? .empty
        rules = try container.decodeIfPresent([RuleEntry].self, forKey: .rules) ?? []
    }

    static let empty = ContentManifest(
        meta: ContentMeta(title: "Krähenfels: Die letzte Kutsche", appTitle: "Krähenfels", subtitle: "SL-Begleiter", system: "How to be a Hero", setting: "Schwarzwald, November 1890", language: "de", version: "4.0.0", minimumIOS: "17.0"),
        scenes: [], handouts: [], audioCues: [], guide: .empty, rules: []
    )

    private enum CodingKeys: String, CodingKey {
        case meta, phases, travelHooks, threatLevels, facts, endings, maps, locations, scenes, handouts, audioCues, npcs, clues, guide, rules
    }
}

struct PhaseEntry: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let detail: String
    let symbol: String
}

struct TravelHook: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let prompt: String
    let linkedClueIds: [String]
}

struct ThreatLevel: Codable, Identifiable, Hashable {
    var id: Int { level }
    let level: Int
    let title: String
    let detail: String
    let trigger: String
}

struct FactEntry: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let details: String
    let clueIds: [String]
    let fallback: String
}

struct EndingEntry: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let summary: String
    let requiredFactIds: [String]
    let cost: String
}

struct MapEntry: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let playerAsset: String
    let gmAsset: String
    let spoiler: Bool
}

struct LocationEntry: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let mapId: String
    let sceneIds: [String]
    let npcIds: [String]
    let clueIds: [String]
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
    let audioPlan: [AudioPlanEntry]
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
    let phaseId: String?
    let locationIds: [String]
    let recommendation: String

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        title = try container.decode(String.self, forKey: .title)
        shortTitle = try container.decode(String.self, forKey: .shortTitle)
        duration = try container.decode(String.self, forKey: .duration)
        goal = try container.decode(String.self, forKey: .goal)
        handoutIds = try container.decodeIfPresent([String].self, forKey: .handoutIds) ?? []
        audioCueIds = try container.decodeIfPresent([String].self, forKey: .audioCueIds) ?? []
        audioPlan = try container.decodeIfPresent([AudioPlanEntry].self, forKey: .audioPlan) ?? []
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
        phaseId = try container.decodeIfPresent(String.self, forKey: .phaseId)
        locationIds = try container.decodeIfPresent([String].self, forKey: .locationIds) ?? []
        recommendation = try container.decodeIfPresent(String.self, forKey: .recommendation) ?? ""
    }

    private enum CodingKeys: String, CodingKey {
        case id, title, shortTitle, duration, goal, handoutIds, audioCueIds, audioPlan, nextSceneIds
        case readAloud, gmNotes, npcIds, clueIds, soundPreset, stuckPrompts, escalation, checklist, art
        case phaseId, locationIds, recommendation
    }
}

struct AudioPlanEntry: Codable, Identifiable, Hashable {
    var id: String { cueId }
    let cueId: String
    let playWhen: String
    let stopWhen: String
    let gmInstruction: String
    let optional: Bool

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        cueId = try container.decode(String.self, forKey: .cueId)
        playWhen = try container.decodeIfPresent(String.self, forKey: .playWhen) ?? ""
        stopWhen = try container.decodeIfPresent(String.self, forKey: .stopWhen) ?? ""
        gmInstruction = try container.decodeIfPresent(String.self, forKey: .gmInstruction) ?? ""
        optional = try container.decodeIfPresent(Bool.self, forKey: .optional) ?? false
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
    let appearances: [NPCAppearance]
    let cueIds: [String]
    let states: [String]
    let portrait: String?

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
        appearances = try container.decodeIfPresent([NPCAppearance].self, forKey: .appearances) ?? []
        cueIds = try container.decodeIfPresent([String].self, forKey: .cueIds) ?? []
        states = try container.decodeIfPresent([String].self, forKey: .states) ?? []
        portrait = try container.decodeIfPresent(String.self, forKey: .portrait)
    }

    private enum CodingKeys: String, CodingKey {
        case id, name, role, description, knows, hides, givesHandoutIds, prompts, appearances, cueIds, states, portrait
    }
}

struct NPCAppearance: Codable, Hashable, Identifiable {
    var id: String { sceneId }
    let sceneId: String
    let when: String
    let playAs: String
    let openingLine: String
    let turn: String
}

struct ClueEntry: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let details: String
    let required: Bool
    let handoutId: String?
    let factId: String?
    let locationId: String?

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        title = try container.decode(String.self, forKey: .title)
        details = try container.decode(String.self, forKey: .details)
        required = try container.decodeIfPresent(Bool.self, forKey: .required) ?? false
        handoutId = try container.decodeIfPresent(String.self, forKey: .handoutId)
        factId = try container.decodeIfPresent(String.self, forKey: .factId)
        locationId = try container.decodeIfPresent(String.self, forKey: .locationId)
    }

    private enum CodingKeys: String, CodingKey {
        case id, title, details, required, handoutId, factId, locationId
    }
}

struct HandoutEntry: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let format: String
    let spoiler: Bool
    let fallback: String
    let asset: String?
    let previewAsset: String?
    let linkedClueIds: [String]

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        title = try container.decode(String.self, forKey: .title)
        format = try container.decode(String.self, forKey: .format)
        spoiler = try container.decodeIfPresent(Bool.self, forKey: .spoiler) ?? false
        fallback = try container.decode(String.self, forKey: .fallback)
        asset = try container.decodeIfPresent(String.self, forKey: .asset)
        previewAsset = try container.decodeIfPresent(String.self, forKey: .previewAsset)
        linkedClueIds = try container.decodeIfPresent([String].self, forKey: .linkedClueIds) ?? []
    }

    private enum CodingKeys: String, CodingKey {
        case id, title, format, spoiler, fallback, asset, previewAsset, linkedClueIds
    }
}

struct AudioCue: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let scene: String
    let category: String
    let scope: String
    let layer: String
    let file: String
    let mode: String
    let gain: Double
    let fadeMs: Int
    let isClue: Bool
    let printFallbackId: String?
    let description: String
    let playWhen: String
    let stopWhen: String
    let gmInstruction: String

    init(id: String, title: String, scene: String, category: String, scope: String = "native", layer: String? = nil, file: String, mode: String, gain: Double, fadeMs: Int, isClue: Bool, printFallbackId: String?, description: String = "", playWhen: String = "", stopWhen: String = "", gmInstruction: String = "") {
        self.id = id
        self.title = title
        self.scene = scene
        self.category = category
        self.scope = scope
        self.layer = layer ?? category
        self.file = file
        self.mode = mode
        self.gain = gain
        self.fadeMs = fadeMs
        self.isClue = isClue
        self.printFallbackId = printFallbackId
        self.description = description
        self.playWhen = playWhen
        self.stopWhen = stopWhen
        self.gmInstruction = gmInstruction
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        title = try container.decode(String.self, forKey: .title)
        scene = try container.decode(String.self, forKey: .scene)
        category = try container.decode(String.self, forKey: .category)
        scope = try container.decodeIfPresent(String.self, forKey: .scope) ?? "native"
        layer = try container.decodeIfPresent(String.self, forKey: .layer) ?? category
        file = try container.decode(String.self, forKey: .file)
        mode = try container.decode(String.self, forKey: .mode)
        gain = try container.decodeIfPresent(Double.self, forKey: .gain) ?? 0
        fadeMs = try container.decodeIfPresent(Int.self, forKey: .fadeMs) ?? 0
        isClue = try container.decodeIfPresent(Bool.self, forKey: .isClue) ?? false
        printFallbackId = try container.decodeIfPresent(String.self, forKey: .printFallbackId)
        description = try container.decodeIfPresent(String.self, forKey: .description) ?? ""
        playWhen = try container.decodeIfPresent(String.self, forKey: .playWhen) ?? ""
        stopWhen = try container.decodeIfPresent(String.self, forKey: .stopWhen) ?? ""
        gmInstruction = try container.decodeIfPresent(String.self, forKey: .gmInstruction) ?? ""
    }

    private enum CodingKeys: String, CodingKey {
        case id, title, scene, category, scope, layer, file, mode, gain, fadeMs, isClue, printFallbackId, description
        case playWhen, stopWhen, gmInstruction
    }

    var categoryLabel: String {
        switch layer {
        case "ambient": return "Atmosphäre"
        case "musicBed": return "Grundmusik"
        case "musicLayer": return "Musik-Layer"
        default: return "Effekt"
        }
    }

    var iconName: String {
        switch layer {
        case "ambient": return "wind"
        case "musicBed": return "music.note"
        case "musicLayer": return "waveform.path"
        default: return "sparkles"
        }
    }
}
