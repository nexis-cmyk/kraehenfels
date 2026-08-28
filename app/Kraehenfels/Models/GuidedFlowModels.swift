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
    case itemSearch
    case itemDistribution

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
        case .itemSearch: return "GEGENSTÄNDE FINDEN"
        case .itemDistribution: return "AUSRÜSTUNG VERTEILEN"
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
        case .itemSearch: return "shippingbox.fill"
        case .itemDistribution: return "person.3.sequence.fill"
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
    let failureConsequences: [RollConsequence]
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
        failureConsequences: [RollConsequence] = [],
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
        self.failureConsequences = failureConsequences
        self.guaranteedClue = guaranteedClue
        self.begabung = begabung
        self.required = required
    }

    private enum CodingKeys: String, CodingKey {
        case actor, ability, die, target, modifier, success, failure, critical, criticalFailure
        case reroll, failureConsequences, guaranteedClue, begabung, required
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
        failureConsequences = try container.decodeIfPresent([RollConsequence].self, forKey: .failureConsequences) ?? []
        guaranteedClue = try container.decodeIfPresent(Bool.self, forKey: .guaranteedClue) ?? false
        begabung = try container.decodeIfPresent(Bool.self, forKey: .begabung) ?? false
        required = try container.decodeIfPresent(Bool.self, forKey: .required) ?? false
    }
}

struct RollConsequenceEffect: Codable, Hashable {
    let threatDelta: Int?
    let minimumThreat: Int?

    init(threatDelta: Int? = nil, minimumThreat: Int? = nil) {
        self.threatDelta = threatDelta
        self.minimumThreat = minimumThreat
    }
}

struct RollConsequence: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let detail: String
    let endingIDs: [String]
    let effect: RollConsequenceEffect?

    init(
        id: String,
        title: String,
        detail: String,
        endingIDs: [String] = [],
        effect: RollConsequenceEffect? = nil
    ) {
        self.id = id
        self.title = title
        self.detail = detail
        self.endingIDs = endingIDs
        self.effect = effect
    }

    private enum CodingKeys: String, CodingKey {
        case id, title, detail, endingIDs, effect
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        title = try container.decode(String.self, forKey: .title)
        detail = try container.decode(String.self, forKey: .detail)
        endingIDs = try container.decodeIfPresent([String].self, forKey: .endingIDs) ?? []
        effect = try container.decodeIfPresent(RollConsequenceEffect.self, forKey: .effect)
    }

    func isAvailable(for endingID: String?) -> Bool {
        endingIDs.isEmpty || (endingID.map(endingIDs.contains) ?? false)
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
    let materialInstruction: String?
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
        materialInstruction: String? = nil,
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
        self.materialInstruction = materialInstruction
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
        case id, sceneID, kind, title, body, actionLabel, materialInstruction, roll, clueID, handoutID, handoutIDs
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
        materialInstruction = try container.decodeIfPresent(String.self, forKey: .materialInstruction)
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

enum ItemEffectTiming: String, Codable, Hashable {
    case beforeRoll
    case afterFailure
}

struct ItemEffect: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let detail: String
    let sceneIDs: [String]
    let stepIDs: [String]
    let consequenceIDs: [String]
    let endingIDs: [String]
    let timing: ItemEffectTiming
    let modifier: Int?

    init(
        id: String,
        title: String,
        detail: String,
        sceneIDs: [String] = [],
        stepIDs: [String] = [],
        consequenceIDs: [String] = [],
        endingIDs: [String] = [],
        timing: ItemEffectTiming = .beforeRoll,
        modifier: Int? = nil
    ) {
        self.id = id
        self.title = title
        self.detail = detail
        self.sceneIDs = sceneIDs
        self.stepIDs = stepIDs
        self.consequenceIDs = consequenceIDs
        self.endingIDs = endingIDs
        self.timing = timing
        self.modifier = modifier
    }

    private enum CodingKeys: String, CodingKey {
        case id, title, detail, sceneIDs, stepIDs, consequenceIDs, endingIDs, timing, modifier
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        title = try container.decode(String.self, forKey: .title)
        detail = try container.decode(String.self, forKey: .detail)
        sceneIDs = try container.decodeIfPresent([String].self, forKey: .sceneIDs) ?? []
        stepIDs = try container.decodeIfPresent([String].self, forKey: .stepIDs) ?? []
        consequenceIDs = try container.decodeIfPresent([String].self, forKey: .consequenceIDs) ?? []
        endingIDs = try container.decodeIfPresent([String].self, forKey: .endingIDs) ?? []
        timing = try container.decodeIfPresent(ItemEffectTiming.self, forKey: .timing) ?? .beforeRoll
        modifier = try container.decodeIfPresent(Int.self, forKey: .modifier)
    }

    func isAvailable(for stepID: String, endingID: String?) -> Bool {
        let matchesStep = stepIDs.isEmpty || stepIDs.contains(stepID)
        let matchesEnding = endingIDs.isEmpty || (endingID.map(endingIDs.contains) ?? false)
        return matchesStep && matchesEnding
    }
}

