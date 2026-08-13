import XCTest
@testable import Kraehenfels

final class ContentStoreTests: XCTestCase {
    func testEmptyManifestIsSafeFallback() {
        XCTAssertEqual(ContentManifest.empty.meta.minimumIOS, "17.0")
        XCTAssertTrue(ContentManifest.empty.scenes.isEmpty)
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

        let begabung = RollEvaluator.evaluate(roll: 1, target: 100, begabung: true)
        XCTAssertTrue(begabung.isSuccess)
        XCTAssertFalse(begabung.isCriticalSuccess)
    }

    func testGuidedRollsMarkConditionalAndMandatorySteps() {
        let conditional = GuidedFlowCatalog.steps(for: "S01").first(where: { $0.id == "S01_ACT" })?.roll
        let finale = GuidedFlowCatalog.steps(for: "S07").first(where: { $0.id == "S07_DANGER" })?.roll
        XCTAssertFalse(conditional?.required ?? true)
        XCTAssertTrue(finale?.required ?? false)
    }

    func testGuidedFlowKeepsAllInvestigationLocationsOpen() {
        let options = GuidedFlowCatalog.steps(for: "S02").last?.options.compactMap(\.destinationSceneID)
        XCTAssertEqual(Set(options ?? []), Set(["S03", "S04", "S05"]))
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
}
