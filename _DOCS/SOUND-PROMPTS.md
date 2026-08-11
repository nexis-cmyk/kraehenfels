# Kraehenfels sound prompt catalog

Status: Die vorhandenen Dateien sind technisch gueltige Platzhalter. Sie wurden prozedural erzeugt, also aus Rauschen, Sinuswellen, einfachen Huellen und FFmpeg-Exporten. Das erklaert den "Bumm, Tsch"-Eindruck. Fuer die Runde brauchen wir fuer die meisten Cues echte Foley-Quellen oder AI-generierte Audioquellen, danach Schnitt, Looping, Lautheit und Einbau in die App.

Die Prompts sind auf Englisch formuliert, weil viele Audio-Generatoren damit besser arbeiten. Keine Prompts nennen ein reales Werk, einen Komponisten oder eine bekannte Aufnahme.

## Technische Zielwerte

- Ambience: 45 bis 60 Sekunden, seamless loop, unaufdringlich, 48 kHz WAV oder M4A.
- Musik: 30 bis 60 Sekunden, loop oder one-shot wie in der App, keine erkennbare Fremdmelodie.
- SFX: 2 bis 8 Sekunden, one-shot, trocken genug, damit die App selbst mischen kann.
- Sprache: keine verstaendlichen Worte, ausser wir entscheiden spaeter bewusst etwas anderes.
- Mix: lieber leiser und sauber als uebertrieben. Am Tisch sollen die Spieler sprechen koennen.

## Empfohlener Ersatzweg

1. Ambience und Musik zuerst ersetzen. Das gibt der Runde sofort mehr Atmosphaere.
2. Danach die zehn wichtigsten SFX ersetzen: Achse, Pferde, Glocken, Schmiede, Schritte, Stimmen, Klopfen, Atem, Eisbruch, Resonanzabbruch.
3. Jede neue Datei unter exakt demselben Dateinamen exportieren, damit App und Manifest nicht umgebaut werden muessen.
4. Jede Datei nach dem Import einmal im Browser und einmal auf dem iPhone testen.

## Ambience

### A01 - Postkutsche im Schneesturm

Datei: `A01_Postkutsche_im_Schneesturm.m4a`

Soll klingen wie: Eine geschlossene Postkutsche auf einer verschneiten Waldstrasse um 1890. Holz, Leder, Pferdegeschirr, dumpfe Raeder, Wind und Schnee sollen fuehlbar sein, aber keine Musik und keine Stimmen.

Prompt: `Realistic 1890 horse carriage in a heavy winter storm, wooden wheels creaking, leather harness movement, muffled hooves in snow, cold wind around the carriage, dark rural forest road, no speech, no music, seamless loop, 50 seconds, 48 kHz.`

### A03 - Kraehenfels bei Tag

Datei: `A03_Kraehenfels_bei_Tag.m4a`

Soll klingen wie: Ein kleines Schwarzwalddorf im Winter, tagsueber, aber unangenehm still. Man hoert Wind zwischen Haeusern, ferne Kraehen, Kaminzug und vereinzelte Schritte auf Schnee.

Prompt: `Small isolated Black Forest village in winter daylight, cold wind between wooden houses, distant crows, chimney draft, sparse footsteps in snow, uneasy silence, realistic field recording feel, no speech, no music, seamless loop, 50 seconds, 48 kHz.`

### A04 - Wirtsstube am Abend

Datei: `A04_Wirtsstube_am_Abend.m4a`

Soll klingen wie: Eine warme, alte Wirtsstube, die trotzdem nicht freundlich wirkt. Feuer, Holz, Kruege, Stuehle und ein sehr leises, unverstaendliches Murmeln im Hintergrund.

Prompt: `Old rural tavern interior in 1890, fireplace crackle, wooden chairs, ceramic mugs, low indistinct room murmur with no understandable words, door draft from winter outside, tense but natural, no music, seamless loop, 55 seconds, 48 kHz.`

### A05 - Dorf nach Mitternacht

Datei: `A05_Dorf_nach_Mitternacht.m4a`

Soll klingen wie: Kraehenfels nach Mitternacht. Fast leer. Wind drueckt gegen Fensterlaeden, Schnee schluckt alles, und ab und zu wirkt es, als wuerde irgendwo Holz arbeiten.

