import XCTest
@testable import Kraehenfels

final class ContentStoreTests: XCTestCase {
    func testEmptyManifestIsSafeFallback() {
        XCTAssertEqual(ContentManifest.empty.meta.minimumIOS, "17.0")
        XCTAssertTrue(ContentManifest.empty.scenes.isEmpty)
        XCTAssertTrue(ContentManifest.empty.guide.steps.isEmpty)
    }

    func testV6AudioPlanDecodesWithLayerInstructions() throws {
        let payload = #"""
        {
          "meta": {"title":"Test","appTitle":"Test","subtitle":"SL","system":"HTBAH","setting":"1890","language":"de","version":"3.3.0","minimumIOS":"17.0"},
          "scenes": [{"id":"S03","title":"Kirche","shortTitle":"Kirche","duration":"30 Minuten","goal":"Eid finden","audioCueIds":["SFX10"],"audioPlan":[{"cueId":"SFX10","playWhen":"Nach Gastrecht","stopWhen":"Endet selbst","gmInstruction":"Einmal spielen","optional":false}],"nextSceneIds":[]}],
          "handouts": [],
          "audioCues": [{"id":"SFX10","title":"Falscher Glockenschlag","scene":"S03","category":"sfx","scope":"native","layer":"sfx","file":"V6_SFX10_Falscher_Glockenschlag.wav","mode":"oneShot","gain":-0.17,"fadeMs":0,"isClue":true,"printFallbackId":"H04","description":"Eine falsche Glocke.","playWhen":"Nach Gastrecht","stopWhen":"Endet selbst","gmInstruction":"Einmal spielen"}]
        }
        """#.data(using: .utf8)!

        let manifest = try JSONDecoder().decode(ContentManifest.self, from: payload)
        XCTAssertEqual(manifest.meta.version, "3.3.0")
        XCTAssertEqual(manifest.scenes.first?.audioPlan.first?.cueId, "SFX10")
        XCTAssertEqual(manifest.audioCues.first?.layer, "sfx")
        XCTAssertEqual(manifest.audioCues.first?.printFallbackId, "H04")
    }

    func testLegacyCueStillDecodes() throws {
        let payload = #"""
        {"id":"A01","title":"Alt","scene":"S01","category":"ambient","file":"old.m4a","mode":"loop","gain":0,"fadeMs":0,"isClue":false,"printFallbackId":null}
        """#.data(using: .utf8)!
        let cue = try JSONDecoder().decode(AudioCue.self, from: payload)
        XCTAssertEqual(cue.layer, "ambient")
        XCTAssertEqual(cue.scope, "native")
        XCTAssertTrue(cue.gmInstruction.isEmpty)
    }

    func testMaterialMetadataDecodesForHandoutsItemsAndGuideSteps() throws {
        let handout = try JSONDecoder().decode(HandoutEntry.self, from: #"""
        {"id":"H01","title":"Auftrag","format":"PNG","spoiler":false,"fallback":"Vorlesen","asset":"h01.pdf","previewAsset":"handout-h01.png","linkedClueIds":[]}
        """#.data(using: .utf8)!)
        XCTAssertEqual(handout.previewAsset, "handout-h01.png")

        let item = try JSONDecoder().decode(AdventureItem.self, from: #"""
        {"id":"blanket","title":"Wolldecke","locationID":"seat","detail":"SL-Text","playerCardDetail":"Spielertext","playerCardUses":["Einmal verwenden"],"playerCardAsset":"item-wool-blanket.png"}
        """#.data(using: .utf8)!)
        XCTAssertEqual(item.playerCardAsset, "item-wool-blanket.png")
        XCTAssertEqual(item.playerCardUses, ["Einmal verwenden"])

        let step = try JSONDecoder().decode(GuideStep.self, from: #"""
        {"id":"S01_CLUE","sceneID":"S01","kind":"clue","title":"Auftrag","body":"Text","materialInstruction":"Jetzt H01 zeigen."}
        """#.data(using: .utf8)!)
        XCTAssertEqual(step.materialInstruction, "Jetzt H01 zeigen.")
    }

    func testRollEvaluatorMatchesHowToBeAHeroThresholds() {
        let critical = RollEvaluator.evaluate(roll: 4, target: 60)
        XCTAssertTrue(critical.isCriticalSuccess)
        XCTAssertTrue(critical.isSuccess)

        let success = RollEvaluator.evaluate(roll: 60, target: 60)
        XCTAssertTrue(success.isSuccess)
        XCTAssertFalse(success.isCriticalSuccess)

        let failure = RollEvaluator.evaluate(roll: 70, target: 60)
        XCTAssertFalse(failure.isSuccess)
        XCTAssertFalse(failure.isCriticalFailure)

        let fumble = RollEvaluator.evaluate(roll: 97, target: 60)
        XCTAssertTrue(fumble.isCriticalFailure)

        let exactLowerEdge = RollEvaluator.evaluate(roll: 1, target: 5)
        XCTAssertFalse(exactLowerEdge.isCriticalSuccess)

        let exactUpperEdge = RollEvaluator.evaluate(roll: 97, target: 65)
        XCTAssertTrue(exactUpperEdge.isCriticalFailure)

        let begabung = RollEvaluator.evaluate(roll: 1, target: 100, begabung: true)
        XCTAssertTrue(begabung.isSuccess)
        XCTAssertTrue(begabung.isCriticalSuccess)

        let targetHundredFumble = RollEvaluator.evaluate(roll: 100, target: 100)
        XCTAssertTrue(targetHundredFumble.isCriticalFailure)
        XCTAssertFalse(targetHundredFumble.isSuccess)
    }

    func testEveryStoryRollSupportsSuccessFailureAndCriticalFailure() {
        let storyRolls = [
            "S01_ACT", "S02_ROLL", "S03_ROLL", "S04_ROLL", "S05_ROLL", "S06_ROLL", "S07_DANGER"
        ]

        for stepID in storyRolls {
            let success = RollEvaluator.evaluate(roll: 60, target: 60)
            let failure = RollEvaluator.evaluate(roll: 61, target: 60)
            let criticalFailure = RollEvaluator.evaluate(roll: 100, target: 60)

            XCTAssertTrue(success.isSuccess, stepID)
            XCTAssertFalse(success.isCriticalFailure, stepID)
            XCTAssertFalse(failure.isSuccess, stepID)
            XCTAssertFalse(failure.isCriticalFailure, stepID)
            XCTAssertFalse(criticalFailure.isSuccess, stepID)
            XCTAssertTrue(criticalFailure.isCriticalFailure, stepID)
        }
    }

    func testSharedGuideDecodesConditionalAndMandatorySteps() throws {
        let payload = #"""
        {
          "characters": [],
          "setupItems": [],
          "playerBriefing": "Briefing",
          "hiddenFromPlayers": "Spoiler",
          "steps": {
            "S01": [
              {"id":"S01_ACT","sceneID":"S01","kind":"playerAction","title":"Handlung","body":"Text","roll":{"actor":"Figur","ability":"Handeln","target":"65","success":"Erfolg","failure":"Misserfolg"}},
              {"id":"S01_DANGER","sceneID":"S01","kind":"roll","title":"Pflicht","body":"Text","actionLabel":"Prüfen","roll":{"actor":"Figur","ability":"Wissen","target":"60","success":"Erfolg","failure":"Misserfolg","required":true}}
            ]
          }
        }
        """#.data(using: .utf8)!
        let guide = try JSONDecoder().decode(GuideContent.self, from: payload)
        let conditional = guide.steps(for: "S01").first(where: { $0.id == "S01_ACT" })?.roll
        let finale = guide.steps(for: "S01").first(where: { $0.id == "S01_DANGER" })?.roll
        XCTAssertFalse(conditional?.required ?? true)
        XCTAssertTrue(finale?.required ?? false)
    }

    func testGuideContentDecodesCoachFindsAndOldGuidesDefaultSafely() throws {
        let payload = #"""
        {
          "setupItems": [],
          "playerBriefing": "Eigene Figuren",
          "hiddenFromPlayers": "Spoiler",
          "itemFindLocations": [{"id":"seat","title":"Sitzbank","detail":"Unter der Bank","itemIDs":["blanket"]}],
          "items": [{"id":"blanket","title":"Wolldecke","locationID":"seat","detail":"Warm","initialUses":1,"effects":[]}],
          "steps": {"S01":[{"id":"S01_ITEMS","sceneID":"S01","kind":"itemSearch","title":"Funde","body":"Text"}]}
        }
        """#.data(using: .utf8)!

        let guide = try JSONDecoder().decode(GuideContent.self, from: payload)
        XCTAssertTrue(guide.characters.isEmpty)
        XCTAssertEqual(guide.itemFindLocations.first?.itemIDs, ["blanket"])
        XCTAssertEqual(guide.item(for: "blanket")?.initialUses, 1)
        XCTAssertEqual(guide.steps(for: "S01").first?.kind, .itemSearch)

        let legacyPayload = #"{"setupItems":[],"playerBriefing":"Alt","hiddenFromPlayers":"Alt","steps":{}}"#.data(using: .utf8)!
        let legacyGuide = try JSONDecoder().decode(GuideContent.self, from: legacyPayload)
        XCTAssertTrue(legacyGuide.itemFindLocations.isEmpty)
        XCTAssertTrue(legacyGuide.items.isEmpty)
    }

    func testLegacyRollResolutionWithoutItemUseIDsRemainsReadable() throws {
        let id = UUID().uuidString
        let payload = #"""
        {
          "id":"PLACEHOLDER",
          "stepID":"S02_ROLL",
          "roll":70,
          "target":60,
          "label":"Misserfolg",
          "isSuccess":false,
          "isCriticalFailure":false,
          "consequenceID":"door-noise",
          "consequenceTitle":"Lärm"
        }
        """#.replacingOccurrences(of: "PLACEHOLDER", with: id).data(using: .utf8)!

        let record = try JSONDecoder().decode(RollResolutionRecord.self, from: payload)
        XCTAssertEqual(record.stepID, "S02_ROLL")
        XCTAssertTrue(record.itemUseIDs.isEmpty)
    }

    func testRollConsequenceDecodesEndingFilterAndEffects() throws {
        let payload = #"""
        {
          "id":"S02_ROLL",
          "sceneID":"S02",
          "kind":"roll",
          "title":"Tür",
          "body":"Text",
          "roll":{
            "actor":"Figur",
            "ability":"Handeln",
            "target":"60",
            "success":"Erfolg",
            "failure":"Misserfolg",
            "failureConsequences":[
              {"id":"noise","title":"Lärm","detail":"Die Tür bleibt nicht unbemerkt.","effect":{"threatDelta":1}},
              {"id":"time","title":"Zeit","detail":"Die Gruppe verliert Zeit.","endingIDs":["E01"]}
            ]
          }
        }
        """#.data(using: .utf8)!

        let step = try JSONDecoder().decode(GuideStep.self, from: payload)
        XCTAssertEqual(step.roll?.failureConsequences.count, 2)
        XCTAssertEqual(step.roll?.failureConsequences.first?.effect?.threatDelta, 1)
        XCTAssertTrue(step.roll?.failureConsequences[1].isAvailable(for: "E01") ?? false)
        XCTAssertFalse(step.roll?.failureConsequences[1].isAvailable(for: "E02") ?? true)
    }

    func testGuidedFlowKeepsAllInvestigationLocationsOpen() {
        let options = [
            GuideOption(id: "church", title: "Kirche", detail: "", destinationSceneID: "S03"),
            GuideOption(id: "smithy", title: "Schmiede", detail: "", destinationSceneID: "S04"),
            GuideOption(id: "woods", title: "Waldspur", detail: "", destinationSceneID: "S05")
        ].compactMap(\.destinationSceneID)
        XCTAssertEqual(Set(options), Set(["S03", "S04", "S05"]))
    }

    func testFactRoutesUseAlternativeEvidence() {
        let facts = ContentManifest.empty.facts
        XCTAssertTrue(facts.isEmpty)
        let fact = FactEntry(id: "F04", title: "", details: "", clueIds: ["C06", "C07", "C08"], fallback: "")
        XCTAssertEqual(fact.clueIds.count, 3)
    }

    @MainActor
    func testFinaleCountsTwoSuccessesBeforeAdvancing() {
        let defaults = UserDefaults(suiteName: "kraehenfels.tests.finale")!
        defaults.removePersistentDomain(forName: "kraehenfels.tests.finale")
        let session = SessionStore(defaults: defaults)
        let success = RollEvaluator.evaluate(roll: 50, target: 60)

        XCTAssertEqual(session.recordFinaleRoll(success), .ongoing(successes: 1, failures: 0))
        XCTAssertEqual(session.recordFinaleRoll(success), .resolved(success: true))
        XCTAssertEqual(session.finaleSuccesses, 2)
        XCTAssertEqual(session.finaleFailures, 0)
    }

    @MainActor
    func testFinaleCriticalFailureCountsAsTwoFailures() {
        let defaults = UserDefaults(suiteName: "kraehenfels.tests.finale-fumble")!
        defaults.removePersistentDomain(forName: "kraehenfels.tests.finale-fumble")
        let session = SessionStore(defaults: defaults)
        let fumble = RollEvaluator.evaluate(roll: 100, target: 60)

        XCTAssertEqual(session.recordFinaleRoll(fumble), .resolved(success: false))
        XCTAssertEqual(session.finaleFailures, 2)
    }

    @MainActor
    func testFinaleSupportsAllEndingsAndMultipleRolls() {
        let consequences = [
            RollConsequence(id: "time", title: "Zeit", detail: "", endingIDs: ["E01", "E03"]),
            RollConsequence(id: "warmth", title: "Wärme", detail: "", endingIDs: ["E02", "E03"]),
            RollConsequence(id: "trust", title: "Vertrauen", detail: "", endingIDs: ["E01", "E02"])
        ]
        for endingID in ["E01", "E02", "E03"] {
            XCTAssertEqual(consequences.filter { $0.isAvailable(for: endingID) }.count, 2)
        }

        let suiteName = "kraehenfels.tests.finale-multiple-rolls"
        let defaults = UserDefaults(suiteName: suiteName)!
        defaults.removePersistentDomain(forName: suiteName)
        let session = SessionStore(defaults: defaults)
        let failure = RollEvaluator.evaluate(roll: 70, target: 60)
        let success = RollEvaluator.evaluate(roll: 50, target: 60)

        XCTAssertEqual(session.recordFinaleRoll(failure, consequence: consequences[0]), .ongoing(successes: 0, failures: 1))
        XCTAssertEqual(session.recordFinaleRoll(success), .ongoing(successes: 1, failures: 1))
        XCTAssertEqual(session.recordFinaleRoll(success), .resolved(success: true))
        XCTAssertEqual(session.rollResolutions.filter { $0.stepID == "S07_DANGER" }.count, 3)
    }

    @MainActor
    func testV5SessionStartsFreshAndPersistsResumeState() {
        let suiteName = "kraehenfels.tests.v5-session"
        let defaults = UserDefaults(suiteName: suiteName)!
        defaults.removePersistentDomain(forName: suiteName)

        let session = SessionStore(defaults: defaults)
        XCTAssertFalse(session.hasStartedSession)
        XCTAssertEqual(session.currentSceneID, "S01")

        session.beginGuidedSession()
        XCTAssertTrue(session.hasStartedSession)

        let resumed = SessionStore(defaults: defaults)
        XCTAssertTrue(resumed.hasStartedSession)
        XCTAssertEqual(resumed.currentSceneID, "S01")
    }

    @MainActor
    func testFinishingGuidedSessionMarksEpilogueAndStopsResumeState() {
        let suiteName = "kraehenfels.tests.finish-session"
        let defaults = UserDefaults(suiteName: suiteName)!
        defaults.removePersistentDomain(forName: suiteName)

        let session = SessionStore(defaults: defaults)
        session.beginGuidedSession()
        session.currentSceneID = "S08"
        session.finishGuidedSession()

        XCTAssertFalse(session.hasStartedSession)
        XCTAssertTrue(session.completedSceneIDs.contains("S08"))

        let resumed = SessionStore(defaults: defaults)
        XCTAssertFalse(resumed.hasStartedSession)
        XCTAssertTrue(resumed.completedSceneIDs.contains("S08"))
    }

    @MainActor
    func testV5SnapshotWithoutRollResolutionsRemainsReadable() throws {
        let suiteName = "kraehenfels.tests.v5-legacy-snapshot"
        let defaults = UserDefaults(suiteName: suiteName)!
        defaults.removePersistentDomain(forName: suiteName)
        let payload: [String: Any] = [
            "playerNames": ["Clara", "", ""],
            "sessionNote": "Alte Notiz",
            "sceneNotes": ["S01": "Spur"],
            "currentSceneID": "S02",
            "completedSceneIDs": ["S01"],
            "checkedClueIDs": ["C01"],
            "completedChecklistIDs": [],
            "npcStates": [:],
            "threatLevel": 2,
            "selectedHooks": [:]
        ]
        defaults.set(try JSONSerialization.data(withJSONObject: payload), forKey: "kraehenfels.sessionJournal.v5")

        let session = SessionStore(defaults: defaults)

        XCTAssertEqual(session.currentSceneID, "S02")
        XCTAssertEqual(session.threatLevel, 2)
        XCTAssertTrue(session.rollResolutions.isEmpty)
    }

    @MainActor
    func testRollConsequenceIsAppliedAndPersistedAfterConfirmation() {
        let suiteName = "kraehenfels.tests.roll-consequence"
        let defaults = UserDefaults(suiteName: suiteName)!
        defaults.removePersistentDomain(forName: suiteName)
        let session = SessionStore(defaults: defaults)
        let failure = RollEvaluator.evaluate(roll: 70, target: 60)
        let consequence = RollConsequence(
            id: "noise",
            title: "Lärm",
            detail: "Die Tür bleibt nicht unbemerkt.",
            effect: RollConsequenceEffect(threatDelta: 1)
        )

        session.recordRoll(stepID: "S02_ROLL", result: failure, consequence: consequence)

        XCTAssertEqual(session.threatLevel, 1)
        XCTAssertEqual(session.latestRollResolution(for: "S02_ROLL")?.consequenceTitle, "Lärm")
        let resumed = SessionStore(defaults: defaults)
        XCTAssertEqual(resumed.latestRollResolution(for: "S02_ROLL")?.consequenceID, "noise")
    }

    @MainActor
    func testMinimumThreatConsequenceDoesNotLowerExistingThreat() {
        let suiteName = "kraehenfels.tests.roll-minimum-threat"
        let defaults = UserDefaults(suiteName: suiteName)!
        defaults.removePersistentDomain(forName: suiteName)
        let session = SessionStore(defaults: defaults)
        session.setThreatLevel(5)
        let failure = RollEvaluator.evaluate(roll: 70, target: 60)
        let consequence = RollConsequence(
            id: "procession-visible",
            title: "Prozession",
            detail: "Die Schritte sind vor dem Fenster.",
            effect: RollConsequenceEffect(minimumThreat: 4)
        )

        session.recordRoll(stepID: "S06_ROLL", result: failure, consequence: consequence)

        XCTAssertEqual(session.threatLevel, 5)
    }

    @MainActor
    func testChangingEndingRemovesDependentFinaleRolls() {
        let suiteName = "kraehenfels.tests.ending-change"
        let defaults = UserDefaults(suiteName: suiteName)!
        defaults.removePersistentDomain(forName: suiteName)
        let session = SessionStore(defaults: defaults)
        let failure = RollEvaluator.evaluate(roll: 70, target: 60)
        session.recordFinaleRoll(failure)

        XCTAssertNotNil(session.latestRollResolution(for: "S07_DANGER"))
        session.setSelectedEnding("E02")

        XCTAssertNil(session.latestRollResolution(for: "S07_DANGER"))
        XCTAssertEqual(session.finaleFailures, 0)
    }

    @MainActor
    func testStepBackRestoresPositionWithoutRemovingFoundClues() {
        let suiteName = "kraehenfels.tests.step-back"
        let defaults = UserDefaults(suiteName: suiteName)!
        defaults.removePersistentDomain(forName: suiteName)

        let session = SessionStore(defaults: defaults)
        session.beginGuidedSession()
        session.checkedClueIDs.insert("C01")
        session.advanceGuideStep(in: "S01", stepID: "S01_READ", stepCount: 5)

        XCTAssertEqual(session.guidedStepIndex, 1)
        XCTAssertTrue(session.stepBack())
        XCTAssertEqual(session.currentSceneID, "S01")
        XCTAssertEqual(session.guidedStepIndex, 0)
        XCTAssertTrue(session.checkedClueIDs.contains("C01"))
    }

    @MainActor
    func testBranchResetKeepsCluesAndRemovesDependentProgress() {
        let suiteName = "kraehenfels.tests.branch-reset"
        let defaults = UserDefaults(suiteName: suiteName)!
        defaults.removePersistentDomain(forName: suiteName)

        let session = SessionStore(defaults: defaults)
        session.beginGuidedSession()
        session.checkedClueIDs.insert("C01")
        session.currentSceneID = "S04"
        session.completedSceneIDs = ["S03", "S04"]
        session.completedGuideStepIDs = ["S04_CLUE"]
        session.rollHistory = ["S04_ROLL": "50 / 60 · Erfolg"]
        session.recordRoll(stepID: "S04_ROLL", result: RollEvaluator.evaluate(roll: 50, target: 60))

        session.advanceToScene("S03", from: "S04")
        session.resetDependentPath(from: "S03")

        XCTAssertEqual(session.currentSceneID, "S03")
        XCTAssertFalse(session.completedSceneIDs.contains("S04"))
        XCTAssertFalse(session.completedGuideStepIDs.contains("S04_CLUE"))
        XCTAssertTrue(session.rollHistory["S04_ROLL"] == nil)
        XCTAssertTrue(session.latestRollResolution(for: "S04_ROLL") == nil)
        XCTAssertTrue(session.checkedClueIDs.contains("C01"))
    }

    @MainActor
    func testCoachItemsRequireAllSixAssignmentsAndAllThreeFigures() {
        let suiteName = "kraehenfels.tests.coach-items"
        let defaults = UserDefaults(suiteName: suiteName)!
        defaults.removePersistentDomain(forName: suiteName)

        let session = SessionStore(defaults: defaults)
        session.beginGuidedSession()
        let itemIDs = ["blanket", "bandage", "rope", "lantern", "tools", "revolver"]
        session.discoverItems(itemIDs)
        itemIDs.dropLast().enumerated().forEach { index, itemID in
            session.assignItem(itemID, toPlayerAt: index % 2)
        }

        XCTAssertFalse(session.isItemDistributionComplete(for: itemIDs))
        session.assignItem(itemIDs.last!, toPlayerAt: 2)
        XCTAssertTrue(session.isItemDistributionComplete(for: itemIDs))

        let resumed = SessionStore(defaults: defaults)
        XCTAssertEqual(resumed.discoveredItemIDs, Set(itemIDs))
        XCTAssertEqual(resumed.itemOwners[itemIDs.last!], 2)
    }

    @MainActor
    func testItemUseCanBeRolledBackBeforeConfirmedRecord() {
        let suiteName = "kraehenfels.tests.coach-item-rollback"
        let defaults = UserDefaults(suiteName: suiteName)!
        defaults.removePersistentDomain(forName: suiteName)

        let session = SessionStore(defaults: defaults)
        session.beginGuidedSession()
        session.discoverItems(["bandage"])
        session.assignItem("bandage", toPlayerAt: 0)

        let draft = session.useItem(itemID: "bandage", effectID: "bandage-first-aid", sceneID: "S01", stepID: "S01_ACT", maximumUses: 2)
        XCTAssertNotNil(draft)
        session.undoItemUse(draft!.id)
        XCTAssertTrue(session.itemUseRecords.isEmpty)
        XCTAssertEqual(session.remainingUses(for: AdventureItem(id: "bandage", title: "Verband", locationID: "seat", detail: "", initialUses: 2)), 2)
    }

    @MainActor
    func testDependentPathResetRemovesOnlyLaterItemUses() {
        let suiteName = "kraehenfels.tests.coach-item-path-reset"
        let defaults = UserDefaults(suiteName: suiteName)!
        defaults.removePersistentDomain(forName: suiteName)

        let session = SessionStore(defaults: defaults)
        session.beginGuidedSession()
        session.discoverItems(["rope", "tools"])
        session.assignItem("rope", toPlayerAt: 0)
        session.assignItem("tools", toPlayerAt: 1)
        _ = session.useItem(itemID: "rope", effectID: "rope-rescue", sceneID: "S02", stepID: "S02_ROLL", maximumUses: 1)
        _ = session.useItem(itemID: "tools", effectID: "tools-door", sceneID: "S04", stepID: "S04_ROLL", maximumUses: 1)

        session.resetDependentPath(from: "S03")

        XCTAssertEqual(session.itemUseRecords.map(\.sceneID), ["S02"])
    }
}
