# Handoff 29

## Web-Leitstand auf nativen GM-Stand synchronisiert

- Die PC-Webansicht enthält jetzt den vollständigen Spielleiter-Einstieg aus dem nativen Leitstand: Vorbereitung in fünf Punkten, drei fertige Reisende, Spielerbriefing und Spoiler-Trennung.
- `web/js/guided-flow.js` führt alle 41 geführten Schritte über S01–S08 mit Vorlesetext, SL-Info, Spieleraktionen, garantierten Hinweisen, NPC-/Handout-Verweisen, Würfelproben, Auslösern, Wahlmöglichkeiten und drei Enden.
- Würfelhilfe nutzt dieselbe W100-Logik wie Swift: Zielwert eingeben, Ergebnis auswerten, kritische Erfolge und Patzer anzeigen; Hinweise bleiben unabhängig vom Wurf erreichbar.
- Der geführte Modus speichert Setup-Häkchen, aktuellen Schritt, Würfelergebnisse, Ende und Tischnotizen lokal im Browser.
- `web/js/app.js` nutzt den geführten Modus beim Start sowie beim Szenenwechsel; der ältere freie Szenen-Leitstand bleibt für Material- und Audioübersichten erreichbar.
- Service-Worker-Shell auf `shell7` und Asset-Version auf `r3` angehoben, damit kein alter Web-Cache die native Parität verdeckt.

## Verifikation

- `python tools/build_content_v5.py` erfolgreich; Native-/Web-Manifeste byte-identisch.
- `python tools/build_web_preview.py` erfolgreich: 8 Artworks, 20 Audio-Dateien.
- `python tools/validate_guided_flow.py` erfolgreich: 41 Schritte, 8 Szenen, 7 Ziele.
- `python tools/validate_project.py` erfolgreich: 8 Szenen, 10 Handouts, 6 NPCs, 11 Hinweise, 20 Audio-Cues.
- `node --check web/js/app.js` und `node --check web/js/guided-flow.js` erfolgreich.
- Lokaler Browser-Test auf 1440×1000: Home → Spielleiter-Start → Vorbereitung → S01 Vorlesen → S02 → Würfelpanel → Ergebnisweiterlauf.
- Der automatisierte Browser meldet beim ersten Sound erwartungsgemäß Autoplay-Block; die Schrittführung läuft trotzdem weiter und zeigt den Fehler im Audio-Status an.
