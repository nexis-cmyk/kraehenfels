# Audio V5: Quellen und Produktionsprompts

Stand: 12. August 2026. Zielversion: `3.2.0-rc1` für die native iPhone-App.

## Herkunft

Alle 20 Cues wurden für Krähenfels neu mit ElevenLabs Sound Effects v2 erzeugt. Es wurden keine fremden Pen-and-Paper-Soundbibliotheken und keine alten Platzhalter übernommen. Die gewählte Variante wurde als WAV mit 48 kHz oder als ursprüngliches MP3 geladen und anschließend lokal normalisiert. M01 und M02 wurden als echte 30-Sekunden-Quellen erzeugt, an der Schnittkante überblendet und auf vier beziehungsweise anderthalb Minuten verlängert.

Die Dateien unter `audio/generated/` und `app/Kraehenfels/Resources/Audio/` sind die geprüften Ausgaben. `_TMP/V5_candidates/` enthält nur lokale Arbeitsquellen und gehört nicht zum Release.

## Produktionsprompts

### Atmosphären

- **A01 Kutschenstraße:** `30 seconds continuous realistic 1890 Black Forest winter road at night. Steady wind through dense firs, powder snow sweeping a narrow road, quiet wooden carriage creaks, soft leather harness movement and restrained horses breathing at rest. Wide natural exterior stereo with slow variation. No break, gallop, voices, bell, music or boom. Start and end on the same steady wind texture for seamless editing.`
- **A02 Gasthaus:** `30 seconds continuous realistic interior ambience in a small 1890 Black Forest inn at night. Low hearth fire, soft timber settling, occasional ceramic cup touch, restrained chairs shifting and indistinct guests murmuring far away. Intimate warm room under winter tension, slow natural variation. No clear words, singing, laughter, footsteps, knocking, bell, music or dramatic hit. Begin and end on the same quiet room tone for seamless editing.`
- **A03 Dorf am Morgen:** `Seamless realistic winter morning in a tiny 1890 Black Forest village. Light wind between timber houses, sparse distant work, one cart wheel far away, melting snow and very few birds. No crowd, bell, voices, music or ominous drone.`
- **A04 Kirche ohne Glocke:** `30 seconds continuous realistic interior ambience inside an unheated stone village church in 1890 winter. Long cold stone reverb, faint wind leaking through old door seams, tiny wood contractions in pews and roof, and one distant raven muffled outside. Hollow sacred space with slow natural variation. No bell, organ, choir, speech, footsteps, heartbeat, music or impact. Begin and end with the same low room air for seamless editing.`
- **A05 Schmiede:** `Seamless realistic interior loop in a small 1890 blacksmith workshop between jobs. Steady coal forge fire, slow leather bellows breathing at intervals, soft metal cooling ticks, chain and tool rack settling, and a little winter air under the door. No hammer strike, repeated clanging, voices, horses, music or cinematic drone.`
- **A06 Waldspur:** `Seamless realistic deep winter pine forest in the Black Forest. Broad quiet wind passes through tall fir crowns, fine snow moves across the ground, one distant branch releases snow occasionally, and the space feels large and empty. No footsteps, breath, animals, voices, bell, music or horror drone.`
- **A07 Rathausarchiv:** `Seamless realistic cramped 1890 village archive after midnight. Loose paper shifts softly, an iron stove gives occasional cooling ticks, old floorboards settle, and muted winter wind presses against small closed windows. Dry intimate room perspective. No writing, page turning by a person, voices, clock, bell or music.`
- **A08 Alte Eiche:** `30 seconds continuous realistic winter night at an ancient hollow oak shrine in dense pines. Wind circles through the trunk, massive wood bends slowly, loose snow brushes exposed roots and one short iron shrine chain moves softly at rare intervals. Wide natural exterior stereo, tense but believable. No creature, breath, steps, bell, chant, music, drone or impact. Start and end on the same wind bed for seamless editing.`

### Musik

- **M01 Krähenfels-Motiv:** `30 seconds of restrained dark folk-horror underscore for quiet tabletop dialogue. A memorable two-note low cello motif, sparse felted upright piano notes, and a soft bowed folk drone in a cold wooden room. Slow, minimal, intimate, with no climax. No vocals, choir, drums, percussion, brass, synth lead, trailer boom or impact. Begin and end on the same held low texture for seamless editing.`
- **M02 Die Prozession:** `30 seconds of tense ritual-procession underscore for an 1890 Black Forest night. Slow low bowed strings, a sparse wooden pulse far behind the beat, muted frame-drum skin no louder than footsteps, and dry folk resonance. It must layer beneath a quieter cello theme and leave space for speech. No vocals, chant, lead melody, heavy drums, brass, synth or trailer impact. Begin and end on the same low texture for seamless editing.`

