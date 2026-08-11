#!/usr/bin/env python3
"""Build the printable Kraehenfels game pack.

The player-facing props intentionally use different visual languages: a real
newspaper, church register, ticket, cabinet photograph, hymn sheet, workshop
ledger, witness statement, personal letter, and ritual card.
"""

from __future__ import annotations

import os
import re
import random
from pathlib import Path
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, A5, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Flowable,
    Image,
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
ASSETS = ROOT / "print" / "assets"
COVER_ART = ASSETS / "kraehenfels-cover.png"
ELISABETH_PHOTO = ASSETS / "elisabeth-abele-cabinet-photo.png"
BELL_ETCHING = ASSETS / "bell-and-clapper-etching.png"
AERIAL_MAP = ASSETS / "kraehenfels-aerial-map.png"
WOCHENBLATT_WOODCUT = ASSETS / "wochenblatt-woodcut.png"
STALLMACHEREI_ETCHING = ASSETS / "stallmacherei-technical-etching.png"
MINE_SURVEY = ASSETS / "alter-grubenplan-survey.png"
SCENE_ART = [
    ("S01 · Ankunft", ASSETS / "scene-arrival-graphic-novel.png"),
    ("S02 · Krähenfels", ASSETS / "scene-village-graphic-novel.png"),
    ("S03 · Kirche", ASSETS / "scene-chapel-graphic-novel.png"),
    ("S04 · Schmiede", ASSETS / "scene-forge-graphic-novel.png"),
    ("S05 · Grube", ASSETS / "scene-mine-graphic-novel.png"),
    ("S06 · Die Weiße Frau", ASSETS / "scene-white-woman-graphic-novel.png"),
    ("S08 · Finale", ASSETS / "scene-finale-graphic-novel.png"),
]


def register_fonts() -> tuple[str, str, str, str]:
    candidates = [
        (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/arialbd.ttf")),
        (Path("C:/Windows/Fonts/segoeui.ttf"), Path("C:/Windows/Fonts/segoeuib.ttf")),
        (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")),
    ]
    for regular, bold in candidates:
        if regular.exists() and bold.exists():
            pdfmetrics.registerFont(TTFont("KraehenSans", str(regular)))
            pdfmetrics.registerFont(TTFont("KraehenSansBold", str(bold)))
            serif = Path("C:/Windows/Fonts/georgia.ttf")
            serif_bold = Path("C:/Windows/Fonts/georgiab.ttf")
            if serif.exists() and serif_bold.exists():
                pdfmetrics.registerFont(TTFont("KraehenSerif", str(serif)))
                pdfmetrics.registerFont(TTFont("KraehenSerifBold", str(serif_bold)))
                return "KraehenSans", "KraehenSansBold", "KraehenSerif", "KraehenSerifBold"
            return "KraehenSans", "KraehenSansBold", "Times-Roman", "Times-Bold"
    return "Helvetica", "Helvetica-Bold", "Times-Roman", "Times-Bold"


FONT, FONT_BOLD, SERIF, SERIF_BOLD = register_fonts()
SCRIPT = SERIF
_script_font = Path("C:/Windows/Fonts/segoesc.ttf")
if _script_font.exists():
    pdfmetrics.registerFont(TTFont("KraehenScript", str(_script_font)))
    SCRIPT = "KraehenScript"
INK = colors.HexColor("#1C2827")
FROST = colors.HexColor("#B8D5E8")
BLUE = colors.HexColor("#315F67")
PALE = colors.HexColor("#E7ECE8")
LINE = colors.HexColor("#869A91")
RED = colors.HexColor("#7D392C")
PARCHMENT = colors.HexColor("#EFE4CF")
PARCHMENT_DARK = colors.HexColor("#D4C09A")
PINE = colors.HexColor("#233D39")
UMBER = colors.HexColor("#6B5137")
WAX = colors.HexColor("#75362C")


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text.replace("&", "&amp;"), style)


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="KTitle", parent=styles["Title"], fontName=SERIF_BOLD,
    fontSize=24, leading=28, textColor=INK, alignment=TA_LEFT,
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
    name="KCardTitle", parent=styles["Heading2"], fontName=SERIF_BOLD,
    fontSize=15, leading=18, textColor=INK, spaceAfter=2 * mm,
))


def scaled_image(path: Path, max_width: float, max_height: float) -> Image:
    """Return a proportionally scaled Platypus image."""
    source = ImageReader(str(path))
    width, height = source.getSize()
    scale = min(max_width / width, max_height / height)
    return Image(str(path), width=width * scale, height=height * scale)


def draw_parchment(c: canvas.Canvas, width: float, height: float, *, dark: bool = False) -> None:
    c.saveState()
    c.setFillColor(INK if dark else PARCHMENT)
    c.rect(0, 0, width, height, stroke=0, fill=1)
    if not dark:
        c.setStrokeColor(colors.HexColor("#DCCBAA"))
        c.setLineWidth(0.22)
        for offset in range(-20, int(width / mm) + 30, 9):
            c.line(offset * mm, 0, (offset + 20) * mm, height)
    c.restoreState()


def draw_fir(c: canvas.Canvas, x: float, y: float, size: float, color=PINE) -> None:
    c.saveState()
    c.setFillColor(color)
    c.setStrokeColor(color)
    c.setLineWidth(0.35)
    c.rect(x - size * 0.055, y, size * 0.11, size * 0.25, stroke=0, fill=1)
    for level, width_ratio in ((0.18, 0.42), (0.34, 0.60), (0.52, 0.82), (0.70, 1.0)):
        base_y = y + size * level
        half = size * width_ratio / 2
        c.line(x, base_y + size * 0.30, x - half, base_y)
        c.line(x, base_y + size * 0.30, x + half, base_y)
    c.restoreState()


def draw_bell_mark(c: canvas.Canvas, x: float, y: float, size: float, color=INK) -> None:
    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(max(0.55, size * 0.06))
    c.arc(x - size * 0.44, y - size * 0.17, x + size * 0.44, y + size * 0.62, 0, 180)
    c.line(x - size * 0.44, y + size * 0.22, x - size * 0.34, y - size * 0.34)
    c.line(x + size * 0.44, y + size * 0.22, x + size * 0.34, y - size * 0.34)
    c.line(x - size * 0.34, y - size * 0.34, x + size * 0.34, y - size * 0.34)
    c.circle(x, y - size * 0.40, size * 0.09, stroke=0, fill=1)
    c.line(x, y - size * 0.13, x, y - size * 0.40)
    c.restoreState()


def draw_house(c: canvas.Canvas, x: float, y: float, size: float, label: str | None = None) -> None:
    c.saveState()
    c.setFillColor(colors.HexColor("#CFC3A5"))
    c.setStrokeColor(UMBER)
    c.setLineWidth(0.7)
    c.rect(x - size * 0.42, y, size * 0.84, size * 0.43, stroke=1, fill=1)
    c.setFillColor(UMBER)
    roof = c.beginPath()
    roof.moveTo(x - size * 0.50, y + size * 0.43)
    roof.lineTo(x, y + size * 0.78)
    roof.lineTo(x + size * 0.50, y + size * 0.43)
    roof.close()
    c.drawPath(roof, stroke=1, fill=1)
    c.setFillColor(INK)
    c.rect(x - size * 0.07, y, size * 0.14, size * 0.25, stroke=0, fill=1)
    if label:
        c.setFillColor(INK)
        c.setFont(FONT_BOLD, 6.6)
        c.drawCentredString(x, y - size * 0.22, label)
    c.restoreState()


def draw_church(c: canvas.Canvas, x: float, y: float, size: float, label: str | None = None) -> None:
    c.saveState()
    c.setFillColor(colors.HexColor("#D7CFB8"))
    c.setStrokeColor(UMBER)
    c.setLineWidth(0.8)
    c.rect(x - size * 0.36, y, size * 0.72, size * 0.48, stroke=1, fill=1)
    c.rect(x - size * 0.12, y + size * 0.48, size * 0.24, size * 0.55, stroke=1, fill=1)
    c.setFillColor(UMBER)
    roof = c.beginPath()
    roof.moveTo(x - size * 0.20, y + size * 1.03)
    roof.lineTo(x, y + size * 1.32)
    roof.lineTo(x + size * 0.20, y + size * 1.03)
    roof.close()
    c.drawPath(roof, stroke=1, fill=1)
    c.setFillColor(INK)
    c.circle(x, y + size * 0.74, size * 0.055, stroke=0, fill=1)
    if label:
        c.setFont(FONT_BOLD, 6.6)
        c.drawCentredString(x, y - size * 0.20, label)
    c.restoreState()


def draw_ornament(c: canvas.Canvas, x: float, y: float, width: float, color=UMBER) -> None:
    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(0.55)
    c.line(x, y, x + width, y)
    c.circle(x + width / 2, y, 1.6, stroke=1, fill=0)
    c.line(x + width / 2 - 8, y - 3, x + width / 2, y)
    c.line(x + width / 2 + 8, y - 3, x + width / 2, y)
    c.restoreState()
styles.add(ParagraphStyle(
    name="KCenter", parent=styles["Normal"], fontName=FONT,
    fontSize=10, leading=13, textColor=INK, alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="KMap", parent=styles["Normal"], fontName=FONT_BOLD,
    fontSize=9, leading=11, textColor=INK, alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="HandoutBody", parent=styles["BodyText"], fontName=SERIF,
    fontSize=9.5, leading=13.2, textColor=INK,
))
styles.add(ParagraphStyle(
    name="HandoutCaption", parent=styles["BodyText"], fontName=FONT,
    fontSize=7.4, leading=9.4, textColor=UMBER, alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="TableHeader", parent=styles["BodyText"], fontName=FONT_BOLD,
    fontSize=7.8, leading=9.2, textColor=colors.white,
))


