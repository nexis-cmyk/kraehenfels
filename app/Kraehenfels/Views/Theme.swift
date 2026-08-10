import SwiftUI

enum FrostTheme {
    static let ink = Color(red: 0.035, green: 0.055, blue: 0.09)
    static let panel = Color(red: 0.065, green: 0.095, blue: 0.15)
    static let panelRaised = Color(red: 0.09, green: 0.13, blue: 0.20)
    static let frost = Color(red: 0.71, green: 0.84, blue: 0.92)
    static let cobalt = Color(red: 0.29, green: 0.56, blue: 0.82)
    static let warning = Color(red: 0.82, green: 0.48, blue: 0.43)
    static let quiet = Color(red: 0.58, green: 0.67, blue: 0.75)
}

struct FrostCard<Content: View>: View {
    let content: Content

    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    var body: some View {
        content
            .padding(16)
            .background(FrostTheme.panel, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(FrostTheme.frost.opacity(0.12), lineWidth: 1))
    }
}

struct SectionLabel: View {
    let title: String

    var body: some View {
        Text(title.uppercased())
            .font(.caption.weight(.semibold))
            .tracking(1.4)
            .foregroundStyle(FrostTheme.quiet)
    }
}
