import SwiftUI

enum FrostTheme {
    static let ink = Color(red: 0.024, green: 0.075, blue: 0.055)
    static let panel = Color(red: 0.055, green: 0.129, blue: 0.094)
    static let panelRaised = Color(red: 0.082, green: 0.188, blue: 0.145)
    static let frost = Color(red: 0.902, green: 0.941, blue: 0.91)
    static let accent = Color(red: 0.545, green: 0.686, blue: 0.584)
    static let warning = Color(red: 0.788, green: 0.471, blue: 0.408)
    static let quiet = Color(red: 0.635, green: 0.702, blue: 0.655)
    static let line = Color(red: 0.161, green: 0.271, blue: 0.224)

    // Kept as a compatibility alias while the view layer moves to the Waldnacht vocabulary.
    static let cobalt = accent
}

struct FrostCard<Content: View>: View {
    let content: Content

    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    var body: some View {
        content
            .padding(16)
            .background(FrostTheme.panel, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: 14, style: .continuous).stroke(FrostTheme.line, lineWidth: 1))
    }
}

struct SectionLabel: View {
    let title: String

    var body: some View {
        Text(title)
            .font(.caption.weight(.semibold))
            .foregroundStyle(FrostTheme.quiet)
    }
}