def page_frame(canv: canvas.Canvas, doc: BaseDocTemplate) -> None:
    canv.saveState()
    width, height = doc.pagesize
    draw_parchment(canv, width, height)
    canv.setStrokeColor(PARCHMENT_DARK)
    canv.setLineWidth(0.65)
    canv.roundRect(9 * mm, 9 * mm, width - 18 * mm, height - 18 * mm, 2 * mm, stroke=1, fill=0)
    canv.setStrokeColor(UMBER)
    canv.setLineWidth(0.45)
    canv.line(16 * mm, height - 12 * mm, width - 16 * mm, height - 12 * mm)
    draw_ornament(canv, width / 2 - 16 * mm, height - 12 * mm, 32 * mm)
    canv.setStrokeColor(UMBER)
    canv.setLineWidth(0.5)
    canv.line(16 * mm, 12 * mm, width - 16 * mm, 12 * mm)
    canv.setFont(FONT_BOLD, 7)
    canv.setFillColor(UMBER)
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
    items.append(Spacer(1, 1.2 * mm))
    return items


def art_banner(path: Path, width: float = 176 * mm, height: float = 54 * mm) -> list:
    """A visual scene separator used only where it supports table usability."""
    image = scaled_image(path, width, height)
    return [image, Spacer(1, 2.8 * mm)]


