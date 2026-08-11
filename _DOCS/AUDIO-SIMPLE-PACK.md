# Kraehenfels simple sound pack

Ziel: weniger Soundstress. Nicht 46 perfekte Einzelclips bauen. Fuer den Spielabend reicht ein kleines Set, das stark genug ist und die Runde nicht ueberlaedt.

## Entscheidung

Ich wuerde fuer die erste Runde dieses Set nehmen:

- 5 Loop-Sounds fuer Orte und Stimmung
- 1 leises Hintergrundthema
- 12 starke Effektknoepfe

Die App kann technisch weiter alle 46 Cue-Dateien haben. Im Simple-Pack-Modus werden mehrere App-Dateien aus denselben guten Quellen gebaut. Der Leitstand zeigt jedoch nur einen Vertreter je hörbarer Funktion. Unwichtige, stumme oder doppelte Knöpfe bleiben aus den Szenen heraus, damit keine alten Platzhalter stören.

## Was du wirklich brauchst

### Loops

`LOOP01_Winterdorf_Wald.m4a`

Winterdorf und Wald. Kalter Wind, Schnee, Holzhaeuser, Tannen, sehr wenige Kraehen in der Ferne. Diesen Loop kannst du fuer Ankunft, Dorf, Nacht und Wald laufen lassen.

`LOOP02_Wirtsstube.m4a`

Wirtshaus. Feuer, Holz, Kruege, leises unverstaendliches Murmeln, Tuerzug. Warm, aber nicht gemuetlich.

`LOOP03_Kapelle_Glockenturm.m4a`

Kapelle, Friedhof und Glockenturm. Kalte Luft, Steinraum, Holz arbeitet, ganz ferner Glockennachhall.

`LOOP04_Grube_Flutstollen.m4a`

Grube und Flutstollen. Feuchter Stein, Luftzug, Tropfen, Holzstuetzen, niedriges Druecken.

`LOOP05_Finale_Froststurm.m4a`

Finale. Wind, Eis, Druck, Glockenresonanz, alles etwas zu nah.

### Hintergrundmusik

`MUSIC01_Dunkles_Grundthema.m4a`

Ein sehr leises dunkles Folk-Horror-Thema. Kein Song mit klarer Melodie. Eher eine Schicht unter der Szene. Wenn es nervt, laesst du es weg und spielst nur Loops.

### Effektknoepfe

`SFX01_Kutschenunfall.wav`

Achse bricht, Pferde erschrecken, Hufe im Schnee. Ein einziger guter Crash reicht.

`SFX02_Fenster_Ast.wav`

Ast bricht oder Fensterladen schlaegt im Wind. Das ist dein allgemeiner "da war etwas"-Knopf.

`SFX03_Glocke_Normal.wav`

Eine alte Bronzeglocke, normal und realistisch.

`SFX04_Glocke_Falsch.wav`

Dieselbe Glocke, aber dumpf, kalt, verstimmt und falsch.

`SFX05_Metall_Kloeppel.wav`

Metall vibriert oder der Kloeppel bewegt sich von selbst.

`SFX06_Schritte_Schnee.wav`

Langsame Stiefel im Schnee.

`SFX07_Barfuss_Schritte.wav`

Barfuesse auf kaltem Stein oder hartem Schnee.

`SFX08_Stimmen_Berg.wav`

Unverstaendliche Stimmen tief im Berg. Keine Worte, keine Namen.

`SFX09_Klopfen_Boden.wav`

Klopfen von unten. Holz oben, Tiefe darunter.

`SFX10_Atem_Nah.wav`

Ein kurzer kalter Atem hinter einer Person.

`SFX11_Weisse_Frau_Motiv.wav`

Zwei hohe fallende Toene oder ein sehr kurzer wortloser Liedrest. Das ist das Zeichen der Weissen Frau.

`SFX12_Eisbruch_Finale.wav`

Eis bricht, Resonanz kippt, Finale-Stinger. Den nutzt du fuer Eskalation, Erfolg oder Scheitern.

## Einfachster kostenloser Weg

Route A ist am stressfreisten:

1. Loops bei Mixkit oder Pixabay suchen und herunterladen.
2. SFX bei Adobe Firefly erzeugen. Firefly kann Soundeffekte aus Textprompt erzeugen und als WAV herunterladen.
3. Alles in einen Ordner legen.
4. Dateien exakt nach der Liste oben benennen.
5. Import starten:

```powershell
python tools/import_audio_replacements.py "C:\Pfad\zu\simple-sounds" --simple-pack --sync-web
python tools/build_web_preview.py
python tools/validate_project.py
```

Route B, wenn du gar nichts generieren willst:

1. Nur Mixkit und Pixabay verwenden.
2. Suchbegriffe nutzen: `winter wind`, `forest wind`, `old tavern`, `fireplace`, `church bell`, `mine ambience`, `wood creak`, `footsteps snow`, `whisper tunnel`, `ice crack`, `breath`.
3. Die besten Treffer herunterladen.
4. Grob passend umbenennen.
5. Import laufen lassen.

Route C, wenn du schnell sehr spezielle Effekte willst:

