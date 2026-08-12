import SwiftUI

struct RulesView: View {
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
                rule("Wann würfeln?", "Nur wenn eine Handlung unsicher ist und ein Misserfolg etwas verändert. Pflicht-Hinweise werden niemals hinter einem Wurf versteckt.")
                rule("Zielwert bestimmen", "Passt eine gelernte Fähigkeit, würfelt die Figur auf deren Wert. Fehlt eine passende Fähigkeit, würfelt sie auf die zugehörige Begabung: Handeln, Wissen oder Soziales. Der Zielwert steht auf dem Figurenblatt.")
                rule("Probe", "W100 gleich oder kleiner als der verwendete Wert ist Erfolg. Kritischer Erfolg ist das untere Zehntel des Wertes. Kritischer Misserfolg beginnt bei 90 plus einem Zehntel des verwendeten Wertes und reicht bis 100.")
                rule("Begabung", "Eine Begabungsprobe ist erlaubt, wenn keine gelernte Fähigkeit passt. Sie kann keinen kritischen Erfolg erzielen. Ein kritischer Misserfolg bleibt auch bei einer Begabung möglich.")
                rule("Geistesblitz", "Die Punkte jeder Begabung entsprechen ihrem Wert geteilt durch 10 und kaufmännisch gerundet. Ein Punkt erlaubt einen neuen Wurf auf eine misslungene, nicht kritisch misslungene Probe derselben Begabung. Eingesetzte Punkte sind verbraucht.")
                rule("Kampf", "Initiative ist W10 plus Handeln und wird vor jedem Kampf neu gewürfelt. Wer überrascht wurde, setzt die erste Runde aus. Ein Angriff ist eine passende Fertigkeitsprobe. Einmal pro Runde darf eine Figur auf Handeln parieren. Kritische Angriffe und Schusswaffen sind nicht parierbar.")
                rule("Schaden und Lebenspunkte", "Jede Figur startet mit 100 LP. Unter 10 LP wird sie bewusstlos, bei 0 LP stirbt sie. Ein einzelner Treffer mit mehr als 60 Schaden macht sofort bewusstlos. Schaden wird mit der zur Waffe passenden Zahl an W10 ausgewürfelt; kritische Angriffe verdoppeln den Schaden.")
                rule("Improvisation", "Ein Fehlschlag verschärft die Lage, blockiert aber keine wichtige Spur. Kosten können Zeit, Wärme, Vertrauen, Lebenspunkte oder ein Geistesblitz sein.")
            }
            .padding(20)
            .safeAreaPadding(.bottom, 88)
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