def cover_page(path: Path, title: str, subtitle: str) -> None:
    """Draw a cinematic opening page, then append the written briefing separately."""
    width, height = A4
    c = canvas.Canvas(str(path), pagesize=A4, pageCompression=1)
    c.setTitle(title)
    c.drawImage(str(COVER_ART), 0, 0, width=width, height=height, mask="auto")
    c.setFillColor(colors.Color(0.02, 0.05, 0.06, alpha=0.55))
    c.rect(0, 0, width, height, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#EEE3CE"))
    c.setFont(SERIF_BOLD, 32)
    c.drawCentredString(width / 2, height - 46 * mm, title)
    c.setStrokeColor(colors.HexColor("#CFB985"))
    c.setLineWidth(0.8)
    c.line(43 * mm, height - 52 * mm, width - 43 * mm, height - 52 * mm)
    draw_bell_mark(c, width / 2, height - 60 * mm, 10 * mm, colors.HexColor("#CFB985"))
    c.setFont(FONT_BOLD, 10)
    c.drawCentredString(width / 2, height - 69 * mm, subtitle.upper())
    c.setFont(SERIF, 16)
    c.drawCentredString(width / 2, 33 * mm, "Die Glocke schweigt. Der Berg antwortet trotzdem.")
    c.setFillColor(colors.HexColor("#D8CBAE"))
    c.setFont(FONT_BOLD, 7.6)
    c.drawCentredString(width / 2, 18 * mm, "KRÄHENFELS  /  NOVEMBER 1890  /  HOW TO BE A HERO")
    c.showPage()
    c.save()


def append_pdf(base: Path, addition: Path, output: Path) -> None:
    """Concatenate PDFs without changing their visual content."""
    from pypdf import PdfReader, PdfWriter

    writer = PdfWriter()
    for source in (base, addition):
        reader = PdfReader(str(source))
        for page in reader.pages:
            writer.add_page(page)
    with output.open("wb") as stream:
        writer.write(stream)


def draw_map(path: Path, gm: bool = False) -> None:
    width, height = landscape(A4)
    c = canvas.Canvas(str(path), pagesize=(width, height), pageCompression=1)
    c.setTitle("Kraehenfels Karte")
    draw_parchment(c, width, height, dark=True)
    inset_x, inset_y = 8 * mm, 8 * mm
    inset_w, inset_h = width - 16 * mm, height - 16 * mm
    c.drawImage(ImageReader(str(AERIAL_MAP)), inset_x, inset_y, width=inset_w, height=inset_h,
                preserveAspectRatio=True, anchor="c", mask="auto")
    c.setStrokeColor(colors.HexColor("#D8C69C"))
    c.setLineWidth(1.1)
    c.roundRect(inset_x, inset_y, inset_w, inset_h, 2 * mm, stroke=1, fill=0)

    # The image contains the terrain. Labels are deliberately overlaid as
    # physical map tags so the game locations remain readable at the table.
    c.setFillColor(colors.Color(0.96, 0.91, 0.79, alpha=0.94))
    c.roundRect(15 * mm, height - 38 * mm, 83 * mm, 24 * mm, 2 * mm, stroke=0, fill=1)
    c.setStrokeColor(colors.HexColor("#B89D6B"))
    c.setLineWidth(0.55)
    c.roundRect(15 * mm, height - 38 * mm, 83 * mm, 24 * mm, 2 * mm, stroke=1, fill=0)
    c.setFillColor(INK)
    c.setFont(SERIF_BOLD, 21)
    c.drawString(20 * mm, height - 23 * mm, "Krähenfels")
    c.setFont(FONT, 7.6)
    c.setFillColor(UMBER)
    c.drawString(20 * mm, height - 30 * mm, "Luftansicht des Dorfes · November 1890")
    draw_bell_mark(c, 90 * mm, height - 26 * mm, 5 * mm, UMBER)
    c.setFillColor(colors.Color(0.96, 0.91, 0.79, alpha=0.94))
    c.roundRect(width - 63 * mm, height - 28 * mm, 48 * mm, 14 * mm, 2 * mm, stroke=0, fill=1)
    c.setFillColor(RED if gm else UMBER)
    c.setFont(FONT_BOLD, 8)
    c.drawCentredString(width - 39 * mm, height - 21.5 * mm, "SL-KARTE / SPOILER" if gm else "H02 · SPIELERKARTE")

    def map_tag(label: str, tx: float, ty: float, px: float, py: float) -> None:
        c.saveState()
        c.setStrokeColor(colors.Color(0.96, 0.91, 0.79, alpha=0.90))
        c.setLineWidth(1.4)
        c.line(px, py, tx, ty - 1.5 * mm)
        c.setFillColor(colors.Color(0.96, 0.91, 0.79, alpha=0.94))
        c.roundRect(tx - 1.5 * mm, ty - 4.3 * mm, pdfmetrics.stringWidth(label, FONT_BOLD, 7.2) + 3 * mm, 6.2 * mm, 1.0 * mm, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont(FONT_BOLD, 7.2)
        c.drawString(tx, ty - 2.2 * mm, label)
        c.restoreState()

    # Landmark positions are tied to the illustrated terrain: inn at centre
    # left, church to its right, smithy lower left, bridge above, mine upper right.
    map_tag("Zur Krähe", 60 * mm, 96 * mm, 96 * mm, 109 * mm)
    map_tag("Kirche / Friedhof", 150 * mm, 94 * mm, 170 * mm, 106 * mm)
    map_tag("Schmiede", 26 * mm, 68 * mm, 45 * mm, 73 * mm)
    map_tag("Brücke", 102 * mm, 160 * mm, 121 * mm, 149 * mm)
    map_tag("alter Grubenweg", 188 * mm, 148 * mm, 229 * mm, 147 * mm)
    map_tag("verlassene Grube", 225 * mm, 159 * mm, 242 * mm, 178 * mm)
    c.setFillColor(colors.Color(0.96, 0.91, 0.79, alpha=0.94))
    c.roundRect(17 * mm, 17 * mm, 95 * mm, 22 * mm, 2 * mm, stroke=0, fill=1)
    c.setStrokeColor(colors.HexColor("#B89D6B"))
    c.setLineWidth(0.5)
    c.roundRect(17 * mm, 17 * mm, 95 * mm, 22 * mm, 2 * mm, stroke=1, fill=0)

    # Hidden routes and clues on GM map.
    if gm:
        c.setStrokeColor(RED)
        c.setLineWidth(1.7)
        c.setDash(4, 3)
        c.bezier(156 * mm, 72 * mm, 177 * mm, 91 * mm, 194 * mm, 85 * mm, 213 * mm, 100 * mm)
        c.bezier(213 * mm, 100 * mm, 229 * mm, 110 * mm, 229 * mm, 129 * mm, 239 * mm, 144 * mm)
        c.setDash()
        c.setFillColor(RED)
        c.setFont(FONT_BOLD, 8)
        c.drawString(180 * mm, 90 * mm, "Flutstollen")
        c.drawString(220 * mm, 122 * mm, "Kammer")
        c.setFont(FONT, 7.3)
        c.drawString(171 * mm, 82 * mm, "H08: Plan")
        c.drawString(218 * mm, 114 * mm, "H09: Sauter")
        c.setFillColor(RED)
        c.setFont(FONT_BOLD, 8)
        c.drawString(22 * mm, 32 * mm, "Wahrheit für die SL")
        c.setFont(FONT, 7.6)
        c.drawString(22 * mm, 26 * mm, "Elisabeth hat die Kinder gerettet. Der Widerhall trägt Stimmen.")
        c.drawString(22 * mm, 21 * mm, "Finale: 3 - 1 - 2 - 4 und Elisabeth Abele.")
    else:
        c.setFillColor(INK)
        c.setFont(FONT_BOLD, 8)
        c.drawString(22 * mm, 32 * mm, "Randnotiz")
        c.setFont(FONT, 7.6)
        c.drawString(22 * mm, 26 * mm, "Nach Sonnenuntergang keine Glocke.")
        c.drawString(22 * mm, 21 * mm, "Kein Singen. Keine fremden Namen rufen.")
    # Compass and scale.
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 8)
    c.drawString(width - 35 * mm, 35 * mm, "N")
    c.setStrokeColor(INK)
    c.setLineWidth(1)
    c.line(width - 34 * mm, 25 * mm, width - 34 * mm, 33 * mm)
    c.line(width - 34 * mm, 33 * mm, width - 36 * mm, 29 * mm)
    c.line(width - 34 * mm, 33 * mm, width - 32 * mm, 29 * mm)
    c.line(width - 57 * mm, 20 * mm, width - 37 * mm, 20 * mm)
    c.setFont(FONT, 7)
    c.drawCentredString(width - 47 * mm, 14 * mm, "ca. 500 Schritte")
    c.setFillColor(colors.HexColor("#F3E4C6"))
    c.setFont(FONT_BOLD, 7)
    c.drawString(13 * mm, 11 * mm, "KRÄHENFELS  /  DIE WEISSE FRAU SCHWEIGT")
    c.drawRightString(width - 13 * mm, 11 * mm, "KARTE")
    c.showPage()
    c.save()


def draw_mine_plan(path: Path, gm: bool = False) -> None:
    """Draw H08 as an incomplete mine plan with an optional SL overlay."""
    width, height = landscape(A4)
    c = canvas.Canvas(str(path), pagesize=(width, height), pageCompression=1)
    c.setTitle("Alter Flur- und Grubenplan")
    draw_parchment(c, width, height)
    c.setStrokeColor(PARCHMENT_DARK)
    c.setLineWidth(0.7)
    c.roundRect(8 * mm, 8 * mm, width - 16 * mm, height - 16 * mm, 2 * mm, stroke=1, fill=0)
    c.setFillColor(INK)
    c.setFont(SERIF_BOLD, 22)
    c.drawString(18 * mm, height - 19 * mm, "H08  /  Alter Flur- und Grubenplan")
    c.setFont(FONT, 9)
    c.setFillColor(UMBER)
    c.drawString(18 * mm, height - 25 * mm, "Gefunden zwischen Werkzeugkiste und nassem Holz")
    draw_bell_mark(c, 142 * mm, height - 21.5 * mm, 5.6 * mm, UMBER)
    if gm:
        c.setFillColor(RED)
        c.setFont(FONT_BOLD, 9)
        c.drawRightString(width - 18 * mm, height - 20 * mm, "SL-OVERLAY / SPOILER")
    else:
        c.setFillColor(UMBER)
        c.setFont(FONT_BOLD, 9)
        c.drawRightString(width - 18 * mm, height - 20 * mm, "SPIELERHANDOUT")

    left, bottom = 25 * mm, 28 * mm
    c.setStrokeColor(UMBER)
    c.setLineWidth(1.2)
    c.roundRect(left, bottom, 200 * mm, 102 * mm, 3 * mm, stroke=1, fill=0)
    c.saveState()
    clip = c.beginPath()
    clip.roundRect(left, bottom, 200 * mm, 102 * mm, 3 * mm)
    c.clipPath(clip, stroke=0, fill=0)
    c.drawImage(ImageReader(str(MINE_SURVEY)), left, bottom, width=200 * mm, height=102 * mm,
                preserveAspectRatio=False, mask="auto")
    c.restoreState()
    # A deliberately incomplete set of field labels. The surveying marks remain
    # visible beneath them so the prop reads as an actual plan rather than a diagram.
    def survey_label(label: str, x: float, y: float, *, red: bool = False) -> None:
        c.saveState()
        c.setFillColor(colors.Color(0.94, 0.89, 0.78, alpha=0.86))
        c.roundRect(x - 2 * mm, y - 3.5 * mm, pdfmetrics.stringWidth(label, FONT_BOLD, 7.4) + 4 * mm, 6 * mm, 1.0 * mm, stroke=0, fill=1)
        c.setFillColor(RED if red else INK)
        c.setFont(FONT_BOLD, 7.4)
        c.drawString(x, y - 1.4 * mm, label)
        c.restoreState()

    survey_label("Mundloch", 34 * mm, 80 * mm)
    survey_label("Schacht", 113 * mm, 80 * mm)
    survey_label("Seilzugweg", 104 * mm, 116 * mm)
    survey_label("Kapelle", 76 * mm, 67 * mm)
    survey_label("Bachlauf", 143 * mm, 61 * mm)
    survey_label("Flutstollen", 177 * mm, 60 * mm)
    survey_label("Abele", 178 * mm, 48 * mm)
    c.setStrokeColor(INK)
    c.setLineWidth(1.0)
    c.setDash(3, 2)
    c.line(165 * mm, 63 * mm, 185 * mm, 63 * mm)
    c.setDash()
    c.setFillColor(UMBER)
    c.setFont(SERIF, 8.4)
    c.drawString(30 * mm, 34 * mm, "Notiz am Rand: Der Plan ist an drei Stellen nass und nicht vollständig lesbar.")
    if gm:
        c.setStrokeColor(RED)
        c.setLineWidth(1.4)
        c.circle(184 * mm, 63 * mm, 7 * mm, stroke=1, fill=0)
        c.setDash(3, 2)
        c.line(184 * mm, 70 * mm, 192 * mm, 113 * mm)
        c.setDash()
        c.setFillColor(colors.Color(0.98, 0.91, 0.88, alpha=0.94))
        c.roundRect(190 * mm, 110 * mm, 65 * mm, 20 * mm, 2 * mm, stroke=0, fill=1)
        c.setStrokeColor(RED)
        c.setLineWidth(0.6)
        c.roundRect(190 * mm, 110 * mm, 65 * mm, 20 * mm, 2 * mm, stroke=1, fill=0)
        c.setFillColor(RED)
        c.setFont(FONT_BOLD, 8)
        c.drawString(194 * mm, 123 * mm, "SL: Widerhall unter dem Stein")
        c.setFont(FONT, 7.2)
        c.drawString(194 * mm, 117 * mm, "Flutstollen ist die direkte Route.")
        c.drawString(194 * mm, 113 * mm, "Kammer liegt unter der Kapelle.")
    c.setStrokeColor(UMBER)
    c.line(18 * mm, 12 * mm, width - 18 * mm, 12 * mm)
    c.setFillColor(UMBER)
    c.setFont(FONT_BOLD, 7)
    c.drawString(18 * mm, 7 * mm, "KRÄHENFELS  /  H08")
    c.drawRightString(width - 18 * mm, 7 * mm, "GRUBENPLAN")
    c.showPage()
    c.save()


HANDOUTS = {
    "H01": ("Kutschschein und Frachtzettel", "POSTKUTSCHE FREIBURG – FREUDENSTADT<br/>17. November 1890, Abfahrt 16:10 Uhr<br/><br/>Fahrgäste: drei Reisende, Namen nicht eingetragen.<br/>Fracht: ein verschnürtes Eisenstück, Absender <b>W. Abele, Krähenfels</b>.<br/><br/><i>Nicht öffnen. Nicht läuten. Bei Frost nicht berühren.</i><br/><br/>Umleitung über Krähenfels wegen Schnee auf der Passstraße."),
    "H03": ("Krähenfelser Wochenblatt", "<b>Winterdienst verschoben</b><br/><br/>Der neue Klöppel für die obere Kirchenglocke ist eingetroffen. Die Montage wird bis zum Ende des Frostes verschoben. Die Glocke wird seit dem Unglück von 1848 nicht mehr nach Einbruch der Dunkelheit geläutet.<br/><br/><b>Vermisster Holzsammler</b><br/><br/>Wilhelm Abele, 42, wurde am alten Grubenweg zuletzt gesehen.<br/><br/><b>Aus dem Gemeinderat</b><br/><br/>Besucher sollen sich nach Sonnenuntergang in ihren Unterkünften aufhalten."),
    "H04": ("Kirchenbuchauszug", "<b>Krähenfels, 3. Dezember 1848</b><br/><br/>Heute wurde Elisabeth Abele, Kantorin und Lehrerin, im Schnee oberhalb der Grube gefunden. Sie hatte drei Kinder aus dem eingestürzten Stollen geführt. Der Rückweg blieb ihr versperrt.<br/><br/>Die Glocke schlug danach viermal, obwohl niemand im Turm war.<br/><br/><i>... nicht die Frau ...<br/>... was unter dem Stein ...<br/>... die Stimme ...</i>"),
    "H05": ("Kabinettfoto von 1848", "<br/><br/><b>ELISABETH ABELE</b><br/><br/>Kantorin · Krähenfels · Winter 1848<br/><br/><i>Sie hat uns herausgeführt. Nicht die Hexe.</i>"),
    "H06": ("Liedblatt ohne letzte Strophe", "<b>Lied für den Heimweg</b><br/><br/>Wenn der erste Schnee fällt,<br/>wenn der zweite Weg schweigt,<br/>wenn der dritte Ton ruft,<br/>bleibt der vierte Stein.<br/><br/><font size='18'>3   1   2   4</font><br/><br/><i>Nicht die Glocke antwortet. Das Echo tut es.</i>"),
    "H07": ("Werkbuch der Stellmacherei", "<b>Eintrag vom 15. November 1890, Emil Bopp</b><br/><br/>Die Kutschenachse aus Freiburg ist sauber gearbeitet. Der Bruch sitzt nicht an der schwächsten Stelle. Metallstaub liegt im Holz, als hätte etwas von innen dagegen geschlagen.<br/><br/>Der neue Glockenklöppel besteht aus altem Grubeneisen. Beim Anschlagen summt er, auch wenn die Glocke gedämpft wird.<br/><br/><b>Nicht zusammen mit der Glocke lagern.</b>"),
    "H08": ("Alter Flur- und Grubenplan", "<b>Drei Wege vom Dorf zur verlassenen Grube</b><br/><br/>1. Försterweg, endet am verschütteten Mundloch<br/>2. Bachlauf, führt zu einem niedrigen Flutstollen<br/>3. alter Seilzugweg, führt zu einer Kammer unter der Kapelle<br/><br/>Kreis am Rand: <b>Abele, Werkzeug und Liedblatt</b>."),
    "H09": ("Bericht von Lorenz Sauter", "<i>Ich höre schlecht, aber der Berg hört zu gut.</i><br/><br/>Die Stimmen kommen nicht aus einer Richtung. Sie nehmen Wörter, die gerade gesprochen wurden, und geben sie später zurück. Erst leise. Dann mit einer Stimme, die man kennt.<br/><br/>Elisabeth war nicht die Frau, die den Berg weckte. Sie war die Frau, die ihn unten hielt.<br/><br/>Wenn ihr den Klöppel habt, lasst ihn nicht allein schwingen. Gebt ihm eine Antwort."),
    "H10": ("Elisabeths Brief", "<b>An Wilhelm, falls ich nicht zurückkehre.</b><br/><br/>Die Leute werden sagen, ich hätte die Kinder in die Grube geführt. Das stimmt nicht. Ich habe sie herausgeführt. Was unten blieb, trägt unsere Stimmen wie Mäntel.<br/><br/>Der neue Klöppel ist aus dem Eisen des ersten Einsturzes. Er öffnet den Widerhall, wenn er ohne Antwort läutet. Nennt meinen vollen Namen und singt die Gegenfolge: <b>drei, eins, zwei, vier</b>.<br/><br/>Wenn niemand antwortet, schmilzt das Eisen. Wenn ihr schweigt, hört der Berg auf euch.<br/><br/><b>Elisabeth Abele</b>"),
    "H11": ("Finale: Schlagfolge und Lied", "<b>1.</b> Klöppel sichern oder schmelzen.<br/><b>2.</b> Gegenfolge hörbar machen: <b>3 – 1 – 2 – 4</b>.<br/><b>3.</b> Den Namen vollständig sprechen: <b>Elisabeth Abele</b>.<br/><b>4.</b> Entscheiden, ob die Glocke, die Grube oder das Eisen das Ende trägt.<br/><br/><i>Die Weiße Frau greift niemanden an. Sie wartet auf eine Antwort, die nicht aus dem Berg kommt.</i>"),
}

HANDOUT_PRINT_LABELS = {
    "H01": "H01 · einzeln ausgeben · Kutschenszene",
    "H03": "H03 · einzeln ausgeben · Gasthaus",
    "H04": "H04 · zusammen mit H06 ausgeben",
    "H05": "H05 · nach der Erscheinung ausgeben",
    "H06": "H06 · zusammen mit H04 ausgeben",
    "H07": "H07 · einzeln ausgeben · Schmiede",
    "H08": "H08 · zusammen mit 01_Grubenplan_H08.pdf ausgeben",
    "H09": "H09 · einzeln ausgeben · Grube",
    "H10": "H10 · zurückhalten bis Vor Mitternacht",
    "H11": "H11 · Finale · mit H06 bereitlegen",
}


def draw_wax_seal(c: canvas.Canvas, x: float, y: float, radius: float) -> None:
    c.saveState()
    c.setFillColor(WAX)
    c.setStrokeColor(colors.HexColor("#4B221D"))
    c.setLineWidth(0.7)
    c.circle(x, y, radius, stroke=1, fill=1)
    c.setStrokeColor(colors.HexColor("#C88C70"))
    c.setLineWidth(0.6)
    c.circle(x, y, radius * 0.70, stroke=1, fill=0)
    c.setFillColor(colors.HexColor("#E2B39A"))
    c.setFont(SERIF_BOLD, radius * 0.92)
    c.drawCentredString(x, y - radius * 0.33, "K")
    c.restoreState()


def draw_scissors(c: canvas.Canvas, x: float, y: float, size: float = 4 * mm) -> None:
    c.saveState()
    c.setStrokeColor(UMBER)
    c.setLineWidth(0.65)
    c.circle(x - size * 0.18, y - size * 0.15, size * 0.20, stroke=1, fill=0)
    c.circle(x + size * 0.18, y - size * 0.15, size * 0.20, stroke=1, fill=0)
    c.line(x - size * 0.04, y, x - size * 0.63, y + size * 0.82)
    c.line(x + size * 0.04, y, x + size * 0.63, y + size * 0.82)
    c.restoreState()


def draw_crop_marks(c: canvas.Canvas, x: float, y: float, width: float, height: float) -> None:
    c.saveState()
    c.setStrokeColor(colors.Color(0.34, 0.24, 0.15, alpha=0.6))
    c.setLineWidth(0.4)
    length = 3.2 * mm
    for px, py, sx, sy in ((x, y, -1, -1), (x + width, y, 1, -1), (x, y + height, -1, 1), (x + width, y + height, 1, 1)):
        c.line(px + sx * length, py, px + sx * 0.7 * mm, py)
        c.line(px, py + sy * length, px, py + sy * 0.7 * mm)
    c.restoreState()


def draw_prop_page(c: canvas.Canvas, x: float, y: float, width: float, height: float, fill=PARCHMENT) -> None:
    """A restrained outer edge; individual prop functions supply their own identity."""
    c.setFillColor(fill)
    c.setStrokeColor(UMBER)
    c.setLineWidth(0.75)
    c.roundRect(x, y, width, height, 1.5 * mm, stroke=1, fill=1)


def draw_paper_wear(c: canvas.Canvas, x: float, y: float, width: float, height: float, *, seed: int, water: bool = False) -> None:
    """Keep paper props tactile without compromising print contrast."""
    c.saveState()
    rng = random.Random(seed)
    tint = colors.HexColor("#A98A5D") if not water else colors.HexColor("#68818B")
    for _ in range(7 if water else 4):
        cx = x + rng.uniform(8, width / mm - 8) * mm
        cy = y + rng.uniform(8, height / mm - 8) * mm
        radius = rng.uniform(4, 13) * mm
        c.setFillColor(colors.Color(tint.red, tint.green, tint.blue, alpha=0.035 if not water else 0.045))
        c.circle(cx, cy, radius, stroke=0, fill=1)
    c.setStrokeColor(colors.Color(0.34, 0.24, 0.15, alpha=0.18))
    c.setLineWidth(0.25)
    for _ in range(4):
        start_x = x + rng.uniform(5, width / mm - 15) * mm
        start_y = y + rng.uniform(5, height / mm - 10) * mm
        c.line(start_x, start_y, start_x + rng.uniform(5, 18) * mm, start_y + rng.uniform(-1, 1) * mm)
    c.restoreState()


def draw_fold(c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float) -> None:
    c.saveState()
    c.setStrokeColor(colors.Color(0.32, 0.23, 0.14, alpha=0.23))
    c.setLineWidth(0.42)
    c.setDash(1.3, 1.4)
    c.line(x1, y1, x2, y2)
    c.setDash()
    c.restoreState()


def prop_paragraph(c: canvas.Canvas, text: str, x: float, top: float, width: float, height: float, *, size: float = 8.4, leading: float = 11, font: str | None = None, color=INK, align=TA_LEFT) -> None:
    style = ParagraphStyle("Prop", fontName=font or FONT, fontSize=size, leading=leading, textColor=color, alignment=align)
    paragraph = Paragraph(text, style)
    _, paragraph_height = paragraph.wrap(width, height)
    paragraph.drawOn(c, x, top - paragraph_height)


def draw_handout_card(
    c: canvas.Canvas, x: float, y: float, width: float, height: float,
    hid: str, title: str, body: str,
) -> None:
    c.saveState()
    if hid == "H01":
        # A carriage ticket, with dispatch rules and a postal seal.
        draw_prop_page(c, x, y, width, height, colors.HexColor("#EADBBC"))
        draw_paper_wear(c, x, y, width, height, seed=101)
        c.setStrokeColor(UMBER)
        c.setDash(2, 2)
        c.line(x + 10 * mm, y + 6 * mm, x + 10 * mm, y + height - 6 * mm)
        c.setDash()
        c.setFont(FONT_BOLD, 7)
        c.setFillColor(UMBER)
        c.drawString(x + 14 * mm, y + height - 13 * mm, "GROSSHERZOGLICHE POSTKUTSCHE")
        c.setFillColor(INK)
        c.setFont(SERIF_BOLD, 17)
        c.drawString(x + 14 * mm, y + height - 24 * mm, "FAHRTSCHEIN & FRACHTZETTEL")
        c.setStrokeColor(INK)
        c.setLineWidth(1.3)
        c.line(x + 14 * mm, y + height - 29 * mm, x + width - 12 * mm, y + height - 29 * mm)
        c.setFillColor(RED)
        c.setFont(FONT_BOLD, 8)
        c.drawRightString(x + width - 13 * mm, y + height - 13 * mm, "No. 017-1890")
        c.setFont(FONT, 7.6)
        c.setFillColor(INK)
        c.drawString(x + 14 * mm, y + height - 39 * mm, "FREIBURG  >  FREUDENSTADT     17. XI. 1890     16:10 UHR")
        for row in range(4):
            rule_y = y + height - (49 + row * 18) * mm
            c.setStrokeColor(colors.HexColor("#B99B70"))
            c.setLineWidth(0.35)
            c.line(x + 14 * mm, rule_y, x + width - 14 * mm, rule_y)
        prop_paragraph(c, "<b>Fahrgäste:</b> drei Reisende, Namen nicht eingetragen.<br/><br/><b>Fracht:</b> ein verschnürtes Eisenstück. Absender: <b>W. Abele, Krähenfels</b>.<br/><br/><i>Nicht öffnen. Nicht läuten. Bei Frost nicht berühren.</i><br/><br/>Umleitung über Krähenfels wegen Schnee auf der Passstraße.", x + 14 * mm, y + height - 43 * mm, width - 38 * mm, 92 * mm, size=8.2, leading=10.2)
        draw_wax_seal(c, x + width - 23 * mm, y + 24 * mm, 9 * mm)
        c.saveState()
        c.translate(x + width - 47 * mm, y + 51 * mm)
        c.rotate(-7)
        c.setFillColor(colors.HexColor("#D8C29A"))
        c.setStrokeColor(UMBER)
        c.setLineWidth(0.7)
        c.roundRect(0, 0, 30 * mm, 16 * mm, 1.2 * mm, stroke=1, fill=1)
        c.setFillColor(RED)
        c.setFont(FONT_BOLD, 6.4)
        c.drawCentredString(15 * mm, 10 * mm, "FRACHT  ·  NICHT LÄUTEN")
        c.setFillColor(UMBER)
        c.setFont(FONT, 5.8)
        c.drawCentredString(15 * mm, 5 * mm, "W. Abele / Krähenfels")
        c.restoreState()
        c.setFillColor(UMBER)
        c.setFont(FONT_BOLD, 6.7)
        c.drawString(x + 14 * mm, y + 12 * mm, "ABSCHNITT BEIM KUTSCHER BELASSEN")

    elif hid == "H03":
        # Actual newspaper composition: masthead, datum, woodcut and columns.
        draw_prop_page(c, x, y, width, height, colors.HexColor("#E9E5D9"))
        draw_paper_wear(c, x, y, width, height, seed=103)
        c.setStrokeColor(INK)
        c.setLineWidth(0.8)
        c.rect(x + 6 * mm, y + 6 * mm, width - 12 * mm, height - 12 * mm, stroke=1, fill=0)
        c.setFont(SERIF_BOLD, 18)
        c.setFillColor(INK)
        c.drawCentredString(x + width / 2, y + height - 16 * mm, "KRÄHENFELSER WOCHENBLATT")
        c.setFont(FONT_BOLD, 6.6)
        c.drawCentredString(x + width / 2, y + height - 22 * mm, "SONNTAGSBEILAGE · 17. NOVEMBER 1890 · PREIS 2 PFENNIG")
        c.setLineWidth(1.4)
        c.line(x + 9 * mm, y + height - 26 * mm, x + width - 9 * mm, y + height - 26 * mm)
        c.drawImage(ImageReader(str(WOCHENBLATT_WOODCUT)), x + 10 * mm, y + height - 66 * mm, width=width - 20 * mm, height=37 * mm, preserveAspectRatio=True, anchor="c", mask="auto")
        c.setFont(SERIF_BOLD, 9)
        c.drawString(x + 11 * mm, y + height - 74 * mm, "WINTERDIENST VERSCHOBEN")
        newspaper_width = (width - 28 * mm) / 2
        left = "Der neue Klöppel für die obere Kirchenglocke ist eingetroffen. Die Montage wird bis zum Ende des Frostes verschoben. Die Glocke wird seit dem Unglück von 1848 nicht mehr nach Einbruch der Dunkelheit geläutet.<br/><br/><b>VERMISSTER HOLZSAMMLER</b><br/><br/>Wilhelm Abele, 42, wurde am alten Grubenweg zuletzt gesehen."
        right = "<b>AUS DEM GEMEINDERAT</b><br/><br/>Besucher sollen sich nach Sonnenuntergang in ihren Unterkünften aufhalten.<br/><br/>Wer nach Einbruch der Dunkelheit einen Ton aus dem Grubenhang hört, möge die Straße nehmen und nicht antworten.<br/><br/><i>Redaktion und Druck: Krähenfels.</i>"
        prop_paragraph(c, left, x + 10 * mm, y + height - 78 * mm, newspaper_width, 74 * mm, size=7.3, leading=8.6, font=SERIF)
        prop_paragraph(c, right, x + 15 * mm + newspaper_width, y + height - 78 * mm, newspaper_width, 74 * mm, size=7.3, leading=8.6, font=SERIF)
        c.setStrokeColor(INK)
        c.setLineWidth(0.35)
        c.line(x + width / 2, y + 11 * mm, x + width / 2, y + height - 78 * mm)
        c.setStrokeColor(INK)
        c.setLineWidth(0.25)
        c.line(x + 10 * mm, y + 14 * mm, x + width - 10 * mm, y + 14 * mm)
        c.setFillColor(INK)
        c.setFont(SERIF_BOLD, 6.4)
        c.drawString(x + 11 * mm, y + 9 * mm, "KLEINANZEIGE: Laternenöl gegen Salz und Brot. Bei Nacht keine Lieferung.")

    elif hid == "H04":
        # Parish register: ruled paper, red margin and a dated historic record.
        draw_prop_page(c, x, y, width, height, colors.HexColor("#F0E2C5"))
        draw_paper_wear(c, x, y, width, height, seed=104, water=True)
        c.setStrokeColor(colors.HexColor("#C3B08A"))
        c.setLineWidth(0.28)
        for row in range(12):
            c.line(x + 19 * mm, y + 15 * mm + row * 11 * mm, x + width - 10 * mm, y + 15 * mm + row * 11 * mm)
        c.setStrokeColor(RED)
        c.setLineWidth(1.0)
        c.line(x + 17 * mm, y + 9 * mm, x + 17 * mm, y + height - 9 * mm)
        c.setFillColor(RED)
        c.setFont(SERIF_BOLD, 9)
        c.drawCentredString(x + width / 2, y + height - 15 * mm, "AUS DEM KIRCHENBUCH ZU KRÄHENFELS")
        c.setFont(SERIF, 8)
        c.setFillColor(UMBER)
        c.drawString(x + 21 * mm, y + height - 27 * mm, "3. Dezember 1848 · Nachtrag des Küsters")
        c.setFont(FONT_BOLD, 6.5)
        c.setFillColor(RED)
        c.drawRightString(x + width - 12 * mm, y + height - 27 * mm, "Blatt 47b · Rand beschädigt")
        prop_paragraph(c, "Heute wurde Elisabeth Abele, Kantorin und Lehrerin, im Schnee oberhalb der Grube gefunden. Sie hatte drei Kinder aus dem eingestürzten Stollen geführt. Der Rückweg blieb ihr versperrt.<br/><br/>Die Glocke schlug danach viermal, obwohl niemand im Turm war.<br/><br/><i>... nicht die Frau ...<br/>... was unter dem Stein ...<br/>... die Stimme ...</i>", x + 22 * mm, y + height - 34 * mm, width - 36 * mm, 101 * mm, size=8.4, leading=11.1, font=SERIF)
        draw_bell_mark(c, x + width - 23 * mm, y + 20 * mm, 8 * mm, UMBER)
        c.setStrokeColor(colors.HexColor("#8D6E44"))
        c.setLineWidth(0.55)
        c.setDash(1.2, 1.5)
        c.line(x + width - 11 * mm, y + 29 * mm, x + width - 16 * mm, y + 72 * mm)
        c.setDash()

    elif hid == "H05":
        # Separate cabinet photo with photographer imprint and mat border.
        c.setFillColor(colors.HexColor("#382E29"))
        c.rect(x, y, width, height, stroke=0, fill=1)
        c.setFillColor(colors.HexColor("#D4C59F"))
        c.rect(x + 8 * mm, y + 8 * mm, width - 16 * mm, height - 16 * mm, stroke=0, fill=1)
        c.setStrokeColor(colors.HexColor("#171311"))
        c.setLineWidth(1.2)
        c.rect(x + 13 * mm, y + 31 * mm, width - 26 * mm, height - 50 * mm, stroke=1, fill=0)
        c.drawImage(ImageReader(str(ELISABETH_PHOTO)), x + 15 * mm, y + 34 * mm, width=width - 30 * mm, height=height - 57 * mm, mask="auto", preserveAspectRatio=True, anchor="c")
        c.setFillColor(colors.HexColor("#261F1B"))
        c.setFont(SERIF_BOLD, 11)
        c.drawCentredString(x + width / 2, y + 23 * mm, "ELISABETH ABELE")
        c.setFont(SERIF, 7.4)
        c.drawCentredString(x + width / 2, y + 16 * mm, "Kantorin · Krähenfels · Winter 1848")
        c.setFont(SERIF, 6.5)
        c.drawCentredString(x + width / 2, y + 11 * mm, "Atelieraufnahme auf nassem Kollodium")
        c.saveState()
        c.translate(x + 17 * mm, y + 18 * mm)
        c.rotate(2)
        c.setFont(SCRIPT, 7.2)
        c.setFillColor(colors.HexColor("#5F4A36"))
        c.drawString(0, 0, "Sie hat uns herausgeführt.")
        c.restoreState()
        c.setFillColor(colors.HexColor("#5F4A36"))
        c.setFont(SCRIPT, 7.0)
        c.drawRightString(x + width - 17 * mm, y + 18 * mm, "Nicht die Hexe.")

    elif hid == "H06":
        # A hymn sheet: centred title, staffs and the indispensable sequence.
        draw_prop_page(c, x, y, width, height, colors.HexColor("#F4EBD5"))
        draw_paper_wear(c, x, y, width, height, seed=106)
        c.setFillColor(INK)
        c.setFont(SERIF_BOLD, 16)
        c.drawCentredString(x + width / 2, y + height - 17 * mm, "LIED FÜR DEN HEIMWEG")
        c.setFont(SERIF, 8)
        c.drawCentredString(x + width / 2, y + height - 24 * mm, "für eine Stimme und die obere Glocke")
        for staff in (y + 101 * mm, y + 66 * mm):
            c.setStrokeColor(UMBER)
            c.setLineWidth(0.35)
            for row in range(5):
                c.line(x + 12 * mm, staff + row * 2.2 * mm, x + width - 12 * mm, staff + row * 2.2 * mm)
            for note_x, note_y in ((25, 3), (43, 7), (62, 4), (82, 9), (105, 5)):
                cx = x + note_x * mm
                cy = staff + note_y * mm
                c.setFillColor(INK)
                c.ellipse(cx - 1.6 * mm, cy - 1.1 * mm, cx + 1.6 * mm, cy + 1.1 * mm, stroke=0, fill=1)
                c.setLineWidth(0.65)
                c.line(cx + 1.4 * mm, cy, cx + 1.4 * mm, cy + 8 * mm)
        prop_paragraph(c, "Wenn der erste Schnee fällt,<br/>wenn der zweite Weg schweigt,<br/>wenn der dritte Ton ruft,<br/>bleibt der vierte Stein.", x + 19 * mm, y + 94 * mm, width - 38 * mm, 34 * mm, size=9.3, leading=11.5, font=SERIF, align=TA_CENTER)
        c.setFillColor(RED)
        c.setFont(SERIF_BOLD, 24)
        c.drawCentredString(x + width / 2, y + 48 * mm, "3   1   2   4")
        c.setFillColor(UMBER)
        c.setFont(SERIF, 8.2)
        c.drawCentredString(x + width / 2, y + 36 * mm, "Nicht die Glocke antwortet. Das Echo tut es.")
        draw_bell_mark(c, x + width - 22 * mm, y + 20 * mm, 8 * mm, UMBER)

    elif hid == "H07":
        # A working ledger with red accounting lines and technical plate.
        draw_prop_page(c, x, y, width, height, colors.HexColor("#E9DFC8"))
        draw_paper_wear(c, x, y, width, height, seed=107)
        c.setFillColor(INK)
        c.setFont(SERIF_BOLD, 15)
        c.drawString(x + 12 * mm, y + height - 16 * mm, "WERKBUCH DER STELLMACHEREI")
        c.setFont(FONT, 7.4)
        c.setFillColor(UMBER)
        c.drawString(x + 12 * mm, y + height - 23 * mm, "Emil Bopp · Eintrag vom 15. November 1890")
        c.setStrokeColor(RED)
        c.setLineWidth(0.9)
        c.line(x + 16 * mm, y + 10 * mm, x + 16 * mm, y + height - 29 * mm)
        c.setStrokeColor(colors.HexColor("#BCA986"))
        c.setLineWidth(0.28)
        for row in range(9):
            c.line(x + 18 * mm, y + 14 * mm + row * 12 * mm, x + width - 62 * mm, y + 14 * mm + row * 12 * mm)
        c.drawImage(ImageReader(str(STALLMACHEREI_ETCHING)), x + width - 58 * mm, y + 18 * mm, width=48 * mm, height=82 * mm, preserveAspectRatio=True, anchor="c", mask="auto")
        prop_paragraph(c, "Die Kutschenachse aus Freiburg ist sauber gearbeitet. Der Bruch sitzt nicht an der schwächsten Stelle. Metallstaub liegt im Holz, als hätte etwas von innen dagegen geschlagen.<br/><br/>Der neue Glockenklöppel besteht aus altem Grubeneisen. Beim Anschlagen summt er, auch wenn die Glocke gedämpft wird.<br/><br/><b>Nicht zusammen mit der Glocke lagern.</b>", x + 20 * mm, y + height - 34 * mm, width - 84 * mm, 95 * mm, size=8.0, leading=10.1)
        c.setStrokeColor(RED)
        c.setLineWidth(1.1)
        c.circle(x + width - 34 * mm, y + 42 * mm, 17 * mm, stroke=1, fill=0)
        c.setFont(FONT_BOLD, 5.9)
        c.setFillColor(RED)
        c.drawCentredString(x + width - 34 * mm, y + 17 * mm, "VIBRATION BEI KÄLTE")

    elif hid == "H08":
        # Folded field note that points deliberately to the full-size mine plan.
        draw_prop_page(c, x, y, width, height, colors.HexColor("#E7D6B5"))
        draw_paper_wear(c, x, y, width, height, seed=108, water=True)
        c.setStrokeColor(UMBER)
        c.setLineWidth(0.8)
        c.setDash(3, 2)
        c.line(x + width / 2, y + 8 * mm, x + width / 2, y + height - 8 * mm)
        c.setDash()
        c.setFont(SERIF_BOLD, 15)
        c.setFillColor(INK)
        c.drawString(x + 12 * mm, y + height - 17 * mm, "ALTER FLUR- UND GRUBENPLAN")
        c.setFont(FONT_BOLD, 7)
        c.setFillColor(RED)
        c.drawRightString(x + width - 12 * mm, y + height - 16 * mm, "BEILAGE H08")
        c.setStrokeColor(UMBER)
        c.setLineWidth(0.7)
        c.roundRect(x + 11 * mm, y + 20 * mm, width / 2 - 18 * mm, 85 * mm, 1.4 * mm, stroke=1, fill=0)
        c.drawImage(ImageReader(str(MINE_SURVEY)), x + 12.5 * mm, y + 21.5 * mm, width=width / 2 - 21 * mm, height=82 * mm, preserveAspectRatio=False, mask="auto")
        c.setFillColor(colors.Color(0.91, 0.83, 0.67, alpha=0.88))
        c.roundRect(x + 16 * mm, y + 25 * mm, 27 * mm, 7 * mm, 1 * mm, stroke=0, fill=1)
        c.setFillColor(RED)
        c.setFont(FONT_BOLD, 5.9)
        c.drawCentredString(x + 29.5 * mm, y + 27.5 * mm, "FLUTSTOLLEN?")
        prop_paragraph(c, "<b>Drei Wege vom Dorf zur verlassenen Grube</b><br/><br/>1. Försterweg, endet am verschütteten Mundloch<br/>2. Bachlauf, führt zu einem niedrigen Flutstollen<br/>3. alter Seilzugweg, führt zu einer Kammer unter der Kapelle<br/><br/>Kreis am Rand: <b>Abele, Werkzeug und Liedblatt</b><br/><br/><i>Die vollständige Karte ist als großes Handout H08 beigelegt.</i>", x + width / 2 + 9 * mm, y + height - 30 * mm, width / 2 - 20 * mm, 102 * mm, size=8.3, leading=10.6)

    elif hid == "H09":
        # Creased witness statement, more intimate and less formal than a letter.
        draw_prop_page(c, x, y, width, height, colors.HexColor("#EEE0C5"))
        draw_paper_wear(c, x, y, width, height, seed=109, water=True)
        c.setStrokeColor(colors.HexColor("#B9A17C"))
        c.setLineWidth(0.4)
        c.line(x + 11 * mm, y + height - 25 * mm, x + width - 11 * mm, y + 16 * mm)
        c.line(x + 16 * mm, y + 12 * mm, x + width - 18 * mm, y + height - 15 * mm)
        c.setFillColor(INK)
        c.setFont(SERIF_BOLD, 12)
        c.drawString(x + 14 * mm, y + height - 17 * mm, "AUSSAGE VON LORENZ SAUTER")
        c.setFillColor(UMBER)
        c.setFont(SERIF, 7.6)
        c.drawString(x + 14 * mm, y + height - 24 * mm, "Aufgenommen im Hinterzimmer der Krähe")
        prop_paragraph(c, "<i>Ich höre schlecht, aber der Berg hört zu gut.</i><br/><br/>Die Stimmen kommen nicht aus einer Richtung. Sie nehmen Wörter, die gerade gesprochen wurden, und geben sie später zurück. Erst leise. Dann mit einer Stimme, die man kennt.<br/><br/>Elisabeth war nicht die Frau, die den Berg weckte. Sie war die Frau, die ihn unten hielt.<br/><br/>Wenn ihr den Klöppel habt, lasst ihn nicht allein schwingen. Gebt ihm eine Antwort.", x + 17 * mm, y + height - 35 * mm, width - 34 * mm, 103 * mm, size=10.2, leading=13.5, font=SCRIPT)
        c.setStrokeColor(colors.HexColor("#8C6E4D"))
        c.setLineWidth(0.4)
        c.circle(x + width - 35 * mm, y + 33 * mm, 15 * mm, stroke=1, fill=0)
        c.setFont(SCRIPT, 7.4)
        c.setFillColor(RED)
        c.drawString(x + 18 * mm, y + 22 * mm, "Nicht antworten, wenn er ihren Namen sagt.")
        c.setFillColor(UMBER)
        c.setFont(SERIF, 10)
        c.drawRightString(x + width - 16 * mm, y + 16 * mm, "L. Sauter")

    elif hid == "H10":
        # Folded personal letter, with salutation, signature, and wax seal.
        draw_prop_page(c, x, y, width, height, colors.HexColor("#F0E4CE"))
        draw_paper_wear(c, x, y, width, height, seed=110, water=True)
        c.setStrokeColor(colors.HexColor("#C0AE8E"))
        c.setLineWidth(0.35)
        c.line(x + 10 * mm, y + height - 28 * mm, x + width - 10 * mm, y + height - 28 * mm)
        c.setFillColor(INK)
        c.setFont(SCRIPT, 12)
        c.drawString(x + 14 * mm, y + height - 17 * mm, "An Wilhelm, falls ich nicht zurückkehre.")
        prop_paragraph(c, "Die Leute werden sagen, ich hätte die Kinder in die Grube geführt. Das stimmt nicht. Ich habe sie herausgeführt. Was unten blieb, trägt unsere Stimmen wie Mäntel.<br/><br/>Der neue Klöppel ist aus dem Eisen des ersten Einsturzes. Er öffnet den Widerhall, wenn er ohne Antwort läutet. Nennt meinen vollen Namen und singt die Gegenfolge: <b>drei, eins, zwei, vier</b>.<br/><br/>Wenn niemand antwortet, schmilzt das Eisen. Wenn ihr schweigt, hört der Berg auf euch.<br/><br/><b>Elisabeth Abele</b>", x + 15 * mm, y + height - 36 * mm, width - 30 * mm, 111 * mm, size=10.1, leading=13.0, font=SCRIPT)
        draw_fold(c, x + 12 * mm, y + 58 * mm, x + width - 12 * mm, y + 58 * mm)
        draw_fold(c, x + width / 2, y + 11 * mm, x + width / 2, y + height - 12 * mm)
        draw_wax_seal(c, x + width - 22 * mm, y + 17 * mm, 7 * mm)

    else:  # H11, a distilled ritual card for the finale.
        c.setFillColor(INK)
        c.rect(x, y, width, height, stroke=0, fill=1)
        c.setStrokeColor(colors.HexColor("#C8B171"))
        c.setLineWidth(0.9)
        c.rect(x + 6 * mm, y + 6 * mm, width - 12 * mm, height - 12 * mm, stroke=1, fill=0)
        c.setFillColor(colors.HexColor("#F0DFC0"))
        c.setFont(SERIF_BOLD, 14)
        c.drawCentredString(x + width / 2, y + height - 18 * mm, "DIE ANTWORT")
        c.setFont(SERIF_BOLD, 29)
        c.setFillColor(colors.HexColor("#C9A454"))
        c.drawCentredString(x + width / 2, y + height - 39 * mm, "3 · 1 · 2 · 4")
        c.setStrokeColor(colors.HexColor("#C8B171"))
        c.setLineWidth(0.4)
        for ring in (17 * mm, 23 * mm):
            c.circle(x + width / 2, y + 57 * mm, ring, stroke=1, fill=0)
        draw_bell_mark(c, x + width / 2, y + 57 * mm, 11 * mm, colors.HexColor("#C9A454"))
        prop_paragraph(c, "<b>1.</b> Klöppel sichern oder schmelzen.<br/><b>2.</b> Gegenfolge hörbar machen.<br/><b>3.</b> Den Namen vollständig sprechen: <b>Elisabeth Abele</b>.<br/><b>4.</b> Entscheiden, ob Glocke, Grube oder Eisen das Ende trägt.", x + 17 * mm, y + 38 * mm, width - 34 * mm, 36 * mm, size=8.2, leading=10.1, font=SERIF, color=colors.HexColor("#F0DFC0"), align=TA_CENTER)
    c.restoreState()


def build_handouts(
    path: Path,
    handout_ids: list[str],
    *,
    heading: str = "Krähenfels · Spielerhinweise",
    instruction: str = "ZWEI GETRENNTE A5-HANDOUTS · AN DER MITTELLINIE SCHNEIDEN",
    reserved: bool = False,
) -> None:
    width, height = landscape(A4)
    c = canvas.Canvas(str(path), pagesize=(width, height), pageCompression=1)
    c.setTitle("Kraehenfels SL-Reservierung" if reserved else "Kraehenfels Spielerhinweise")
    entries = [(handout_id, HANDOUTS[handout_id]) for handout_id in handout_ids]
    for page_index in range(0, len(entries), 2):
        draw_parchment(c, width, height)
        c.setFillColor(INK)
        c.setFont(SERIF_BOLD, 16)
        c.drawString(10 * mm, height - 11 * mm, heading)
        c.setFillColor(RED if reserved else UMBER)
        c.setFont(FONT_BOLD, 6.8)
        c.drawRightString(width - 10 * mm, height - 10 * mm, instruction)
        draw_ornament(c, 105 * mm, height - 11 * mm, 32 * mm)
        card_width = (width - 28 * mm) / 2
        card_height = height - 29 * mm
        for column, (hid, (title, body)) in enumerate(entries[page_index:page_index + 2]):
            card_x = 9 * mm + column * (card_width + 10 * mm)
            c.setFillColor(RED if hid in {"H10", "H11"} else UMBER)
            c.setFont(FONT_BOLD, 6.6)
            c.drawString(card_x, height - 18 * mm, HANDOUT_PRINT_LABELS[hid].upper())
            draw_crop_marks(c, card_x, 9 * mm, card_width, card_height)
            draw_handout_card(c, card_x, 9 * mm, card_width, card_height, hid, title, body)
        cut_x = width / 2
        c.setStrokeColor(RED if reserved else UMBER)
        c.setLineWidth(0.55)
        c.setDash(2.2, 2.2)
        c.line(cut_x, 7 * mm, cut_x, height - 20 * mm)
        c.setDash()
        c.setFillColor(PARCHMENT)
        c.roundRect(cut_x - 13 * mm, height / 2 - 6 * mm, 26 * mm, 12 * mm, 1.5 * mm, stroke=0, fill=1)
        draw_scissors(c, cut_x, height / 2 + 1 * mm)
        c.setFillColor(RED if reserved else UMBER)
        c.setFont(FONT_BOLD, 5.8)
        c.drawCentredString(cut_x, height / 2 - 3 * mm, "HIER SCHNEIDEN")
        c.showPage()
    c.save()


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
    quick_rules = [
        [p("<b>PROBE</b><br/><br/>W100 gleich oder kleiner als der Wert: Erfolg.<br/><br/>Unteres Zehntel: kritischer Erfolg.<br/><br/>Ab 90 plus einem Zehntel: kritischer Patzer.", styles["KSmall"]),
         p("<b>BEGABUNG</b><br/><br/>Punkte einer Begabung addieren, durch 10 teilen und kaufmännisch runden.<br/><br/>Den Wert auf passende Fähigkeiten addieren, maximal 100.", styles["KSmall"])],
        [p("<b>GEISTESBLITZ</b><br/><br/>Begabung durch 10.<br/><br/>Ein Punkt erlaubt einen neuen Wurf bei einer misslungenen, nicht kritischen Probe.<br/><br/>Erneuert sich zum nächsten Abenteuer.", styles["KSmall"]),
         p("<b>SCHADEN</b><br/><br/>Unter 10 Lebenspunkten: bewusstlos.<br/><br/>Bei 0: tot.<br/><br/>Mehr als 60 Schaden in einem Angriff macht bewusstlos.", styles["KSmall"])],
    ]
    quick_table = Table(quick_rules, colWidths=[84 * mm, 84 * mm], rowHeights=[49 * mm, 49 * mm])
    quick_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#F4EBD8")),
        ("BACKGROUND", (1, 0), (1, 0), PALE),
        ("BACKGROUND", (0, 1), (0, 1), PALE),
        ("BACKGROUND", (1, 1), (1, 1), colors.HexColor("#F4EBD8")),
        ("BOX", (0, 0), (-1, -1), 0.85, UMBER),
        ("INNERGRID", (0, 0), (-1, -1), 0.55, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 5 * mm),
    ]))
    impulse = Table([[p("<font color='#F3E5CA'><b>ROLLENIMPULSE</b><br/>Werkzeug · Notizbuch · gutes Gesicht · falscher Grund · Schnee lesen · nicht glauben</font>", styles["KBody"])]], colWidths=[168 * mm])
    impulse.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), INK), ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#F3E5CA")),
        ("BOX", (0, 0), (-1, -1), 0.7, UMBER), ("LEFTPADDING", (0, 0), (-1, -1), 5 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5 * mm), ("TOPPADDING", (0, 0), (-1, -1), 4 * mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 4 * mm),
    ]))
    story += [quick_table, Spacer(1, 6 * mm), impulse]
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
        PageBreak(),
    ]
    story += title_block("Dein Start in 90 Sekunden", "Diese Seite liegt neben dir, bis die Kutsche umkippt.")
    start_cards = [
        [
            p("<b>1 · Tisch aufbauen</b><br/><br/>Lege Spielerkarte und Figurenbau aus. H01 bleibt im Umschlag bei dir. H02 bis H09 liegen verdeckt in Reihenfolge bereit. H10 und H11 bleiben außer Sicht. Öffne in der App <b>Panne</b>, stelle die Lautstärke leise ein.", styles["KSmall"]),
            p("<b>2 · Das sagst du zuerst</b><br/><br/><i>Ihr seid drei Reisende in einer Postkutsche nach Freiburg. Sagt kurz: Wer seid ihr, warum reist ihr und was fällt euch an der Person links von euch zuerst auf?</i><br/><br/>Dann lies den Vorlesetext von S01 vor.", styles["KSmall"]),
        ],
        [
            p("<b>3 · Die ersten fünf Minuten</b><br/><br/>Starte A01. Lies S01. Frage danach nur: <i>Was tut ihr?</i> Gib H01, sobald jemand die Kiste oder den Bruch untersucht. Starte SFX01 genau beim Umkippen, SFX04 bei der Spur. Ein Wurf entscheidet nur, wie es aussieht – nie, ob H01 gefunden wird.", styles["KSmall"]),
            p("<b>Wenn du nicht weißt, was jetzt passiert</b><br/><br/>Schau auf <b>12_SL_Am_Tisch.pdf</b>. Nenne den nächsten sichtbaren Impuls. Gib den Hinweis der Szene. Lass einen NSC handeln. Stelle dann wieder die Frage: <i>Was tut ihr?</i><br/><br/>Du musst keine Lösung verstecken und keinen perfekten Plan haben.", styles["KSmall"]),
        ],
        [
            p("<b>Deine drei Regeln</b><br/><br/>1. Beschreibe kurz und konkret, dann frage nach einer Handlung.<br/>2. Bei guten Ideen: lass sie funktionieren oder gib eine Spur.<br/>3. Bei einem Fehlschlag: Kosten statt Sackgasse – Zeit, Lärm, Kälte oder Misstrauen.", styles["KSmall"]),
            p("<b>Der wichtigste Moment</b><br/><br/>S06 ist keine Kampfbegegnung. Die Weiße Frau warnt. Sie zeigt auf Klöppel und Grube, greift nicht an und spricht nicht. Im Finale haben die Spieler immer drei echte Wege: Glocke, Schmiede oder Flutstollen.<br/><br/>Nach dem Finale: Stille lassen, dann Epilog fragen.", styles["KSmall"]),
        ],
    ]
    start_table = Table(start_cards, colWidths=[84 * mm, 84 * mm], rowHeights=[52 * mm, 53 * mm, 53 * mm])
    start_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#F4EBD8")),
        ("BACKGROUND", (1, 0), (1, 0), PALE),
        ("BACKGROUND", (0, 1), (0, 1), PALE),
        ("BACKGROUND", (1, 1), (1, 1), colors.HexColor("#F4EBD8")),
        ("BACKGROUND", (0, 2), (0, 2), colors.HexColor("#F4EBD8")),
        ("BACKGROUND", (1, 2), (1, 2), PALE),
        ("BOX", (0, 0), (-1, -1), 0.85, UMBER),
        ("INNERGRID", (0, 0), (-1, -1), 0.55, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 5 * mm),
    ]))
    story += [start_table]
    temp_dir = ROOT / "_TMP"
    temp_dir.mkdir(exist_ok=True)
    cover = temp_dir / "kraehenfels-spielstart-cover.pdf"
    briefing = temp_dir / "kraehenfels-spielstart-briefing.pdf"
    cover_page(cover, "Die Weiße Frau schweigt", "Ein Schwarzwald-Folk-Horror für drei Spieler und eine Spielleitung")
    build_story_pdf(briefing, story, "Spielstart")
    append_pdf(cover, briefing, path)


