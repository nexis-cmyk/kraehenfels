# Kraehenfels audio rebuild master prompt

Diese Datei ist der Prompt, den du an eine andere KI, einen Audio-Service oder einen Sound-Designer geben kannst. Ziel ist ein kompletter Ersatz der aktuellen Platzhalter-Sounds.

Die App erwartet die bestehenden Dateinamen. Wenn der Audio-Service nur WAV exportieren kann, ist das okay. In dem Fall koennen wir die Dateien danach mit `tools/import_audio_replacements.py` ins richtige Format wandeln.

## Kopierprompt

```text
Create a complete replacement audio pack for a tabletop horror scenario called "Die Weisse Frau schweigt".

The setting is Kraehenfels, a small isolated Black Forest village in November 1890. The mood is cold, rural, haunted, grounded and intimate. This is not action fantasy. It should feel like old wood, wet stone, snow, bells, breath and silence at a real game table.

Important rules:
- Deliver separate audio files for every cue listed below.
- Use the exact target filename for each file.
- If exact file extensions are not possible, export clean WAV files with the same base name. The app team will convert them later.
- Use 48 kHz audio.
- Keep ambience and music controlled enough for people to talk over at a table.
- Ambience loops must be seamless.
- SFX one-shots need a clean start, no click, no watermark and no huge trailer impact.
- Do not use copyrighted melodies, named artists, named film scores or recognizable commercial sound design.
- Do not include understandable speech. Whispers are allowed only when the prompt says they must be unintelligible.
- Do not add random jump scares.
- Avoid generic "boom, whoosh, riser" sounds. The pack should sound like real locations and physical objects.

Global mix targets:
- Ambience: subtle, loopable, around 45 to 60 seconds.
- Music: sparse horror underscore, around 30 to 60 seconds.
- One-shot SFX: usually 2 to 8 seconds.
- Peak below -1 dB.
- No clipping.

Generate these files:

A01_Postkutsche_im_Schneesturm.m4a
Realistic 1890 horse carriage in a heavy winter storm. Wooden wheels creak, leather harness moves, muffled hooves hit snow, cold wind wraps around the carriage. Dark rural forest road. No speech, no music. Seamless loop, 50 seconds.

A03_Kraehenfels_bei_Tag.m4a
Small isolated Black Forest village in winter daylight. Cold wind between wooden houses, distant crows, chimney draft, sparse footsteps in snow. Uneasy quiet. No speech, no music. Seamless loop, 50 seconds.

A04_Wirtsstube_am_Abend.m4a
Old rural tavern interior in 1890. Fireplace crackle, wooden chairs, ceramic mugs, low indistinct room murmur with no understandable words, winter draft at the door. Tense but natural. No music. Seamless loop, 55 seconds.

A05_Dorf_nach_Mitternacht.m4a
Snow covered village after midnight. Very quiet. Winter wind presses against shutters, old beams creak in the distance, snow muffles everything. Isolated and tense. No speech, no music. Seamless loop, 55 seconds.

A06_Kapelle_und_Friedhof.m4a
Small rural chapel and graveyard at night in winter. Cold room tone, old roof beams settling, wind through cracks, faint bronze bell resonance in stone. No choir, no speech, no music. Seamless loop, 50 seconds.

A07_Weisse_Spur_im_Wald.m4a
Deep winter forest trail in the Black Forest. Close snow crunch, wind through fir trees, branches carrying snow, distant unexplained movement. Restrained and realistic. No roar, no speech, no music. Seamless loop, 50 seconds.

A08_Finale_Froststurm.m4a
Supernatural blizzard around an old church bell tower. Violent winter wind, ice stress cracking through wood and stone, low pressure rumble, distant distorted bronze resonance. Cinematic horror ambience, no melody, no speech. Seamless loop, 55 seconds.

A09_Grubenluft_Layer.m4a
Abandoned underground mine tunnel. Cold airflow through damp stone, distant water drops, low pressure tone, old timber supports creaking softly. Claustrophobic and realistic. No speech, no music. Seamless loop, 55 seconds.

A10_Frostspannung_Layer.m4a
Unnatural frost spreading through wood, glass and stone. Tiny ice cracks, crystalline stress sounds, thin high shimmer, subtle low cold drone. Close and unsettling. No melody, no speech. Seamless loop, 45 seconds.

M01_Ankunft_in_Kraehenfels.m4a
Sparse dark folk horror underscore for a winter village arrival in 1890. Low bowed strings, faint frame drum pulse, distant harmonium texture, slow and restrained. No recognizable melody, no speech. Seamless loop, 45 seconds.

M02_Das_Dorf_verschweigt_etwas.m4a
Restrained investigation tension underscore. Low bowed bass, muted piano notes, slow irregular pulses, quiet scraping texture. Uneasy but not loud. No jump scare, no speech. Seamless loop, 45 seconds.

M03_Die_Weisse_Frau_naht.m4a
Ghostly approach music for a pale woman in a winter village. Breathy textures, bowed glass, thin strings, distant wordless female-like tone with no lyrics. Fragile and cold. No speech. Seamless loop, 40 seconds.

M04_Ihr_altes_Lied.m4a
Old wordless folk lament fragment. Very soft female humming with no lyrics, winter air, distant room reverb. Fragile, old, sad and unsettling. No recognizable copyrighted melody. One-shot, 25 seconds.

M05_Frost_und_Opfer.m4a
Final ritual tension underscore. Low heartbeat pulse, bowed metal, cold string textures, distant nonverbal choir-like air, rising pressure without action rhythm. No words, no recognizable melody. Seamless loop, 45 seconds.

M06_Tauwetter_Epilog.m4a
Quiet unresolved thaw epilogue. Soft piano or dulcimer notes, distant melting water drops, cold room tone. Bittersweet but still uneasy. No speech, no recognizable melody. One-shot, 35 seconds.

SFX01_Achse_bricht.wav
Heavy wooden carriage axle breaking under load. Stressed wood creak, sudden splintering snap, low carriage jolt into packed snow. Realistic foley, no speech, no music. One-shot, 3 seconds.

SFX02_Pferde_scheuen.wav
Two startled carriage horses in winter. Short whinny, snorting breath, leather harness pulling tight, hooves scraping and slipping in snow. Realistic animal foley, no human voices, no music. One-shot, 4 seconds.

SFX03_Hufe_im_Schnee.wav
Horse hooves struggling and running through deep snow. Uneven rhythm, heavy close impacts, snow crunch and scatter, rural winter road. No speech, no music. One-shot, 4 seconds.

SFX04_Astbruch.wav
Large snow loaded tree branch cracking and falling nearby in a winter forest. Wood fibers split, snow dumps down, muffled impact on forest floor. Realistic, no speech, no music. One-shot, 3 seconds.

SFX05_Kraehen.wav
A few distant crows over a cold winter village. Sparse calls, natural valley reverb, realistic and bleak. No other loud animals, no speech, no music. One-shot, 6 seconds.

SFX06_Stille.wav
True digital silence for a sudden absence of ambience. No noise, no tone, no reverb, no speech, no music. One-shot, 2 seconds.

SFX07_Glocke_normal.wav
Single old bronze church bell strike in a small rural stone church. Close but natural, warm metal body, long realistic decay. No distortion, no music, no speech. One-shot, 7 seconds.

SFX08_Glocke_falsch.wav
Single old bronze church bell strike muffled by ice and fog. Wrong detuned overtones, cold unnatural resonance, long frozen decay, subtle horror tone. No cheap distortion, no speech, no music. One-shot, 8 seconds.

SFX09_Schmiede.wav
Small 1890 village blacksmith workshop. Coal forge, bellows breathing, hammer striking anvil, small metal clinks, wooden room tone. Realistic foley, no speech, no music. Seamless loop, 18 seconds.

SFX10_Metall_vibriert.wav
Close iron object or bell clapper touched once and vibrating too long. Metallic ring, low sympathetic vibration, unsettling but realistic. No speech, no music. One-shot, 4 seconds.

SFX11_Schritte.wav
Adult leather boots walking five slow steps through packed winter snow. Medium close perspective, varied crunch texture, rural night ambience tail. No speech, no music. One-shot, 4 seconds.

SFX12_Barfuss_Schritte.wav
Bare feet walking softly on cold wet stone and hard snow. Sticky quiet steps, unnatural timing, close perspective, unsettling but not loud. No speech, no music. One-shot, 4 seconds.

SFX13_Stimmen_ohne_Worte.wav
Distant human-like whispers and voices from deep mine tunnels. Layered echoes, completely unintelligible, no words, no names, damp stone reverb, subtle horror. No music. One-shot, 8 seconds.

SFX14_Schlaege_unter_Boden.wav
Three heavy subterranean knocks heard through old wooden floor and stone. Muffled impact, low resonance, irregular spacing, close interior perspective. No speech, no music. One-shot, 4 seconds.

SFX15_Atem_hinter_dir.wav
Close cold breath directly behind the listener. One quiet inhale and exhale, slight cloth movement, intimate and frightening. No voice, no words, no music. One-shot, 3 seconds.

SFX16_Weisse_Frau_Motiv.wav
Two thin descending glass and metal tones. Ghostly signature motif, fragile cold shimmer, short decay. No melody beyond the two tones, no speech, no music bed. One-shot, 3 seconds.

SFX17_Kloeppel_schlaegt.wav
Single iron bell clapper striking an old bronze bell by itself. Close metal impact, large bell body resonance, empty church tower reverb. No speech, no music. One-shot, 6 seconds.

SFX18_Frost_breitet_sich_aus.wav
Frost rapidly spreading across wood, glass and stone. Tiny ice crystals cracking, close surface tension, low cold pressure underneath. Realistic with a supernatural edge, no speech, no music. One-shot, 6 seconds.

SFX19_Herzschlag.wav
Slow muted human heartbeat heard through ice and old floorboards. Soft organic thump, cold room resonance, unsettling and restrained. Not a kick drum, no speech, no music. Seamless loop, 8 seconds.

SFX20_Eisbruch.wav
Thick ice sheet breaking violently. Deep crack spreading, sharp ice shards, brief water surge underneath, large but realistic impact. No speech, no music. One-shot, 5 seconds.

SFX21_Bannung.wav
Supernatural release after a successful banishment. Cold pressure tone dissolves, air returns to the room, faint thawing drip. Restrained relief, no triumphant music, no speech. One-shot, 6 seconds.

SFX22_Scheitern.wav
Failed banishment horror sting. Sudden pressure drop, distorted distant bell resonance, cold burst of wind, low impact without explosion. Frightening but not cartoonish, no speech, no music. One-shot, 6 seconds.

SFX23_Fensterladen_im_Wind.wav
Loose wooden window shutter banging in winter wind. Two or three irregular impacts, old house exterior, cold air gusts, realistic wood detail. No speech, no music. One-shot, 4 seconds.

SFX24_Fernes_Laeuten.wav
Several distant church bell strokes across a snowy valley at night. Soft and heavily reverberant, hard to locate, old bronze tone. No speech, no music. One-shot, 12 seconds.

SFX25_Holz_unter_Spannung.wav
Old wooden beams flexing under heavy strain. Deep timber groan, small fiber creaks, slow pressure build, close interior perspective. No collapse, no speech, no music. One-shot, 5 seconds.

SFX26_Wasser_im_Flutstollen.wav
Water in an old underground flood tunnel. Shallow flow over stone, scattered drips, damp mine reverb, cold and close. Realistic ambience layer, no speech, no music. Seamless loop, 18 seconds.

SFX27_Wiederhallende_Schritte.wav
Footsteps in a mine tunnel followed by delayed unnatural echoes. Echo timing slightly wrong, damp stone reflections, one walker only. Tense and realistic, no speech, no music. One-shot, 7 seconds.

SFX28_Klopfen_unter_Boden.wav
Close knocking from beneath old floorboards. Three or four taps, wooden surface detail with deep space underneath, quiet room tail. No speech, no music. One-shot, 4 seconds.

SFX29_Glockenresonanz.wav
Old bell resonance detuning and bending unnaturally. Beating metal overtones, low subharmonic under the decay, cold stone tower reverb. No speech, no music. One-shot, 8 seconds.

SFX30_Atem_im_Raum.wav
Brief breath in an otherwise empty cold room. Medium distance, small reverb tail, barely human. No words, no speech, no music. One-shot, 3 seconds.

SFX31_Resonanzabbruch.wav
Sustained old bell resonance suddenly cut off into dead silence. Tiny room tail before the cutoff, supernatural pressure drop. No explosion, no speech, no music. One-shot, 5 seconds.

Before delivery, check:
- Every listed file exists.
- All filenames match exactly.
- Loops do not click at the loop point.
- No file contains watermark audio.
- No file contains understandable speech.
- No file clips.
- SFX06 is true silence.
```

