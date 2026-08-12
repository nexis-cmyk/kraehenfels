import Foundation

enum GuideStepKind: String, Hashable {
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

struct RollSpec: Hashable {
    let actor: String
    let ability: String
    let die: String
    let target: String
    let modifier: String
    let success: String
    let failure: String
    let critical: String
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
        self.reroll = reroll
        self.guaranteedClue = guaranteedClue
        self.begabung = begabung
        self.required = required
    }
}

struct GuideOption: Identifiable, Hashable {
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

struct GuideStep: Identifiable, Hashable {
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
}

struct QuickCharacter: Identifiable, Hashable {
    let id: String
    let name: String
    let role: String
    let hook: String
    let strengths: [String]
    let skills: [String]
    let tablePrompt: String
}

struct SetupItem: Identifiable, Hashable {
    let id: String
    let title: String
    let detail: String
}

enum GuidedFlowCatalog {
    static let characters: [QuickCharacter] = [
        QuickCharacter(
            id: "CHAR_CLARA",
            name: "Clara Neumann",
            role: "Journalistin",
            hook: "Eine Person aus Claras Umfeld verschwand auf derselben Strecke.",
            strengths: ["Wissen", "Soziales", "Menschen einschätzen"],
            skills: ["Wissen 65", "Soziales 60", "Menschen einschätzen 70", "Handeln 35"],
            tablePrompt: "Clara fragt nach Namen, Widersprüchen und Dingen, die andere lieber verschweigen."
        ),
        QuickCharacter(
            id: "CHAR_OTTO",
            name: "Otto Weiss",
            role: "Ehemaliger Gendarm",
            hook: "Otto erkennt später einen Namen im Gästebuch aus einem alten Fall.",
            strengths: ["Handeln", "Wahrnehmung", "Spuren sichern"],
            skills: ["Handeln 65", "Wahrnehmung 70", "Spuren sichern 65", "Soziales 40"],
            tablePrompt: "Otto achtet auf Türen, Wege, Werkzeuge und darauf, wer wann wo gewesen ist."
        ),
        QuickCharacter(
            id: "CHAR_JAKOB",
            name: "Dr. Jakob Adler",
            role: "Landarzt",
            hook: "Jakob soll Bürgermeister Gruber einen versiegelten Auftrag übergeben.",
            strengths: ["Erste Hilfe", "Wissen", "Ruhig bleiben"],
            skills: ["Erste Hilfe 75", "Wissen 60", "Ruhig bleiben 65", "Handeln 35"],
            tablePrompt: "Jakob hilft Verletzten zuerst und stellt dann die Fragen, die niemand hören will."
        )
    ]

    static let setupItems: [SetupItem] = [
        SetupItem(id: "print", title: "Drucksachen", detail: "Spielerkarte, Detailkarten, Handouts H01–H10 und drei Figurenblätter."),
        SetupItem(id: "dice", title: "Würfel und Stifte", detail: "W100 (oder zwei W10), W10 für Initiative und Schaden, Papier für Notizen."),
        SetupItem(id: "audio", title: "Audioausgabe", detail: "iPhone-Lautsprecher oder Bluetooth-Box; Audio-Check einmal abspielen."),
        SetupItem(id: "spoilers", title: "Spoiler trennen", detail: "H09 und die SL-Karte bleiben bei dir. Spieler sehen nur die Spielerkarte."),
        SetupItem(id: "safety", title: "Sicherheitscheck", detail: "Kurz klären, welche Horror-Motive heute okay sind und wann ihr pausiert.")
    ]

    static func steps(for sceneID: String) -> [GuideStep] {
        switch sceneID {
        case "S01": return coachSteps
        case "S02": return innSteps
        case "S03": return churchSteps
        case "S04": return smithySteps
        case "S05": return woodsSteps
        case "S06": return archiveSteps
        case "S07": return oakSteps
        case "S08": return epilogueSteps
        default: return []
        }
    }

    static func index(of stepID: String, in sceneID: String) -> Int {
        steps(for: sceneID).firstIndex(where: { $0.id == stepID }) ?? 0
    }

