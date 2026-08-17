# Handoff 30

## Supabase-Live-Sync für Soundbewertungen

- Supabase-Projekt `izmavtdomkckwqnsudcj` ist über `supabase/schema.sql` angebunden. `public.audio_ratings` nutzt `(user_id, cue_id)` als Primärschlüssel, erlaubt nur eigene Zeilen per RLS und ist für `supabase_realtime` aktiviert.
- Web nutzt `web/js/supabase-sync.js` mit dem Publishable-Key aus `web/js/supabase-config.js`. Die Leitstand-Startseite und jede Szenenansicht zeigen den Cloud-Status; im Soundboard stehen ✓/× pro Cue. Offline-Bewertungen bleiben in `localStorage` und werden nach Anmeldung hochgeladen.
- iOS nutzt `SupabaseManager` plus `CloudAccountView`, die über den offiziellen `supabase-swift`-SPM-Client in `app/project.yml` eingebunden sind. Audio-Check-Bewertungen werden lokal gehalten und nach Google-Anmeldung upserted; Realtime löst eine erneute Abfrage aus.
- Auth-Redirects im Supabase-Dashboard sind gesetzt: GitHub Pages, `http://localhost:4173/` und `de.kraehenfels.spielleitung://auth-callback`. Google ist noch nicht aktiv, solange Client-ID und Client-Secret im Supabase-Google-Provider fehlen.

## Verifikation

- `node --check web/js/app.js` erfolgreich.
- `node --check web/js/supabase-sync.js` erfolgreich.
- `git diff --check` erfolgreich.
- Browser-Test auf `http://localhost:4173/?cloud=1`: Cloud-Karte sichtbar, Szene S02 geöffnet, Soundboard sichtbar, ✓-Bewertung zählt lokal hoch.
- Native Xcode-Build konnte unter Windows nicht ausgeführt werden; nach `xcodegen generate` auf macOS muss der SPM-Auflösungslauf einmal getestet werden.

## Nächster Schritt

Google-OAuth-Daten direkt im Supabase-Dashboard eintragen und Provider aktivieren. Danach Web- und iOS-App mit demselben Konto anmelden und eine Bewertung setzen; sie sollte in `audio_ratings` erscheinen und zwischen den Clients live aktualisieren.