## Wenn der Service nur einzeln generiert

Dann zuerst diese Gruppe machen:

```text
A01_Postkutsche_im_Schneesturm.m4a
A03_Kraehenfels_bei_Tag.m4a
A04_Wirtsstube_am_Abend.m4a
A05_Dorf_nach_Mitternacht.m4a
A06_Kapelle_und_Friedhof.m4a
A07_Weisse_Spur_im_Wald.m4a
A08_Finale_Froststurm.m4a
A09_Grubenluft_Layer.m4a
A10_Frostspannung_Layer.m4a
```

Danach die Musik:

```text
M01_Ankunft_in_Kraehenfels.m4a
M02_Das_Dorf_verschweigt_etwas.m4a
M03_Die_Weisse_Frau_naht.m4a
M04_Ihr_altes_Lied.m4a
M05_Frost_und_Opfer.m4a
M06_Tauwetter_Epilog.m4a
```

Danach die wichtigsten Effekte:

```text
SFX01_Achse_bricht.wav
SFX02_Pferde_scheuen.wav
SFX07_Glocke_normal.wav
SFX08_Glocke_falsch.wav
SFX09_Schmiede.wav
SFX12_Barfuss_Schritte.wav
SFX13_Stimmen_ohne_Worte.wav
SFX14_Schlaege_unter_Boden.wav
SFX15_Atem_hinter_dir.wav
SFX20_Eisbruch.wav
SFX31_Resonanzabbruch.wav
```

Den Rest danach auffuellen. Genau diese Reihenfolge bringt am schnellsten einen hoerbaren Unterschied am Spieltisch.
