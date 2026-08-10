import XCTest
@testable import Kraehenfels

final class ContentStoreTests: XCTestCase {
    func testEmptyManifestIsSafeFallback() {
        XCTAssertEqual(ContentManifest.empty.meta.minimumIOS, "17.0")
        XCTAssertTrue(ContentManifest.empty.scenes.isEmpty)
    }
}
