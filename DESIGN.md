# Krähenfels App Design System

## Richtung

**Schwarzer Frost**: eine ruhige, fast schwarze Spielleiteroberfläche mit kaltem Blau für Orientierung. Das Interface fühlt sich wie ein dunkler Tisch mit einer einzigen Laterne an. Es ist kein Buch, keine Karte aus Pergament und kein Halloween-Dashboard.

## Tokens

| Token | Wert | Verwendung |
| --- | --- | --- |
| `ink` | `#090E17` | App-Hintergrund |
| `panel` | `#111826` | Karten und Audiozeilen |
| `panelRaised` | `#172133` | hervorgehobene Aktion |
| `frost` | `#B5D6EA` | Haupttext und primäre Aktion |
| `cobalt` | `#4A8FCE` | aktive Zustände, Links, Szenennummern |
| `quiet` | `#94AABC` | sekundärer Text |
| `warning` | `#D17B6E` | Spoiler und Stop-Aktion |

## Typografie

Die App nutzt die Systemschrift und die Dynamic-Type-Skala. Große runde Überschriften schaffen Orientierung, während Cue-Titel kurz bleiben. Keine Information wird nur über Farbe vermittelt.

## Layout

- 20 pt Außenabstand auf dem iPhone.
- 18 pt Kartenradius, 14 pt Audiozeilenradius.
- Mindestens 44 pt Touch-Zielgröße.
- Eine primäre Aktion pro Ansicht.
- Atmosphären, Musik und Effekte bleiben als getrennte Reihen sichtbar.

## Accessibility

VoiceOver erhält auf jeder Audiozeile einen sprechenden Titel und den Status „Läuft“ oder „Gestoppt“. Die Sicherheitslautstärke reduziert alle Audios auf einen sicheren Faktor. Die App respektiert Dynamic Type und bleibt auch ohne Audio verständlich, weil jedes wichtige akustische Motiv ein Papier-Fallback hat.
