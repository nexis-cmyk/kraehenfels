import Foundation

enum GuideStepKind: String, Codable, Hashable {
    case readAloud
    case gmInfo
    case playerAction
    case trigger
    case roll
    case clue
    case choice
    case next

    var label: String {
        switch self {
        case .readAloud: return "JETZT VORLESEN"
        case .gmInfo: return "NUR FÜR DIE SPIELLEITUNG"
        case .playerAction: return "DIE SPIELER KÖNNEN JETZT"
        case .trigger: return "WENN DAS PASSIERT"
        case .roll: return "WÜRFELPROBE"
        case .clue: return "HINWEIS ODER GEGENSTAND"
        case .choice: return "ENTSCHEIDUNG"
        case .next: return "NÄCHSTER SCHRITT"
        }
    }

    var symbol: String {
        switch self {
        case .readAloud: return "quote.opening"
        case .gmInfo: return "eye.slash.fill"
        case .playerAction: return "person.3.fill"
        case .trigger: return "bolt.fill"
        case .roll: return "dice.fill"
        case .clue: return "doc.text.magnifyingglass"
        case .choice: return "arrow.triangle.branch"
        case .next: return "arrow.right.circle.fill"
        }
    }
}

struct RollSpec: Codable, Hashable {
    let actor: String
    let ability: String
    let die: String
    let target: String
    let modifier: String
    let success: String
    let failure: String
    let critical: String
    let criticalFailure: String
    let reroll: String
    let guaranteedClue: Bool
    let begabung: Bool
    let required: Bool

    init(
        actor: String,
        ability: String,
        target: String,
        modifier: String = "Kein Modifikator.",
        success: String,
        failure: String,
        critical: String = "Besonders schnell und ohne Zusatzkosten.",
        criticalFailure: String = "Der Misserfolg tritt mit einer zusätzlichen Komplikation ein.",
        reroll: String = "Ein Geistesblitz darf eine nicht kritisch misslungene Probe wiederholen.",
        guaranteedClue: Bool = false,
        begabung: Bool = false,
        required: Bool = false
    ) {
        self.actor = actor
        self.ability = ability
        self.die = "W100"
        self.target = target
        self.modifier = modifier
        self.success = success
        self.failure = failure
        self.critical = critical
        self.criticalFailure = criticalFailure
        self.reroll = reroll
        self.guaranteedClue = guaranteedClue
        self.begabung = begabung
        self.required = required
    }

    private enum CodingKeys: String, CodingKey {
        case actor, ability, die, target, modifier, success, failure, critical, criticalFailure
        case reroll, guaranteedClue, begabung, required
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        actor = try container.decode(String.self, forKey: .actor)
        ability = try container.decode(String.self, forKey: .ability)
        die = try container.decodeIfPresent(String.self, forKey: .die) ?? "W100"
        target = try container.decode(String.self, forKey: .target)
        modifier = try container.decodeIfPresent(String.self, forKey: .modifier) ?? "Kein Modifikator."
        success = try container.decode(String.self, forKey: .success)
        failure = try container.decode(String.self, forKey: .failure)
        critical = try container.decodeIfPresent(String.self, forKey: .critical) ?? "Besonders schnell und ohne Zusatzkosten."
        criticalFailure = try container.decodeIfPresent(String.self, forKey: .criticalFailure) ?? "Der Misserfolg tritt mit einer zusätzlichen Komplikation ein."
        reroll = try container.decodeIfPresent(String.self, forKey: .reroll) ?? "Ein Geistesblitz darf eine nicht kritisch misslungene Probe wiederholen."
        guaranteedClue = try container.decodeIfPresent(Bool.self, forKey: .guaranteedClue) ?? false
        begabung = try container.decodeIfPresent(Bool.self, forKey: .begabung) ?? false
        required = try container.decodeIfPresent(Bool.self, forKey: .required) ?? false
    }
}

struct GuideOption: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let detail: String
    let destinationSceneID: String?
    let endingID: String?

    init(id: String, title: String, detail: String, destinationSceneID: String? = nil, endingID: String? = nil) {
        self.id = id
        self.title = title
        self.detail = detail
        self.destinationSceneID = destinationSceneID
        self.endingID = endingID
    }
}