Prompt: `Snow covered rural village after midnight, very quiet, winter wind pressing against shutters, distant wooden beams creaking, soft snow ambience, isolated and tense, no speech, no music, seamless loop, 55 seconds, 48 kHz.`

### A06 - Kapelle und Friedhof

Datei: `A06_Kapelle_und_Friedhof.m4a`

Soll klingen wie: Eine kleine Kapelle mit Friedhof bei Nacht. Kalte Raumluft, Holz im Dachstuhl, leiser Wind durch Ritzen und ein kaum merklicher Nachhall alter Glocken.

Prompt: `Small rural chapel and graveyard at night in winter, cold interior room tone, old roof beams settling, wind through cracks, faint distant bronze bell resonance in the stone, no choir, no speech, no music, seamless loop, 50 seconds, 48 kHz.`

### A07 - Weisse Spur im Wald

Datei: `A07_Weisse_Spur_im_Wald.m4a`

Soll klingen wie: Ein Waldpfad im tiefen Schnee. Nahe Schneeschritte, Tannen im Wind, Aeste unter Last und eine Bewegung in der Ferne, die man nicht eindeutig zuordnen kann.

Prompt: `Deep winter forest trail in the Black Forest, close snow crunch footsteps, wind through fir trees, branches under snow weight, distant unexplained movement, realistic and restrained, no monster roar, no speech, no music, seamless loop, 50 seconds, 48 kHz.`

### A08 - Finale im Froststurm

Datei: `A08_Finale_Froststurm.m4a`

Soll klingen wie: Ein uebernatuerlicher Schneesturm beim Finale. Wind, Eisstress, tiefer Druck, Metallresonanz vom Glockenturm und ein Gefuehl, dass der Ort gleich reisst.

Prompt: `Supernatural blizzard around an old church bell tower, violent winter wind, ice stress cracking through wood and stone, low pressure rumble, distant distorted bronze resonance, cinematic horror ambience, no melody, no speech, seamless loop, 55 seconds, 48 kHz.`

### A09 - Grubenluft Layer

Datei: `A09_Grubenluft_Layer.m4a`

Soll klingen wie: Kalte Luft in einem verlassenen Stollen. Feuchter Stein, Tropfen, tiefer Luftzug und Holzstuetzen, die zu lange gehalten haben.

Prompt: `Abandoned underground mine tunnel, cold airflow through damp stone, distant water drops, low pressure tone, old timber supports creaking softly, claustrophobic and realistic, no speech, no music, seamless loop, 55 seconds, 48 kHz.`

### A10 - Frostspannung Layer

Datei: `A10_Frostspannung_Layer.m4a`

Soll klingen wie: Frost, der unnatuerlich schnell in Holz, Glas und Stein kriecht. Kleine Risse, kristalline Spannung und ein duenner hoher Ton, der unangenehm nahe ist.

Prompt: `Unnatural frost spreading through wood, glass and stone, tiny ice cracks, crystalline stress sounds, thin high shimmer, subtle low cold drone, close and unsettling, no melody, no speech, seamless loop, 45 seconds, 48 kHz.`

## Musik

### M01 - Ankunft in Kraehenfels

Datei: `M01_Ankunft_in_Kraehenfels.m4a`

Soll klingen wie: Zurueckhaltende Folk-Horror-Musik fuer die Ankunft. Dunkle Streicher, wenig Bewegung, kein Heldenthema.

Prompt: `Sparse dark folk horror underscore for a winter village arrival in 1890, low bowed strings, faint frame drum pulse, distant harmonium texture, slow and restrained, no recognizable melody, no speech, seamless loop, 45 seconds, 48 kHz.`

### M02 - Das Dorf verschweigt etwas

Datei: `M02_Das_Dorf_verschweigt_etwas.m4a`

Soll klingen wie: Ermittlungsdruck unter der Oberflaeche. Langsame tiefe Toene, leise Reibung, kleine Impulse, aber kein Jumpscare.

Prompt: `Restrained investigation tension underscore, low bowed bass, muted piano notes, slow irregular pulses, quiet scraping texture, uneasy but not loud, no jump scare, no speech, seamless loop, 45 seconds, 48 kHz.`

### M03 - Die Weisse Frau naht

Datei: `M03_Die_Weisse_Frau_naht.m4a`

Soll klingen wie: Die Praesenz der Weissen Frau rueckt naeher. Hauchige Flaechen, Glas, leise Streicher, vielleicht eine Stimme ohne Worte, aber nichts Verstaendliches.

