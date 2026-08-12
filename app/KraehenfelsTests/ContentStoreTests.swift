import XCTest
@testable import Kraehenfels

final class ContentStoreTests: XCTestCase {
    func testEmptyManifestIsSafeFallback() {
        XCTAssertEqual(ContentManifest.empty.meta.minimumIOS, "17.0")
        XCTAssertTrue(ContentManifest.empty.scenes.isEmpty)
    }

    func testV5AudioPlanDecodesWithLayerInstructions() throws {
        let payload = #"""
        {
          "meta": {"title":"Test","appTitle":"Test","subtitle":"SL","system":"HTBAH","setting":"1890","language":"de","version":"3.2.0-rc1","minimumIOS":"17.0"},
          "scenes": [{"id":"S03","title":"Kirche","shortTitle":"Kirche","duration":"30 Minuten","goal":"Eid finden","audioCueIds":["SFX10"],"audioPlan":[{"cueId":"SFX10","playWhen":"Nach Gastrecht","stopWhen":"Endet selbst","gmInstruction":"Einmal spielen","optional":false}],"nextSceneIds":[]}],
          "handouts": [],
          "audioCues": [{"id":"SFX10","title":"Falscher Glockenschlag","scene":"S03","category":"sfx","scope":"native","layer":"sfx","file":"V5_SFX10_Falscher_Glockenschlag.wav","mode":"oneShot","gain":-0.17,"fadeMs":0,"isClue":true,"printFallbackId":"H04","description":"Eine falsche Glocke.","playWhen":"Nach Gastrecht","stopWhen":"Endet selbst","gmInstruction":"Einmal spielen"}]
        }
        """#.data(using: .utf8)!

        let manifest = try JSONDecoder().decode(ContentManifest.self, from: payload)
        XCTAssertEqual(manifest.meta.version, "3.2.0-rc1")
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
}