    private static let coachSteps: [GuideStep] = [
        GuideStep(id: "S01_READ", sceneID: "S01", kind: .readAloud, title: "Der Unfall beginnt", body: "Der Schnee kommt waagerecht durch die Tannen. Ein Knacken läuft durch die Kutsche. Dann kippt die Welt, Pferdeatem schlägt gegen die Scheiben und irgendwo im Wald ruft der Kutscher nach Hilfe.", actionLabel: "Vorgelesen", audioCueID: "M01"),
        GuideStep(id: "S01_GM", sceneID: "S01", kind: .gmInfo, title: "Was wirklich passiert ist", body: "Die Achse wurde vor der Abfahrt angesägt. Der Kutscher lebt und ist im Wald verschwunden. Gib den Spielern Raum, spontan zu handeln; sie müssen den Unfall nicht verhindern.", actionLabel: "Verstanden"),
        GuideStep(id: "S01_ACT", sceneID: "S01", kind: .playerAction, title: "Erste Reaktionen", body: "Lass die Gruppe Verletzte versorgen, die Pferde beruhigen und die Umgebung prüfen. Beschreibe nur, was sie konkret untersuchen.", actionLabel: "Handlungen zugelassen", roll: RollSpec(actor: "Eine passende Figur", ability: "Handeln oder Erste Hilfe", target: "Der Wert der gewählten Fertigkeit", modifier: "Bei eisigem Boden −10, wenn die Beschreibung das rechtfertigt.", success: "Die Figur verliert keine zusätzliche Wärme oder Zeit.", failure: "Die Hilfe gelingt trotzdem, kostet aber Zeit oder eine kleine Verletzung.", critical: "Die Gruppe findet sofort einen sicheren Weg zum Auftrag.")),
        GuideStep(id: "S01_CLUE", sceneID: "S01", kind: .clue, title: "Kutschauftrag übergeben", body: "Der Auftrag liegt unter dem Sitz. Zeige H01. Die frischen Kerben an der Achse und Grubers genaue Umleitung sind Pflichtinformationen und werden nicht weggewürfelt.", actionLabel: "H01 zeigen", clueID: "C01", handoutID: "H01"),
        GuideStep(id: "S01_NEXT", sceneID: "S01", kind: .next, title: "Der Weg nach Krähenfels", body: "Sobald die Gruppe den Auftrag hat und weitergehen will, endet die Unfallszene. Starte beim Aufbruch die Kutschenstraßen-Atmosphäre aus und führe zum Schwarzen Keiler.", actionLabel: "Zum Schwarzen Keiler", audioCueID: "A01", options: [GuideOption(id: "toS02", title: "Zum Schwarzen Keiler", detail: "Die Lichter des Dorfes werden sichtbar.", destinationSceneID: "S02")])
    ]

