import SwiftUI

struct CloudAccountView: View {
    @EnvironmentObject private var cloud: SupabaseManager
    @State private var isWorking = false

    var body: some View {
        FrostCard {
            VStack(alignment: .leading, spacing: 10) {
                HStack(alignment: .top, spacing: 10) {
                    Image(systemName: cloud.status == .connected ? "checkmark.icloud.fill" : "icloud")
                        .font(.title3)
                        .foregroundStyle(cloud.status == .connected ? .green : FrostTheme.cobalt)
                    VStack(alignment: .leading, spacing: 3) {
                        SectionLabel(title: "LIVE-SYNC")
                        Text("Soundbewertungen zentral sammeln")
                            .font(.headline)
                            .foregroundStyle(.white)
                        Text(cloud.userEmail.map { "Verbunden als \($0)" } ?? cloud.status.label)
                            .font(.caption)
                            .foregroundStyle(FrostTheme.quiet)
                    }
                    Spacer()
                }

                Text("Passt oder Falsch wird deinem Konto in Supabase zugeordnet. Die Inhalte der App bleiben geschützt, bis die Anmeldung abgeschlossen ist.")
                    .font(.caption)
                    .foregroundStyle(FrostTheme.quiet)
                    .fixedSize(horizontal: false, vertical: true)

                if cloud.status == .connected {
                    HStack {
                        Label("\(cloud.ratings.count) Bewertungen synchronisiert", systemImage: "arrow.triangle.2.circlepath")
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(.green)
                        Spacer()
                        Button("Abmelden") {
                            Task { await cloud.signOut() }
                        }
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(FrostTheme.warning)
                    }
                } else {
                    Button {
                        isWorking = true
                        Task {
                            await cloud.signInWithGoogle()
                            isWorking = false
                        }
                    } label: {
                        HStack {
                            if isWorking { ProgressView().tint(FrostTheme.ink) }
                            Text(isWorking ? "Anmeldung läuft …" : "Mit Google anmelden")
                                .font(.subheadline.weight(.semibold))
                            Spacer()
                            Image(systemName: "arrow.up.right")
                        }
                        .foregroundStyle(FrostTheme.ink)
                        .padding(.horizontal, 14)
                        .frame(maxWidth: .infinity, minHeight: 44)
                        .background(FrostTheme.frost, in: RoundedRectangle(cornerRadius: 12, style: .continuous))
                    }
                    .buttonStyle(.plain)
                    .disabled(isWorking)
                }

                if let error = cloud.lastError {
                    Label(error, systemImage: "exclamationmark.triangle.fill")
                        .font(.caption)
                        .foregroundStyle(FrostTheme.warning)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
        }
        .task {
            _ = await cloud.start()
        }
    }
}
