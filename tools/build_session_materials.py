#!/usr/bin/env python3
"""Build the player-safe session pack and the GM NPC direction guide."""

from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import build_invitation
from build_print_pack_v3 import (
    ASSETS,
    CHARCOAL,
    COBALT,
    FROST,
    INK,
    PANEL,
    PANEL_RAISED,
    PAPER,
    PAPER_DARK,
    QUIET,
    RUST,
    WARNING,
    draw_handout,
    image_cover,
    page_title,
    paragraph,
    text_style,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "content" / "manifest.json"
OUTPUT_DIR = ROOT / "output" / "pdf"
TMP_DIR = ROOT / "tmp" / "pdfs" / "session-materials"
PLAYER_PDF = OUTPUT_DIR / "Kraehenfels-Spielermaterial-Druck.pdf"
NPC_PDF = OUTPUT_DIR / "Kraehenfels-NPC-Regie.pdf"
PAGE_MAP = TMP_DIR / "page-map.json"


MAP_ORDER = [
    ("MAP01", "Bekannte Orte: Gasthaus, Kirche, Schmiede, Rathaus und Waldweg"),
    ("MAP02", "Sichtbar: Schankraum, Theke, Küche, Treppe und Gästezimmer"),
    ("MAP03", "Sichtbar: Kirchenschiff, Sakristei, Archiv und Friedhof"),
    ("MAP04", "Sichtbar: Esse, Amboss, Werkzeugwand und Eisenlager"),
    ("MAP05", "Sichtbar: Sitzungssaal, Archiv und Bürgermeisterzimmer"),
    ("MAP06", "Sichtbar: Forstweg, Alte Eiche, Schrein und Steinkreis"),
]


PAGE_NAMES = [
    "00_Vor_dem_Spiel/01_Einladung",
    "00_Vor_dem_Spiel/02_Spieler-Kurzregeln",
    "01_Kutschenpanne/01_H01_Kutschauftrag",
    "01_Kutschenpanne/02_Gegenstandskarten",
    "02_Ankunft/01_Karte_Kraehenfels",
    "03_Gasthaus/01_Karte_Schwarzer_Keiler",
    "03_Gasthaus/02_H02_Kraehenfelser_Bote",
    "03_Gasthaus/03_H03_Gaestebuch",
    "04_Kirche/01_Karte_Kirche",
    "04_Kirche/02_H04_Kirchenbuch",
    "05_Schmiede/01_Karte_Schmiede",
    "05_Schmiede/02_H06_Werkblatt",
    "06_Waldspur/01_H07_Lenis_Zeichnung",
    "06_Waldspur/02_H08_Holzabreibung",
    "06_Waldspur/03_H10_Forstweg",
    "07_Archiv/01_Karte_Rathausarchiv",
    "07_Archiv/02_H05_Winterbuchhaltung",
    "07_Archiv/03_H09_Ritualfragment",
    "08_Finale/01_Karte_Alte_Eiche",
    "08_Finale/02_Endkarten",
]


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def draw_rule_box(
    c: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    title: str,
    body: str,
    accent=COBALT,
) -> None:
    c.setFillColor(PANEL)
    c.setStrokeColor(accent)
    c.setLineWidth(0.8)
    c.roundRect(x, y, width, height, 3 * mm, fill=1, stroke=1)
    c.setFillColor(accent)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x + 6 * mm, y + height - 9 * mm, title.upper())
    paragraph(
        c,
        body,
        x + 6 * mm,
        y + 6 * mm,
        width - 12 * mm,
        height - 19 * mm,
        text_style(f"rule-{title}-{x}-{y}", 8.8, 11.2, FROST),
    )


