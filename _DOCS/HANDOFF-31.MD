# Handoff 31

## Verbindliche Google-Anmeldung

- Die Web-Oberfläche zeigt vor einer gültigen Supabase-Sitzung nur noch eine eigene Krähenfels-Anmeldeseite. Sidebar, Leitstand, Audio-Transport und Spielinhalte bleiben bis dahin verborgen.
- Nach der Google-Anmeldung öffnet sich der Leitstand automatisch; der lokale Cache bleibt für die bereits geladene Sitzung nutzbar. Abmelden führt wieder zur Anmeldeseite.
- Die iOS-App verwendet denselben Gate: `RootView` zeigt ausschließlich `AuthGateView`, bis `SupabaseManager.status == .connected` gilt. Erst danach sind Spielleiter-Modus, Materialien, Audio-Check und Einstellungen erreichbar.
- Der Cloud-Status behandelt Start, Google-OAuth, Fehler und nicht erreichbare Supabase-Verbindungen getrennt. Die Oberflächen nennen die nächste sinnvolle Aktion statt einen stillen Offline-Fallback anzubieten.

## Noch im Supabase-Dashboard

Google ist absichtlich noch nicht aktiviert, weil Client-ID und Client-Secret nicht im Chat oder Repository landen dürfen. Im geöffneten Google-Provider müssen die OAuth-Daten direkt eingetragen und der Provider aktiviert werden. Als Google-Callback bleibt:

`https://izmavtdomkckwqnsudcj.supabase.co/auth/v1/callback`

## Verifikation

- `node --check web/js/app.js` und `node --check web/js/supabase-sync.js` bleiben Pflichtprüfungen.
- Der Browser-Server muss nach dem neuen Service-Worker-Cache einmal hart neu geladen werden; Cache-Key ist `kraehenfels-web-v3.3.0-auth1`.
- Ein nativer iOS-Build ist unter Windows nicht möglich. Nach `xcodegen generate` auf macOS muss der Supabase-SPM-Lauf inklusive OAuth-Redirect einmal gebaut und auf einem Gerät getestet werden.
