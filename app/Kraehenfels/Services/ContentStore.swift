import Foundation
import Combine

@MainActor
final class ContentStore: ObservableObject {
    @Published private(set) var manifest: ContentManifest

    init() {
        manifest = .empty
        load()
    }

    func load() {
        guard let url = Bundle.main.url(forResource: "manifest", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let decoded = try? JSONDecoder().decode(ContentManifest.self, from: data) else { return }
        manifest = decoded
    }

    func scene(for id: String) -> SceneEntry? {
        manifest.scenes.first(where: { $0.id == id })
    }

    func handout(for id: String) -> HandoutEntry? {
        manifest.handouts.first(where: { $0.id == id })
    }

    func cues(for scene: SceneEntry) -> [AudioCue] {
        scene.audioCueIds.compactMap { id in manifest.audioCues.first(where: { $0.id == id }) }
    }
}