def draw_player_rules(c: canvas.Canvas) -> None:
    c.setPageSize(A4)
    width, height = A4
    page_title(c, "Kurzregeln für Spieler", "How to be a Hero · am Tisch")
    paragraph(
        c,
        "Beschreibt zuerst, was eure Figur tut. Die Spielleitung sagt, ob ein Wurf nötig ist und welcher Wert passt. Gewürfelt wird nur, wenn die Handlung unsicher ist und ein Fehlschlag die Lage verändert.",
        18 * mm,
        height - 72 * mm,
        width - 36 * mm,
        25 * mm,
        text_style("rules-intro", 11, 15, colors.white),
    )

    gap = 6 * mm
    box_width = (width - 36 * mm - gap) / 2
    left = 18 * mm
    right = left + box_width + gap
    draw_rule_box(c, left, 156 * mm, box_width, 50 * mm, "W100-Probe", "Würfelt W100. Das Ergebnis ist ein Erfolg, wenn es kleiner oder gleich eurem Fähigkeits- oder Begabungswert ist.")
    draw_rule_box(c, right, 156 * mm, box_width, 50 * mm, "Kritische Ergebnisse", "Kritischer Erfolg: Wurf kleiner oder gleich 10 Prozent des Wertes.<br/><br/>Kritischer Misserfolg: Wurf größer oder gleich 90 plus 10 Prozent des Wertes.", WARNING)
    draw_rule_box(c, left, 99 * mm, box_width, 50 * mm, "Fehlschlag", "Ein Fehlschlag verschärft die Geschichte. Ihr wählt oder bestätigt eine passende Folge. Wichtige Hinweise verschwinden dadurch nicht.", WARNING)
    draw_rule_box(c, right, 99 * mm, box_width, 50 * mm, "Gegenstände", "Ein Gegenstand wird vor dem Wurf eingesetzt, wenn seine Karte das verlangt. Er erhöht dann den Zielwert um 10. Anwendungen werden abgestrichen.")
    draw_rule_box(c, left, 35 * mm, box_width, 57 * mm, "Initiative und Angriff", "Initiative: 1W10 plus Handeln.<br/><br/>Ein Angriff ist eine passende Fertigkeitsprobe. Einmal pro Runde darf eine Figur auf Handeln parieren. Schusswaffen und kritische Angriffe sind nicht parierbar.")
    draw_rule_box(c, right, 35 * mm, box_width, 57 * mm, "Schaden und LP", "Schaden wird mit den Waffenwürfeln ausgewürfelt. Kritische Angriffe verdoppeln den Schaden.<br/><br/>Unter 10 LP wird eine Figur bewusstlos, bei 0 LP stirbt sie. Mehr als 60 Schaden durch einen Treffer macht sofort bewusstlos.")
    c.setFillColor(QUIET)
    c.setFont("Helvetica", 7.5)
    c.drawString(18 * mm, 18 * mm, "Eure vollständigen Charakterbögen und das offizielle Regelwerk bleiben maßgeblich.")


def draw_item_cards_page(c: canvas.Canvas, data: dict) -> None:
    c.setPageSize(A4)
    width, height = A4
    locations = {entry["id"]: entry["title"] for entry in data.get("guide", {}).get("itemFindLocations", [])}
    items = data.get("guide", {}).get("items", [])
    margin_x, margin_y = 12 * mm, 12 * mm
    gap_x, gap_y = 5 * mm, 5 * mm
    card_width = (width - 2 * margin_x - gap_x) / 2
    card_height = (height - 2 * margin_y - 2 * gap_y) / 3
    for index, item in enumerate(items):
        column = index % 2
        row = index // 2
        x = margin_x + column * (card_width + gap_x)
        y = height - margin_y - (row + 1) * card_height - row * gap_y
        accent = RUST if item.get("weapon") else COBALT
        c.setFillColor(PAPER)
        c.setStrokeColor(accent)
        c.setLineWidth(1.2)
        c.roundRect(x, y, card_width, card_height, 3 * mm, fill=1, stroke=1)
        c.setFillColor(accent)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(x + 7 * mm, y + card_height - 10 * mm, "GEGENSTAND · KUTSCHE")
        c.setFillColor(CHARCOAL)
        c.setFont("Helvetica-Bold", 13.5)
        c.drawString(x + 7 * mm, y + card_height - 20 * mm, item["title"])
        c.setFillColor(accent)
        c.setFont("Helvetica-Bold", 7.2)
        c.drawString(x + 7 * mm, y + card_height - 27 * mm, f"Fundort · {locations[item['locationID']]}")
        c.setStrokeColor(PAPER_DARK)
        c.line(x + 7 * mm, y + card_height - 31 * mm, x + card_width - 7 * mm, y + card_height - 31 * mm)
        lines = [f"<b>Beschreibung:</b> {escape(item.get('playerCardDetail', item['detail']))}"]
        lines.extend(escape(use) for use in item.get("playerCardUses", []))
        if item.get("weapon"):
            weapon = item["weapon"]
            lines.append(f"<b>Waffe:</b> {escape(weapon['skill'])} · {escape(weapon['damageDice'])} Schaden · nicht parierbar")
        paragraph(
            c,
            "<br/><br/>".join(lines),
            x + 7 * mm,
            y + 9 * mm,
            card_width - 14 * mm,
            card_height - 43 * mm,
            text_style(f"safe-item-{index}", 7.4, 9.2, CHARCOAL),
        )
        c.setFillColor(QUIET)
        c.setFont("Helvetica-Oblique", 6.4)
        c.drawString(x + 7 * mm, y + 4 * mm, "Ausschneiden · Weitergeben erlaubt · Anwendung abstreichen")


