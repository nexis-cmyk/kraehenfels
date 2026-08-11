import SwiftUI

@main
struct KraehenfelsApp: App {
    @StateObject private var content = ContentStore()
    @StateObject private var audio = AudioEngine()
    @StateObject private var session = SessionStore()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(content)
                .environmentObject(audio)
                .environmentObject(session)
                .preferredColorScheme(.dark)
        }
    }
}
