import AVFoundation
import Combine
import Foundation

@MainActor
final class AudioEngine: NSObject, ObservableObject, AVAudioPlayerDelegate {
    @Published var masterVolume: Double = 0.48 { didSet { updateVolumes() } }
    @Published var ambientVolume: Double = 0.68 { didSet { updateVolumes() } }
    @Published var musicVolume: Double = 0.54 { didSet { updateVolumes() } }
    @Published var effectsVolume: Double = 0.84 { didSet { updateVolumes() } }
    @Published var safetyMode = false { didSet { updateVolumes() } }
    @Published var readAloudDuck = false { didSet { updateVolumes() } }

    @Published private(set) var activeCueIDs: Set<String> = []
    @Published private(set) var lastError: String?
    @Published private(set) var lastEvent: String?
    @Published private(set) var lastLoadedResource: String?
    @Published private(set) var sessionStatus = "Audio wird vorbereitet …"

    private var players: [String: AVAudioPlayer] = [:]
    private var cueByPlayerKey: [String: AudioCue] = [:]
    private var observers: [NSObjectProtocol] = []

    override init() {
        super.init()
        observeAudioSession()
        _ = configureSession()
    }

    deinit {
        observers.forEach { NotificationCenter.default.removeObserver($0) }
    }

    var activeLayerSummary: String {
        let active = cueByPlayerKey.values.filter { activeCueIDs.contains($0.id) }
        let layers = Set(active.map(\.layer))
        if layers.isEmpty { return "Keine Layer aktiv" }
        let ordered = ["musicBed", "musicLayer", "ambient", "sfx"]
        return ordered.filter(layers.contains).compactMap(layerLabel).joined(separator: " · ")
    }

    func play(_ cue: AudioCue) {
        switch cue.layer {
        case "ambient": playLoop(cue, replacingLayer: true)
        case "musicBed", "musicLayer": playLoop(cue, replacingLayer: false)
        default: playOneShot(cue)
        }
    }

    func playPreset(_ cues: [AudioCue]) {
        guard let ambient = cues.first(where: { $0.layer == "ambient" }) else {
            lastEvent = "Diese Szene hat keine eigene Atmosphäre."
            return
        }
        playLoop(ambient, replacingLayer: true)
        lastEvent = "Atmosphäre gestartet: \(ambient.title)"
    }

    func runSelfTest() {
        let testCue = AudioCue(
            id: "__selftest",
            title: "Audio-Selbsttest",
            scene: "",
            category: "sfx",
            layer: "sfx",
            file: "V5_TEST_Audio.wav",
            mode: "oneShot",
            gain: 0,
            fadeMs: 0,
            isClue: false,
            printFallbackId: nil,
            description: "Ein klarer kurzer Testton."
        )
        playOneShot(testCue)
    }

    func clearDiagnostics() {
        lastError = nil
        lastEvent = nil
    }

    func stop(_ cue: AudioCue, fade: Bool = true) {
        let keys = cueByPlayerKey.compactMap { key, value in value.id == cue.id ? key : nil }
        keys.forEach { stopPlayer(key: $0, fadeMilliseconds: fade ? cue.fadeMs : 0) }
    }

    func toggle(_ cue: AudioCue) {
        if cue.mode == "oneShot" {
            playOneShot(cue)
        } else if isPlaying(cue) {
            stop(cue)
        } else {
            play(cue)
        }
    }

    func stopLayer(_ layer: String, fadeMilliseconds: Int = 500) {
        let keys = cueByPlayerKey.compactMap { key, cue in cue.layer == layer ? key : nil }
        keys.forEach { stopPlayer(key: $0, fadeMilliseconds: fadeMilliseconds) }
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

    func toggleReadAloudDuck() {
        readAloudDuck.toggle()
        lastEvent = readAloudDuck ? "Musik zum Vorlesen abgesenkt." : "Normale Mischung wiederhergestellt."
    }

    func startReadAloud(cue: AudioCue?) {
        readAloudDuck = true
        if let cue {
            play(cue)
            lastEvent = "Vorlese-Cue bereit: \(cue.title)"
        } else {
            lastEvent = "Vorlesen bereit; kein eigener Cue für diesen Schritt."
        }
    }

    func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        guard let key = players.first(where: { $0.value === player })?.key else { return }
        let cueID = cueByPlayerKey[key]?.id
        players[key] = nil
        cueByPlayerKey[key] = nil
        refreshActiveCueIDs()
        if !flag, let cueID {
            lastError = "Der Cue wurde unterbrochen: \(cueID)."
        }
    }

    private func playLoop(_ cue: AudioCue, replacingLayer: Bool) {
        guard configureSession() else { return }
        if isPlaying(cue) {
            lastEvent = "Läuft bereits: \(cue.title)"
            return
        }
        if replacingLayer {
            stopLayer(cue.layer, fadeMilliseconds: cue.fadeMs)
        }
        guard let player = makePlayer(for: cue) else { return }
        player.numberOfLoops = -1
        player.volume = 0
        players[cue.id] = player
        cueByPlayerKey[cue.id] = cue
        refreshActiveCueIDs()
        guard player.play() else {
            lastError = "Der Cue konnte nicht gestartet werden: \(cue.file)"
            removePlayer(key: cue.id)
            return
        }
        player.setVolume(volume(for: cue), fadeDuration: Double(cue.fadeMs) / 1000)
        lastEvent = "Gestartet: \(cue.title)"
    }