def draw_player_map(c: canvas.Canvas, map_entry: dict, legend: str) -> None:
    c.setPageSize(landscape(A4))
    width, height = landscape(A4)
    page_title(c, map_entry["title"], "Spielerkarte · spoilerfrei")
    image_cover(c, ASSETS / map_entry["playerAsset"], 18 * mm, 24 * mm, width - 36 * mm, height - 72 * mm)
    c.setFillColor(FROST)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(20 * mm, 12 * mm, legend)


def draw_ending_cards(c: canvas.Canvas, data: dict) -> None:
    c.setPageSize(A4)
    width, height = A4
    endings = {entry["id"]: entry for entry in data["endings"]}
    cards = [
        ("ÖFFNEN", "Gastrecht widerrufen", "Das Dorf spricht öffentlich aus, dass Gruber das Gastrecht gebrochen hat. Die Opferung endet.", endings["E01"]["cost"]),
        ("ERINNERN", "Gastrecht erneuern", "Die Namen der verschwundenen Gäste werden laut genannt und an der Eiche zurückgegeben. Die Opferung endet.", endings["E02"]["cost"]),
        ("BRECHEN", "Bindung zerstören", "Altes Eisen und Feuer zerstören die Geweihreliquie. Der Knochenhirsch bricht zusammen.", endings["E03"]["cost"]),
    ]
    margin = 12 * mm
    gap = 5 * mm
    card_height = (height - 2 * margin - 2 * gap) / 3
    for index, (verb, title, result, cost) in enumerate(cards):
        y = height - margin - (index + 1) * card_height - index * gap
        c.setFillColor(PAPER)
        c.setStrokeColor(RUST)
        c.setLineWidth(1.3)
        c.roundRect(margin, y, width - 2 * margin, card_height, 3 * mm, fill=1, stroke=1)
        c.setFillColor(RUST)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(margin + 8 * mm, y + card_height - 11 * mm, "ENTSCHEIDUNG AN DER ALTEN EICHE")
        c.setFillColor(CHARCOAL)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(margin + 8 * mm, y + card_height - 23 * mm, verb)
        c.setFillColor(COBALT)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin + 52 * mm, y + card_height - 22 * mm, title)
        paragraph(c, f"<b>Was geschieht:</b> {escape(result)}<br/><br/><b>Preis:</b> {escape(cost)}", margin + 8 * mm, y + 12 * mm, width - 2 * margin - 16 * mm, card_height - 43 * mm, text_style(f"ending-{index}", 9.2, 12, CHARCOAL))
        c.setFillColor(QUIET)
        c.setFont("Helvetica-Oblique", 6.5)
        c.drawString(margin + 8 * mm, y + 5 * mm, "Ausschneiden und erst im Finale auslegen")