Prompt: `Ghostly approach music for a pale woman in a winter village, breathy textures, bowed glass, thin strings, distant wordless female-like tone with no lyrics, fragile and cold, no speech, seamless loop, 40 seconds, 48 kHz.`

### M04 - Ihr altes Lied

Datei: `M04_Ihr_altes_Lied.m4a`

Soll klingen wie: Ein altes Lied, aber ohne echte Worte. Es darf sich wie eine Erinnerung anfuehlen, nicht wie ein sauber gesungener Song.

Prompt: `Old wordless folk lament fragment, very soft female humming with no lyrics, winter air, distant room reverb, fragile and old, unsettling but sad, no recognizable copyrighted melody, one-shot, 25 seconds, 48 kHz.`

### M05 - Frost und Entscheidung

Datei: `M05_Frost_und_Opfer.m4a`

Soll klingen wie: Finale Spannung fuer die Entscheidung. Tiefer Puls, Metall, kalte Flaechen, Druck im Raum. Keine Action-Musik, eher Ritual und Panik.

Prompt: `Final ritual tension underscore, low heartbeat pulse, bowed metal, cold string textures, distant nonverbal choir-like air, rising pressure without action rhythm, no words, no recognizable melody, seamless loop, 45 seconds, 48 kHz.`

### M06 - Tauwetter

Datei: `M06_Tauwetter_Epilog.m4a`

Soll klingen wie: Ein kurzes Nachspiel nach dem Horror. Tauwasser, leiser Raum, ein bittersuesser musikalischer Rest, der nicht komplett gut ausgeht.

Prompt: `Quiet unresolved thaw epilogue, soft piano or dulcimer notes, distant melting water drops, cold room tone, bittersweet but still uneasy, no speech, no recognizable melody, one-shot, 35 seconds, 48 kHz.`

## SFX

### SFX01 - Achse bricht

Datei: `SFX01_Achse_bricht.wav`

Soll klingen wie: Die Holzachse der Postkutsche gibt unter Last nach. Erst Knarzen, dann harter Splitterbruch, dann dumpfer Ruck im Schnee.

Prompt: `Heavy wooden carriage axle breaking under load, stressed wood creak, sudden splintering snap, low carriage jolt into packed snow, realistic foley, no speech, no music, one-shot, 3 seconds, 48 kHz WAV.`

### SFX02 - Pferde scheuen

Datei: `SFX02_Pferde_scheuen.wav`

Soll klingen wie: Zwei erschrockene Pferde direkt vor der Kutsche. Schnauben, kurzes Wiehern, Lederzeug, Hufe rutschen im Schnee.

Prompt: `Two startled carriage horses in winter, short whinny, snorting breath, leather harness pulling tight, hooves scraping and slipping in snow, realistic animal foley, no human voices, no music, one-shot, 4 seconds, 48 kHz WAV.`

### SFX03 - Hufe im Schnee

Datei: `SFX03_Hufe_im_Schnee.wav`

Soll klingen wie: Hufe, die im tiefen Schnee unregelmaessig losbrechen. Nah, schwer, etwas chaotisch.

Prompt: `Horse hooves struggling and running through deep snow, uneven rhythm, heavy close impacts, snow crunch and scatter, rural winter road, no speech, no music, one-shot, 4 seconds, 48 kHz WAV.`

### SFX04 - Astbruch hinter der Kutsche

Datei: `SFX04_Astbruch.wav`

Soll klingen wie: Ein grosser Ast bricht unter Schnee direkt hinter den Spielern. Holzfasern, Schnee, Aufprall im Wald.

Prompt: `Large snow loaded tree branch cracking and falling nearby in a winter forest, wood fibers splitting, snow dumping, muffled impact on forest floor, realistic, no speech, no music, one-shot, 3 seconds, 48 kHz WAV.`

### SFX05 - Ferne Kraehen

Datei: `SFX05_Kraehen.wav`

Soll klingen wie: Ein paar ferne Kraehen ueber dem Dorf. Kalt, spaerlich, nicht cartoonhaft.

Prompt: `A few distant crows over a cold winter village, sparse calls, natural valley reverb, realistic and bleak, no other animals, no speech, no music, one-shot, 6 seconds, 48 kHz WAV.`

### SFX06 - Ploetzliche Stille

