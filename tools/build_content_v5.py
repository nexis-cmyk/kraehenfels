#!/usr/bin/env python3
"""Build the native 3.3 manifest from the shared canon."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "adventure" / "canon.json"
NATIVE_OUTPUTS = [
    ROOT / "content" / "manifest.json",
    ROOT / "app" / "Kraehenfels" / "Resources" / "manifest.json",
]


def cue(
    cue_id: str,
    title: str,
    scene: str,
    layer: str,
    filename: str,
    mode: str,
    gain: float,
    fade_ms: int,
    description: str,
    play_when: str,
    stop_when: str,
    instruction: str,
    *,
    is_clue: bool = False,
    fallback: str | None = None,
) -> dict[str, object]:
    legacy_category = "music" if layer in {"musicBed", "musicLayer"} else layer
    return {
        "id": cue_id,
        "title": title,
        "scene": scene,
        "category": legacy_category,
        "scope": "native",
        "layer": layer,
        "file": filename,
        "mode": mode,
        "gain": gain,
        "fadeMs": fade_ms,
        "isClue": is_clue,
        "printFallbackId": fallback,
        "description": description,
        "playWhen": play_when,
        "stopWhen": stop_when,
        "gmInstruction": instruction,
    }


AUDIO_CUES = [
    cue("A01", "Kutschenstraße", "S01", "ambient", "V6_A01_Kutschenstrasse.m4a", "loop", -0.22, 1800, "Winterwind, rollendes Wagenholz, Geschirr und unruhige Pferde auf der nächtlichen Straße.", "Sobald alle am Tisch sitzen.", "Beim Eintritt in das Gasthaus.", "Leise starten. Stimmen müssen jederzeit klar darüber liegen."),
    cue("A02", "Gasthaus", "S02", "ambient", "V6_A02_Gasthaus.m4a", "loop", -0.30, 1600, "Herdfeuer, altes Gebälk, Geschirr und ein gedämpftes Stimmenmeer ohne verständliche Worte.", "Wenn Gruber die Tür öffnet.", "Wenn die Gruppe das Gasthaus verlässt.", "Warm, aber nicht gemütlich laut mischen."),
    cue("A03", "Dorf am Morgen", "S08", "ambient", "V5_A03_Dorf_am_Morgen.m4a", "loop", -0.28, 1800, "Kalter Morgenwind, fernes Dorfleben und das erste Tauwasser.", "Mit dem ersten Satz des Epilogs.", "Nach dem letzten persönlichen Nachhall.", "Keine Schockeffekte mehr. Der Morgen soll echt wirken."),
    cue("A04", "Kirche ohne Glocke", "S03", "ambient", "V5_A04_Kirche_ohne_Glocke.m4a", "loop", -0.32, 2000, "Kalte Steinkirche, undichte Türen, arbeitendes Holz und ein ferner Rabe.", "Beim Öffnen der Kirchentür.", "Beim Verlassen der Kirche.", "Sehr leise halten, damit die Leere des Raums trägt."),
    cue("A05", "Schmiede", "S04", "ambient", "V6_A05_Schmiede.m4a", "loop", -0.27, 1600, "Tiefe Esse, Blasebalg und einzelne Metallresonanzen zwischen zwei Arbeiten.", "Wenn Marta die Gruppe hereinlässt.", "Beim Verlassen der Schmiede.", "Der einzelne Schmiedeschlag bleibt SFX05 vorbehalten."),
    cue("A06", "Waldspur", "S05", "ambient", "V5_A06_Waldspur.m4a", "loop", -0.30, 1800, "Tiefer Winterwald, Schnee und weiter Raum ohne menschliche Schritte.", "Hinter den letzten Häusern.", "Beim Eintritt ins Rathausarchiv oder am Szenenwechsel.", "Nicht mit Prozessionsschritten verwechseln. Diese Fläche bleibt leer."),
    cue("A07", "Rathausarchiv", "S06", "ambient", "V5_A07_Rathausarchiv.m4a", "loop", -0.31, 1600, "Papier, Ofenmetall, altes Holz und Wind an kleinen Fenstern.", "Sobald die Bücher auf dem Tisch liegen.", "Wenn draußen die Prozession sichtbar wird.", "Trocken und nah mischen. M02 später darunter einblenden."),
    cue("A08", "Alte Eiche", "S07", "ambient", "V6_A08_Alte_Eiche.m4a", "loop", -0.27, 1800, "Froststurm, hohler Stamm, arbeitendes Holz und eine lose Eisenkette am Schrein.", "Sobald die Eiche vollständig sichtbar ist.", "Wenn die Entscheidung gefallen ist.", "Die Natur ist der Vordergrund. M02 bleibt darunter."),
    cue("M01", "Krähenfels-Motiv", "S01", "musicBed", "V5_M01_Kraehenfels_Motiv.m4a", "loop", -0.34, 2600, "Leises Zweitonmotiv aus Cello, Filzklavier und gestrichenem Bordun.", "Vor dem ersten Vorlesetext.", "Nach dem letzten Satz des Epilogs.", "Das ist das dauerhafte Grundmotiv. Nur zum Vorlesen absenken, nicht bei jedem Szenenwechsel neu starten."),
    cue("M02", "Die Prozession", "S06", "musicLayer", "V5_M02_Prozession.m4a", "loop", -0.38, 1800, "Tiefe Streicher, ferner Holzpuls und gedämpfte Rahmentrommel.", "Wenn die Gruppe versteht, dass sich das Dorf versammelt.", "Nach der Entscheidung an der Eiche.", "Unter M01 legen. Im Finale langsam anheben, niemals darüber springen lassen."),
    cue("SFX01", "Achse bricht", "S01", "sfx", "V6_SFX01_Achse_bricht.wav", "oneShot", -0.14, 0, "Ein harter Holzbruch, schepperndes Geschirr und der Wagen kippt hörbar aus dem Takt.", "Nach dem Satz: Ein Knacken läuft durch die Kutsche.", "Endet selbst.", "Einmal auslösen und danach eine Sekunde nichts sagen."),
    cue("SFX02", "Pferde scheuen", "S01", "sfx", "V6_SFX02_Pferde_scheuen.wav", "oneShot", -0.12, 0, "Zwei kurze Hufschläge im Schnee, ein erschrockenes Schnauben und straffes Geschirr.", "Direkt nach dem Achsenbruch.", "Endet selbst.", "Nur einmal. Die Pferde galoppieren nicht davon."),
    cue("SFX03", "Riegel von außen", "S02", "sfx", "V5_SFX03_Riegel_von_aussen.wav", "oneShot", -0.16, 0, "Ein schwerer Eisenriegel läuft durch zwei Halterungen und fällt zu.", "Wenn nachts die Zimmertür von außen verriegelt wird.", "Endet selbst.", "Blicke nach dem Geräusch nicht sofort zur Gruppe. Lass sie reagieren.", is_clue=True, fallback="H03"),
    cue("SFX04", "Geweih an der Tür", "S02", "sfx", "V6_SFX04_Geweih_an_der_Tuer.wav", "oneShot", -0.20, 0, "Trockenes Holz knarrt unter Gewicht, dann kratzt ein harter Rand zweimal über die Tür.", "Optional nach einer längeren Stille im Gasthaus.", "Endet selbst.", "Nur als Vorzeichen nutzen. Noch kein Wesen zeigen.", is_clue=True, fallback="H07"),
    cue("SFX05", "Ein Schmiedeschlag", "S04", "sfx", "V6_SFX05_Einzelner_Schmiedeschlag.wav", "oneShot", -0.12, 0, "Genau ein Hammerhieb auf heißes Eisen mit kurzem, sauberem Ambossring.", "Wenn Marta die drei schwarzen Nägel zeigt.", "Endet selbst.", "Ein Schlag. Danach erklärt Marta den Preis des Eisens.", is_clue=True, fallback="H06"),
    cue("SFX06", "Atem hinter der Figur", "S05", "sfx", "V6_SFX06_Atem_hinter_der_Figur.wav", "oneShot", -0.22, 0, "Ein einzelner naher Atemzug im Raum, ohne Stimme und ohne musikalischen Ton.", "Nachdem die Spur ihre Richtung scheinbar gewechselt hat.", "Endet selbst.", "Leise auslösen. Nicht verraten, hinter welcher Figur er war.", is_clue=True, fallback="H08"),
    cue("SFX07", "Prozessionsschritte", "S06", "sfx", "V5_SFX07_Prozessionsschritte.wav", "oneShot", -0.18, 0, "Viele langsame Lederstiefel im Schnee, Wolle und knarrende Holzmasken.", "Wenn die erste Reihe auf der Dorfstraße sichtbar wird.", "Endet selbst.", "M02 kurz davor leise starten. Dann diesen Cue einmal spielen.", is_clue=True, fallback="H07"),
    cue("SFX08", "Knochenhirsch hebt den Kopf", "S07", "sfx", "V6_SFX08_Knochenhirsch.wav", "oneShot", -0.20, 0, "Tiefes Gelenk, schweres Gewicht im Schnee, trockenes Holz und ein hohler Atemzug.", "Beim ersten vollständigen Anblick des Knochenhirsches.", "Endet selbst.", "Erst auslösen, wenn du das Wesen wirklich zeigst."),
    cue("SFX09", "Die Bindung reißt", "S07", "sfx", "V6_SFX09_Bindung_reisst.wav", "oneShot", -0.12, 0, "Eine gespannte Resonanz bricht ab, Eisen springt frei und der Druck fällt hörbar aus dem Raum.", "Nur beim Ende Zerstörung, sobald die Reliquie endgültig bricht.", "Endet selbst.", "Bei Widerruf oder Erneuerung niemals abspielen."),
    cue("SFX10", "Falscher Glockenschlag", "S03", "sfx", "V6_SFX10_Falscher_Glockenschlag.wav", "oneShot", -0.17, 0, "Ein einzelner tiefer Glockenschlag mit leicht schwebender, unnatürlicher Verstimmung.", "Unmittelbar nachdem Falk das Wort Gastrecht ausgesprochen hat.", "Endet selbst.", "Nur einmal. Die Kirche besitzt sichtbar keine funktionsfähige Glocke.", is_clue=True, fallback="H04"),
]


SCENE_AUDIO = {
    "S01": ["M01", "A01", "SFX01", "SFX02"],
    "S02": ["A02", "SFX03", "SFX04"],
    "S03": ["A04", "SFX10"],
    "S04": ["A05", "SFX05"],
    "S05": ["A06", "SFX06"],
    "S06": ["A07", "M02", "SFX07"],
    "S07": ["A08", "M02", "SFX08", "SFX09"],
    "S08": ["A03", "M01"],
}


def main() -> None:
    manifest = json.loads(CANON.read_text(encoding="utf-8"))
    manifest["meta"]["version"] = "3.3.0"
    manifest["audioCues"] = AUDIO_CUES
    cues = {item["id"]: item for item in AUDIO_CUES}
    for scene in manifest["scenes"]:
        cue_ids = SCENE_AUDIO[scene["id"]]
        scene["audioCueIds"] = cue_ids
        scene["soundPreset"] = cues[cue_ids[0]]["title"]
        scene["audioPlan"] = [
            {
                "cueId": cue_id,
                "playWhen": cues[cue_id]["playWhen"],
                "stopWhen": cues[cue_id]["stopWhen"],
                "gmInstruction": cues[cue_id]["gmInstruction"],
                "optional": cue_id in {"SFX04", "SFX09"},
            }
            for cue_id in cue_ids
        ]

    payload = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    CANON.write_text(payload, encoding="utf-8")
    for output in NATIVE_OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    print("Built native 3.3.0 content. Web 3.1.0 was not changed.")


if __name__ == "__main__":
    main()
