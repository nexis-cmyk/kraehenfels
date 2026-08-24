import SwiftUI

struct RulesView: View {
    @EnvironmentObject private var content: ContentStore

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                VStack(alignment: .leading, spacing: 7) {
                    Text("HOW TO BE A HERO")
                        .font(.caption.weight(.bold))
                        .tracking(1.5)
                        .foregroundStyle(FrostTheme.cobalt)
                    Text("Kurzregeln für Krähenfels")
                        .font(.system(size: 31, weight: .bold, design: .rounded))
                        .foregroundStyle(FrostTheme.frost)
                    Text("Die App führt dich durch die passende Probe. Diese Seite erklärt, warum sie so funktioniert.")
                        .font(.subheadline)
                        .foregroundStyle(FrostTheme.quiet)
                }
                ForEach(content.manifest.rules) { entry in
                    rule(entry.title, entry.body)
                }
            }
            .padding(20)
        }
        .background(FrostTheme.ink.ignoresSafeArea())
        .navigationTitle("Regeln")
        .navigationBarTitleDisplayMode(.inline)
    }

    private func rule(_ title: String, _ body: String) -> some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 7) {
                SectionLabel(title: title)
                Text(body)
                    .font(.body)
                    .foregroundStyle(.white.opacity(0.92))
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }
}