Datei: `SFX06_Stille.wav`

Soll klingen wie: Eigentlich gar nicht. Das ist ein Spielleiter-Cue, bei dem die App die Atmosphaere kurz hart wegnehmen sollte.

Prompt: `True digital silence for a sudden absence of ambience, no noise, no tone, no reverb, no speech, no music, one-shot, 2 seconds, 48 kHz WAV.`

### SFX07 - Glocke normal

Datei: `SFX07_Glocke_normal.wav`

Soll klingen wie: Eine alte Bronzeglocke in einer kleinen Dorfkirche. Einzelner Schlag, natuerlicher Nachhall.

Prompt: `Single old bronze church bell strike in a small rural stone church, close but natural, warm metal body, long realistic decay, no distortion, no music, no speech, one-shot, 7 seconds, 48 kHz WAV.`

### SFX08 - Glocke aus dem Eis

Datei: `SFX08_Glocke_falsch.wav`

Soll klingen wie: Dieselbe Glocke, aber durch Eis und Nebel falsch gemacht. Dumpfer Anfang, verstimmte Obertone, langer kalter Nachhall.

Prompt: `Single old bronze church bell strike muffled by ice and fog, wrong detuned overtones, cold unnatural resonance, long frozen decay, subtle horror tone, no cheap distortion, no speech, no music, one-shot, 8 seconds, 48 kHz WAV.`

### SFX09 - Schmiedefeuer und Amboss

Datei: `SFX09_Schmiede.wav`

Soll klingen wie: Eine kleine Dorfschmiede. Kohlefeuer, Blasebalg, Hammer auf Amboss, Metallbewegung.

Prompt: `Small 1890 village blacksmith workshop, coal forge, bellows breathing, hammer striking anvil, small metal clinks, wooden room tone, realistic foley, no speech, no music, seamless loop, 18 seconds, 48 kHz WAV.`

### SFX10 - Metall vibriert

Datei: `SFX10_Metall_vibriert.wav`

Soll klingen wie: Ein Eisenstueck oder Glockenkloeppel wird beruehrt und schwingt zu lange nach. Nah, metallisch, seltsam lebendig.

Prompt: `Close iron object or bell clapper touched once and vibrating too long, metallic ring, low sympathetic vibration, unsettling but realistic, no speech, no music, one-shot, 4 seconds, 48 kHz WAV.`

### SFX11 - Schritte im Schnee

Datei: `SFX11_Schritte.wav`

Soll klingen wie: Stiefel im Schnee, fuenf Schritte, mittlere Naehe. Normaler Mensch, aber langsam.

Prompt: `Adult leather boots walking five slow steps through packed winter snow, medium close perspective, varied crunch texture, rural night ambience tail, no speech, no music, one-shot, 4 seconds, 48 kHz WAV.`

### SFX12 - Barfuessige Schritte

Datei: `SFX12_Barfuss_Schritte.wav`

Soll klingen wie: Nackte Fuesse auf kaltem Stein oder hartem Schnee. Leise, feucht, falscher Rhythmus.

Prompt: `Bare feet walking softly on cold wet stone and hard snow, sticky quiet steps, unnatural timing, close perspective, unsettling but not loud, no speech, no music, one-shot, 4 seconds, 48 kHz WAV.`

### SFX13 - Stimmen im Berg

Datei: `SFX13_Stimmen_ohne_Worte.wav`

Soll klingen wie: Stimmen tief im Stollen, aber ohne verstaendliche Worte. Menschlich genug, um schlimm zu sein, undeutlich genug, um kein Text zu sein.

Prompt: `Distant human-like whispers and voices from deep mine tunnels, layered echoes, completely unintelligible, no words, no names, damp stone reverb, subtle horror, no music, one-shot, 8 seconds, 48 kHz WAV.`

### SFX14 - Schlaege unter dem Boden

Datei: `SFX14_Schlaege_unter_Boden.wav`

Soll klingen wie: Drei schwere Schlaege unter Holz und Stein. Nicht direkt laut, aber koerperlich.

Prompt: `Three heavy subterranean knocks heard through old wooden floor and stone, muffled impact, low resonance, irregular spacing, close interior perspective, no speech, no music, one-shot, 4 seconds, 48 kHz WAV.`

### SFX15 - Atem hinter einer Person

Datei: `SFX15_Atem_hinter_dir.wav`

