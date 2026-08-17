import SwiftUI

struct AuthGateView: View {
    @EnvironmentObject private var cloud: SupabaseManager
    @State private var isWorking = false

    private var isPreparing: Bool {
        cloud.status == .starting || cloud.status == .authenticating
    }

    var body: some View {
        ZStack {
            FrostTheme.ink.ignoresSafeArea()

            ScrollView {
                VStack(spacing: 22) {
                    Image(systemName: "bell.and.waves.left.and.right.fill")
                        .font(.system(size: 36, weight: .medium))
                        .foregroundStyle(FrostTheme.frost)
                        .frame(width: 78, height: 78)
                        .background(FrostTheme.panelRaised, in: RoundedRectangle(cornerRadius: 22, style: .continuous))
                        .overlay(RoundedRectangle(cornerRadius: 22, style: .continuous).stroke(FrostTheme.frost.opacity(0.16), lineWidth: 1))

                    VStack(spacing: 8) {
                        Text("KRÄHENFELS · DIE LETZTE KUTSCHE")
                            .font(.caption.weight(.semibold))
                            .tracking(1.6)
                            .foregroundStyle(FrostTheme.cobalt)
                            .multilineTextAlignment(.center)
                        Text(title)
                            .font(.system(size: 32, weight: .bold, design: .rounded))
                            .foregroundStyle(FrostTheme.frost)
                            .multilineTextAlignment(.center)
                        Text(detail)
                            .font(.subheadline)
                            .foregroundStyle(FrostTheme.quiet)
                            .multilineTextAlignment(.center)
                            .fixedSize(horizontal: false, vertical: true)
                    }

                    VStack(alignment: .leading, spacing: 12) {
                        feature("lock.fill", title: "Geschützter Leitstand", detail: "Die Abenteuerinhalte öffnen sich erst nach der Anmeldung.")
                        feature("checkmark.circle.fill", title: "Soundbewertungen synchron", detail: "Passt und Falsch werden deinem Konto zugeordnet und zwischen Geräten abgeglichen.")
                        feature("arrow.clockwise", title: "Beim nächsten Mal direkt weiter", detail: "Deine Sitzung bleibt auf diesem Gerät aktiv, bis du dich abmeldest.")
                    }
                    .padding(16)
                    .background(FrostTheme.panel, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                    .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(FrostTheme.frost.opacity(0.12), lineWidth: 1))

                    Button {
                        isWorking = true
                        Task {
                            await cloud.signInWithGoogle()
                            isWorking = false
                        }
                    } label: {
                        HStack(spacing: 10) {
                            if isWorking || isPreparing {
                                ProgressView().tint(FrostTheme.ink)
                            } else {
                                Text("G")
                                    .font(.headline.weight(.bold))
                                    .frame(width: 24, height: 24)
                                    .background(.white, in: Circle())
                                    .foregroundStyle(Color(red: 0.26, green: 0.52, blue: 0.96))
                            }
                            Text(buttonTitle)
                                .font(.headline.weight(.semibold))
                        }
                        .frame(maxWidth: .infinity, minHeight: 52)
                    }
                    .buttonStyle(.plain)
                    .foregroundStyle(FrostTheme.ink)
                    .background(FrostTheme.frost, in: RoundedRectangle(cornerRadius: 15, style: .continuous))
                    .disabled(isPreparing || isWorking)

                    if let error = cloud.lastError {
                        Text(error)
                            .font(.caption)
                            .foregroundStyle(FrostTheme.warning)
                            .multilineTextAlignment(.center)
                            .fixedSize(horizontal: false, vertical: true)
                    }

                    Text("Google verwaltet die Anmeldung. Krähenfels verwendet nur die Konto-ID und E-Mail-Adresse, die für die Sitzung nötig sind.")
                        .font(.caption2)
                        .foregroundStyle(FrostTheme.quiet.opacity(0.9))
                        .multilineTextAlignment(.center)
                        .fixedSize(horizontal: false, vertical: true)
                }
                .padding(24)
                .frame(maxWidth: 520)
                .frame(maxWidth: .infinity)
            }
        }
    }

    private var title: String {
        switch cloud.status {
        case .starting: return "Anmeldung wird geprüft."
        case .authenticating: return "Weiter zu Google …"
        case .error: return "Anmeldung erforderlich."
        case .signedOut: return "Nur für die Spielleitung."
        case .connected: return "Willkommen zurück."
        }
    }

    private var detail: String {
        switch cloud.status {
        case .starting: return "Einen Moment — Krähenfels prüft deine sichere Sitzung."
        case .authenticating: return "Schließe die Google-Anmeldung ab. Danach öffnet sich dein Leitstand automatisch."
        case .error: return "Die Anmeldung konnte nicht abgeschlossen werden. Versuche es noch einmal."
        default: return "Melde dich mit Google an, damit Soundbewertungen und dein Spielstand deinem Konto zugeordnet werden können."
        }
    }

    private var buttonTitle: String {
        if isWorking || cloud.status == .authenticating { return "Anmeldung läuft …" }
        return "Mit Google anmelden"
    }

    @ViewBuilder
    private func feature(_ symbol: String, title: String, detail: String) -> some View {
        HStack(alignment: .top, spacing: 11) {
            Image(systemName: symbol)
                .foregroundStyle(FrostTheme.cobalt)
                .frame(width: 24, height: 24)
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.white)
                Text(detail)
                    .font(.caption)
                    .foregroundStyle(FrostTheme.quiet)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }
}