def build_soundboard_cues(path: Path) -> None:
    rows = [[p(text, styles["TableHeader"]) for text in ["Cue", "Wann", "Bedienung", "Fallback am Tisch"]]]
    cue_rows = [
        ("A01 / SFX01", "Kutschenpanne", "Wind leise legen, Achse erst beim Bruch auslösen", "Wind beschreiben, dann Holzknacken"),
        ("A04 / SFX23", "Dorf / Wirtshaus", "Nur die Wirtsstube legen; Fensterladen als kurzen Akzent", "Stimmen absenken und Pausen setzen"),
        ("A06 / SFX07 / SFX08", "Kirche", "Kapelle leise, dann Glocke normal und ein falscher Ton", "3 – 1 – 2 – 4 auf Tisch klopfen"),
        ("A03 / SFX10", "Schmiede", "Dorfluft unterlegen, Metallvibration nur beim Klöppel", "Einmal mit einem Löffel ans Glas tippen"),
        ("A09 / SFX11–14", "Grube", "Grubenluft legen; einzelne Schritte, Stimmen oder Schläge nur als Reaktion", "Sätze der Spieler verzögert wiederholen"),
        ("A05 / SFX15–17", "Weiße Frau", "Erst Stille, dann einen einzelnen Atem-, Motiv- oder Klöppelton", "Zwei hohe fallende Töne summen"),
        ("SFX18 / SFX29", "Vor Mitternacht", "Frost oder Resonanz nur setzen, wenn die Hinweise zusammenfallen", "Ein Glas kurz anreiben und danach still sein"),
        ("A08 / M05 / SFX20", "Finale", "Froststurm leise; Musik nur für die Entscheidung, Eisbruch als Abschluss", "Liedblatt H06 sichtbar in die Mitte legen"),
        ("–", "Epilog", "Keine neue Tonspur: Nach dem Finale bewusst Stille lassen", "Fenster öffnen oder Wasser einschenken"),
    ]
    for row in cue_rows:
        rows.append([p(cell, styles["KSmall"]) for cell in row])
    table = Table(rows, colWidths=[23 * mm, 35 * mm, 51 * mm, 64 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INK), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD), ("FONTNAME", (0, 1), (-1, -1), FONT),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.5 * mm), ("RIGHTPADDING", (0, 0), (-1, -1), 2.5 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5 * mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
    ]))
    story = title_block("Soundboard-Cues", "Jeder akustische Hinweis hat eine gedruckte Entsprechung")
    story += [scaled_image(BELL_ETCHING, 37 * mm, 38 * mm), Spacer(1, 2 * mm)]
    story += [p("Grundregel: Geräusch leise starten und nur hervorheben, wenn die Szene es verdient. Ein Cue darf auch ausbleiben. Die Sounddateien sind original prozedural erzeugt und ohne Sprachaufnahmen.", styles["KBody"]), Spacer(1, 4 * mm), table, Spacer(1, 6 * mm)]
    story += [p("Lautstärke: Master 35 bis 50 Prozent. SFX kurz auf 60 Prozent, nie dauerhaft. Bei empfindlichen Mitspielern alle Hochfrequenzen und die Herzschlagspur reduzieren.", styles["KBody"])]
    build_story_pdf(path, story, "Soundboard-Cues")


