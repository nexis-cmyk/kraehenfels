# Handoff 28

## PC-Webansicht aus dem nativen Leitstand

- Die Web-PWA bleibt inhaltlich mit `content/manifest.json` und den nativen Ressourcen synchronisiert.
- Große Browserfenster zeigen jetzt eine Desktop-Kommandobrücke: Szenenleiste links, Fortschritt, aktueller Leitstand und Sound-Stop oben rechts.
- Schmale Fenster behalten die iPhone-nahe Ansicht mit fixer Motiv/Vorlesen/STOP-Leiste.
- Die Startseite beginnt mit „Spielleiter-Modus starten“ und führt danach in S01; Szenenwechsel, Hinweise, NPCs, Handouts, Karten und Soundboard bleiben direkt erreichbar.
- CSS- und JavaScript-URLs tragen einen Versionssuffix. Der Service-Worker erhält beim Web-Build einen neuen Shell-Suffix, damit alte Browserstände nach Änderungen zuverlässig verworfen werden.

## Verifikation

- `python tools/build_web_preview.py` erfolgreich: 8 Artwork-Dateien und 20 Audio-Dateien synchronisiert.
- Lokaler Server `python -m http.server 4173 --directory web` gestartet.
- Browserprüfung bei 1440×1000: Home-Leitstand, Start in den Spielleiter-Modus, S02-Navigation, 2 Cues, 3 NPCs, 6 Karten und 2 Handouts sichtbar.
- Automatisierter Audio-Klick meldet den erwartbaren Browser-Autoplay-Schutz; beim ersten Ton muss die Spielleitung direkt im Browser klicken.
