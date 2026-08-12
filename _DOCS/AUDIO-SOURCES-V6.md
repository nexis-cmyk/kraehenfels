# Audio V6: Quellen und Cue-Übergabe

Stand: 12. August 2026. Zielversion: `3.3.0-rc1`.

Die acht im Hörtest passenden Dateien bleiben unverändert: A03, A04, A06, A07, M01, M02, SFX03 und SFX07. Die folgende Liste beschreibt die zwölf Ersatzdateien. Sie wurden lokal aus den vorhandenen Quellen zusammengesetzt. Es ist kein externer Download zur Laufzeit nötig.

| Cue | Datei | Was im Spiel zu hören sein soll | Erzeugung / Prompttext |
| --- | --- | --- | --- |
| A01 | `V6_A01_Kutschenstrasse.m4a` | Winterwind, Wagenholz, Geschirr und unruhige Pferde auf der Nachtstraße | "realistische nächtliche Postkutsche im Schwarzwald, Wind an den Scheiben, Holzfedern, Lederzeug und Pferdeatem, keine Stimmen, ruhige Endlosschleife" |
| A02 | `V6_A02_Gasthaus.m4a` | Herdfeuer, Gebälk, Geschirr und undeutliche Gäste im Hintergrund | "warme, aber misstrauische Wirtsstube um 1890, leises Herdfeuer, altes Holz, einzelne Teller, entfernte unverständliche Stimmen, keine Melodie" |
| A05 | `V6_A05_Schmiede.m4a` | Tiefe Esse, Resonanzraum und einzelne Metallarbeit | "kleine Schwarzwaldschmiede bei Nacht, tiefer Ofen, Blasebalg, Metallhall und einzelne weit auseinanderliegende Hammerschläge, keine Sprache" |
| A08 | `V6_A08_Alte_Eiche.m4a` | Froststurm, hohler Stamm, arbeitendes Holz und lose Eisenkette | "Waldheiligtum im Froststurm, hohler uralter Stamm, Schnee an Wurzeln, langsames Holzknarren, lose Eisenkette, keine Musik und keine Stimmen" |
| SFX01 | `V6_SFX01_Achse_bricht.wav` | Ein harter Holzbruch, Geschirr scheppert, der Wagen kippt | "ein einzelner kurzer Kutschenunfall: angesägte Holzachse bricht, Metall und Geschirr scheppern, kein langer Absturz, keine Stimmen" |
| SFX02 | `V6_SFX02_Pferde_scheuen.wav` | Zwei Hufschläge, erschrockenes Schnauben und straffes Geschirr | "zwei kurze Pferdehufschläge im Schnee, erschrockenes Schnauben, gespanntes Zaumzeug, kein Galopp und kein Wiehern" |
| SFX04 | `V6_SFX04_Geweih_an_der_Tuer.wav` | Holz knarrt, ein harter Rand kratzt zweimal über die Tür | "unheimliches Geweih streift eine alte Holztür: ein Knarren, zweimal trockenes Kratzen, danach Stille, kein Monsterlaut" |
| SFX05 | `V6_SFX05_Einzelner_Schmiedeschlag.wav` | Genau ein sauberer Hammerhieb auf heißes Eisen | "genau ein einzelner Schmiedehammer auf glühendes Eisen, kurzer heller Ambossring, kein Rhythmus, keine weiteren Schläge" |
| SFX06 | `V6_SFX06_Atem_hinter_der_Figur.wav` | Ein einzelner naher Atemzug ohne Wort | "ein einziger menschlicher Atemzug direkt hinter dem Zuhörer, sehr nah, trocken, ohne Stimme, ohne Musik" |
| SFX08 | `V6_SFX08_Knochenhirsch.wav` | Gelenk, schweres Gewicht im Schnee, trockenes Holz und hohler Atem | "erster vollständiger Anblick eines übernatürlichen Knochenhirsches: ein trockenes Gelenk, Gewicht im Schnee, Holzknacken und ein hohler Atemzug, kein Brüllen" |
| SFX09 | `V6_SFX09_Bindung_reisst.wav` | Gespannte Resonanz bricht ab, Eisen springt frei, Druck fällt | "eine überdehnte magische Eisenbindung reißt in einem kurzen Moment, Metall springt frei, tiefe Resonanz bricht abrupt ab, kein Donner" |
| SFX10 | `V6_SFX10_Falscher_Glockenschlag.wav` | Ein einzelner tiefer, leicht verstimmter Glockenschlag | "ein einzelner historischer Glockenschlag aus großer Entfernung, leicht verstimmt und unnatürlich schwebend, kein Nachschlag" |

Die V6-Dateien werden mit 48 kHz, Stereo, Zielpegel und einem True-Peak-Limit für die iPhone- und Bluetooth-Ausgabe ausgegeben. Die technische Prüfung steht in [`AUDIO-V6-QA.md`](AUDIO-V6-QA.md). Der Hörtest in der App bleibt die letzte Entscheidung: Wenn eine Datei am Tisch falsch wirkt, wird sie dort mit "Falsch" markiert und vor dem Release ersetzt.