def build_sl_reference(path: Path) -> None:
    story = title_block("SL-Schnellreferenz", "Spoiler / offene Fäden / Enden")
    story += [scaled_image(BELL_ETCHING, 42 * mm, 43 * mm), Spacer(1, 2 * mm)]
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


def build_at_table_reference(path: Path) -> None:
    rows = [[p(text, styles["TableHeader"]) for text in ["Szene", "Wer gibt / was kommt", "Nächster Impuls", "Sound", "Stufe"]]]
    reference_rows = [
        ("S01 Panne", "Fund in der Kiste: H01 · C01/C02", "Laterne führt nach Krähenfels", "Preset Panne · SFX01", "0"),
        ("S02 Dorf", "Rosa: H02/H03 · C03", "Rosa oder Jakob bietet einen Ort an", "Preset Dorf · SFX23", "1"),
        ("S03 Kirche", "Martin: H04/H06 · C04/C05", "Martin zählt 3-1-2-4", "Preset Kirche · SFX08", "2"),
        ("S04 Schmiede", "Emil: H07 · C06", "Klöppel vibriert am Amboss", "Preset Schmiede · SFX10", "2"),
        ("S05 Grube", "Lorenz: H08/H09 · C07/C08", "Klopfen antwortet auf drei Schläge", "Preset Grube · A09/SFX14", "3"),
        ("S06 Erscheinung", "Elisabeth zeigt H05 · C09", "Hand zeigt auf Turm und Klöppel", "Preset Erscheinung · SFX16", "4"),
        ("S07 Wahrheit", "Rosa: H10 · C10/C11", "Drei Finale nennen", "Frost / Resonanz · SFX18", "4"),
        ("S08 Finale", "SL legt H11 bereit", "Ein Preis, kein Sackgassenwurf", "Preset Finale · M05/SFX20", "5"),
        ("S09 Epilog", "Folgen der Wahl", "Jede Figur bekommt einen Nachhall", "Bewusst still", "0"),
    ]
    for row in reference_rows:
        rows.append([p(cell, styles["KSmall"]) for cell in row])
    table = Table(rows, colWidths=[25 * mm, 42 * mm, 45 * mm, 43 * mm, 15 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INK), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD), ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.2 * mm), ("RIGHTPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2.6 * mm), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6 * mm),
    ]))
    story = title_block("Am Tisch", "Eine Seite für die Spielleitung · frei durch die Szenen navigieren, aber nie einen Kernhinweis verstecken.")
    story += [table, Spacer(1, 5 * mm)]
    story += [p("Wenn die Gruppe feststeckt: keinen neuen Würfelwurf verlangen. Gib stattdessen den nächsten sichtbaren Hinweis, lass einen NPC handeln oder starte nur einen kurzen Cue. Ein Fehlwurf verändert die Lage, nicht den Zugang zur Geschichte.", styles["KBody"])]
    build_story_pdf(path, story, "Am Tisch")