    private static let innSteps: [GuideStep] = [
        GuideStep(id: "S02_READ", sceneID: "S02", kind: .readAloud, title: "Die Lichter im Schnee", body: "Hinter den Tannen erscheinen drei gelbe Fenster. Das Schild Zum Schwarzen Keiler knarrt über einer Tür, aus der Wärme und der Geruch von nassem Holz dringen.", actionLabel: "Vorgelesen", audioCueID: "A02"),
        GuideStep(id: "S02_GM", sceneID: "S02", kind: .gmInfo, title: "Gasthaus-Zustände", body: "Gruber öffnet die Eingangstür freundlich. Das Gästezimmer ist zunächst offen. Erst wenn die Gruppe schlafen möchte oder zwei wesentliche Gespräche geführt hat, verriegelt Gruber die Zimmertür von außen. Spiele SFX03 dann einmal.", actionLabel: "Zustände notiert", npcID: "N01"),
        GuideStep(id: "S02_ACT", sceneID: "S02", kind: .playerAction, title: "Freie Ermittlungsrunde", body: "Die Spieler dürfen essen, mit Gruber, Elara oder Leni sprechen, das Gästebuch ansehen oder die Räume auf der Inn-Karte untersuchen. Eine Untersuchung liefert den relevanten Hinweis immer.", actionLabel: "Freies Spiel öffnen", npcID: "N02", npcIDs: ["N01", "N06"]),
        GuideStep(id: "S02_CLUE", sceneID: "S02", kind: .clue, title: "Gästebuch und Riegel", body: "Zeige H03, sobald jemand nach früheren Gästen, roten Strichen oder der verschlossenen Tür fragt. C03 und C04 sind garantiert. Bei einem passenden Gespräch nennt Elara zusätzlich den letzten gestrichenen Namen.", actionLabel: "H03 zeigen", clueID: "C03", handoutID: "H03", audioCueID: "SFX03"),
        GuideStep(id: "S02_ROLL", sceneID: "S02", kind: .roll, title: "Tür öffnen oder umgehen", body: "Nur würfeln, wenn die Gruppe die verriegelte Tür gewaltsam oder mit Werkzeug öffnen will. Fenster, Elara oder ein zweiter Weg bleiben als Alternativen offen.", actionLabel: "Probe auswerten", roll: RollSpec(actor: "Die Figur mit der besten Idee", ability: "Handeln oder Schlösser", target: "Der Wert der gewählten Fertigkeit", modifier: "−10 bei Eile; kein Malus bei einem ruhigen Werkzeugversuch.", success: "Die Tür öffnet sich leise. Die Gruppe behält die Initiative.", failure: "Die Tür öffnet sich mit Lärm oder Zeitverlust. Der Hinweis bleibt erhalten und die Bedrohung steigt um 1.", critical: "Die Gruppe entdeckt zusätzlich, wer den Riegel angebracht hat.")),
        GuideStep(id: "S02_CHOICE", sceneID: "S02", kind: .choice, title: "Welcher Spur folgt die Gruppe?", body: "Empfiehl zwei Orte, wenn die Gruppe unsicher ist. Jede Reihenfolge ist gültig. Der nächste Schritt wird später wieder zum Ermittlungszentrum zurückführen.", actionLabel: "Ort wählen", options: [
            GuideOption(id: "church", title: "Kirche und Kirchenbuch", detail: "Das ursprüngliche Gastrecht prüfen.", destinationSceneID: "S03"),
            GuideOption(id: "smithy", title: "Schmiede", detail: "Die drei schwarzen Nägel untersuchen.", destinationSceneID: "S04"),
            GuideOption(id: "woods", title: "Waldspur", detail: "Lenis Zeichnung und Elias befragen.", destinationSceneID: "S05")
        ])
    ]

