# Krähenfels Audio V5: verbindlicher Gesamtplan

## Ziel

Version 3.2.0 ersetzt das bisherige Soundboard der nativen iPhone-App. Die neue Fassung soll am Tisch leicht zu bedienen sein und vor allem richtig klingen. Jeder Cue muss eindeutig zu erkennen sein, zur angegebenen Szene passen und auf einer Bluetooth-Box funktionieren, ohne Gespräche zu überdecken.

Die Web-App bleibt auf Version 3.1.0 online. Sie dient nur noch als Notfall-Fallback und erhält weder neue Sounds noch weitere Funktionen. Der neue Audioplan gilt für die iPhone-App und die gedruckten Spielleiterunterlagen.

## Verbindliches Audio-Set

### Musik

- `M01 Krähenfels-Motiv`: ungefähr vier Minuten, instrumental und nahtlos wiederholbar. Dunkles Cello, gedämpftes Klavier und eine dezente historische Folk-Farbe bilden ein ruhiges, wiedererkennbares Motiv.
- `M02 Die Prozession`: 60 bis 90 Sekunden langer Zusatz-Layer für Enthüllung und Finale. Er läuft bei Bedarf über M01.
- Beide Stücke bleiben frei von Gesang, modernen Synthesizer-Leads, dominanten Drums und Trailer-Booms.
- M01 startet manuell über "Spiel beginnen". Es läuft über Szenenwechsel, beim Sperren des iPhones und beim kurzen Wechsel in eine andere App weiter.
- Bei Vorlesetexten kann die Spielleitung M01 mit einem Tastendruck absenken. Im Epilog blendet die App das Motiv langsam aus.

