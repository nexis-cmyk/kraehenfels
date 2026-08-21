import SwiftUI

enum FrostTheme {
    static let ink = Color(red: 0.027, green: 0.067, blue: 0.051)
    static let panel = Color(red: 0.067, green: 0.133, blue: 0.102)
    static let panelRaised = Color(red: 0.094, green: 0.188, blue: 0.137)
    static let frost = Color(red: 0.91, green: 0.95, blue: 0.92)
    static let cobalt = Color(red: 0.43, green: 0.69, blue: 0.48)
    static let warning = Color(red: 0.82, green: 0.43, blue: 0.33)
    static let quiet = Color(red: 0.63, green: 0.71, blue: 0.66)
    static let line = Color(red: 0.15, green: 0.25, blue: 0.19)
}

struct FrostCard<Content: View>: View {
    let content: Content

    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    var body: some View {
        content
            .padding(14)
            .background(FrostTheme.panel, in: RoundedRectangle(cornerRadius: 12, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: 12, style: .continuous).stroke(FrostTheme.line, lineWidth: 1))
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