    private func playOneShot(_ cue: AudioCue) {
        guard configureSession(), let player = makePlayer(for: cue) else { return }
        let key = "\(cue.id)#\(UUID().uuidString)"
        player.numberOfLoops = 0
        player.volume = volume(for: cue)
        players[key] = player
        cueByPlayerKey[key] = cue
        refreshActiveCueIDs()
        guard player.play() else {
            lastError = "Der Cue konnte nicht gestartet werden: \(cue.file)"
            removePlayer(key: key)
            return
        }
        lastEvent = "Ausgelöst: \(cue.title)"
    }

    private func makePlayer(for cue: AudioCue) -> AVAudioPlayer? {
        lastError = nil
        let resource = cue.file as NSString
        guard let url = Bundle.main.url(
            forResource: resource.deletingPathExtension,
            withExtension: resource.pathExtension,
            subdirectory: "Audio"
        ) else {
            lastError = "Audio-Datei fehlt im App-Bundle: \(cue.file)"
            lastEvent = "Nicht geladen: \(cue.file)"
            return nil
        }
        do {
            let player = try AVAudioPlayer(contentsOf: url)
            player.delegate = self
            player.prepareToPlay()
            lastLoadedResource = cue.file
            return player
        } catch {
            lastError = "Audio-Datei konnte nicht geöffnet werden (\(cue.file)): \(error.localizedDescription)"
            lastEvent = "Nicht geöffnet: \(cue.file)"
            return nil
        }
    }

    private func stopPlayer(key: String, fadeMilliseconds: Int) {
        guard let player = players[key] else { return }
        let delay = Double(max(0, fadeMilliseconds)) / 1000
        if delay > 0, player.isPlaying {
            player.setVolume(0, fadeDuration: delay)
            DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self, weak player] in
                guard let self, let player, self.players[key] === player else { return }
                player.stop()
                self.removePlayer(key: key)
            }
        } else {
            player.stop()
            removePlayer(key: key)
        }
    }

    private func removePlayer(key: String) {
        players[key] = nil
        cueByPlayerKey[key] = nil
        refreshActiveCueIDs()
    }

    private func refreshActiveCueIDs() {
        activeCueIDs = Set(cueByPlayerKey.values.map(\.id))
    }

    @discardableResult
    private func configureSession() -> Bool {
        let session = AVAudioSession.sharedInstance()
        do {
            try session.setCategory(.playback, mode: .default, options: [.mixWithOthers])
            try session.setActive(true)
            updateSessionStatus()
            return true
        } catch {
            sessionStatus = "Audio-Ausgabe konnte nicht aktiviert werden."
            lastError = "AVAudioSession: \(error.localizedDescription)"
            return false
        }
    }

    private func observeAudioSession() {
        let center = NotificationCenter.default
        observers.append(center.addObserver(forName: AVAudioSession.routeChangeNotification, object: nil, queue: .main) { [weak self] _ in
            Task { @MainActor in self?.updateSessionStatus() }
        })
        observers.append(center.addObserver(forName: AVAudioSession.interruptionNotification, object: nil, queue: .main) { [weak self] notification in
            Task { @MainActor in self?.handleInterruption(notification) }
        })
    }

    private func handleInterruption(_ notification: Notification) {
        guard let raw = notification.userInfo?[AVAudioSessionInterruptionTypeKey] as? UInt,
              let type = AVAudioSession.InterruptionType(rawValue: raw) else { return }
        if type == .began {
            lastEvent = "Audio durch einen Anruf oder eine andere App unterbrochen."
        } else {
            _ = configureSession()
            lastEvent = "Audio-Ausgabe ist wieder bereit. Laufende Layer bei Bedarf neu starten."
        }
    }

    private func updateSessionStatus() {
        let session = AVAudioSession.sharedInstance()
        let outputs = session.currentRoute.outputs.map { output in
            switch output.portType {
            case .bluetoothA2DP, .bluetoothLE, .bluetoothHFP: return "Bluetooth: \(output.portName)"
            case .headphones: return "Kopfhörer: \(output.portName)"
            default: return output.portName
            }
        }
        let route = outputs.isEmpty ? "kein Ausgabegerät" : outputs.joined(separator: ", ")
        let muted = session.outputVolume <= 0.001 ? " · iPhone-Lautstärke ist stumm" : ""
        sessionStatus = "Ausgabe: \(route)\(muted)"
    }

    private func updateVolumes() {
        for (key, player) in players {
            guard let cue = cueByPlayerKey[key] else { continue }
            player.setVolume(volume(for: cue), fadeDuration: 0.18)
        }
    }

    private func volume(for cue: AudioCue) -> Float {
        let linearGain = pow(10.0, cue.gain / 20.0)
        let safetyFactor = safetyMode ? 0.58 : 1.0
        let duckFactor = readAloudDuck && cue.layer.hasPrefix("music") ? 0.30 : 1.0
        let layerVolume: Double
        switch cue.layer {
        case "ambient": layerVolume = ambientVolume
        case "musicBed", "musicLayer": layerVolume = musicVolume
        default: layerVolume = effectsVolume
        }
        return Float(min(1, max(0, masterVolume * layerVolume * safetyFactor * duckFactor * linearGain)))
    }

    private func layerLabel(_ layer: String) -> String? {
        switch layer {
        case "musicBed": return "Grundmusik"
        case "musicLayer": return "Prozession"
        case "ambient": return "Atmosphäre"
        case "sfx": return "Effekt"
        default: return nil
        }
    }
}