Eleven Music ist die Hauptquelle. Da eine Generation höchstens fünf Minuten lang sein kann, wird das vierminütige Ergebnis als sauber geprüfter Loop verwendet. [Eleven Music](https://elevenlabs.io/docs/overview/capabilities/music)

### Ortsatmosphären

- `A01 Kutschenstraße`: Schnee, Wagenholz, Lederzeug, Pferdeatem und Waldwind.
- `A02 Gasthaus`: Herdfeuer, Holzraum, entferntes Geschirr und Wind an den Läden.
- `A03 Krähenfels am Morgen`: Tauwasser, wenige Schritte, Bach und erste Arbeit im Dorf.
- `A04 Kirche ohne Glocke`: kalter Steinraum, Kerzen, altes Holz und Zugluft im Turm.
- `A05 Schmiede`: Kohlefeuer, Blasebalg und leise Werkstattgeräusche. Kein wiederholtes Hämmern im Loop.
- `A06 Waldspur`: Tannenwind, Schnee, einzelne Äste und große räumliche Distanz.
- `A07 Rathausarchiv`: Papier, Ofenrest, Holzboden und gedämpfter Wind hinter den Fenstern.
- `A08 Alte Eiche`: Wind um einen hohlen Stamm, knarrendes Holz, Schnee an den Wurzeln und eine lose Schreinkette.

Die Atmosphären werden aus echten oder realistisch generierten Einzellayern gebaut. Allgemeine Natur- und Raumaufnahmen dürfen aus Pixabay oder Freesound stammen, wenn die konkrete Datei CC0, CC BY oder eine für die App passende Lizenz trägt. Für jede Fremdquelle werden URL, Urheber, Lizenz, Abrufdatum und Bearbeitung festgehalten.

Tabletop-Audio-SoundPads werden nicht in die App kopiert. Die SoundPad-Dateien sind nicht für Downloads außerhalb der Website vorgesehen. Die regulären Ambiences stehen unter CC BY-NC-ND. [Tabletop-Audio-Lizenz](https://tabletopaudio.com/about.html)

### Einzeleffekte

- `SFX01 Achse bricht`: erst Holzspannung, dann ein klarer Bruch und leichtes Wagenmetall.
- `SFX02 Pferde scheuen`: Schnauben, ein Huftritt und gespanntes Lederzeug.
- `SFX03 Riegel von außen`: schweres Eisen gleitet in zwei Halterungen einer Holztür.
- `SFX04 Geweih an der Gasthaustür`: trockener Knochen kratzt über Holz und klopft zweimal.
- `SFX05 Einzelner Schmiedeschlag`: genau ein Hammerschlag auf heißes Eisen mit natürlichem Nachklang.
- `SFX06 Atem hinter einer Figur`: ein menschlich großer Atemzug im kalten Wald, ohne Worte oder Monsterstimme.
- `SFX07 Prozessionsschritte`: mehrere langsame Stiefel im Schnee, Kleidung und hölzerne Masken.
- `SFX08 Knochenhirsch hebt den Kopf`: trockene Gelenke, Schnee unter Gewicht und ein hohler Atemzug.
- `SFX09 Bindung reißt`: gespanntes Leder und Eisen geben nach. Danach fällt der Druck hörbar ab.
- `SFX10 Falscher Glockenschlag`: ein einzelner historischer Glockenton mit unnatürlicher, leicht verstimmter Resonanz.

Die Kirche verwendet nur SFX10. Der Schmiedeschlag gehört ausschließlich in die Schmiede. SFX04 wird im Gasthaus ausgelöst und nicht im Wald. SFX09 gehört in das Zerstörungsende der Finalszene, nicht in den Epilog.

## Produktionsverfahren

ElevenLabs bleibt der Hauptgenerator für geschichtsspezifische Effekte. Jeder Prompt beschreibt genau einen Vorgang. Eine Generation liefert vier Varianten; keine Variante wird allein wegen ihres Dateinamens übernommen. Für komplexe Abläufe werden mehrere einzelne Aufnahmen erzeugt und anschließend lokal zusammengesetzt. [ElevenLabs Sound Effects](https://elevenlabs.io/docs/eleven-creative/playground/sound-effects)

Für jeden Cue gilt:

1. Eine Sollbeschreibung und eine Liste unerwünschter Geräusche werden festgelegt.
2. Vier Varianten werden erzeugt und einzeln geprüft.
3. Varianten mit Stimmen, Musik, Explosionen, modernen Geräuschen oder generischen Kinoeffekten scheiden aus.
4. Die beste Variante wird geschnitten, entrauscht und auf den Zielpegel gebracht.
5. Dateiname, Cue-ID, Beschreibung und tatsächlicher Inhalt werden gemeinsam geprüft.
6. Erst danach wird die Datei in das Kandidatenpaket übernommen.

Wenn ElevenLabs einen Cue nach zwei überarbeiteten Prompt-Runden noch falsch interpretiert, wird derselbe Cue mit Stable Audio Open erzeugt oder aus einer geprüften Foley-Quelle aufgebaut. [Stable Audio Open](https://stability.ai/news-updates/introducing-stable-audio-open)

Neue Kandidaten heißen `V5_*`. Die bisherigen `V3_*`-Dateien bleiben bis zur vollständigen Abnahme erhalten und werden nicht automatisch überschrieben.

## Spielleiter-Ablauf

| Szene | Start der Szene | Einzeleffekte und Zeitpunkt | Ende der Szene |
|---|---|---|---|
| S01 Kutschenpanne | M01 starten, danach A01 | SFX01 beim beschriebenen Knacken; SFX02 direkt nach dem Bruch | A01 ausblenden |
| S02 Gasthaus | A02 starten, M01 läuft weiter | SFX03 beim Verriegeln; SFX04 später als optionales Omen an der Tür | A02 ausblenden |
| S03 Kirche | A04 starten | SFX10 einmal nach dem ausgesprochenen Wort "Gastrecht" | A04 ausblenden |
| S04 Schmiede | A05 starten | SFX05 wenn Marta die drei schwarzen Nägel zeigt | A05 ausblenden |
| S05 Waldspur | A06 starten | SFX06 nachdem die Spur scheinbar ihre Richtung wechselt | A06 ausblenden |
| S06 Wahrheit | A07 starten | M02 leise beim Erkennen der Prozession; SFX07 beim Blick auf die Straße | A07 ausblenden, M02 darf weiterlaufen |
| S07 Alte Eiche | A08 starten, M01 absenken, M02 anheben | SFX08 beim ersten vollständigen Auftreten; SFX09 nur beim Zerstörungsende | A08 und M02 passend zum gewählten Ende ausblenden |
| S08 Tauwetter | A03 starten, M01 wieder leicht anheben | Kein zusätzlicher Schockeffekt | Nach dem letzten Satz M01 und A03 langsam ausblenden |

In der App und im gedruckten Soundleitfaden steht bei jedem Cue:

- was hörbar sein muss
- wann er gestartet wird
- ob er einmalig oder als Loop läuft
- welche Lautstärke vorgesehen ist
- wann er gestoppt oder ausgeblendet wird
- ob er notwendig oder optional ist
- welcher gedruckte Hinweis denselben Informationswert trägt

## App und Datenmodell

Das Manifest erhält optionale, rückwärtskompatible Felder:

```json
{
  "scope": "global",
  "layer": "musicBed",
  "playWhen": "Vor dem ersten Vorlesetext",
  "stopWhen": "Nach dem letzten Satz des Epilogs",
  "gmInstruction": "Einmal starten und während des Abenteuers laufen lassen."
}
```

Jede Szene erhält eine geordnete `audioPlan`-Liste mit `cueId`, `action`, `moment`, `instruction` und `optional`.

Die native Audio-Engine verwaltet vier unabhängige Kanäle:

- globales Musikbett
- zusätzlicher Musik- oder Prozessions-Layer
- eine wechselnde Ortsatmosphäre
- gleichzeitig auslösbare Einzeleffekte

Ein Szenen-Preset wechselt nur die Ortsatmosphäre. M01 bleibt aktiv. M02 kann darübergelegt werden. Einzeleffekte stoppen keine Loops. Atmosphären wechseln mit einem echten Crossfade.

Die App erhält außerdem:

- globalen Start und Stop für M01
- sichtbaren Status aller laufenden Layer
- getrennte Regler für Musik, Atmosphäre und Effekte
- eine Taste zum Absenken der Musik während des Vorlesens
- eine ständig erreichbare Taste "Alles stoppen"
- sichtbare Dateifehler mit Cue-ID und Dateiname
- Hintergrundwiedergabe bei gesperrtem Bildschirm und App-Wechsel
- Bluetooth-A2DP-Ausgabe sowie saubere Behandlung von Anrufen und Gerätewechseln
- einen Audio-Prüfbereich mit Sollbeschreibung, Play-Taste und Markierung "passt" oder "falsch"

## Technische Qualitätskontrolle

Die automatische Prüfung umfasst:

- Cue-ID, Dateiname und Manifest-Zuordnung
- Dauer, Sample-Rate, Kanalzahl und Bundle-Vollständigkeit
- Stille, Clipping, Gleichspannungsanteil und Spitzenpegel
- Lautheit nach EBU R128
- hörbare Sprünge und Klicks am Loop-Übergang
- akustische Fingerabdrücke gegen doppelte oder fast identische Dateien
- lokale CLAP-Analyse gegen Sollbeschreibung und Negativbegriffe wie "Explosion", "Musik", "Stimme" oder "Trailer-Boom"

Zielpegel für den Bluetooth-Mix:

- M01 ungefähr -27 LUFS
- Atmosphären ungefähr -25 LUFS
- M02 ungefähr -25 LUFS
- Einzeleffekte ungefähr -18 LUFS
- maximal -1,5 dBTP

Der Mix wird zuerst über die vorgesehene Bluetooth-Box geprüft. Ein zweiter Test über den iPhone-Lautsprecher stellt sicher, dass alle wichtigen Geräusche trotzdem erkennbar bleiben.

## Abnahme und Release

Ein Cue gilt nur dann als fertig, wenn:

- der Klang blind zur Bezeichnung passt
- kein anderer Cue praktisch gleich klingt
- der Cue in der richtigen Szene und am richtigen Auslöser erscheint
- leise Musik und Atmosphäre das Gespräch am Tisch nicht verdecken
- die Datei offline und bei gesperrtem Bildschirm funktioniert
- ein optionaler Audiohinweis immer eine visuelle oder gedruckte Entsprechung besitzt

Der Release läuft in dieser Reihenfolge:

1. Quellen und Lizenzen erfassen.
2. Prompts und Sollbeschreibungen festlegen.
3. Kandidaten erzeugen oder beschaffen.
4. Varianten prüfen, schneiden, mischen und normalisieren.
5. Manifest, Audio-Engine, Szenenansicht und Druckleitfaden auf V5 umstellen.
6. Native Tests, Audioanalyse und Bundle-Prüfung ausführen.
7. Eine Test-IPA `3.2.0-rc1` veröffentlichen, ohne den AltStore-Feed zu ändern.
8. Alle Cues über die Bluetooth-Box und den iPhone-Lautsprecher prüfen.
9. Fehlerhafte Cues ersetzen und die Prüfung wiederholen.
10. Die finale IPA `3.2.0` bauen und erst dann den AltStore-Feed aktualisieren.
11. Änderungen dokumentieren, committen und pushen.

Die Web-App und deren Veröffentlichung bleiben auf Version 3.1.0 eingefroren.