def build_player_body(path: Path, data: dict) -> None:
    maps = {entry["id"]: entry for entry in data["maps"]}
    handouts = {entry["id"]: entry for entry in data["handouts"]}
    c = canvas.Canvas(str(path), pagesize=A4)
    draw_player_rules(c)
    c.showPage()
    draw_handout(c, "H01", handouts["H01"]["title"])
    c.showPage()
    draw_item_cards_page(c, data)
    c.showPage()
    draw_player_map(c, maps["MAP01"], MAP_ORDER[0][1])
    c.showPage()
    draw_player_map(c, maps["MAP02"], MAP_ORDER[1][1])
    c.showPage()
    for handout_id in ("H02", "H03"):
        c.setPageSize(A4)
        draw_handout(c, handout_id, handouts[handout_id]["title"])
        c.showPage()
    draw_player_map(c, maps["MAP03"], MAP_ORDER[2][1])
    c.showPage()
    c.setPageSize(A4)
    draw_handout(c, "H04", handouts["H04"]["title"])
    c.showPage()
    draw_player_map(c, maps["MAP04"], MAP_ORDER[3][1])
    c.showPage()
    c.setPageSize(A4)
    draw_handout(c, "H06", handouts["H06"]["title"])
    c.showPage()
    for handout_id in ("H07", "H08", "H10"):
        c.setPageSize(A4)
        draw_handout(c, handout_id, handouts[handout_id]["title"])
        c.showPage()
    draw_player_map(c, maps["MAP05"], MAP_ORDER[4][1])
    c.showPage()
    c.setPageSize(A4)
    draw_handout(c, "H05", handouts["H05"]["title"])
    c.showPage()
    c.setPageSize(A4)
    draw_handout(c, "H09", handouts["H09"]["title"])
    c.showPage()
    draw_player_map(c, maps["MAP06"], MAP_ORDER[5][1])
    c.showPage()
    draw_ending_cards(c, data)
    c.showPage()
    c.save()


def merge_player_pack(invitation_path: Path, body_path: Path) -> None:
    writer = PdfWriter()
    for source in (invitation_path, body_path):
        for page in PdfReader(str(source)).pages:
            writer.add_page(page)
    writer.add_metadata({
        "/Title": "Krähenfels - Spielermaterial",
        "/Subject": "Spoilerfreies Druck- und Versandpaket",
        "/Author": "Krähenfels Spielleitung",
    })
    with PLAYER_PDF.open("wb") as output:
        writer.write(output)


def draw_timeline_page(c: canvas.Canvas, data: dict) -> None:
    width, height = A4
    page_title(c, "NPC-Regie", "Wer tritt wann auf? · Schnellübersicht")
    intro = "Spiele nie alle Figuren gleichzeitig. Pro Szene reicht meist eine führende Stimme und höchstens eine zweite Figur, die widerspricht oder einen Hinweis gibt. Die Spielerfiguren behalten das letzte Wort."
    paragraph(c, intro, 18 * mm, height - 65 * mm, width - 36 * mm, 20 * mm, text_style("npc-intro", 10, 13, colors.white))
    rows = [
        ("S01", "Kutschenpanne", "Keine feste Dorfperson. Nur Kutscherstimme aus dem Wald, falls du Druck brauchst."),
        ("S02", "Gasthaus", "Gruber begrüßt zuerst. Elara beobachtet hinter der Theke. Leni erscheint später und nur kurz."),
        ("S03", "Kirche", "Falk an der Sakristeitür. Er gibt H04 bei der richtigen Frage, nicht nach einem Pflichtwurf."),
        ("S04", "Schmiede", "Marta prüft die Absicht. Danach zeigt sie H06 und gibt bei klarer Entscheidung altes Eisen."),
        ("S05", "Waldspur", "Leni gibt H07 am sicheren Waldrand und bleibt zurück. Elias gibt H08 und die drei Verben."),
        ("S06", "Archiv", "Gruber konfrontiert die Gruppe. Elara und Falk nur bei gewonnenem Vertrauen. Marta und Elias bleiben Erinnerung oder frühere Aussage."),
        ("S07", "Alte Eiche", "Gruber führt die Prozession. Elara, Elias und Marta helfen nur nach vorherigem Vertrauen. Leni bleibt im Gasthaus, Falk bei der Kirche."),
        ("S08", "Epilog", "Zuerst die Spielerfiguren. Danach höchstens ein oder zwei kurze NPC-Sätze, passend zum gewählten Ende."),
    ]
    top = height - 91 * mm
    row_height = 23 * mm
    for index, (scene_id, title, direction) in enumerate(rows):
        y = top - (index + 1) * row_height
        c.setFillColor(PANEL if index % 2 == 0 else PANEL_RAISED)
        c.roundRect(18 * mm, y, width - 36 * mm, row_height - 2 * mm, 2 * mm, fill=1, stroke=0)
        c.setFillColor(COBALT)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(23 * mm, y + row_height - 10 * mm, scene_id)
        c.setFillColor(FROST)
        c.drawString(40 * mm, y + row_height - 10 * mm, title)
        paragraph(c, direction, 23 * mm, y + 4 * mm, width - 46 * mm, row_height - 15 * mm, text_style(f"timeline-{scene_id}", 7.5, 9.2, colors.white))
    c.setFillColor(QUIET)
    c.setFont("Helvetica", 7)
    c.drawString(18 * mm, 12 * mm, "Regie statt Dialog: Nutze die Impulse situativ und gib die Entscheidung immer an die Spielerfiguren zurück.")


