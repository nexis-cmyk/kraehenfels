import SwiftUI

struct RulesView: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                Text("How to be a Hero")
                    .font(.system(size: 31, weight: .bold, design: .rounded))
                    .foregroundStyle(FrostTheme.frost)
                rule("Probe", "W100 gleich oder kleiner als der Wert ist Erfolg. Unteres Zehntel ist ein kritischer Erfolg. Ab 90 plus einem Zehntel ist es ein kritischer Patzer.")
                rule("Begabung", "Punkte der Begabung addieren, durch 10 teilen und kaufmännisch runden. Begabung auf passende Fähigkeiten addieren, maximal bis 100.")
                rule("Geistesblitz", "Begabung durch 10. Ein Punkt erlaubt einen neuen Wurf bei einer misslungenen, nicht kritischen Probe. Erneuert sich zum nächsten Abenteuer.")
                rule("Lebenspunkte", "100 LP. Unter 10 LP bewusstlos. Bei 0 tot. Mehr als 60 Schaden in einem Angriff macht bewusstlos.")
                rule("Improvisation", "Ein Fehlschlag verschärft die Lage, blockiert aber keine wichtige Spur. Kosten können Zeit, Wärme, Vertrauen oder einen Geistesblitz sein.")
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
