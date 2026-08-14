# Handoff 27

## Web-Leitstand auf native RC3-Startansicht synchronisiert

- Die Web-Vorschau startet jetzt wie die iPhone-App in einer Leitstand-Startseite statt direkt in S01.
- Startseite enthält Spielleiter-Modus, Jetzt-weiterspielen-Karte, Tischstatus, Nachtstand, acht Szenen und die vier Schnellzugriffe Materialien/Regeln/Audio-Check/Akte.
- Eine feste mobile Transportleiste bietet Motiv, Vorlesen und STOP; Szenenansicht besitzt eine Zurück-Schaltfläche zum Leitstand.
- Das bestehende Szenen-Detail mit Hinweisen, NPCs, Handouts, Karten und Soundboard bleibt erhalten.
- Service-Worker-Cache wurde mit `-shell2` versioniert; `tools/build_web_preview.py` erzeugt denselben Cache-Suffix automatisch.

## Prüfung

- `python tools/build_web_preview.py`
- `python tools/validate_project.py`
- `node --check web/js/app.js`
- Lokale Browserprüfung bei 393×852: Startseite, Szene öffnen, zurück zum Leitstand und Audio-Check-Sprung funktionieren.
