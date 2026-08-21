import SwiftUI

struct SessionView: View {
    @EnvironmentObject private var session: SessionStore
    @State private var showClearConfirmation = false

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
                    ForEach(SessionStore.nightPhases) { phase in
                        Label(phase.title, systemImage: phase.symbol).tag(phase.id)
                    }
                }
                Text(session.currentNightPhase.detail)
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

            Section {
                Button(role: .destructive) {
                    showClearConfirmation = true
                } label: {
                    Label("Tischdaten löschen", systemImage: "trash")
                }
            } footer: {
                Text("Hinweise, Szenenfortschritt und Audio-Einstellungen bleiben erhalten.")
            }
        }
        .navigationTitle("Am Tisch")
        .navigationBarTitleDisplayMode(.inline)
        .alert("Tischdaten löschen?", isPresented: $showClearConfirmation) {
            Button("Löschen", role: .destructive) { session.clearJournal() }
            Button("Abbrechen", role: .cancel) { }
        } message: {
            Text("Die drei Namen sowie alle eigenen Session- und Szenennotizen werden von diesem iPad entfernt.")
        }
    }
}
