import SwiftUI

@main
struct KraehenfelsApp: App {
    @StateObject private var content = ContentStore()
    @StateObject private var audio = AudioEngine()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(content)
                .environmentObject(audio)
                .preferredColorScheme(.dark)
        }
    }
}