struct ItemWeapon: Codable, Hashable {
    let skill: String
    let damageDice: String
    let ammunition: Int
    let unparryable: Bool

    init(skill: String, damageDice: String, ammunition: Int, unparryable: Bool = false) {
        self.skill = skill
        self.damageDice = damageDice
        self.ammunition = ammunition
        self.unparryable = unparryable
    }
}

struct AdventureItem: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let locationID: String
    let detail: String
    let playerCardDetail: String?
    let playerCardUses: [String]
    let playerCardAsset: String?
    let initialUses: Int
    let effects: [ItemEffect]
    let weapon: ItemWeapon?

    init(
        id: String,
        title: String,
        locationID: String,
        detail: String,
        playerCardDetail: String? = nil,
        playerCardUses: [String] = [],
        playerCardAsset: String? = nil,
        initialUses: Int = 1,
        effects: [ItemEffect] = [],
        weapon: ItemWeapon? = nil
    ) {
        self.id = id
        self.title = title
        self.locationID = locationID
        self.detail = detail
        self.playerCardDetail = playerCardDetail
        self.playerCardUses = playerCardUses
        self.playerCardAsset = playerCardAsset
        self.initialUses = max(0, initialUses)
        self.effects = effects
        self.weapon = weapon
    }

    private enum CodingKeys: String, CodingKey {
        case id, title, locationID, detail, playerCardDetail, playerCardUses, playerCardAsset
        case initialUses, effects, weapon
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        title = try container.decode(String.self, forKey: .title)
        locationID = try container.decode(String.self, forKey: .locationID)
        detail = try container.decode(String.self, forKey: .detail)
        playerCardDetail = try container.decodeIfPresent(String.self, forKey: .playerCardDetail)
        playerCardUses = try container.decodeIfPresent([String].self, forKey: .playerCardUses) ?? []
        playerCardAsset = try container.decodeIfPresent(String.self, forKey: .playerCardAsset)
        initialUses = max(0, try container.decodeIfPresent(Int.self, forKey: .initialUses) ?? 1)
        effects = try container.decodeIfPresent([ItemEffect].self, forKey: .effects) ?? []
        weapon = try container.decodeIfPresent(ItemWeapon.self, forKey: .weapon)
    }
}

struct ItemFindLocation: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let detail: String
    let itemIDs: [String]
}

struct GuideContent: Codable {
    let characters: [QuickCharacter]
    let setupItems: [SetupItem]
    let playerBriefing: String
    let hiddenFromPlayers: String
    let itemFindLocations: [ItemFindLocation]
    let items: [AdventureItem]
    let steps: [String: [GuideStep]]

    init(
        characters: [QuickCharacter] = [],
        setupItems: [SetupItem] = [],
        playerBriefing: String = "",
        hiddenFromPlayers: String = "",
        itemFindLocations: [ItemFindLocation] = [],
        items: [AdventureItem] = [],
        steps: [String: [GuideStep]] = [:]
    ) {
        self.characters = characters
        self.setupItems = setupItems
        self.playerBriefing = playerBriefing
        self.hiddenFromPlayers = hiddenFromPlayers
        self.itemFindLocations = itemFindLocations
        self.items = items
        self.steps = steps
    }

