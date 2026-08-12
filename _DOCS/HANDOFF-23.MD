# Handoff 23: Native Audio V5 Release Candidate

## Stand

Die native Fassung `3.2.0-rc1` ist veröffentlicht. Die Web-App bleibt bewusst auf `3.1.0`. Der Kanon enthält jetzt für jede Szene eine geordnete `audioPlan`-Liste mit Zeitpunkt, Stop-Bedingung, Spielleiteranweisung und Optional-Markierung.

## Umgesetzt

- 20 neu erzeugte V5-Cues: acht Atmosphären, M01 als dauerhaftes Motiv, M02 als Prozessions-Layer und zehn One-Shots.
- Fehlerhafte globale ElevenLabs-Downloads erkannt und alle zehn One-Shots über ihre konkrete Verlaufskarte erneut eindeutig geladen.
- M01 und M02 als echte 30-Sekunden-Quellen neu erzeugt, an der Naht überblendet und auf 240 beziehungsweise 90 Sekunden erweitert.
- Technische Audio-QA mit 48 kHz, Stereo, Lautheit, True Peak, Loop-Naht, SHA-256 und akustischem Fingerprint. Letzter Lauf: PASS, null Dubletten.
- SwiftUI-Audioengine auf vier unabhängige Ebenen umgestellt. Atmosphären-Presets stoppen die Musik nicht mehr; One-Shots können überlappen.
- Globale Transportleiste mit M01, Vorlesen-Ducking und STOP ergänzt.
- Szene zeigt Cue-Reihenfolge, Auslösemoment, konkrete SL-Anweisung und Optional-Markierung.
- Audio-Check für alle 20 Cues mit lokaler Bewertung `Passt` oder `Falsch` ergänzt.
- Eigener hörbarer Testton, Routinganzeige, Bluetooth-Ausgabe, Unterbrechungs- und Routenbehandlung ergänzt.
- Gedruckter Sound-Regieplan neu erzeugt und visuell geprüft.
- GitHub-Xcode-Build und iOS-Simulator-Unit-Tests erfolgreich abgeschlossen.
- IPA und separaten RC-AltStore-Feed veröffentlicht: `https://github.com/nexis-cmyk/kraehenfels/releases/tag/v3.2.0-rc1`.

## Noch vor einem finalen Release

1. `3.2.0-rc1` auf dem iPhone installieren.
2. In Einstellungen den Selbsttest ausführen und im Audio-Check alle 20 Cues über iPhone-Lautsprecher und die tatsächliche Bluetooth-Box bewerten.
3. Jeden als `Falsch` markierten Cue gezielt ersetzen. Erst danach `3.2.0` veröffentlichen und den dauerhaften AltStore-Feed aktualisieren.

## Reproduzierbare Befehle

```powershell
python tools/build_content_v5.py
python tools/process_audio_v5.py
python tools/validate_audio_v5.py
python tools/build_print_pack_v3.py
python tools/validate_project.py
```
