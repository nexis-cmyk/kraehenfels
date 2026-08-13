# Krähenfels, Abnahme 26

Stand: 13. August 2026 · Arbeitsstand nach `bb2f86f`

## Ergebnis

Die geplante Überarbeitung des geführten Spielleiter-Modus ist umgesetzt. Der Leitstand startet mit Vorbereitung und Sicherheitscheck, zeigt pro Schritt Vorlesetext, geheime Information, Spieleraktionen, Auslöser, Hinweis, Würfelstatus und nächsten Schritt. Materialien, Karten, NPC-Dossiers, Regeln und aktuelle Soundplanung sind aus dem jeweiligen Abschnitt erreichbar.

## Funktionsprüfung

- `python tools/validate_project.py`: bestanden, 8 Szenen, 10 Handouts, 6 NPCs, 11 Hinweise, 20 Audio-Cues.
- `python tools/validate_audio_v6.py`: bestanden, 20 Dateien, keine Ähnlichkeitswarnung.
- `python tools/validate_guided_flow.py`: bestanden, 41 geführte Schritte, 8 Szenen, 7 Ziele.
- `python -m compileall -q tools`: bestanden.
- `git diff --check`: bestanden.
- GitHub/macOS: Der native Build läuft auf dem Runner; ein zwischenzeitlicher SwiftUI-Fehler in `audioPlanPanel` wurde gefunden und korrigiert. Die CI meldet Compilerfehler nun als Annotation statt nur als Exit 65.

## Spielmechanik

Die finale Gefahrenszene zählt jetzt echte Würfe. Zwei Erfolge lösen die Erfolgsseite aus, zwei Fehlschläge die Gegenseite; ein kritischer Misserfolg zählt als zwei Fehlschläge. Der Würfelhelfer weist ungültige Eingaben sichtbar zurück und zeigt Zielwert, Modifikator, Erfolg, Fehlschlag sowie kritische Folgen. Schritte ohne Probe tragen einen eigenen Würfelstatus, damit die Spielleitung nicht raten muss.

## Vorlesen und Audio

Ein Vorleseschritt öffnet einen bestätigten Dialog. Mit "Sound starten und vorlesen" beginnt der passende Cue und die Musik wird abgesenkt. Der Vorlesetext bleibt sichtbar, bis "Vorgelesen, weiter" gedrückt wird. Abbrechen oder Weitergehen stellt die normale Mischung wieder her. Der Szenen-Soundplan nennt je Cue Startmoment, Stopmoment und Spielleiteranweisung.

## Release und Installation

Der dauerhafte AltStore-Feed liegt unter [`source.json`](../altstore/source.json) und zeigt auf den GitHub-Pages-Mirror. Der Mirror antwortet mit HTTP 200; die IPA ist 158.430.077 Bytes groß und liefert Range-Anfragen. Der Feed meldet Version 3.3.0 und SHA-256 `2edba11f0b96867b1521185d69aeb3aff9496c18b64748f52b3bb455c92cde9e`. Für eine Neuinstallation in AltStore die bestehende Quelle aktualisieren oder entfernen und genau den Raw-GitHub-Link aus der README erneut hinzufügen.

## Offene Tischabnahme

Die verbleibende Abnahme ist bewusst physisch: jeden Cue einmal über iPhone und Box hören, die Druck-PDFs ausschneiden und die 8 Szenen mit drei Spielern durchspielen. Diese Punkte brauchen echte Geräte und ersetzen keine weitere Codeänderung.
