# Krähenfels – Release-Audit 25

Stand: 13. August 2026 · geprüfter Stand: `3.3.0-rc1`

Dieser Audit prüft Repository, Content-Graph, SwiftUI-Leitstand, Audio-Metadaten, Druckpaket und Release-Pipeline als zusammenhängendes Spiel. Die Bewertung bezieht sich auf den Stand vor den Änderungen dieser Arbeitsrunde.

## A. Gesamtbewertung

| Bereich | Stand | Begründung |
| --- | ---: | --- |
| Technik | 8/10 | Content- und Audio-Validatoren bestehen; native Kompilierung läuft auf GitHub/macOS, nicht lokal auf Windows. |
| Story | 8/10 | Alle acht Szenen sind vom Start erreichbar; Pflichtspuren besitzen Fallbacks. |
| NPCs | 7/10 | Sechs Dossiers sind vorhanden, aber Auftreten, Wissen und mögliche Handouts waren im Ablauf nicht überall direkt sichtbar. |
| Gameplay | 6/10 | W100-Helfer und geführte Szenen existieren; die finale Zwei-Erfolge-vor-zwei-Fehlschläge-Regel wurde bisher nicht als Zustand geführt. |
| Spielleiter-Unterstützung | 7/10 | Rollenlabels und Schnellzugriffe sind vorhanden; Soundplan und Vorlesen-Übergang brauchen einen bestätigten Ablauf. |
| Sounds | 8/10 technisch / 6/10 am Tisch | 20 Dateien, gültige Formate und keine Duplikate; der technische Test ersetzt keinen echten Hörtest. Einige Szenen-Cues waren nur im Manifest, nicht im Schritt sichtbar. |
| Bilder | 8/10 | Karten und Szenenbilder sind im nativen Bundle vorhanden; Handout-PDFs sind Druckmaterial und wurden in der App bisher nur als Dateiname angezeigt. |
| UI/UX | 7/10 | Safe-Area-Abstand und Scroll-Hinweise sind gesetzt; Eingabefehler im Würfelhelfer und freie Szenensprünge waren nicht klar genug. |
| Release-Bereitschaft | 8/10 | IPA-Build und GitHub-Pages-Mirror wurden erfolgreich geprüft; der Feed-Generator verwendete für künftige Releases noch die CDN-URL. |

## B. Gefundene Blocker (P0)

Im geprüften Stand wurde kein P0 gefunden. `validate_project.py`, `validate_audio_v6.py`, Python-Compile und `git diff --check` liefen erfolgreich. Die letzte native IPA wurde auf GitHub/macOS gebaut und als ZIP-IPA verifiziert.

## C. Kritische Probleme (P1)

1. **Finale-Probe war nur beschrieben, nicht geführt.** `S07_DANGER` nennt „zwei Erfolge vor zwei Fehlschlägen“, aber der Zustand zählte vorher nur den letzten Wurf und sprang nach jeder Auswertung weiter. Dadurch konnte die Regel am Tisch nicht korrekt umgesetzt werden.
2. **Vorlesen und Sound waren getrennte Bedienhandlungen.** Ein Schritt zeigte einen Audio-Cue, startete ihn aber nicht nach einer Bestätigung zusammen mit dem Vorlesemoment. Der gewünschte Ablauf „vorbereiten → bestätigen → vorlesen“ fehlte.
3. **Audio-Plan war nicht vollständig im aktuellen Schritt erreichbar.** Szenen wie Kirche, Waldspur und Prozession hatten im Manifest korrekt geplante Cues, die aber nicht alle als direkte Spielleiter-Aktion im Leitstand erschienen.
4. **Würfelhelfer akzeptierte ungültige Eingaben still.** Leere, nicht numerische oder außerhalb von 1–100 liegende Werte erzeugten keine sichtbare Rückmeldung.
5. **Künftige Release-Feeds konnten wieder auf GitHub-CDN zeigen.** `tools/update_altstore_feed.py` erzeugte weiterhin `releases/download/...`; der aktuelle dauerhafte Feed nutzt zwar den Pages-Mirror, aber der Generator war nicht konsistent.

## D. Story- und Logikprüfung

Der Story-Graph `S01 → S02 → S03/S04/S05 → S06 → S07 → S08` ist vollständig erreichbar. Die Archiv-Option wird erst nach zwei Ermittlungsorten angeboten. Pflicht-Hinweise sind in der App unabhängig von Proben vorgesehen und besitzen Text-Fallbacks.

Gefundene kleinere Klarheitsprobleme:

- `S05_NEXT` heißt „Archiv oder Eiche“, bietet aber bewusst noch keine direkte Eiche-Option. Die Beschreibung erklärt das, der Titel war trotzdem missverständlich.
- S02 listet H02 im Manifest, während der geführte Schritt zuerst H03 zeigt. H02 ist ein optionaler Zeitungsbeleg und darf nicht als notwendige Spur behandelt werden; der Leitstand muss das ausdrücklich zeigen.
- Die manuelle Szenenliste erlaubt weiterhin einen GM-Sprung. Das ist nützlich für Wiedereinstieg und Tests, muss aber sichtbar als Abkürzung und nicht als normaler Auslöser gekennzeichnet werden.

## E. NPC-Prüfung