    private static let churchSteps: [GuideStep] = [
        GuideStep(id: "S03_READ", sceneID: "S03", kind: .readAloud, title: "Die kalte Kirche", body: "Die Kirchentür gibt nach. Dahinter riecht es nach nassem Stein und altem Wachs. Eine Seite im Kirchenbuch ist sauber herausgeschnitten.", actionLabel: "Vorgelesen", audioCueID: "A04"),
        GuideStep(id: "S03_ACT", sceneID: "S03", kind: .playerAction, title: "Falk befragen", body: "Matthias Falk bleibt bei der Sakristeitür. Er hilft, wenn jemand nicht nur nach Gruber, sondern nach dem Sinn des Gastrechts fragt.", actionLabel: "Gespräch führen", npcID: "N04"),
        GuideStep(id: "S03_CLUE", sceneID: "S03", kind: .clue, title: "Das alte Gastrecht", body: "Zeige H04 oder lies die Ersatzzeile vor: Wer unter einem Krähenfelser Dach schläft, steht bis zum Hahnenschrei unter Schutz. Dieser Hinweis ist nicht von einer Probe abhängig.", actionLabel: "H04 zeigen", clueID: "C05", handoutID: "H04", npcID: "N04"),
        GuideStep(id: "S03_ROLL", sceneID: "S03", kind: .roll, title: "Falk zum Geständnis bringen", body: "Nur würfeln, wenn Falk trotz einer klaren Frage schweigt. Die Eidzeile bleibt gefunden; der Wurf entscheidet nur, ob Falk zusätzlich seine Mitschuld offenlegt.", actionLabel: "Probe auswerten", roll: RollSpec(actor: "Die Figur, die Falk anspricht", ability: "Soziales", target: "Der Wert der gewählten sozialen Fertigkeit", modifier: "+10, wenn die Gruppe H03 oder den versiegelten Auftrag zeigt.", success: "Falk nennt Grubers Vater und den entfernten Buchabschnitt.", failure: "Falk bleibt vage; die Gruppe kann die fehlende Verbindung später im Archiv schließen.", critical: "Falk übergibt freiwillig den zweiten Schlüssel.")),
        GuideStep(id: "S03_NEXT", sceneID: "S03", kind: .next, title: "Zurück ins Ermittlungszentrum", body: "Markiere Kirche als besucht. Danach darf die Gruppe zur Schmiede, zur Waldspur oder – falls zwei Orte besucht sind – ins Archiv wechseln.", actionLabel: "Ort wählen", options: [GuideOption(id: "smithy", title: "Schmiede", detail: "Das Eisen prüfen.", destinationSceneID: "S04"), GuideOption(id: "woods", title: "Waldspur", detail: "Zur Eiche folgen.", destinationSceneID: "S05"), GuideOption(id: "archive", title: "Rathausarchiv", detail: "Nur empfehlen, wenn zwei Ermittlungsorte besucht sind.", destinationSceneID: "S06")])
    ]

    private static let smithySteps: [GuideStep] = [
        GuideStep(id: "S04_READ", sceneID: "S04", kind: .readAloud, title: "Die Schmiede", body: "Hinter der Tür glimmt die Esse. Marta lässt den Hammer sinken und betrachtet zuerst die Hände, nicht die Gesichter der Reisenden.", actionLabel: "Vorgelesen", audioCueID: "A05"),
        GuideStep(id: "S04_ACT", sceneID: "S04", kind: .playerAction, title: "Marta entscheidet", body: "Marta hilft, wenn die Gruppe sagt, wofür sie das Eisen braucht. Sie gibt keine Waffe aus bloßer Neugier heraus.", actionLabel: "Absicht ausspielen", npcID: "N05"),
        GuideStep(id: "S04_CLUE", sceneID: "S04", kind: .clue, title: "Drei schwarze Nägel", body: "Zeige H06. Die Zeichnung erklärt, dass drei handgeschmiedete Nägel Geweih und Holzherz binden. Feuer kann die Bindung zerstören.", actionLabel: "H06 zeigen", clueID: "C07", handoutID: "H06", npcID: "N05", audioCueID: "SFX05"),
        GuideStep(id: "S04_ROLL", sceneID: "S04", kind: .roll, title: "Marta überzeugen", body: "Nur würfeln, wenn die Gruppe keine klare Absicht formuliert oder Marta misstrauisch bleibt. Der Hinweis und die Zeichnung werden nicht blockiert.", actionLabel: "Probe auswerten", roll: RollSpec(actor: "Die Figur mit der besten Begründung", ability: "Soziales oder Handeln", target: "Der Wert der gewählten Fertigkeit", modifier: "+10, wenn die Gruppe das Gastrecht aus der Kirche kennt.", success: "Marta gibt das Eisen und nennt den Preis der Zerstörung.", failure: "Marta verlangt eine Gegenleistung oder folgt später selbst.", critical: "Marta schärft das Eisen ohne Gegenleistung.")),
        GuideStep(id: "S04_NEXT", sceneID: "S04", kind: .next, title: "Zurück ins Ermittlungszentrum", body: "Markiere die Schmiede als besucht und biete Waldspur, Kirche oder – nach zwei Orten – das Archiv an.", actionLabel: "Ort wählen", options: [GuideOption(id: "woods", title: "Waldspur", detail: "Lenis Spur folgen.", destinationSceneID: "S05"), GuideOption(id: "church", title: "Kirche", detail: "Das Gastrecht prüfen.", destinationSceneID: "S03"), GuideOption(id: "archive", title: "Rathausarchiv", detail: "Buchhaltung und Ritualfragment suchen.", destinationSceneID: "S06")])
    ]