def build_sl_adventure(path: Path) -> None:
    raw = (ROOT / "content" / "scenario.md").read_text(encoding="utf-8")
    # Markdown-lite conversion, retaining headings and paragraphs.
    story = art_banner(COVER_ART, 176 * mm, 56 * mm)
    story += title_block("SL-Abenteuer", "Die Weiße Frau schweigt / spoilerhaltig")
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
    story.append(PageBreak())
    story += title_block("Szenenbilder", "Die Bildstrecke gehört zur SL-Fassung und kann als atmosphärische Zwischenfolie liegen bleiben.")
    for index, (label, art_path) in enumerate(SCENE_ART):
        if art_path.exists():
            story += [p(label, styles["KCardTitle"]), scaled_image(art_path, 176 * mm, 58 * mm), Spacer(1, 4 * mm)]
        if index % 2 == 1 and index != len(SCENE_ART) - 1:
            story.append(PageBreak())
    build_story_pdf(path, story, "SL-Abenteuer")


def main() -> None:
    draw_map(OUTPUT / "01_Karte_Spieler.pdf", gm=False)
    draw_map(OUTPUT / "01_Karte_SL.pdf", gm=True)
    draw_mine_plan(OUTPUT / "01_Grubenplan_H08.pdf", gm=False)
    draw_mine_plan(OUTPUT / "01_Grubenplan_SL.pdf", gm=True)
    build_handouts(OUTPUT / "02_Handouts.pdf", ["H01", "H03", "H04", "H05", "H06", "H07", "H08", "H09"])
    build_handouts(
        OUTPUT / "13_SL_Spoiler-Handouts.pdf",
        ["H10", "H11"],
        heading="Krähenfels · SL-Reservierung",
        instruction="SPOILER-HANDOUTS · ERST ZUM PASSENDEN MOMENT AUSTEILEN",
        reserved=True,
    )
    build_character_sheet(OUTPUT / "03_Figurenbau.pdf")
    build_start_pdf(OUTPUT / "00_Spielstart.pdf")
    build_sl_adventure(OUTPUT / "10_SL_Abenteuer.pdf")
    build_sl_reference(OUTPUT / "11_SL_Schnellreferenz.pdf")
    build_at_table_reference(OUTPUT / "12_SL_Am_Tisch.pdf")
    build_soundboard_cues(OUTPUT / "14_Soundboard-Cues.pdf")
    print(f"Wrote printable pack to {OUTPUT}")


if __name__ == "__main__":
    main()