Soll klingen wie: Kalter Atem direkt hinter dem Ohr. Ein kurzer Ein- und Ausatmer, vielleicht ein wenig Stoffbewegung.

Prompt: `Close cold breath directly behind the listener, one quiet inhale and exhale, slight cloth movement, intimate and frightening, no voice, no words, no music, one-shot, 3 seconds, 48 kHz WAV.`

### SFX16 - Zwei hohe fallende Toene

Datei: `SFX16_Weisse_Frau_Motiv.wav`

Soll klingen wie: Das kurze Zeichen der Weissen Frau. Zwei duenne fallende Toene aus Glas oder Metall, sofort wieder weg.

Prompt: `Two thin descending glass and metal tones, ghostly signature motif, fragile cold shimmer, short decay, no melody beyond the two tones, no speech, no music bed, one-shot, 3 seconds, 48 kHz WAV.`

### SFX17 - Ein Kloeppelschlag von selbst

Datei: `SFX17_Kloeppel_schlaegt.wav`

Soll klingen wie: Der Kloeppel schlaegt allein gegen die Glocke. Metallkontakt, groesser als er sein duerfte.

Prompt: `Single iron bell clapper striking an old bronze bell by itself, close metal impact, large bell body resonance, empty church tower reverb, no speech, no music, one-shot, 6 seconds, 48 kHz WAV.`

### SFX18 - Frost breitet sich aus

Datei: `SFX18_Frost_breitet_sich_aus.wav`

Soll klingen wie: Eis kriecht schnell ueber Oberflaechen. Kleine Risse, Knacken, kalter Druck.

Prompt: `Frost rapidly spreading across wood, glass and stone, tiny ice crystals cracking, close surface tension, low cold pressure underneath, realistic with supernatural edge, no speech, no music, one-shot, 6 seconds, 48 kHz WAV.`

### SFX19 - Herzschlag im Frost

Datei: `SFX19_Herzschlag.wav`

Soll klingen wie: Ein langsamer Herzschlag, als kaeme er durch Eis oder Boden. Kein Kickdrum, eher Koerperhorror.

Prompt: `Slow muted human heartbeat heard through ice and old floorboards, soft organic thump, cold room resonance, unsettling and restrained, not a kick drum, no speech, no music, seamless loop, 8 seconds, 48 kHz WAV.`

### SFX20 - Eisbruch

Datei: `SFX20_Eisbruch.wav`

Soll klingen wie: Dickes Eis bricht ploetzlich. Splitter, tiefer Riss, vielleicht Wasser darunter.

Prompt: `Thick ice sheet breaking violently, deep crack spreading, sharp ice shards, brief water surge underneath, large but realistic impact, no speech, no music, one-shot, 5 seconds, 48 kHz WAV.`

### SFX21 - Bannung gelingt

Datei: `SFX21_Bannung.wav`

Soll klingen wie: Kein Triumph, eher Druck faellt ab. Kalter Ton loest sich, Luft kommt zurueck, ein Tropfen oder warmes Knacken.

Prompt: `Supernatural release after a successful banishment, cold pressure tone dissolving, air returning to the room, faint thawing drip, restrained relief, no triumphant music, no speech, one-shot, 6 seconds, 48 kHz WAV.`

### SFX22 - Bannung scheitert

Datei: `SFX22_Scheitern.wav`

Soll klingen wie: Der Raum wird schlagartig falsch. Druckabfall, verzerrte Glocke, kalter Windstoss, abrupte Gefahr.

Prompt: `Failed banishment horror sting, sudden pressure drop, distorted distant bell resonance, cold burst of wind, low impact without explosion, frightening but not cartoonish, no speech, no music, one-shot, 6 seconds, 48 kHz WAV.`

### SFX23 - Fensterladen im Wind

Datei: `SFX23_Fensterladen_im_Wind.wav`

Soll klingen wie: Ein loser Holzladen schlaegt im Wind. Zwei oder drei harte Bewegungen, mit kaltem Aussenhall.

Prompt: `Loose wooden window shutter banging in winter wind, two or three irregular impacts, old house exterior, cold air gusts, realistic wood detail, no speech, no music, one-shot, 4 seconds, 48 kHz WAV.`

### SFX24 - Fernes Laeuten

Datei: `SFX24_Fernes_Laeuten.wav`

Soll klingen wie: Glockenschlaege weit weg ueber Schnee. Nicht klar lokalisierbar, leise und lang.