def draw_secret_box(c: canvas.Canvas, x: float, y: float, width: float, title: str, entries: list[str], accent) -> None:
    box_height = 28 * mm
    c.setFillColor(PANEL)
    c.setStrokeColor(accent)
    c.setLineWidth(0.7)
    c.roundRect(x, y, width, box_height, 2 * mm, fill=1, stroke=1)
    c.setFillColor(accent)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x + 5 * mm, y + box_height - 8 * mm, title.upper())
    text = "<br/>".join(f"• {escape(entry)}" for entry in entries)
    paragraph(c, text, x + 5 * mm, y + 5 * mm, width - 10 * mm, box_height - 15 * mm, text_style(f"secret-{title}-{x}", 7.2, 9, colors.white))


def draw_npc_page(c: canvas.Canvas, npc: dict, scenes: dict[str, dict]) -> None:
    width, height = A4
    page_title(c, npc["name"], f"{npc['role']} · NPC-Dossier")
    paragraph(c, escape(npc["description"]), 18 * mm, height - 63 * mm, width - 36 * mm, 18 * mm, text_style(f"desc-{npc['id']}", 9.6, 12, colors.white))
    gap = 6 * mm
    box_width = (width - 36 * mm - gap) / 2
    draw_secret_box(c, 18 * mm, height - 101 * mm, box_width, "Weiß", npc.get("knows", []), COBALT)
    draw_secret_box(c, 18 * mm + box_width + gap, height - 101 * mm, box_width, "Verschweigt", npc.get("hides", []), WARNING)

    appearances = npc.get("appearances", [])
    start_y = height - 106 * mm
    bottom = 13 * mm
    gap_y = 3 * mm
    card_height = (start_y - bottom - gap_y * max(0, len(appearances) - 1)) / max(1, len(appearances))
    for index, appearance in enumerate(appearances):
        y = start_y - (index + 1) * card_height - index * gap_y
        scene = scenes.get(appearance["sceneId"], {})
        c.setFillColor(PANEL_RAISED)
        c.setStrokeColor(PAPER_DARK)
        c.setLineWidth(0.5)
        c.roundRect(18 * mm, y, width - 36 * mm, card_height, 2.5 * mm, fill=1, stroke=1)
        c.setFillColor(COBALT)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(23 * mm, y + card_height - 7 * mm, f"{appearance['sceneId']} · {scene.get('shortTitle', scene.get('title', 'Szene'))}")
        presence = appearance.get("presence", {})
        mode = presence.get("mode", "always")
        mode_label = {
            "always": "einsetzen",
            "conditional": "situationsabhängig",
            "contextual": "situationsabhängig",
            "manual": "manuell",
            "afterClue": "nach Hinweis",
            "afterStep": "nach Schritt",
            "state": "nach Haltung",
            "ending": "im Epilog",
            "never": "nicht einsetzen",
        }.get(mode, mode)
        c.setFillColor(WARNING if mode == "never" else RUST if mode in {"conditional", "contextual", "manual", "afterClue", "afterStep", "state", "ending"} else COBALT)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawRightString(width - 23 * mm, y + card_height - 7 * mm, mode_label.upper())

        # Keep the page count stable while still carrying every new direction
        # field. Each appearance is a compact two-column briefing: the left
        # column answers why/how, the right column handles concrete clue cues.
        inner_x = 23 * mm
        inner_y = y + 2.5 * mm
        inner_width = width - 46 * mm
        body_height = max(8 * mm, card_height - 10 * mm)
        column_gap = 4 * mm
        left_width = inner_width * 0.44
        right_width = inner_width - left_width - column_gap
        left_content = (
            f"<b>EINSETZEN:</b> {escape(presence.get('instruction', ''))}<br/>"
            f"<b>NICHT:</b> {escape(presence.get('absentInstruction', ''))}<br/>"
            f"<b>WARUM:</b> {escape(appearance.get('reason', ''))}<br/>"
            f"<b>LAUNE:</b> {escape(appearance.get('mood', ''))}<br/>"
            f"<b>ZIEL:</b> {escape(appearance.get('goal', ''))}<br/>"
            f"<b>VERHALTEN:</b> {escape(appearance.get('behavior', ''))}<br/>"
            f"<b>NÄCHSTES:</b> {escape(appearance.get('nextAction', ''))}"
        )
        reaction_blocks = []
        for reaction in appearance.get("clueReactions", []):
            target = reaction.get("targetState")
            target_suffix = f" · Haltung: {escape(target)}" if target else ""
            reaction_blocks.append(
                f"<b>{escape(reaction.get('clueID', ''))} · WENN HINWEIS GEZEIGT:</b> {escape(reaction.get('reaction', ''))}<br/>"
                f"<b>KLAR:</b> {escape(reaction.get('reveals', ''))}<br/>"
                f"<b>DANACH:</b> {escape(reaction.get('nextAction', ''))}{target_suffix}"
            )
        right_content = "<br/>".join(reaction_blocks) or "Keine konkrete Hinweisreaktion hinterlegt; Haltung und Ziel beibehalten."
        paragraph(c, left_content, inner_x, inner_y, left_width, body_height, text_style(f"appearance-left-{npc['id']}-{index}", 5.55, 6.25, colors.white))
        divider_x = inner_x + left_width + column_gap / 2
        c.setStrokeColor(PAPER_DARK)
        c.setLineWidth(0.35)
        c.line(divider_x, inner_y, divider_x, inner_y + body_height)
        paragraph(c, right_content, inner_x + left_width + column_gap, inner_y, right_width, body_height, text_style(f"appearance-right-{npc['id']}-{index}", 5.2, 5.9, colors.white))
    footer = f"Haltungen: {', '.join(npc.get('states', []))}"
    if npc.get("givesHandoutIds"):
        footer += f" · Verknüpft: {', '.join(npc['givesHandoutIds'])}"
    c.setFillColor(QUIET)
    c.setFont("Helvetica", 7)
    c.drawString(18 * mm, 11 * mm, footer)


def build_npc_guide(data: dict) -> None:
    c = canvas.Canvas(str(NPC_PDF), pagesize=A4)
    draw_timeline_page(c, data)
    c.showPage()
    scenes = {entry["id"]: entry for entry in data["scenes"]}
    for npc in data["npcs"]:
        draw_npc_page(c, npc, scenes)
        c.showPage()
    c.save()


def write_page_map() -> None:
    PAGE_MAP.write_text(
        json.dumps(
            [{"page": index + 1, "name": name} for index, name in enumerate(PAGE_NAMES)],
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    data = load_manifest()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    invitation_path = TMP_DIR / "invitation.pdf"
    body_path = TMP_DIR / "player-body.pdf"
    original_invitation_path = build_invitation.PDF_PATH
    try:
        build_invitation.PDF_PATH = invitation_path
        build_invitation.build_invitation()
    finally:
        build_invitation.PDF_PATH = original_invitation_path
    build_player_body(body_path, data)
    merge_player_pack(invitation_path, body_path)
    build_npc_guide(data)
    write_page_map()
    print(f"Wrote {PLAYER_PDF}")
    print(f"Wrote {NPC_PDF}")
    print(f"Wrote {PAGE_MAP}")


if __name__ == "__main__":
    main()
