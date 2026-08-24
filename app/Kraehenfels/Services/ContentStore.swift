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

    func phase(at index: Int) -> PhaseEntry? {
        guard manifest.phases.indices.contains(index) else { return nil }
        return manifest.phases[index]
    }

    func handout(for id: String) -> HandoutEntry? {
        manifest.handouts.first(where: { $0.id == id })
    }

    func cues(for scene: SceneEntry) -> [AudioCue] {
        scene.audioCueIds.compactMap { id in manifest.audioCues.first(where: { $0.id == id }) }
    }

    func cue(for id: String) -> AudioCue? {
        manifest.audioCues.first(where: { $0.id == id })
    }

    func plannedCues(for scene: SceneEntry) -> [(AudioPlanEntry, AudioCue)] {
        scene.audioPlan.compactMap { plan in
            guard let cue = cue(for: plan.cueId) else { return nil }
            return (plan, cue)
        }
    }

    func steps(for sceneID: String) -> [GuideStep] {
        manifest.guide.steps(for: sceneID)
    }

    var guideCharacters: [QuickCharacter] {
        manifest.guide.characters
    }

    var setupItems: [SetupItem] {
        manifest.guide.setupItems
    }

    func maps(for scene: SceneEntry) -> [MapEntry] {
        let mapIDs = Set(scene.locationIds.compactMap { locationID in
            manifest.locations.first(where: { $0.id == locationID })?.mapId
        })
        return manifest.maps.filter { mapIDs.contains($0.id) }
    }

    func factIsComplete(_ fact: FactEntry, with clues: Set<String>) -> Bool {
        let found = fact.clueIds.filter { clues.contains($0) }.count
        switch fact.id {
        case "F01", "F02", "F03", "F05":
            return found >= 1
        case "F04":
            return found >= 2
        default:
            return !fact.clueIds.isEmpty && fact.clueIds.allSatisfy(clues.contains)
        }
    }

    func completedFacts(for clues: Set<String>) -> [FactEntry] {
        manifest.facts.filter { factIsComplete($0, with: clues) }
    }

    var musicBed: AudioCue? {
        manifest.audioCues.first(where: { $0.layer == "musicBed" })
    }
}
