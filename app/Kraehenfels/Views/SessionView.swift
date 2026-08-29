import SwiftUI

struct SessionView: View {
    @EnvironmentObject private var content: ContentStore
    @EnvironmentObject private var session: SessionStore
    @State private var showTableDataConfirmation = false
    @State private var showRoundResetConfirmation = false

    var body: some View {
        Form {
            Section {
                Text("Diese Angaben bleiben nur auf diesem iPad. Du kannst sie vor jeder Runde neu setzen.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            } header: {
                Text("Am Tisch")
            }

            Section("Reisende") {
                ForEach(0..<3, id: \.self) { index in
                    TextField("Reisender \(index + 1)", text: session.playerNameBinding(at: index))
                        .textInputAutocapitalization(.words)
                        .autocorrectionDisabled()
                }
            }

            Section {
                Picker("Aktueller Moment", selection: Binding(
                    get: { session.nightPhaseIndex },
                    set: { session.setNightPhase($0) }
                )) {
                    ForEach(Array(content.manifest.phases.enumerated()), id: \.offset) { index, phase in
                        Label(phase.title, systemImage: phase.symbol).tag(index)
                    }
                }
                Text(content.phase(at: session.nightPhaseIndex)?.detail ?? "")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            } header: {
                Text("Nachtstand")
            } footer: {
                Text("Du steuerst die Nacht selbst. Der Stand ändert keine Szene und löst nichts automatisch aus.")
            }

            Section {
                TextEditor(text: $session.sessionNote)
                    .frame(minHeight: 132)
                    .accessibilityLabel("Allgemeine Spielnotiz")
            } header: {
                Text("Notiz vor der Runde")
            } footer: {
                Text("Zum Beispiel: Beziehungen der Figuren, Grenzen am Tisch oder offene Ideen für den Einstieg.")
            }

            Section("Geführte Lage") {
                stateRow("Zeitverlust", value: session.time, maximum: 5, symbol: "clock")
                stateRow("Wärme", value: session.warmth, maximum: 5, symbol: "flame")
                stateRow("Vertrauen", value: session.trust, maximum: 5, symbol: "person.2")
                stateRow("Verletzungen", value: session.injuries, maximum: 3, symbol: "cross.case")
                Text("Diese Werte werden aus bestätigten Konsequenzen übernommen. Du kannst sie hier bei Bedarf korrigieren.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            Section {
                Button(role: .destructive) {
                    showTableDataConfirmation = true
                } label: {
                    Label("Namen und Notizen löschen", systemImage: "person.crop.circle.badge.minus")
                }
                Button(role: .destructive) {
                    showRoundResetConfirmation = true
                } label: {
                    Label("Runde komplett zurücksetzen", systemImage: "arrow.counterclockwise.circle")
                }
            } footer: {
                Text("Die erste Aktion entfernt nur Namen und Notizen. Die zweite setzt zusätzlich Szenen, Hinweise, Würfe, Ausrüstung und den Kampfstatus zurück. Audio-Lautstärken bleiben erhalten.")
            }
        }
        .navigationTitle("Am Tisch")
        .navigationBarTitleDisplayMode(.inline)
        .alert("Namen und Notizen löschen?", isPresented: $showTableDataConfirmation) {
            Button("Löschen", role: .destructive) { session.clearTableData() }
            Button("Abbrechen", role: .cancel) { }
        } message: {
            Text("Die drei Namen sowie die allgemeine Notiz und alle Szenennotizen werden von diesem iPad entfernt. Hinweise und Szenenfortschritt bleiben erhalten.")
        }
        .alert("Runde komplett zurücksetzen?", isPresented: $showRoundResetConfirmation) {
            Button("Runde zurücksetzen", role: .destructive) { session.resetRound() }
            Button("Abbrechen", role: .cancel) { }
        } message: {
            Text("Alle Namen, Notizen, Hinweise, Szenenfortschritte, Würfe, Ausrüstung, Lagewerte und der Kampfstatus werden gelöscht. Audio-Lautstärken bleiben erhalten.")
        }
    }

    private func stateRow(_ title: String, value: Int, maximum: Int, symbol: String) -> some View {
        HStack {
            Label(title, systemImage: symbol)
            Spacer()
            Text("\(value)/\(maximum)")
                .font(.subheadline.monospaced().weight(.semibold))
                .foregroundStyle(value == 0 ? .orange : .secondary)
        }
    }
}
