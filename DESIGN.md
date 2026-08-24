# Krähenfels App Design System

## Richtung

**Waldnacht**: eine ruhige, fast schwarze Spielleiteroberfläche mit gedämpftem Waldgrün für Orientierung. Das Interface fühlt sich wie kalte Nachtluft zwischen Tannen an. Es ist kein Buch, keine Karte aus Pergament und kein Halloween-Dashboard.

## Tokens

| Token | Wert | Verwendung |
| --- | --- | --- |
| `ink` | `#06130E` | App-Hintergrund |
| `panel` | `#0D2118` | Karten und Audiozeilen |
| `panelRaised` | `#153025` | hervorgehobene Aktion |
| `frost` | `#E6F0E8` | Haupttext und primäre Aktion |
| `accent` | `#8BAF95` | aktive Zustände, Links, Szenennummern |
| `quiet` | `#A2B3A7` | sekundärer Text |
| `warning` | `#C97868` | Spoiler und Stop-Aktion |

## Typografie

Die App nutzt die Systemschrift und die Dynamic-Type-Skala. Große runde Überschriften schaffen Orientierung, während Cue-Titel kurz bleiben. Keine Information wird nur über Farbe vermittelt.

## Layout

- Zweispaltige Navigation auf dem 11-Zoll-iPad. Die Kontextdetails öffnen sich bei Bedarf als Sheet.
- 20 pt Außenabstand im Inhaltsbereich.
- 14 pt Kartenradius und ein festes Audio-Dock am unteren Rand.
- Mindestens 44 pt Touch-Zielgröße.
- Eine primäre Aktion pro Ansicht.
- Atmosphären, Musik und Effekte bleiben als getrennte Reihen sichtbar.
- Der geführte Ablauf reserviert seinen unteren Bereich über `safeAreaInset`, damit der letzte Schritt vollständig erreichbar bleibt.

## Accessibility

VoiceOver erhält auf jeder Audiozeile einen sprechenden Titel und den Status „Läuft“ oder „Gestoppt“. Die Sicherheitslautstärke reduziert alle Audios auf einen sicheren Faktor. Die App respektiert Dynamic Type und bleibt auch ohne Audio verständlich, weil jedes wichtige akustische Motiv ein Papier-Fallback hat.