    private static let woodsSteps: [GuideStep] = [
        GuideStep(id: "S05_READ", sceneID: "S05", kind: .readAloud, title: "Hinter den letzten Häusern", body: "Hinter dem letzten Zaun wird der Schnee unberührt. Zwischen den Stämmen hängt ein roter Faden, dann endet jede menschliche Spur an einem Kreis aus dunklem Holz.", actionLabel: "Vorgelesen", audioCueID: "A06"),
        GuideStep(id: "S05_ACT", sceneID: "S05", kind: .playerAction, title: "Leni und Elias", body: "Leni zeigt ihre Zeichnung nur, wenn sie ernst genommen wird. Elias spricht zunächst in drei Verben: öffnen, erinnern, brechen.", actionLabel: "Gespräch führen", npcID: "N03", npcIDs: ["N06"]),
        GuideStep(id: "S05_CLUE", sceneID: "S05", kind: .clue, title: "Zeichnung, Rubbing und Forstkarte", body: "Zeige H07, H08 und H10 in dieser Reihenfolge. Sie führen zur Eiche und erklären die drei Handlungsmöglichkeiten. Die Spur selbst ist sicher; ein Würfelwurf bestimmt nur Zeit und Kälte.", actionLabel: "Drei Hinweise zeigen", clueID: "C08", handoutID: "H07", handoutIDs: ["H08", "H10"], npcID: "N06"),
        GuideStep(id: "S05_ROLL", sceneID: "S05", kind: .roll, title: "Durch den Wald", body: "Nur würfeln, wenn die Gruppe bei Sturm, Dunkelheit oder Verfolgung eine riskante Abkürzung nimmt.", actionLabel: "Probe auswerten", roll: RollSpec(actor: "Die führende Figur", ability: "Handeln oder Wahrnehmung", target: "Der Wert der gewählten Fertigkeit", modifier: "−10 bei Sturm; kein Malus auf dem eingezeichneten Forstweg.", success: "Die Gruppe erreicht die Rückseite der Eiche ohne Zeitverlust.", failure: "Die Gruppe erreicht sie trotzdem, verliert aber Wärme oder die Prozession gewinnt Zeit.", critical: "Die Gruppe entdeckt einen sicheren Zugang und einen zusätzlichen Rückzugsweg.")),
        GuideStep(id: "S05_NEXT", sceneID: "S05", kind: .next, title: "Archiv oder Eiche", body: "Markiere die Waldspur als besucht. Wenn noch Tatsachen fehlen, führt der nächste sinnvolle Schritt ins Archiv. Die Eiche bleibt bis zur Wahrheitsphase ein Ziel, kein Finale.", actionLabel: "Ort wählen", options: [GuideOption(id: "archive", title: "Rathausarchiv", detail: "Die Winterbuchhaltung prüfen.", destinationSceneID: "S06"), GuideOption(id: "church", title: "Kirche", detail: "Das Gastrecht ergänzen.", destinationSceneID: "S03"), GuideOption(id: "smithy", title: "Schmiede", detail: "Das Eisen sichern.", destinationSceneID: "S04")])
    ]

