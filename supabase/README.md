# Supabase-Live-Sync für Krähenfels

Die Web- und iOS-App bleiben bis zur Google-Anmeldung gesperrt. Nach der Anmeldung wird die Tabelle `public.audio_ratings` synchronisiert. Jede Bewertung gehört über `user_id` zum eigenen Konto; die RLS-Regeln verhindern den Zugriff auf fremde Bewertungen.

## Einmalige Einrichtung im Dashboard

1. Öffne **Authentication → Providers → Google**.
2. Lege in der Google Cloud Console eine OAuth-Webanwendung an.
3. Trage in Google als autorisierte Weiterleitung exakt ein:

   `https://izmavtdomkckwqnsudcj.supabase.co/auth/v1/callback`

4. Kopiere Client-ID und Client-Secret direkt in den Google-Provider von Supabase und aktiviere ihn. Secrets gehören nicht in dieses Repository und nicht in den Chat.
5. Unter **Authentication → URL Configuration** sind diese Ziele hinterlegt:

   - `https://nexis-cmyk.github.io/kraehenfels/`
   - `http://localhost:4173/`
   - `de.kraehenfels.spielleitung://auth-callback`

Die SQL-Struktur liegt in [`schema.sql`](schema.sql) und wurde im Projekt bereits ausgeführt.

## Datenmodell

`audio_ratings` hat pro Konto und Cue genau eine Zeile. `rating` ist `1` für „Passt“ und `-1` für „Falsch“. Die Tabelle ist für Realtime aktiviert. Web nutzt den Supabase-JavaScript-Client, iOS den offiziellen `supabase-swift`-Client.

## Nutzung

- Web: Leitstand öffnen, **Mit Google anmelden**, im Soundboard ✓ oder × wählen.
- iOS: Beim Start **Mit Google anmelden**, danach in jeder Cue-Karte **Passt** oder **Falsch** wählen. Die Kontoverwaltung bleibt zusätzlich unter **Einstellungen** erreichbar.
- Ohne Anmeldung bleibt die Spieloberfläche geschlossen. Nach erfolgreicher Anmeldung stehen die Cues zur Bewertung bereit und werden live mit dem Konto synchronisiert.

## Sicherheitsgrenze

Im Client liegt ausschließlich der Supabase-Publishable-Key. Er ist für Browser- und iOS-Code vorgesehen. Ein Service-Role-Key darf niemals in die App, in GitHub oder in diese Dokumentation gelangen.