Alle sechs NPCs (Gruber, Elara, Elias, Falk, Marta und Leni) haben Rolle, Wissen, Verschwiegenes, Haltungszustände und mögliche Handouts. Die Orts- und Szenen-IDs stimmen mit dem Manifest überein.

Verbesserungsbedarf lag nicht in fehlenden Daten, sondern in der Tischführung: Ein NPC-Dossier war nur über den zentralen Materialien-Bereich erreichbar. Der Schritt selbst braucht daher direkte NPC-Verknüpfungen und eine kurze „wenn ignoriert“-Alternative. Die geführten Schritte enthalten diese Verknüpfungen nun als Teil der Überarbeitung.

## F. Hinweise und Gegenstände

Die elf Hinweise C01–C11 sind mit Fundort, Handout/Fallback und Fakten verknüpft. F04 verlangt C06+C07+C08; F05 verlangt C09+C10. Die Pflichtketten können nicht durch einen einzelnen Fehlschlag blockiert werden.

Die wichtigste praktische Lücke war die App-Darstellung: Ein Handout konnte bisher als Titel und Dateiname geöffnet werden, nicht als direkt sichtbare Druckansicht. Bis die PDFs als native Bundle-Ressourcen aufgenommen werden, bleibt der exakt formulierte Papier-Fallback der sichere Offline-Weg.

## G. Würfelmechaniken

Der Leitstand verwendet einheitlich W100 ≤ Zielwert. Kritischer Erfolg liegt im unteren Zehntel, kritischer Misserfolg bei `90 + ein Zehntel` bis 100; Begabungsproben erhalten keinen kritischen Erfolg. Die Kurzregeln decken Geistesblitz, Initiative, Angriff, Parade, Schaden und LP ab.

Vor der Überarbeitung waren die Zielwerte und Modifikatoren zwar erklärt, aber die Eingabemaske hatte keine Fehleranzeige und das Finale keinen Mehrwurf-Zustand. Das wird in dieser Runde behoben. Für Kampfmodus bleibt die App bewusst ein Kurzreferenz-/Tracker-Einstieg; die eigentlichen Gegnerwerte müssen im Abenteuertext stehen und werden nicht erfunden.

## H. Sound-Audit

20 native Cues existieren, alle Manifest-Dateien sind vorhanden, technisch lesbar und ohne exakte Duplikate. V6 ersetzt zwölf zuvor beanstandete Dateien. Die Audio-Plan-Reihenfolge entspricht den Szenen-IDs.

Am Tisch ist weiterhin eine Hörprobe nötig. Inhaltlich auffällig war vor allem die Sichtbarkeit: `SFX10` (falscher Glockenschlag), `SFX06` (Atem) und der Prozessions-Layer M02 waren im Manifest geplant, aber nicht immer als aktueller Schritt sichtbar. Die App zeigt nach der Überarbeitung den kompletten Szenenplan mit Start-/Stop-Hinweis und Einzelabspielknopf.

## I. Bilder und Assets

Die zwölf Kartenvarianten und acht Szenenbilder sind im App-Bundle und werden über `SceneArtView` geladen. Der Cross-Reference-Check findet keine fehlenden nativen Art- oder Audio-Dateien. Die zehn Handout-Assets sind als Druck-PDFs im Ausgabe-/Druckpaket definiert, nicht als App-Bundle-Dateien; die App zeigt daher einen Papier-Fallback statt eines defekten Links.

## J. UI/UX

Der Root-Scroll nutzt Safe-Area-Padding plus eine eigene Audio-Leiste. Das bekannte „unten nicht erreichbar“-Problem ist im Code berücksichtigt; die langen Leitstand-Ansichten verwenden denselben Abstand. Verbesserungsbedarf bestand bei:

- sichtbarer Validierung im Würfelhelfer,
- eindeutigem Bestätigungsablauf für Vorlesen + Sound,
- direktem Szenen-Audio-Plan,
- Kennzeichnung von GM-Sprüngen und optionalen Handouts.

## K. Änderungen dieser Arbeitsrunde

- geführter Vorlese-/Sound-Dialog mit „Starten und vorlesen“ sowie „nur markieren“,
- Szenen-Audio-Plan direkt im Leitstand,
- echte Fortschrittszählung der finalen Gefahrenszene,
- Eingabevalidierung und verständliche Fehlermeldungen im W100-Helfer,
- konsistenter Pages-Download im AltStore-Feed-Generator,
- zusätzliche Cross-Reference- und Gameplay-Tests.

## L. Zwei-Wochen-Plan

### Woche 1 – Spielbarkeit sichern

1. Geführten Start, alle acht Szenen und drei Enden auf zwei Geräten durchspielen.
2. Finale-Mehrwürfe, Rücksprung und Wiederaufnahme nach App-Neustart prüfen.
3. Jeden Audio-Cue über iPhone und Box bewerten; falsch markierte Dateien ersetzen.
4. Handout-/Karten-Drucke mit den App-IDs abgleichen.

### Woche 2 – Feinschliff und Release

1. GitHub/macOS-Testlauf, IPA-Hash, Pages-Mirror und AltStore-Feed erneut prüfen.
2. Lange Texte, kleine Displays, VoiceOver-Labels und Scroll-Enden testen.
3. Tischprobe mit drei Spielern; nur echte Blocker nachbessern.
4. Release-Notizen, Druckpaket und endgültige Installationsanleitung aktualisieren.