    private static let archiveSteps: [GuideStep] = [
        GuideStep(id: "S06_READ", sceneID: "S06", kind: .readAloud, title: "Das Rathausarchiv", body: "Das Archiv ist wärmer als die Straße, aber nicht freundlicher. Auf dem Tisch liegt ein Buch, dessen Seiten an den Rändern wie von Frost gekräuselt sind.", actionLabel: "Vorgelesen", audioCueID: "A07"),
        GuideStep(id: "S06_GM", sceneID: "S06", kind: .gmInfo, title: "Wahrheit zusammenführen", body: "Hier fasst du die bereits gefundenen Fakten laut für dich zusammen. Fehlt eine Verbindung, gib die passende Ersatzroute über Falk, Marta, Elias oder Elara. Die Gruppe darf die Lösung selbst formulieren.", actionLabel: "Fakten prüfen", npcID: "N01", npcIDs: ["N04", "N05", "N03", "N02"]),
        GuideStep(id: "S06_CLUE", sceneID: "S06", kind: .clue, title: "Winterbuchhaltung und Ritualfragment", body: "Zeige H05. H09 bleibt ein SL-Spoiler und wird nur gezeigt oder vorgelesen, wenn die Gruppe die drei Folgen noch nicht aus anderen Spuren kennt. C06 und C10 werden dadurch bestätigt.", actionLabel: "H05 zeigen", clueID: "C06", handoutID: "H05"),
        GuideStep(id: "S06_ROLL", sceneID: "S06", kind: .roll, title: "Die Seiten zeitig verbinden", body: "Würfeln nur unter Zeitdruck. Die Seiten und ihre Fakten bleiben gefunden; ein Fehlschlag bedeutet, dass die Prozession früher sichtbar wird.", actionLabel: "Probe auswerten", roll: RollSpec(actor: "Die Figur mit der besten Rechercheidee", ability: "Wissen", target: "Der Wert der Wissensfertigkeit", modifier: "+10, wenn bereits zwei Ermittlungsorte besucht wurden.", success: "Die Gruppe erkennt Grubers verdrehten Pakt vor dem Glockenschlag.", failure: "Die Erkenntnis kommt erst mit den Schritten vor dem Fenster; erhöhe die Bedrohung auf 4.", critical: "Die Gruppe erkennt auch, welche Person Gruber als Nächstes opfern will.")),
        GuideStep(id: "S06_TRIGGER", sceneID: "S06", kind: .trigger, title: "Die Prozession setzt sich in Bewegung", body: "Wenn die Gruppe die Fakten verbindet oder die Zeit verstreicht, starte M02 leise und spiele SFX07 einmal. Danach gibt es keine weitere Ermittlungsrunde mehr.", actionLabel: "Prozession starten", audioCueID: "SFX07"),
        GuideStep(id: "S06_NEXT", sceneID: "S06", kind: .next, title: "Zur Alten Eiche", body: "Alle Wege führen jetzt zum Finale. Lege die SL-Karte bereit und führe die Gruppe zur Eiche.", actionLabel: "Zum Finale", options: [GuideOption(id: "oak", title: "Zur Alten Eiche", detail: "Die Prozession erreicht den Schrein.", destinationSceneID: "S07")])
    ]