Prompt: `Several distant church bell strokes across a snowy valley at night, soft and heavily reverberant, hard to locate, old bronze tone, no speech, no music, one-shot, 12 seconds, 48 kHz WAV.`

### SFX25 - Holz unter Spannung

Datei: `SFX25_Holz_unter_Spannung.wav`

Soll klingen wie: Alte Balken geben unter Last nach, aber brechen noch nicht. Tiefes Knarzen, zitternde Fasern.

Prompt: `Old wooden beams flexing under heavy strain, deep timber groan, small fiber creaks, slow pressure build, close interior perspective, no collapse, no speech, no music, one-shot, 5 seconds, 48 kHz WAV.`

### SFX26 - Wasser im Flutstollen

Datei: `SFX26_Wasser_im_Flutstollen.wav`

Soll klingen wie: Wasser in einem alten Flutstollen. Tropfen, flacher Lauf, Steinwiderhall.

Prompt: `Water in an old underground flood tunnel, shallow flow over stone, scattered drips, damp mine reverb, cold and close, realistic ambience layer, no speech, no music, seamless loop, 18 seconds, 48 kHz WAV.`

### SFX27 - Wiederhallende Schritte

Datei: `SFX27_Wiederhallende_Schritte.wav`

Soll klingen wie: Schritte mit einem Echo, das zu spaet kommt. Erst normal, dann falsch versetzt aus dem Stollen.

Prompt: `Footsteps in a mine tunnel followed by delayed unnatural echoes, echo timing slightly wrong, damp stone reflections, one walker only, tense and realistic, no speech, no music, one-shot, 7 seconds, 48 kHz WAV.`

### SFX28 - Klopfen unter dem Boden

Datei: `SFX28_Klopfen_unter_Boden.wav`

Soll klingen wie: Klopfen von unten, naeher als SFX14. Holz oben, Tiefe darunter.

Prompt: `Close knocking from beneath old floorboards, three or four taps, wooden surface detail with deep space underneath, quiet room tail, no speech, no music, one-shot, 4 seconds, 48 kHz WAV.`

### SFX29 - Verzerrte Glockenresonanz

Datei: `SFX29_Glockenresonanz.wav`

Soll klingen wie: Eine Glocke schwingt nach und kippt in eine falsche Resonanz. Metall biegt, Obertone schlagen gegeneinander.

Prompt: `Old bell resonance detuning and bending unnaturally, beating metal overtones, low subharmonic under the decay, cold stone tower reverb, no speech, no music, one-shot, 8 seconds, 48 kHz WAV.`

### SFX30 - Kurzer Atem im Raum

Datei: `SFX30_Atem_im_Raum.wav`

Soll klingen wie: Ein kurzer Atemzug in einem eigentlich leeren Raum. Weniger nah als SFX15, mehr "da war etwas".

Prompt: `Brief breath in an otherwise empty cold room, medium distance, small reverb tail, barely human, no words, no speech, no music, one-shot, 3 seconds, 48 kHz WAV.`

### SFX31 - Resonanz bricht ab

Datei: `SFX31_Resonanzabbruch.wav`

Soll klingen wie: Eine laufende Glockenresonanz wird abgeschnitten. Der wichtigste Moment ist die tote Stille danach.

Prompt: `Sustained old bell resonance suddenly cut off into dead silence, tiny room tail before the cutoff, supernatural pressure drop, no explosion, no speech, no music, one-shot, 5 seconds, 48 kHz WAV.`

## Produktionsnotizen fuer die App

- Die Dateinamen sollten gleich bleiben. Dann muessen wir Manifest, Szenen und Soundboard nicht neu verdrahten.
- `SFX06_Stille.wav` sollte spaeter eher als App-Funktion gebaut werden: Atmosphaere fuer 1 bis 2 Sekunden ausblenden, danach kontrolliert wieder rein.
- Loops brauchen einen echten Loop-Test. Ein perfekter Loop ist wichtiger als ein spektakulaerer Einzelklang.
- AI-Sounds muessen nach dem Export noch normalisiert werden. Ziel: keine Peaks, keine Sprachreste, keine lauten Anfangsklicks.
- Fuer das iPhone brauchen wir einen sichtbaren Audio-Testbutton. iOS erlaubt Audio oft erst nach einer echten Nutzeraktion.
