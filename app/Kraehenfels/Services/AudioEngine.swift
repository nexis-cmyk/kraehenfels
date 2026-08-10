import AVFoundation
import Combine
import Foundation

@MainActor
final class AudioEngine: NSObject, ObservableObject, AVAudioPlayerDelegate {
    @Published var masterVolume: Double = 0.45 {
        didSet { updateVolumes() }
    }
    @Published var safetyMode = false {
        didSet { updateVolumes() }
    }
    @Published private(set) var activeCueIDs: Set<String> = []

    private var players: [String: AVAudioPlayer] = [:]
    private var cueByPlayerKey: [String: AudioCue] = [:]

    override init() {
        super.init()
        configureSession()
    }

    func play(_ cue: AudioCue) {
        let resource = cue.file as NSString
        guard let url = Bundle.main.url(forResource: resource.deletingPathExtension, withExtension: resource.pathExtension, subdirectory: "Audio") else { return }
        if cue.category == "ambient" || cue.category == "music" {
            stopCategory(cue.category)
        }
        if let old = players[cue.id] {
            old.stop()
            players[cue.id] = nil
        }
        guard let player = try? AVAudioPlayer(contentsOf: url) else { return }
        player.delegate = self
        player.numberOfLoops = cue.mode == "loop" ? -1 : 0
        player.volume = volume(for: cue)
        player.prepareToPlay()
        players[cue.id] = player
        cueByPlayerKey[cue.id] = cue
        activeCueIDs.insert(cue.id)
        player.play()
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
    }

    func isPlaying(_ cue: AudioCue) -> Bool {
        activeCueIDs.contains(cue.id)
    }

    func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        guard let key = players.first(where: { $0.value === player })?.key else { return }
        players[key] = nil
        cueByPlayerKey[key] = nil
        activeCueIDs.remove(key)
    }

    private func configureSession() {
        let session = AVAudioSession.sharedInstance()
        try? session.setCategory(.playback, mode: .default, options: [.mixWithOthers, .duckOthers])
        try? session.setActive(true)
    }

    private func volume(for cue: AudioCue) -> Float {
        let linearGain = pow(10.0, cue.gain / 20.0)
        let safetyFactor = safetyMode ? 0.58 : 1.0
        return Float(max(0.0, min(1.0, masterVolume * linearGain * safetyFactor)))
    }

    private func updateVolumes() {
        for (id, player) in players {
            guard let cue = cueByPlayerKey[id] else { continue }
            player.volume = volume(for: cue)
        }
    }
}
