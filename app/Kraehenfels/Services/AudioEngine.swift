import AVFoundation
import Combine
import Foundation

@MainActor
final class AudioEngine: NSObject, ObservableObject, AVAudioPlayerDelegate {
    @Published var masterVolume: Double = 0.45 {
        didSet { updateVolumes() }
    }
    @Published var ambientVolume: Double = 0.72 {
        didSet { updateVolumes() }
    }
    @Published var musicVolume: Double = 0.62 {
        didSet { updateVolumes() }
    }
    @Published var effectsVolume: Double = 0.82 {
        didSet { updateVolumes() }
    }
    @Published var safetyMode = false {
        didSet { updateVolumes() }
    }
    @Published private(set) var activeCueIDs: Set<String> = []
    @Published private(set) var lastError: String?
    @Published private(set) var lastEvent: String?
    @Published private(set) var lastLoadedResource: String?
    @Published private(set) var sessionStatus = "Audio wird vorbereitet …"

    private var players: [String: AVAudioPlayer] = [:]
    private var cueByPlayerKey: [String: AudioCue] = [:]

    override init() {
        super.init()
        _ = configureSession()
    }

    func play(_ cue: AudioCue) {
        play(cue, replacingCategory: true)
    }

    func playPreset(_ cues: [AudioCue]) {
        guard configureSession() else { return }
        stopCategory("ambient")
        stopCategory("music")
        let layers = cues.filter { $0.category == "ambient" || $0.category == "music" }
        if layers.isEmpty {
            lastEvent = "Für dieses Preset gibt es keine Atmosphäre oder Musik."
            return
        }
        for cue in layers {
            play(cue, replacingCategory: false)
        }
        lastEvent = "Preset gestartet: \(layers.map(\.title).joined(separator: " + "))"
    }

    func runSelfTest() {
        let testCue = AudioCue(
            id: "__selftest",
            title: "Audio-Selbsttest",
            scene: "",
            category: "sfx",
            file: "V3_SFX05_Schmiedeschlag.wav",
            mode: "oneShot",
            gain: -0.05,
            fadeMs: 0,
            isClue: false,
            printFallbackId: nil
        )
        play(testCue)
    }

    func clearDiagnostics() {
        lastError = nil
        lastEvent = nil
    }

    func stop(_ cue: AudioCue) {
        players[cue.id]?.stop()
        players[cue.id] = nil
        cueByPlayerKey[cue.id] = nil
        activeCueIDs.remove(cue.id)
    }

    func toggle(_ cue: AudioCue) {
        if activeCueIDs.contains(cue.id) { stop(cue) } else { play(cue) }
    }

    func stopCategory(_ category: String) {
        let ids = cueByPlayerKey.compactMap { key, cue in cue.category == category ? key : nil }
        ids.forEach { id in
            players[id]?.stop()
            players[id] = nil
            cueByPlayerKey[id] = nil
            activeCueIDs.remove(id)
        }
    }

    func stopAll() {
        players.values.forEach { $0.stop() }
        players.removeAll()
        cueByPlayerKey.removeAll()
        activeCueIDs.removeAll()
        lastEvent = "Alle Sounds gestoppt."
    }

    func isPlaying(_ cue: AudioCue) -> Bool {
        activeCueIDs.contains(cue.id)
    }

    func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        guard let key = players.first(where: { $0.value === player })?.key else { return }
        players[key] = nil
        cueByPlayerKey[key] = nil
        activeCueIDs.remove(key)
        if !flag {
            lastError = "Der Cue wurde unterbrochen: \(key)."
        }
    }

    @discardableResult
    private func configureSession() -> Bool {
        let session = AVAudioSession.sharedInstance()
        do {
            try session.setCategory(.playback, mode: .default, options: [.mixWithOthers, .duckOthers])
            try session.setActive(true)
            let route = session.currentRoute.outputs.map(\.portName).joined(separator: ", ")
            let routeText = route.isEmpty ? "kein Ausgabegerät" : route
            let volumeText = session.outputVolume <= 0.001 ? " · iPhone-Lautstärke ist stumm" : ""
            sessionStatus = "Ausgabe: \(routeText)\(volumeText)"
            return true
        } catch {
            sessionStatus = "Audio-Ausgabe konnte nicht aktiviert werden."
            lastError = "AVAudioSession: \(error.localizedDescription)"
            return false
        }
    }

    private func play(_ cue: AudioCue, replacingCategory: Bool) {
        lastError = nil
        guard configureSession() else { return }
        let resource = cue.file as NSString
        guard let url = Bundle.main.url(forResource: resource.deletingPathExtension, withExtension: resource.pathExtension, subdirectory: "Audio") else {
            lastError = "Audio-Datei fehlt im App-Bundle: \(cue.file)"
            lastEvent = "Nicht geladen: \(cue.file)"
            return
        }
        if replacingCategory && (cue.category == "ambient" || cue.category == "music") {
            stopCategory(cue.category)
        }
        if let old = players[cue.id] {
            old.stop()
            players[cue.id] = nil
        }
        do {
            let player = try AVAudioPlayer(contentsOf: url)
            player.delegate = self
            player.numberOfLoops = cue.mode == "loop" ? -1 : 0
            player.volume = volume(for: cue)
            player.prepareToPlay()
            players[cue.id] = player
            cueByPlayerKey[cue.id] = cue
            activeCueIDs.insert(cue.id)
            guard player.play() else {
                lastError = "Der Cue konnte nicht gestartet werden: \(cue.file)"
                stop(cue)
                return
            }
            lastLoadedResource = cue.file
            lastEvent = "Geladen: \(cue.title)"
        } catch {
            lastError = "Audio-Datei konnte nicht geöffnet werden (\(cue.file)): \(error.localizedDescription)"
            lastEvent = "Nicht geöffnet: \(cue.file)"
        }
    }

    private func volume(for cue: AudioCue) -> Float {
        let linearGain = pow(10.0, cue.gain / 20.0)
        let safetyFactor = safetyMode ? 0.58 : 1.0
        let categoryVolume: Double
        switch cue.category {
        case "ambient": categoryVolume = ambientVolume
        case "music": categoryVolume = musicVolume
        default: categoryVolume = effectsVolume
        }
        return Float(max(0.0, min(1.0, masterVolume * categoryVolume * linearGain * safetyFactor)))
    }

    private func updateVolumes() {
        for (id, player) in players {
            guard let cue = cueByPlayerKey[id] else { continue }
            player.volume = volume(for: cue)
        }
    }
}