struct GuideStep: Codable, Identifiable, Hashable {
    let id: String
    let sceneID: String
    let kind: GuideStepKind
    let title: String
    let body: String
    let actionLabel: String
    let roll: RollSpec?
    let clueID: String?
    let handoutID: String?
    let handoutIDs: [String]
    let npcID: String?
    let npcIDs: [String]
    let audioCueID: String?
    let options: [GuideOption]

    init(
        id: String,
        sceneID: String,
        kind: GuideStepKind,
        title: String,
        body: String,
        actionLabel: String = "Erledigt",
        roll: RollSpec? = nil,
        clueID: String? = nil,
        handoutID: String? = nil,
        handoutIDs: [String] = [],
        npcID: String? = nil,
        npcIDs: [String] = [],
        audioCueID: String? = nil,
        options: [GuideOption] = []
    ) {
        self.id = id
        self.sceneID = sceneID
        self.kind = kind
        self.title = title
        self.body = body
        self.actionLabel = actionLabel
        self.roll = roll
        self.clueID = clueID
        self.handoutID = handoutID
        self.handoutIDs = handoutIDs
        self.npcID = npcID
        self.npcIDs = npcIDs
        self.audioCueID = audioCueID
        self.options = options
    }

    private enum CodingKeys: String, CodingKey {
        case id, sceneID, kind, title, body, actionLabel, roll, clueID, handoutID, handoutIDs
        case npcID, npcIDs, audioCueID, options
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        sceneID = try container.decode(String.self, forKey: .sceneID)
        kind = try container.decode(GuideStepKind.self, forKey: .kind)
        title = try container.decode(String.self, forKey: .title)
        body = try container.decode(String.self, forKey: .body)
        actionLabel = try container.decodeIfPresent(String.self, forKey: .actionLabel) ?? "Erledigt"
        roll = try container.decodeIfPresent(RollSpec.self, forKey: .roll)
        clueID = try container.decodeIfPresent(String.self, forKey: .clueID)
        handoutID = try container.decodeIfPresent(String.self, forKey: .handoutID)
        handoutIDs = try container.decodeIfPresent([String].self, forKey: .handoutIDs) ?? []
        npcID = try container.decodeIfPresent(String.self, forKey: .npcID)
        npcIDs = try container.decodeIfPresent([String].self, forKey: .npcIDs) ?? []
        audioCueID = try container.decodeIfPresent(String.self, forKey: .audioCueID)
        options = try container.decodeIfPresent([GuideOption].self, forKey: .options) ?? []
    }
}

struct QuickCharacter: Codable, Identifiable, Hashable {
    let id: String
    let name: String
    let role: String
    let hook: String
    let strengths: [String]
    let skills: [String]
    let tablePrompt: String
}

struct SetupItem: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let detail: String
}

struct GuideContent: Codable {
    let characters: [QuickCharacter]
    let setupItems: [SetupItem]
    let playerBriefing: String
    let hiddenFromPlayers: String
    let steps: [String: [GuideStep]]

    static let empty = GuideContent(characters: [], setupItems: [], playerBriefing: "", hiddenFromPlayers: "", steps: [:])

    func steps(for sceneID: String) -> [GuideStep] {
        steps[sceneID] ?? []
    }
}

struct RuleEntry: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let body: String
}

enum RollEvaluator {
    struct Result: Hashable {
        let roll: Int
        let target: Int
        let isSuccess: Bool
        let isCriticalSuccess: Bool
        let isCriticalFailure: Bool

        var label: String {
            if isCriticalFailure { return "Kritischer Misserfolg" }
            if isCriticalSuccess { return "Kritischer Erfolg" }
            return isSuccess ? "Erfolg" : "Misserfolg"
        }
    }

    static func evaluate(roll: Int, target: Int, begabung: Bool = false) -> Result {
        let safeRoll = min(max(roll, 1), 100)
        let safeTarget = min(max(target, 1), 100)
        let criticalSuccess = Double(safeRoll) <= Double(safeTarget) * 0.10
        let criticalFailure = Double(safeRoll) >= 90.0 + Double(safeTarget) * 0.10
        return Result(roll: safeRoll, target: safeTarget, isSuccess: safeRoll <= safeTarget, isCriticalSuccess: criticalSuccess, isCriticalFailure: criticalFailure)
    }
}
