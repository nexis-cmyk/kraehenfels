import Combine
import Foundation
import Supabase

@MainActor
final class SupabaseManager: ObservableObject {
    enum SyncStatus: Equatable {
        case starting
        case signedOut
        case authenticating
        case connected
        case error

        var label: String {
            switch self {
            case .starting: return "Cloud-Verbindung wird vorbereitet …"
            case .signedOut: return "Nicht verbunden · Bewertungen bleiben lokal"
            case .authenticating: return "Google-Anmeldung läuft …"
            case .connected: return "Live mit Supabase verbunden"
            case .error: return "Cloud-Synchronisierung fehlgeschlagen"
            }
        }
    }

    private struct AudioRatingRow: Codable {
        let userID: UUID
        let cueID: String
        let rating: Int
        let client: String?
        let appVersion: String?

        enum CodingKeys: String, CodingKey {
            case userID = "user_id"
            case cueID = "cue_id"
            case rating
            case client
            case appVersion = "app_version"
        }
    }

    private struct AudioRatingPayload: Encodable {
        let userID: UUID
        let cueID: String
        let rating: Int
        let client: String
        let appVersion: String

        enum CodingKeys: String, CodingKey {
            case userID = "user_id"
            case cueID = "cue_id"
            case rating
            case client
            case appVersion = "app_version"
        }
    }

    @Published private(set) var status: SyncStatus = .starting
    @Published private(set) var ratings: [String: Int] = [:]
    @Published private(set) var userEmail: String?
    @Published private(set) var lastError: String?

    private let client: SupabaseClient
    private var userID: UUID?
    private var realtimeChannel: RealtimeChannelV2?
    private var hasStarted = false

    init() {
        client = SupabaseClient(
            supabaseURL: SupabaseConfig.url,
            supabaseKey: SupabaseConfig.publishableKey
        )
    }

    @discardableResult
    func start() async -> [String: Int] {
        guard !hasStarted else { return ratings }
        hasStarted = true
        status = .starting

        do {
            let session = try await client.auth.session
            userID = session.user.id
            userEmail = session.user.email
            ratings = try await fetchRatings()
            subscribeToRatings()
            status = .connected
            lastError = nil
        } catch {
            userID = nil
            userEmail = nil
            ratings = [:]
            status = .signedOut
            lastError = nil
        }
        return ratings
    }

    func signInWithGoogle() async {
        status = .authenticating
        lastError = nil

        do {
            let session = try await client.auth.signInWithOAuth(
                provider: .google,
                redirectTo: SupabaseConfig.redirectURL
            )
            userID = session.user.id
            userEmail = session.user.email
            ratings = try await fetchRatings()
            subscribeToRatings()
            status = .connected
            hasStarted = true
        } catch {
            status = .error
            lastError = error.localizedDescription
        }
    }

    func signOut() async {
        do {
            try await client.auth.signOut()
            if let realtimeChannel {
                await client.removeChannel(realtimeChannel)
            }
            self.realtimeChannel = nil
            userID = nil
            userEmail = nil
            ratings = [:]
            status = .signedOut
            lastError = nil
        } catch {
            status = .error
            lastError = error.localizedDescription
        }
    }

    func setRating(_ cueID: String, rating: Int) async {
        let normalized = min(max(rating, -1), 1)
        ratings[cueID] = normalized
        guard let userID else {
            status = .signedOut
            return
        }

        do {
            try await client
                .from("audio_ratings")
                .upsert(
                    AudioRatingPayload(
                        userID: userID,
                        cueID: cueID,
                        rating: normalized,
                        client: "ios",
                        appVersion: "3.3.0"
                    ),
                    onConflict: "user_id,cue_id"
                )
                .execute()
            status = .connected
            lastError = nil
        } catch {
            status = .error
            lastError = error.localizedDescription
        }
    }

    func pushLocalRatings(_ localRatings: [String: Int]) async {
        guard userID != nil else { return }
        for (cueID, rating) in localRatings {
            if ratings[cueID] == nil {
                await setRating(cueID, rating: rating)
            }
        }
    }

    func clearRatings() async {
        ratings = [:]
        guard let userID else { return }
        do {
            try await client
                .from("audio_ratings")
                .delete()
                .eq("user_id", value: userID)
                .execute()
            status = .connected
            lastError = nil
        } catch {
            status = .error
            lastError = error.localizedDescription
        }
    }

    private func fetchRatings() async throws -> [String: Int] {
        let response = try await client
            .from("audio_ratings")
            .select("cue_id,rating")
            .execute()
        let rows = try response.value as [AudioRatingRow]
        return Dictionary(uniqueKeysWithValues: rows.map { ($0.cueID, $0.rating) })
    }

    private func subscribeToRatings() {
        guard realtimeChannel == nil else { return }
        let channel = client.realtimeV2.channel("audio-ratings")
        _ = channel.onPostgresChange(
            AnyAction.self,
            schema: "public",
            table: "audio_ratings"
        ) { [weak self] _ in
            Task { @MainActor [weak self] in
                guard let self else { return }
                do {
                    self.ratings = try await self.fetchRatings()
                } catch {
                    self.lastError = error.localizedDescription
                }
            }
        }
        realtimeChannel = channel
        Task { await channel.subscribe() }
    }
}