    private static let oakSteps: [GuideStep] = [
        GuideStep(id: "S07_READ", sceneID: "S07", kind: .readAloud, title: "Die Alte Eiche", body: "Die Alte Eiche steht im Schnee wie ein schwarzes Gerippe. Zwischen den Wurzeln hängt die Geweihreliquie. Hinter euch setzt die Prozession ein, vor euch hebt der Knochenhirsch den Kopf.", actionLabel: "Vorgelesen", audioCueID: "A08"),
        GuideStep(id: "S07_GM", sceneID: "S07", kind: .gmInfo, title: "Drei Auswege", body: "Biete die drei Wege erst an, wenn die Gruppe verstanden hat, dass Gastrecht, Erinnerung und Feuer unterschiedliche Folgen haben. Spiele SFX08 nur beim vollständigen ersten Anblick des Wesens.", actionLabel: "Finale vorbereiten", audioCueID: "SFX08"),
        GuideStep(id: "S07_CHOICE", sceneID: "S07", kind: .choice, title: "Die Gruppe entscheidet", body: "Lass die Spieler die Entscheidung in eigenen Worten treffen. Danach wählst du die filmische Gefahrenszene oder schaltest optional den vollständigen HTBAH-Kampf ein.", actionLabel: "Ende wählen", options: [
            GuideOption(id: "revoke", title: "Gastrecht widerrufen", detail: "Das Dorf spricht die Wahrheit öffentlich aus.", endingID: "E01"),
            GuideOption(id: "renew", title: "Gastrecht erneuern", detail: "Eine Figur übernimmt den alten Eid.", endingID: "E02"),
            GuideOption(id: "break", title: "Bindung zerstören", detail: "Eisen und Feuer brechen die Reliquie.", endingID: "E03")
        ]),
        GuideStep(id: "S07_DANGER", sceneID: "S07", kind: .roll, title: "Geführte Gefahrenszene", body: "Im geführten Modus würfelt die Gruppe die passende Fertigkeit des gewählten Endes. Zwei Erfolge vor zwei Fehlschlägen reichen. Bei E01 passt Soziales, bei E02 Wissen oder Soziales, bei E03 Handeln mit dem Eisen.", actionLabel: "Probe auswerten", roll: RollSpec(actor: "Die Figur mit dem stärksten persönlichen Bezug", ability: "Passende Fähigkeit des gewählten Endes", target: "Der Wert der gewählten Fertigkeit", modifier: "Ein zuvor passender Hinweis gibt +10; ein kritischer Misserfolg zählt als zwei Fehlschläge.", success: "Die Szene kippt zugunsten der Gruppe.", failure: "Zeit, Wärme oder Vertrauen gehen verloren; der nächste Versuch bleibt möglich.", critical: "Ein NPC schließt sich sichtbar an.", guaranteedClue: true, required: true)),
        GuideStep(id: "S07_COMBAT", sceneID: "S07", kind: .gmInfo, title: "Optional: vollständiger HTBAH-Kampf", body: "Wenn du Kampfmodus wählst: Initiative mit W10 + Handeln, höchste Zahl zuerst. Angriffe sind Fertigkeitsproben; eine Parade pro Runde ist möglich. Unter 10 LP wird eine Figur bewusstlos, bei 0 LP ist sie tot. Der Knochenhirsch flieht, sobald die Bindung bricht.", actionLabel: "Kampfmodus verstanden"),
        GuideStep(id: "S07_NEXT", sceneID: "S07", kind: .next, title: "Nachhall", body: "Spiele SFX09 ausschließlich bei E03. Markiere das gewählte Ende und öffne den Epilog.", actionLabel: "Zum Epilog", audioCueID: "SFX09", options: [GuideOption(id: "epilogue", title: "Tauwetter", detail: "Die Folgen werden sichtbar.", destinationSceneID: "S08")])
    ]

    private static let epilogueSteps: [GuideStep] = [
        GuideStep(id: "S08_READ", sceneID: "S08", kind: .readAloud, title: "Tauwetter", body: "Am Morgen taut der Schnee in dünnen Rinnsalen. Krähenfels hat wieder Geräusche. Nur die Frage, wer hier künftig Gäste schützt, bleibt unbeantwortet.", actionLabel: "Vorgelesen", audioCueID: "A03"),
        GuideStep(id: "S08_GM", sceneID: "S08", kind: .gmInfo, title: "Persönlicher Nachhall", body: "Gib jeder Figur einen kurzen Satz: Was nimmt sie aus dem Dorf mit? Lass danach drei Atemzüge Stille und beende mit dem Krähenfels-Motiv.", actionLabel: "Nachhall gespielt", audioCueID: "M01"),
        GuideStep(id: "S08_NEXT", sceneID: "S08", kind: .next, title: "Abenteuer abgeschlossen", body: "Frage die Gruppe, welcher Hinweis im Rückblick zuerst Bedeutung bekam. Die Sitzung ist abgeschlossen.", actionLabel: "Sitzung beenden")
    ]
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
        let criticalSuccess = !begabung && safeRoll <= max(1, safeTarget / 10)
        let criticalFailure = safeRoll >= min(100, 90 + safeTarget / 10)
        return Result(roll: safeRoll, target: safeTarget, isSuccess: safeRoll <= safeTarget, isCriticalSuccess: criticalSuccess, isCriticalFailure: criticalFailure)
    }
}