1. ElevenLabs Sound Effects oder Adobe Firefly nehmen.
2. Nur die 12 Effektknoepfe generieren.
3. Loops trotzdem von Mixkit oder Pixabay nehmen, weil fertige Loops oft stabiler sind.

## Copy-Prompt fuer das Simple Pack

```text
Create a small tabletop horror sound pack for "Die Weisse Frau schweigt", set in Kraehenfels, an isolated Black Forest village in November 1890.

The pack must feel cold, rural, grounded and haunted. No action trailer booms, no cheap whooshes, no understandable speech, no copyrighted melodies, no named artists, no watermarks. Keep everything usable at a table where people are talking.

Export 48 kHz WAV or M4A. Loops must be seamless. One-shot effects need a clean start and clean end.

Create exactly these files:

LOOP01_Winterdorf_Wald.m4a
Cold winter village and forest loop. Wind through wooden houses and fir trees, snow muffling the ground, a few distant crows, old timber creaks far away. No speech, no music. Seamless loop, 50 seconds.

LOOP02_Wirtsstube.m4a
Old rural tavern loop. Fireplace crackle, wooden chairs, ceramic mugs, low indistinct room murmur with no understandable words, winter draft at the door. No music. Seamless loop, 50 seconds.

LOOP03_Kapelle_Glockenturm.m4a
Small chapel, graveyard and bell tower loop. Cold stone room tone, old roof beams settling, wind through cracks, faint bronze bell resonance. No choir, no speech, no music. Seamless loop, 50 seconds.

LOOP04_Grube_Flutstollen.m4a
Abandoned mine and flood tunnel loop. Damp stone, cold airflow, distant water drops, low pressure, old wooden supports. No speech, no music. Seamless loop, 50 seconds.

LOOP05_Finale_Froststurm.m4a
Finale blizzard loop. Supernatural winter wind, ice stress in wood and stone, low pressure rumble, distorted bronze bell resonance far away. No melody, no speech. Seamless loop, 50 seconds.

MUSIC01_Dunkles_Grundthema.m4a
Very quiet dark folk horror underscore. Low bowed strings, distant harmonium, slow pulse, sparse and restrained. No recognizable melody, no speech. Seamless loop, 45 seconds.

SFX01_Kutschenunfall.wav
Wooden carriage axle breaks, horses panic, harness pulls tight, hooves scrape in snow, carriage jolts down. Realistic foley, no human voices, no music. One-shot, 5 seconds.

SFX02_Fenster_Ast.wav
Loose wooden shutter bangs in winter wind, followed by a heavy snow-loaded branch cracking nearby. Realistic wood, cold air, no music, no speech. One-shot, 5 seconds.

SFX03_Glocke_Normal.wav
Single old bronze church bell strike in a small rural stone church. Warm metal body, natural long decay. No distortion, no speech, no music. One-shot, 7 seconds.

SFX04_Glocke_Falsch.wav
Single old church bell strike muffled by ice and fog. Detuned overtones, cold unnatural resonance, long frozen decay. No cheap distortion, no speech, no music. One-shot, 8 seconds.

SFX05_Metall_Kloeppel.wav
Close iron bell clapper or forged metal object touched once and vibrating too long. Metallic ring, low sympathetic vibration, unsettling but realistic. No speech, no music. One-shot, 5 seconds.

SFX06_Schritte_Schnee.wav
Slow leather boots walking through packed winter snow. Five uneven steps, medium close perspective, quiet rural night tail. No speech, no music. One-shot, 5 seconds.

SFX07_Barfuss_Schritte.wav
Bare feet walking softly on cold wet stone and hard snow. Sticky quiet steps, unnatural timing, close perspective. No speech, no music. One-shot, 5 seconds.

SFX08_Stimmen_Berg.wav
Distant human-like whispers from deep mine tunnels. Layered echoes, completely unintelligible, no words, no names, damp stone reverb. No music. One-shot, 8 seconds.

SFX09_Klopfen_Boden.wav
Three heavy knocks from beneath old floorboards and stone. Muffled impact, low resonance, irregular spacing, close interior perspective. No speech, no music. One-shot, 5 seconds.

SFX10_Atem_Nah.wav
Close cold breath directly behind the listener. One quiet inhale and exhale, slight cloth movement. No voice, no words, no music. One-shot, 3 seconds.

SFX11_Weisse_Frau_Motiv.wav
Two thin descending glass and metal tones, like a ghostly signature. Fragile cold shimmer, short decay. No melody beyond the two tones, no speech, no music bed. One-shot, 4 seconds.

SFX12_Eisbruch_Finale.wav
Thick ice breaks, old bell resonance bends and suddenly cuts off into dead silence. Deep crack, sharp ice shards, supernatural pressure drop. No explosion, no speech, no music. One-shot, 6 seconds.
```

## Was ich danach mache

Wenn du mir die Dateien gibst, importiere ich sie mit dem Simple-Pack-Modus, teste Web und App-Bundle und passe das Soundboard so an, dass du am Tisch nicht mehr durch 46 Knoepfe denken musst.