    private enum CodingKeys: String, CodingKey {
        case characters, setupItems, playerBriefing, hiddenFromPlayers, itemFindLocations, items, steps
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        characters = try container.decodeIfPresent([QuickCharacter].self, forKey: .characters) ?? []
        setupItems = try container.decodeIfPresent([SetupItem].self, forKey: .setupItems) ?? []
        playerBriefing = try container.decodeIfPresent(String.self, forKey: .playerBriefing) ?? ""
        hiddenFromPlayers = try container.decodeIfPresent(String.self, forKey: .hiddenFromPlayers) ?? ""
        itemFindLocations = try container.decodeIfPresent([ItemFindLocation].self, forKey: .itemFindLocations) ?? []
        items = try container.decodeIfPresent([AdventureItem].self, forKey: .items) ?? []
        steps = try container.decodeIfPresent([String: [GuideStep]].self, forKey: .steps) ?? [:]
    }

    static let empty = GuideContent()

    func steps(for sceneID: String) -> [GuideStep] {
        steps[sceneID] ?? []
    }

    func item(for id: String) -> AdventureItem? {
        items.first(where: { $0.id == id })
    }
}

struct RuleEntry: Codable, Identifiable, Hashable {
    let id: String
    let title: String
    let body: String
}

struct RollResolutionRecord: Codable, Identifiable, Hashable {
    let id: UUID
    let stepID: String
    let roll: Int
    let target: Int
    let label: String
    let isSuccess: Bool
    let isCriticalFailure: Bool
    let consequenceID: String?
    let consequenceTitle: String?
    let itemUseIDs: [String]

    init(stepID: String, result: RollEvaluator.Result, consequence: RollConsequence?, itemUseIDs: [String] = []) {
        id = UUID()
        self.stepID = stepID
        roll = result.roll
        target = result.target
        label = result.label
        isSuccess = result.isSuccess
        isCriticalFailure = result.isCriticalFailure
        consequenceID = consequence?.id
        consequenceTitle = consequence?.title
        self.itemUseIDs = itemUseIDs
    }

    private enum CodingKeys: String, CodingKey {
        case id, stepID, roll, target, label, isSuccess, isCriticalFailure, consequenceID, consequenceTitle, itemUseIDs
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(UUID.self, forKey: .id)
        stepID = try container.decode(String.self, forKey: .stepID)
        roll = try container.decode(Int.self, forKey: .roll)
        target = try container.decode(Int.self, forKey: .target)
        label = try container.decode(String.self, forKey: .label)
        isSuccess = try container.decode(Bool.self, forKey: .isSuccess)
        isCriticalFailure = try container.decode(Bool.self, forKey: .isCriticalFailure)
        consequenceID = try container.decodeIfPresent(String.self, forKey: .consequenceID)
        consequenceTitle = try container.decodeIfPresent(String.self, forKey: .consequenceTitle)
        itemUseIDs = try container.decodeIfPresent([String].self, forKey: .itemUseIDs) ?? []
    }
}

struct ItemUseRecord: Codable, Identifiable, Hashable {
    let id: UUID
    let itemID: String
    let effectID: String
    let sceneID: String
    let stepID: String

    init(itemID: String, effectID: String, sceneID: String, stepID: String) {
        id = UUID()
        self.itemID = itemID
        self.effectID = effectID
        self.sceneID = sceneID
        self.stepID = stepID
    }
}

struct ItemUseSelection: Hashable {
    let itemID: String
    let effectID: String
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
        let isSuccess = safeRoll <= safeTarget && !criticalFailure
        return Result(roll: safeRoll, target: safeTarget, isSuccess: isSuccess, isCriticalSuccess: criticalSuccess, isCriticalFailure: criticalFailure)
    }
}
