#!/usr/bin/env python3
"""Build the printable Kraehenfels game pack.

The script intentionally draws the maps as vector diagrams. They remain legible
in black and white and do not depend on external image assets.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, A5, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs"
OUTPUT.mkdir(exist_ok=True)


def register_fonts() -> tuple[str, str]:
    candidates = [
        (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/arialbd.ttf")),
        (Path("C:/Windows/Fonts/segoeui.ttf"), Path("C:/Windows/Fonts/segoeuib.ttf")),
        (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")),
    ]
    for regular, bold in candidates:
        if regular.exists() and bold.exists():
            pdfmetrics.registerFont(TTFont("KraehenSans", str(regular)))
            pdfmetrics.registerFont(TTFont("KraehenSansBold", str(bold)))
            return "KraehenSans", "KraehenSansBold"
    return "Helvetica", "Helvetica-Bold"


FONT, FONT_BOLD = register_fonts()
INK = colors.HexColor("#152338")
FROST = colors.HexColor("#B8D5E8")
BLUE = colors.HexColor("#2F6FA3")
PALE = colors.HexColor("#F2F6F8")
LINE = colors.HexColor("#9AAEBA")
RED = colors.HexColor("#9A4E4E")


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text.replace("&", "&amp;"), style)


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="KTitle", parent=styles["Title"], fontName=FONT_BOLD,
    fontSize=22, leading=26, textColor=INK, alignment=TA_LEFT,
    spaceAfter=5 * mm,
))
styles.add(ParagraphStyle(
    name="KSub", parent=styles["Normal"], fontName=FONT,
    fontSize=10, leading=13, textColor=BLUE, spaceAfter=4 * mm,
))
styles.add(ParagraphStyle(
    name="KBody", parent=styles["BodyText"], fontName=FONT,
    fontSize=9.6, leading=13.4, textColor=INK, spaceAfter=2.2 * mm,
))
styles.add(ParagraphStyle(
    name="KSmall", parent=styles["BodyText"], fontName=FONT,
    fontSize=8, leading=10.2, textColor=INK, spaceAfter=1.2 * mm,
))
styles.add(ParagraphStyle(
    name="KCardTitle", parent=styles["Heading2"], fontName=FONT_BOLD,
    fontSize=15, leading=18, textColor=INK, spaceAfter=2 * mm,
))
styles.add(ParagraphStyle(
    name="KCenter", parent=styles["Normal"], fontName=FONT,
    fontSize=10, leading=13, textColor=INK, alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="KMap", parent=styles["Normal"], fontName=FONT_BOLD,
    fontSize=9, leading=11, textColor=INK, alignment=TA_CENTER,
))


def page_frame(canv: canvas.Canvas, doc: BaseDocTemplate) -> None:
    canv.saveState()
    width, height = doc.pagesize
    canv.setStrokeColor(LINE)
    canv.setLineWidth(0.5)
    canv.line(16 * mm, 12 * mm, width - 16 * mm, 12 * mm)
    canv.setFont(FONT, 7.5)
    canv.setFillColor(BLUE)
    canv.drawString(16 * mm, 7 * mm, "KRÄHENFELS  /  DIE WEISSE FRAU SCHWEIGT")
    canv.drawRightString(width - 16 * mm, 7 * mm, f"{doc.page:02d}")
    canv.restoreState()


def build_story_pdf(path: Path, story: list, title: str, pagesize=A4) -> None:
    doc = BaseDocTemplate(
        str(path), pagesize=pagesize, leftMargin=17 * mm, rightMargin=17 * mm,
        topMargin=15 * mm, bottomMargin=17 * mm, title=title,
        author="Kraehenfels",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=page_frame)])
    doc.build(story)


def title_block(title: str, subtitle: str = "") -> list:
    items = [p(title, styles["KTitle"])]
    if subtitle:
        items.append(p(subtitle, styles["KSub"]))
    return items


def draw_map(path: Path, gm: bool = False) -> None:
    width, height = landscape(A4)
    c = canvas.Canvas(str(path), pagesize=(width, height), pageCompression=1)
    c.setTitle("Kraehenfels Karte")
    c.setFillColor(PALE)
    c.rect(0, 0, width, height, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 21)
    c.drawString(18 * mm, height - 19 * mm, "Krähenfels")
    c.setFont(FONT, 9)
    c.setFillColor(BLUE)
    c.drawString(18 * mm, height - 25 * mm, "Handskizze für die Reise durch den Schwarzwald")
    if gm:
        c.setFillColor(RED)
        c.setFont(FONT_BOLD, 9)
        c.drawRightString(width - 18 * mm, height - 20 * mm, "SL-KARTE / SPOILER")
    else:
        c.setFillColor(BLUE)
        c.setFont(FONT_BOLD, 9)
        c.drawRightString(width - 18 * mm, height - 20 * mm, "SPIELERKARTE")

    # Roads and terrain
    c.setStrokeColor(colors.HexColor("#6E8797"))
    c.setLineWidth(2.3)
    c.bezier(40 * mm, 54 * mm, 95 * mm, 103 * mm, 131 * mm, 45 * mm, 251 * mm, 48 * mm)
    c.setLineWidth(1.0)
    c.bezier(51 * mm, 59 * mm, 82 * mm, 17 * mm, 114 * mm, 22 * mm, 132 * mm, 50 * mm)
    c.bezier(137 * mm, 49 * mm, 151 * mm, 93 * mm, 178 * mm, 110 * mm, 214 * mm, 127 * mm)
    # Bach
    c.setStrokeColor(BLUE)
    c.setLineWidth(2)
    c.bezier(38 * mm, 120 * mm, 78 * mm, 108 * mm, 97 * mm, 133 * mm, 132 * mm, 118 * mm)
    c.bezier(132 * mm, 118 * mm, 172 * mm, 101 * mm, 208 * mm, 132 * mm, 254 * mm, 113 * mm)
    # Woods
    c.setStrokeColor(colors.HexColor("#B0C1C5"))
    c.setLineWidth(0.8)
    for x in range(39, 249, 11):
        c.line(x * mm, 30 * mm, (x + 8) * mm, 142 * mm)
    # locations
    places = {
        "Zur Krähe": (100, 73),
        "Kirche / Friedhof": (151, 93),
        "Schmiede": (75, 44),
        "Brücke": (122, 54),
        "alter Grubenweg": (198, 115),
        "Kutschenweg nach Freiburg": (39, 50),
        "verlassene Grube": (224, 131),
    }
    c.setFillColor(INK)
    for label, (x, y) in places.items():
        c.setFillColor(colors.white)
        c.circle(x * mm, y * mm, 4.2 * mm, stroke=0, fill=1)
        c.setStrokeColor(INK)
        c.setLineWidth(1.1)
        c.circle(x * mm, y * mm, 4.2 * mm, stroke=1, fill=0)
        c.setFillColor(INK)
        c.setFont(FONT_BOLD if label in {"Zur Krähe", "Kirche / Friedhof"} else FONT, 7.4)
        c.drawCentredString(x * mm, y * mm - 7 * mm, label)
    # Hidden routes and clues on GM map
    if gm:
        c.setStrokeColor(RED)
        c.setLineWidth(1.4)
        c.setDash(4, 3)
        c.bezier(151 * mm, 91 * mm, 166 * mm, 72 * mm, 186 * mm, 72 * mm, 204 * mm, 65 * mm)
        c.bezier(204 * mm, 65 * mm, 219 * mm, 59 * mm, 222 * mm, 44 * mm, 225 * mm, 32 * mm)
        c.setDash()
        c.setFillColor(RED)
        c.setFont(FONT_BOLD, 8)
        c.drawString(176 * mm, 69 * mm, "Flutstollen")
        c.drawString(218 * mm, 38 * mm, "Kammer")
        c.setFont(FONT, 7.3)
        c.drawString(165 * mm, 61 * mm, "H08: Plan")
        c.drawString(215 * mm, 25 * mm, "H09: Sauter")
        c.setFillColor(colors.HexColor("#F8E8E8"))
        c.roundRect(25 * mm, 19 * mm, 110 * mm, 21 * mm, 3 * mm, stroke=0, fill=1)
        c.setFillColor(RED)
        c.setFont(FONT_BOLD, 8)
        c.drawString(30 * mm, 33 * mm, "Wahrheit für die SL")
        c.setFont(FONT, 7.6)
        c.drawString(30 * mm, 26 * mm, "Elisabeth hat die Kinder gerettet. Der Widerhall trägt Stimmen.")
        c.drawString(30 * mm, 21 * mm, "Finale: 3 - 1 - 2 - 4 und Elisabeth Abele.")
    else:
        c.setFillColor(colors.white)
        c.roundRect(25 * mm, 19 * mm, 100 * mm, 21 * mm, 3 * mm, stroke=0, fill=1)
        c.setStrokeColor(LINE)
        c.roundRect(25 * mm, 19 * mm, 100 * mm, 21 * mm, 3 * mm, stroke=1, fill=0)
        c.setFillColor(INK)
        c.setFont(FONT_BOLD, 8)
        c.drawString(30 * mm, 33 * mm, "Randnotiz")
        c.setFont(FONT, 7.6)
        c.drawString(30 * mm, 26 * mm, "Nach Sonnenuntergang keine Glocke.")
        c.drawString(30 * mm, 21 * mm, "Kein Singen. Keine fremden Namen rufen.")
    # compass and scale
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 8)
    c.drawString(width - 35 * mm, 32 * mm, "N")
    c.setStrokeColor(INK)
    c.setLineWidth(1)
    c.line(width - 34 * mm, 22 * mm, width - 34 * mm, 30 * mm)
    c.line(width - 34 * mm, 30 * mm, width - 36 * mm, 26 * mm)
    c.line(width - 34 * mm, 30 * mm, width - 32 * mm, 26 * mm)
    c.line(width - 57 * mm, 20 * mm, width - 37 * mm, 20 * mm)
    c.setFont(FONT, 7)
    c.drawCentredString(width - 47 * mm, 14 * mm, "ca. 500 Schritte")
    c.setStrokeColor(LINE)
    c.line(18 * mm, 12 * mm, width - 18 * mm, 12 * mm)
    c.setFillColor(BLUE)
    c.setFont(FONT, 7.5)
    c.drawString(18 * mm, 7 * mm, "KRÄHENFELS  /  DIE WEISSE FRAU SCHWEIGT")
    c.drawRightString(width - 18 * mm, 7 * mm, "KARTE")
    c.showPage()
    c.save()


def draw_mine_plan(path: Path, gm: bool = False) -> None:
    """Draw H08 as an incomplete mine plan with an optional SL overlay."""
    width, height = landscape(A4)
    c = canvas.Canvas(str(path), pagesize=(width, height), pageCompression=1)
    c.setTitle("Alter Flur- und Grubenplan")
    c.setFillColor(colors.white)
    c.rect(0, 0, width, height, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 21)
    c.drawString(18 * mm, height - 19 * mm, "H08  /  Alter Flur- und Grubenplan")
    c.setFont(FONT, 9)
    c.setFillColor(BLUE)
    c.drawString(18 * mm, height - 25 * mm, "Gefunden zwischen Werkzeugkiste und nassem Holz")
    if gm:
        c.setFillColor(RED)
        c.setFont(FONT_BOLD, 9)
        c.drawRightString(width - 18 * mm, height - 20 * mm, "SL-OVERLAY / SPOILER")
    else:
        c.setFillColor(BLUE)
        c.setFont(FONT_BOLD, 9)
        c.drawRightString(width - 18 * mm, height - 20 * mm, "SPIELERHANDOUT")

    left, bottom = 25 * mm, 28 * mm
    c.setStrokeColor(LINE)
    c.setLineWidth(1.2)
    c.roundRect(left, bottom, 200 * mm, 102 * mm, 3 * mm, stroke=1, fill=0)
    # Three routes
    c.setStrokeColor(INK)
    c.setLineWidth(2.3)
    c.line(38 * mm, 80 * mm, 84 * mm, 80 * mm)
    c.line(84 * mm, 80 * mm, 112 * mm, 102 * mm)
    c.line(84 * mm, 80 * mm, 117 * mm, 57 * mm)
    c.line(117 * mm, 57 * mm, 159 * mm, 57 * mm)
    c.setLineWidth(1.4)
    c.setDash(4, 3)
    c.line(159 * mm, 57 * mm, 199 * mm, 57 * mm)
    c.setDash()
    c.line(84 * mm, 80 * mm, 84 * mm, 123 * mm)
    c.line(84 * mm, 123 * mm, 138 * mm, 123 * mm)
    c.line(138 * mm, 123 * mm, 170 * mm, 108 * mm)
    # rooms
    c.setFillColor(PALE)
    c.rect(30 * mm, 73 * mm, 18 * mm, 14 * mm, stroke=0, fill=1)
    c.rect(105 * mm, 95 * mm, 18 * mm, 14 * mm, stroke=0, fill=1)
    c.rect(151 * mm, 50 * mm, 18 * mm, 14 * mm, stroke=0, fill=1)
    c.rect(163 * mm, 101 * mm, 22 * mm, 14 * mm, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 8)
    c.drawCentredString(39 * mm, 79 * mm, "Mundloch")
    c.drawCentredString(114 * mm, 101 * mm, "Kapelle")
    c.drawCentredString(160 * mm, 56 * mm, "Flutstollen")
    c.drawCentredString(174 * mm, 107 * mm, "Abele")
    c.setFont(FONT, 7.4)
    c.drawString(48 * mm, 84 * mm, "Försterweg")
    c.drawString(88 * mm, 67 * mm, "Bachlauf")
    c.drawString(90 * mm, 119 * mm, "Seilzugweg")
    c.setFillColor(BLUE)
    c.drawString(30 * mm, 34 * mm, "Notiz am Rand: Der Plan ist an drei Stellen nass und nicht vollständig lesbar.")
    if gm:
        c.setStrokeColor(RED)
        c.setLineWidth(1.4)
        c.circle(160 * mm, 57 * mm, 7 * mm, stroke=1, fill=0)
        c.setFillColor(RED)
        c.setFont(FONT_BOLD, 8)
        c.drawString(171 * mm, 62 * mm, "Hier liegt der Flutstollen")
        c.drawString(171 * mm, 51 * mm, "Widerhall unter dem Stein")
        c.setStrokeColor(RED)
        c.setDash(3, 2)
        c.line(174 * mm, 101 * mm, 174 * mm, 80 * mm)
        c.setDash()
        c.setFont(FONT, 7.2)
        c.drawString(177 * mm, 84 * mm, "Kammer unter")
        c.drawString(177 * mm, 78 * mm, "der Kapelle")
    c.setStrokeColor(LINE)
    c.line(18 * mm, 12 * mm, width - 18 * mm, 12 * mm)
    c.setFillColor(BLUE)
    c.setFont(FONT, 7.5)
    c.drawString(18 * mm, 7 * mm, "KRÄHENFELS  /  H08")
    c.drawRightString(width - 18 * mm, 7 * mm, "GRUBENPLAN")
    c.showPage()
    c.save()


HANDOUTS = {
    "H01": ("Kutschschein und Frachtzettel", "POSTKUTSCHE FREIBURG – FREUDENSTADT<br/>17. November 1890, Abfahrt 16:10 Uhr<br/><br/>Fahrgäste: drei Reisende, Namen nicht eingetragen.<br/>Fracht: ein verschnürtes Eisenstück, Absender <b>W. Abele, Krähenfels</b>.<br/><br/><i>Nicht öffnen. Nicht läuten. Bei Frost nicht berühren.</i><br/><br/>Umleitung über Krähenfels wegen Schnee auf der Passstraße."),
    "H03": ("Krähenfelser Wochenblatt", "<b>Winterdienst verschoben</b><br/><br/>Der neue Klöppel für die obere Kirchenglocke ist eingetroffen. Die Montage wird bis zum Ende des Frostes verschoben. Die Glocke wird seit dem Unglück von 1848 nicht mehr nach Einbruch der Dunkelheit geläutet.<br/><br/><b>Vermisster Holzsammler</b><br/><br/>Wilhelm Abele, 42, wurde am alten Grubenweg zuletzt gesehen.<br/><br/><b>Aus dem Gemeinderat</b><br/><br/>Besucher sollen sich nach Sonnenuntergang in ihren Unterkünften aufhalten."),
    "H04": ("Kirchenbuchauszug", "<b>Krähenfels, 3. Dezember 1848</b><br/><br/>Heute wurde Elisabeth Abele, Kantorin und Lehrerin, im Schnee oberhalb der Grube gefunden. Sie hatte drei Kinder aus dem eingestürzten Stollen geführt. Der Rückweg blieb ihr versperrt.<br/><br/>Die Glocke schlug danach viermal, obwohl niemand im Turm war.<br/><br/><i>... nicht die Frau ...<br/>... was unter dem Stein ...<br/>... die Stimme ...</i>"),
    "H05": ("Kabinettfoto von 1848", "<br/><br/><b>ELISABETH ABELE</b><br/><br/>Krähenfels, Winter 1848<br/><br/>[Auf der Druckseite ist Platz für eine kleine gezeichnete Glocke.]<br/><br/><i>Sie hat uns herausgeführt. Warum erinnert sich niemand?</i>"),
    "H06": ("Liedblatt ohne letzte Strophe", "<b>Lied für den Heimweg</b><br/><br/>Wenn der erste Schnee fällt,<br/>wenn der zweite Weg schweigt,<br/>wenn der dritte Ton ruft,<br/>bleibt der vierte Stein.<br/><br/><font size='18'>3   1   2   4</font><br/><br/><i>Nicht die Glocke antwortet. Das Echo tut es.</i>"),
    "H07": ("Werkbuch der Stellmacherei", "<b>Eintrag vom 15. November 1890, Emil Bopp</b><br/><br/>Die Kutschenachse aus Freiburg ist sauber gearbeitet. Der Bruch sitzt nicht an der schwächsten Stelle. Metallstaub liegt im Holz, als hätte etwas von innen dagegen geschlagen.<br/><br/>Der neue Glockenklöppel besteht aus altem Grubeneisen. Beim Anschlagen summt er, auch wenn die Glocke gedämpft wird.<br/><br/><b>Nicht zusammen mit der Glocke lagern.</b>"),
    "H08": ("Alter Flur- und Grubenplan", "<b>Drei Wege vom Dorf zur verlassenen Grube</b><br/><br/>1. Försterweg, endet am verschütteten Mundloch<br/>2. Bachlauf, führt zu einem niedrigen Flutstollen<br/>3. alter Seilzugweg, führt zu einer Kammer unter der Kapelle<br/><br/>Kreis am Rand: <b>Abele, Werkzeug und Liedblatt</b>."),
    "H09": ("Bericht von Lorenz Sauter", "<i>Ich höre schlecht, aber der Berg hört zu gut.</i><br/><br/>Die Stimmen kommen nicht aus einer Richtung. Sie nehmen Wörter, die gerade gesprochen wurden, und geben sie später zurück. Erst leise. Dann mit einer Stimme, die man kennt.<br/><br/>Elisabeth war nicht die Frau, die den Berg weckte. Sie war die Frau, die ihn unten hielt.<br/><br/>Wenn ihr den Klöppel habt, lasst ihn nicht allein schwingen. Gebt ihm eine Antwort."),
    "H10": ("Elisabeths Brief", "<b>An Wilhelm, falls ich nicht zurückkehre.</b><br/><br/>Die Leute werden sagen, ich hätte die Kinder in die Grube geführt. Das stimmt nicht. Ich habe sie herausgeführt. Was unten blieb, trägt unsere Stimmen wie Mäntel.<br/><br/>Der neue Klöppel ist aus dem Eisen des ersten Einsturzes. Er öffnet den Widerhall, wenn er ohne Antwort läutet. Nennt meinen vollen Namen und singt die Gegenfolge: <b>drei, eins, zwei, vier</b>.<br/><br/>Wenn niemand antwortet, schmilzt das Eisen. Wenn ihr schweigt, hört der Berg auf euch.<br/><br/><b>Elisabeth Abele</b>"),
    "H11": ("Finale: Schlagfolge und Lied", "<b>1.</b> Klöppel sichern oder schmelzen.<br/><b>2.</b> Gegenfolge hörbar machen: <b>3 – 1 – 2 – 4</b>.<br/><b>3.</b> Den Namen vollständig sprechen: <b>Elisabeth Abele</b>.<br/><b>4.</b> Entscheiden, ob die Glocke, die Grube oder das Eisen das Ende trägt.<br/><br/><i>Die Weiße Frau greift niemanden an. Sie wartet auf eine Antwort, die nicht aus dem Berg kommt.</i>"),
}


def build_handouts(path: Path) -> None:
    story: list = []
    for index, (hid, (title, body)) in enumerate(HANDOUTS.items()):
        if index % 2 == 0:
            story.extend(title_block("Spielerhinweise", "Ausschneiden oder als A5-Seite drucken"))
        card = [
            p(f"{hid}  /  {title}", styles["KCardTitle"]),
            p(body, styles["KBody"]),
            Spacer(1, 3 * mm),
        ]
        table = Table([[card]], colWidths=[170 * mm], rowHeights=[90 * mm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("BOX", (0, 0), (-1, -1), 1.1, LINE),
            ("LEFTPADDING", (0, 0), (-1, -1), 7 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 6 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5 * mm),
        ]))
        story.append(table)
        story.append(Spacer(1, 5 * mm))
        if index % 2 == 1:
            story.append(PageBreak())
    if story and isinstance(story[-1], PageBreak):
        story.pop()
    build_story_pdf(path, story, "Spielerhinweise")


def build_character_sheet(path: Path) -> None:
    story = title_block("Figurenbau", "How to be a Hero / drei Reisende / 400 Fähigkeitspunkte")
    story += [
        p("Name: ____________________________________    Alter: ______    Beruf: ______________________________", styles["KBody"]),
        p("Persönlicher Gegenstand: __________________________________________________________________________", styles["KBody"]),
        Spacer(1, 2 * mm),
        p("Rollenimpuls", styles["KCardTitle"]),
        p("Was kann deine Figur, das in dieser Kutsche nützlich wird? ________________________________________________________________", styles["KBody"]),
        p("Was darf die Gruppe niemals erfahren? __________________________________________________________________________________", styles["KBody"]),
        Spacer(1, 2 * mm),
    ]
    rows = [["Begabung", "Punkte", "Begabung / 10", "Fähigkeiten und Punkte"], ["Handeln", "", "", ""], ["Wissen", "", "", ""], ["Soziales", "", "", ""], ["Summe", "400", "", ""]]
    table = Table(rows, colWidths=[35 * mm, 24 * mm, 30 * mm, 81 * mm], rowHeights=[10 * mm, 18 * mm, 18 * mm, 18 * mm, 10 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INK), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD), ("FONTNAME", (0, 1), (-1, -1), FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5), ("GRID", (0, 0), (-1, -1), 0.6, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("BACKGROUND", (0, 4), (-1, 4), PALE),
        ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
    ]))
    story += [table, Spacer(1, 5 * mm), p("Lebenspunkte: 100 / ______    Geistesblitzpunkte: ______    Notizen", styles["KCardTitle"])]
    story += [p("__________________________________________________________________________________________________<br/><br/>__________________________________________________________________________________________________<br/><br/>__________________________________________________________________________________________________", styles["KBody"])]
    story.append(PageBreak())
    story += title_block("HTBAH auf einer Seite", "Diese Seite darf am Tisch liegen bleiben")
    story += [
        p("<b>Probe:</b> W100 gleich oder kleiner als der Wert ist Erfolg. Unteres Zehntel ist ein kritischer Erfolg. Ab 90 plus einem Zehntel ist es ein kritischer Patzer.", styles["KBody"]),
        p("<b>Begabung:</b> Punkte der Begabung addieren, durch 10 teilen und kaufmännisch runden. Begabung auf passende Fähigkeiten addieren, maximal 100.", styles["KBody"]),
        p("<b>Geistesblitz:</b> Begabung durch 10. Ein Punkt erlaubt einen neuen Wurf bei einer misslungenen, nicht kritischen Probe. Erneuert sich zum nächsten Abenteuer.", styles["KBody"]),
        p("<b>Schaden:</b> Unter 10 Lebenspunkten bewusstlos. Bei 0 tot. Mehr als 60 Schaden in einem Angriff macht bewusstlos.", styles["KBody"]),
        Spacer(1, 3 * mm),
        p("Rollenimpulse: Werkzeug / Notizbuch / gutes Gesicht / falscher Grund / Schnee lesen / nicht glauben", styles["KBody"]),
    ]
    build_story_pdf(path, story, "Figurenbau")


def build_start_pdf(path: Path) -> None:
    story = title_block("Die Weiße Frau schweigt", "Ein Schwarzwald-Folk-Horror für drei Spieler und eine Spielleitung")
    story += [
        p("<b>Auf einen Blick</b><br/>How to be a Hero, November 1890, Krähenfels. Die Figuren stranden nach einer Kutschenpanne und tragen einen Glockenklöppel ins Dorf. Die Nacht endet um Mitternacht, aber die Lösung darf an jedem Ort gefunden werden.", styles["KBody"]),
        Spacer(1, 3 * mm),
        p("<b>Was du vorbereitest</b><br/>01 Karten, 02 Handouts, 03 Figurenbau, 10 SL-Abenteuer und 11 Schnellreferenz. Die Soundboard-App kann parallel auf einem iPhone laufen. Ein Tischlautsprecher reicht.", styles["KBody"]),
        p("<b>Session-Rhythmus</b><br/>Ankunft 20 bis 30 Minuten · Dorf 20 bis 30 · Spuren 60 bis 90 · Erscheinung 15 bis 25 · Finale 35 bis 55 · Epilog 10.", styles["KBody"]),
        Spacer(1, 5 * mm),
        p("<b>Safety</b><br/>Vorher kurz absprechen: keine Gewalt gegen Kinder, keine sexualisierte Gewalt, keine detaillierte Folter. Ein Stoppsignal genügt. Horror darf leiser werden, ohne dass jemand die Runde erklären muss.", styles["KBody"]),
        Spacer(1, 7 * mm),
        p("<para alignment='center'><font size='16'>Die Glocke schweigt.<br/>Der Berg antwortet trotzdem.</font></para>", styles["KBody"]),
    ]
    build_story_pdf(path, story, "Spielstart")


def build_soundboard_cues(path: Path) -> None:
    rows = [["Cue", "Wann", "Bedienung", "Fallback am Tisch"]]
    cue_rows = [
        ("A01", "Kutschenpanne", "Loop leise, SFX01 beim Bruch", "Wind beschreiben, dann Holzknacken"),
        ("A03 / A04", "Dorf / Wirtshaus", "Atmosphäre wechseln, keine Musik nötig", "Stimmen absenken und Pausen setzen"),
        ("A06 / SFX08", "Kirche", "Glocke normal, dann falscher Ton", "3 – 1 – 2 – 4 auf Tisch klopfen"),
        ("A07 / SFX13", "Grube", "Wind, Stimmen ohne Worte, Boden", "Sätze der Spieler verzögert wiederholen"),
        ("A05 / M03", "Weiße Frau", "Musik erst nach der Stille starten", "Zwei hohe fallende Töne summen"),
        ("A08 / M04 / M05", "Finale", "Loop unter die Entscheidung, M04 nur einmal", "Liedblatt H06 sichtbar in die Mitte legen"),
        ("M06", "Epilog", "Einmal abspielen, danach Stille", "Fenster öffnen oder Wasser einschenken"),
    ]
    for row in cue_rows:
        rows.append(list(row))
    table = Table(rows, colWidths=[27 * mm, 42 * mm, 58 * mm, 50 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INK), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD), ("FONTNAME", (0, 1), (-1, -1), FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 8), ("LEADING", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.5 * mm), ("RIGHTPADDING", (0, 0), (-1, -1), 2.5 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5 * mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
    ]))
    story = title_block("Soundboard-Cues", "Jeder akustische Hinweis hat eine gedruckte Entsprechung")
    story += [p("Grundregel: Geräusch leise starten und nur hervorheben, wenn die Szene es verdient. Ein Cue darf auch ausbleiben. Die Sounddateien sind original prozedural erzeugt und ohne Sprachaufnahmen.", styles["KBody"]), Spacer(1, 4 * mm), table, Spacer(1, 6 * mm)]
    story += [p("Lautstärke: Master 35 bis 50 Prozent. SFX kurz auf 60 Prozent, nie dauerhaft. Bei empfindlichen Mitspielern alle Hochfrequenzen und die Herzschlagspur reduzieren.", styles["KBody"])]
    build_story_pdf(path, story, "Soundboard-Cues")


def build_sl_reference(path: Path) -> None:
    story = title_block("SL-Schnellreferenz", "Spoiler / offene Fäden / Enden")
    blocks = [
        ("Die Wahrheit", "Elisabeth Abele hat 1848 drei Kinder aus der Grube geführt. Der Widerhall unter dem Stein blieb zurück und kann Stimmen imitieren. Der neue Klöppel aus Grubeneisen öffnet ihn, wenn er ohne Gegenantwort läutet."),
        ("Die Pflichtspuren", "H01 bringt den Klöppel ins Spiel. H03 nennt 1848 und das Schweigegebot. H04 macht Elisabeth zur Retterin. H06 liefert 3 – 1 – 2 – 4. H07 erklärt die Vibration. H08 und H09 öffnen die Grube. H10 bestätigt die Lösung."),
        ("Ende A: Gegenlied", "Die Figuren antworten mit 3 – 1 – 2 – 4 und sprechen Elisabeth Abele. Der Widerhall bricht, Elisabeths Gestalt wird klar und der Schnee fällt normal."),
        ("Ende B: Flutstollen", "Die Figuren öffnen den Flutstollen. Die Grube wird überflutet. Das Dorf ist beschädigt, aber der Widerhall verliert seinen Resonanzraum."),
        ("Ende C: Eisen schmelzen", "Die Figuren schmelzen den Klöppel in der Schmiede unter bewusster Stille. Das Risiko ist hoch, aber der Ton findet keine Glocke mehr."),
        ("Improvisationsregel", "Wenn die Spieler eine gute Idee haben, gib ihr eine Spur. Ein Fehlschlag kostet Zeit, Wärme, Vertrauen oder einen Geistesblitz. Er blockiert niemals die einzige Information."),
    ]
    for heading, body in blocks:
        story += [p(heading, styles["KCardTitle"]), p(body, styles["KBody"]), Spacer(1, 2 * mm)]
    build_story_pdf(path, story, "SL-Schnellreferenz")


def build_sl_adventure(path: Path) -> None:
    raw = (ROOT / "content" / "scenario.md").read_text(encoding="utf-8")
    # Markdown-lite conversion, retaining headings and paragraphs.
    story = title_block("SL-Abenteuer", "Die Weiße Frau schweigt / spoilerhaltig")
    for block in re.split(r"\n\s*\n", raw):
        block = block.strip()
        if not block:
            continue
        if block.startswith("# "):
            story.append(p(block[2:], styles["KTitle"]))
        elif block.startswith("## "):
            story.append(p(block[3:], styles["KCardTitle"]))
        elif block.startswith("### "):
            story.append(p(block[4:], styles["KCardTitle"]))
        else:
            safe = block.replace("&", "&amp;").replace("\n", "<br/>")
            safe = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", safe)
            safe = re.sub(r"\*(.+?)\*", r"<i>\1</i>", safe)
            story.append(p(safe, styles["KBody"]))
    build_story_pdf(path, story, "SL-Abenteuer")


def main() -> None:
    draw_map(OUTPUT / "01_Karte_Spieler.pdf", gm=False)
    draw_map(OUTPUT / "01_Karte_SL.pdf", gm=True)
    draw_mine_plan(OUTPUT / "01_Grubenplan_H08.pdf", gm=False)
    draw_mine_plan(OUTPUT / "01_Grubenplan_SL.pdf", gm=True)
    build_handouts(OUTPUT / "02_Handouts.pdf")
    build_character_sheet(OUTPUT / "03_Figurenbau.pdf")
    build_start_pdf(OUTPUT / "00_Spielstart.pdf")
    build_sl_adventure(OUTPUT / "10_SL_Abenteuer.pdf")
    build_sl_reference(OUTPUT / "11_SL_Schnellreferenz.pdf")
    build_soundboard_cues(OUTPUT / "14_Soundboard-Cues.pdf")
    print(f"Wrote printable pack to {OUTPUT}")


if __name__ == "__main__":
    main()