### Einzel-Cues

- **SFX01 Achse bricht:** `Close realistic Foley recording of a late-19th-century wooden carriage axle under load. First a short strained wooden creak, then one sharp solid timber crack with a few splinters and a brief light rattle of iron wheel fittings. Outdoor winter air, natural stereo perspective. No explosion, impact boom, music, voice or horse.`
- **SFX02 Pferde scheuen:** `Close realistic Foley of two harnessed carriage horses startled in deep snow. One abrupt frightened snort, one short hoof stamp into packed snow, leather harness pulls tight and metal tack jingles briefly. The horses stay in place. No galloping, crowd, carriage crash, music or human voice.`
- **SFX03 Riegel von außen:** `Close interior Foley of a heavy forged-iron door bolt being locked from outside an old wooden inn room. The iron bar scrapes sideways, passes clearly through two metal brackets, then lands with one firm final clunk. No key, modern latch, footsteps, voice, music or impact boom.`
- **SFX04 Geweih an der Tür:** `Close realistic Foley of a dry deer antler slowly scraping across an old wooden inn door, followed by exactly two separate light bone taps. Quiet interior night. No animal call, claws, fist, branch snap, voice, music or cinematic boom.`
- **SFX05 Ein Schmiedeschlag:** `Close realistic 1890 blacksmith Foley: exactly one medium hammer strike on a small piece of hot iron resting on a heavy anvil. Clear metal contact, short natural anvil ring, quiet coal forge room decay. No second strike, rhythm, explosion, music, voice or cinematic bass.`
- **SFX06 Atem hinter der Figur:** `Binaural close Foley of exactly one quiet human breath directly behind a standing listener in a cold winter forest. Intimate moist inhale and exhale, no words. No whisper, growl, animal, footsteps, wind gust, music or impact.`
- **SFX07 Prozessionsschritte:** `Ten seconds realistic close field recording: eight to twelve villagers walk together very slowly through fresh snow at night. Heavy leather boots compress snow in an uneven rhythm, wool coats brush, wooden antler masks creak softly and distant harness iron shifts once. No running, voices, chanting, music, drum, bell, wind roar, whoosh or impact.`
- **SFX08 Knochenhirsch:** `Close supernatural creature Foley in a snowy forest: a very large skeletal stag slowly lifts its head from the ground. One dry neck-joint articulation, compacted snow shifts under heavy weight, antler tips brush a branch, then one low hollow animal breath. No roar, growl, bones shattering, music or impact boom.`
- **SFX09 Bindung reißt:** `Close ritual Foley of an old binding failing under tension. Three leather straps stretch and creak against wrought iron, one strap tears, then one iron fastener snaps free and falls onto frozen earth. The strained resonance and pressure fade into quiet air. No explosion, magic blast, glass, voice or music.`
- **SFX10 Falscher Glockenschlag:** `Exactly one strike of a medium-sized late-19th-century iron village church bell heard from inside a cold stone nave. Clear metal attack and a long natural bell decay with subtle unsettling detuned beating. No second toll, clock chime, orchestra, voice or trailer boom.`

## Technische Verarbeitung

- Atmosphären und Musik: 48 kHz, Stereo, AAC/M4A, Zielwert etwa -25 LUFS; M01 etwa -27 LUFS.
- One-Shots: 48 kHz, Stereo, PCM/WAV, Zielwert etwa -18 LUFS bei maximal -1,5 dBTP.
- M01: 240 Sekunden. M02: 90 Sekunden.
- App-Selbsttest: eigener 880-Hz-Testton, nicht mit einem Spiel-Cue verwechselt.
- Letzter automatischer Lauf: 20 Dateien bestanden, keine exakten oder fast identischen Paare.

Die technische Prüfung ersetzt den Hörtest nicht. Vor dem finalen Release muss jeder Cue in der App einmal über den iPhone-Lautsprecher und einmal über die vorgesehene Bluetooth-Box bewertet werden.
