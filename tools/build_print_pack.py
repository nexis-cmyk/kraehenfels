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
    draw_parchment(c, width, height)
    c.setStrokeColor(PARCHMENT_DARK)
    c.setLineWidth(0.7)
    c.roundRect(8 * mm, 8 * mm, width - 16 * mm, height - 16 * mm, 2 * mm, stroke=1, fill=0)
    c.setFillColor(INK)
    c.setFont(SERIF_BOLD, 23)
    c.drawString(18 * mm, height - 19 * mm, "Krähenfels")
    c.setFont(FONT, 9)
    c.setFillColor(UMBER)
    c.drawString(18 * mm, height - 25 * mm, "Handskizze für die Reise durch den Schwarzwald · November 1890")
    draw_bell_mark(c, 145 * mm, height - 21.5 * mm, 5.8 * mm, UMBER)
    if gm:
        c.setFillColor(RED)
        c.setFont(FONT_BOLD, 9)
        c.drawRightString(width - 18 * mm, height - 20 * mm, "SL-KARTE / SPOILER")
    else:
        c.setFillColor(UMBER)
        c.setFont(FONT_BOLD, 9)
        c.drawRightString(width - 18 * mm, height - 20 * mm, "SPIELERKARTE")

    # Roads and terrain
    c.setStrokeColor(UMBER)
    c.setLineWidth(2.8)
    c.bezier(40 * mm, 54 * mm, 95 * mm, 103 * mm, 131 * mm, 45 * mm, 251 * mm, 48 * mm)
    c.setLineWidth(1.25)
    c.bezier(51 * mm, 59 * mm, 82 * mm, 17 * mm, 114 * mm, 22 * mm, 132 * mm, 50 * mm)
    c.bezier(137 * mm, 49 * mm, 151 * mm, 93 * mm, 178 * mm, 110 * mm, 214 * mm, 127 * mm)
    # Bach
    c.setStrokeColor(colors.HexColor("#4B7780"))
    c.setLineWidth(2.3)
    c.bezier(38 * mm, 120 * mm, 78 * mm, 108 * mm, 97 * mm, 133 * mm, 132 * mm, 118 * mm)
    c.bezier(132 * mm, 118 * mm, 172 * mm, 101 * mm, 208 * mm, 132 * mm, 254 * mm, 113 * mm)
    # Dense Black Forest bands. The repeated pines turn the map into a place,
    # while leaving the routes readable at the table.
    for x, y, size in (
        (35, 35, 13), (48, 31, 16), (60, 35, 12), (69, 29, 14), (84, 33, 13),
        (190, 31, 16), (205, 33, 12), (219, 29, 15), (235, 35, 13), (247, 31, 16),
        (37, 132, 15), (50, 137, 13), (64, 130, 17), (180, 137, 12), (196, 131, 16),
        (211, 140, 14), (232, 132, 17), (246, 138, 12), (256, 130, 15),
    ):
        draw_fir(c, x * mm, y * mm, size * mm, colors.HexColor("#2D4B43"))
    c.setFillColor(colors.HexColor("#E0D2B4"))
    c.setStrokeColor(PARCHMENT_DARK)
    c.setLineWidth(0.65)
    c.roundRect(87 * mm, 60 * mm, 31 * mm, 24 * mm, 2 * mm, stroke=1, fill=1)
    draw_house(c, 102 * mm, 68 * mm, 14 * mm, "Zur Krähe")
    draw_church(c, 151 * mm, 89 * mm, 15 * mm, "Kirche / Friedhof")
    draw_house(c, 75 * mm, 43 * mm, 12 * mm, "Schmiede")
    # bridge and mine headframe
    c.setStrokeColor(UMBER)
    c.setLineWidth(1.2)
    c.line(116 * mm, 52 * mm, 128 * mm, 57 * mm)
    c.line(118 * mm, 49 * mm, 130 * mm, 54 * mm)
    c.setFont(FONT_BOLD, 6.6)
    c.setFillColor(INK)
    c.drawCentredString(123 * mm, 43 * mm, "Brücke")
    c.setStrokeColor(INK)
    c.setLineWidth(1.0)
    c.line(218 * mm, 121 * mm, 226 * mm, 139 * mm)
    c.line(234 * mm, 121 * mm, 226 * mm, 139 * mm)
    c.line(218 * mm, 121 * mm, 234 * mm, 121 * mm)
    c.line(221 * mm, 126 * mm, 231 * mm, 126 * mm)
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 6.6)
    c.drawCentredString(226 * mm, 114 * mm, "verlassene Grube")
    c.setFont(FONT, 6.8)
    c.drawCentredString(197 * mm, 106 * mm, "alter Grubenweg")
    c.drawString(23 * mm, 46 * mm, "Kutschenweg nach Freiburg")
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
        c.setFillColor(colors.HexColor("#F5ECD9"))
        c.roundRect(25 * mm, 19 * mm, 100 * mm, 21 * mm, 3 * mm, stroke=0, fill=1)
        c.setStrokeColor(PARCHMENT_DARK)
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
    c.setStrokeColor(UMBER)
    c.line(18 * mm, 12 * mm, width - 18 * mm, 12 * mm)
    c.setFillColor(UMBER)
    c.setFont(FONT_BOLD, 7)
    c.drawString(18 * mm, 7 * mm, "KRÄHENFELS  /  DIE WEISSE FRAU SCHWEIGT")
    c.drawRightString(width - 18 * mm, 7 * mm, "KARTE")
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
    c.setFillColor(colors.HexColor("#E1D3B8"))
    c.setStrokeColor(UMBER)
    c.setLineWidth(1.2)
    c.roundRect(left, bottom, 200 * mm, 102 * mm, 3 * mm, stroke=1, fill=1)
    c.setStrokeColor(PARCHMENT_DARK)
    c.setLineWidth(0.35)
    for x in range(32, 223, 10):
        c.line(x * mm, 31 * mm, (x + 7) * mm, 128 * mm)
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
    c.setFillColor(colors.HexColor("#EEE4CE"))
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
    c.setFillColor(UMBER)
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
    "H05": ("Kabinettfoto von 1848", "<br/><br/><b>ELISABETH ABELE</b><br/><br/>Krähenfels, Winter 1848<br/><br/>[Auf der Druckseite ist Platz für eine kleine gezeichnete Glocke.]<br/><br/><i>Sie hat uns herausgeführt. Warum erinnert sich niemand?</i>"),
    "H06": ("Liedblatt ohne letzte Strophe", "<b>Lied für den Heimweg</b><br/><br/>Wenn der erste Schnee fällt,<br/>wenn der zweite Weg schweigt,<br/>wenn der dritte Ton ruft,<br/>bleibt der vierte Stein.<br/><br/><font size='18'>3   1   2   4</font><br/><br/><i>Nicht die Glocke antwortet. Das Echo tut es.</i>"),
    "H07": ("Werkbuch der Stellmacherei", "<b>Eintrag vom 15. November 1890, Emil Bopp</b><br/><br/>Die Kutschenachse aus Freiburg ist sauber gearbeitet. Der Bruch sitzt nicht an der schwächsten Stelle. Metallstaub liegt im Holz, als hätte etwas von innen dagegen geschlagen.<br/><br/>Der neue Glockenklöppel besteht aus altem Grubeneisen. Beim Anschlagen summt er, auch wenn die Glocke gedämpft wird.<br/><br/><b>Nicht zusammen mit der Glocke lagern.</b>"),
    "H08": ("Alter Flur- und Grubenplan", "<b>Drei Wege vom Dorf zur verlassenen Grube</b><br/><br/>1. Försterweg, endet am verschütteten Mundloch<br/>2. Bachlauf, führt zu einem niedrigen Flutstollen<br/>3. alter Seilzugweg, führt zu einer Kammer unter der Kapelle<br/><br/>Kreis am Rand: <b>Abele, Werkzeug und Liedblatt</b>."),
    "H09": ("Bericht von Lorenz Sauter", "<i>Ich höre schlecht, aber der Berg hört zu gut.</i><br/><br/>Die Stimmen kommen nicht aus einer Richtung. Sie nehmen Wörter, die gerade gesprochen wurden, und geben sie später zurück. Erst leise. Dann mit einer Stimme, die man kennt.<br/><br/>Elisabeth war nicht die Frau, die den Berg weckte. Sie war die Frau, die ihn unten hielt.<br/><br/>Wenn ihr den Klöppel habt, lasst ihn nicht allein schwingen. Gebt ihm eine Antwort."),
    "H10": ("Elisabeths Brief", "<b>An Wilhelm, falls ich nicht zurückkehre.</b><br/><br/>Die Leute werden sagen, ich hätte die Kinder in die Grube geführt. Das stimmt nicht. Ich habe sie herausgeführt. Was unten blieb, trägt unsere Stimmen wie Mäntel.<br/><br/>Der neue Klöppel ist aus dem Eisen des ersten Einsturzes. Er öffnet den Widerhall, wenn er ohne Antwort läutet. Nennt meinen vollen Namen und singt die Gegenfolge: <b>drei, eins, zwei, vier</b>.<br/><br/>Wenn niemand antwortet, schmilzt das Eisen. Wenn ihr schweigt, hört der Berg auf euch.<br/><br/><b>Elisabeth Abele</b>"),
    "H11": ("Finale: Schlagfolge und Lied", "<b>1.</b> Klöppel sichern oder schmelzen.<br/><b>2.</b> Gegenfolge hörbar machen: <b>3 – 1 – 2 – 4</b>.<br/><b>3.</b> Den Namen vollständig sprechen: <b>Elisabeth Abele</b>.<br/><b>4.</b> Entscheiden, ob die Glocke, die Grube oder das Eisen das Ende trägt.<br/><br/><i>Die Weiße Frau greift niemanden an. Sie wartet auf eine Antwort, die nicht aus dem Berg kommt.</i>"),
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


def draw_handout_card(
    c: canvas.Canvas, x: float, y: float, width: float, height: float,
    hid: str, title: str, body: str,
) -> None:
    c.saveState()
    c.setFillColor(PARCHMENT)
    c.setStrokeColor(UMBER)
    c.setLineWidth(1.1)
    c.roundRect(x, y, width, height, 2.5 * mm, stroke=1, fill=1)
    c.setStrokeColor(PARCHMENT_DARK)
    c.setLineWidth(0.45)
    c.roundRect(x + 3 * mm, y + 3 * mm, width - 6 * mm, height - 6 * mm, 1.4 * mm, stroke=1, fill=0)
    # visual handout tag
    c.setFillColor(INK)
    c.roundRect(x + 7 * mm, y + height - 19 * mm, 21 * mm, 9 * mm, 1.5 * mm, stroke=0, fill=1)
    c.setFillColor(PARCHMENT)
    c.setFont(FONT_BOLD, 7.3)
    c.drawCentredString(x + 17.5 * mm, y + height - 15.8 * mm, hid)
    c.setFillColor(INK)
    c.setFont(SERIF_BOLD, 15)
    c.drawString(x + 32 * mm, y + height - 16.2 * mm, title)
    draw_ornament(c, x + 8 * mm, y + height - 24 * mm, width - 16 * mm)

    body_x = x + 9 * mm
    body_top = y + height - 31 * mm
    body_width = width - 18 * mm

    if hid == "H01":
        c.setFillColor(UMBER)
        c.setFont(SERIF_BOLD, 11)
        c.drawString(body_x, body_top - 7 * mm, "POSTKUTSCHE  ·  FREIBURG — FREUDENSTADT")
        c.setStrokeColor(UMBER)
        c.setLineWidth(0.55)
        for line_y in (body_top - 17 * mm, body_top - 30 * mm, body_top - 43 * mm, body_top - 56 * mm):
            c.line(body_x, line_y, x + width - 9 * mm, line_y)
        draw_wax_seal(c, x + width - 25 * mm, y + 31 * mm, 10 * mm)
        body_top -= 21 * mm
    elif hid == "H03":
        c.setFillColor(INK)
        c.setFont(SERIF_BOLD, 18)
        c.drawCentredString(x + width / 2, body_top - 6 * mm, "KRÄHENFELSER WOCHENBLATT")
        c.setFont(FONT_BOLD, 7)
        c.drawCentredString(x + width / 2, body_top - 12 * mm, "SONNTAGSBEILAGE · 17. NOVEMBER 1890 · PREIS 2 PFENNIG")
        c.setStrokeColor(UMBER)
        c.line(body_x, body_top - 16 * mm, x + width - 9 * mm, body_top - 16 * mm)
        draw_bell_mark(c, x + width - 22 * mm, body_top - 34 * mm, 8 * mm, UMBER)
        body_width -= 32 * mm
        body_top -= 23 * mm
    elif hid == "H04":
        c.setStrokeColor(PARCHMENT_DARK)
        c.setLineWidth(0.35)
        for row in range(10):
            c.line(body_x, body_top - (7 + row * 12) * mm, x + width - 9 * mm, body_top - (7 + row * 12) * mm)
        draw_bell_mark(c, x + width - 22 * mm, y + 29 * mm, 8 * mm, UMBER)
    elif hid == "H05":
        image = ImageReader(str(ELISABETH_PHOTO))
        photo_w = width - 26 * mm
        photo_h = 110 * mm
        c.drawImage(image, x + 13 * mm, y + 44 * mm, width=photo_w, height=photo_h, mask="auto", preserveAspectRatio=True, anchor="c")
        caption = Paragraph("<b>Elisabeth Abele</b><br/>Krähenfels, Winter 1848", styles["HandoutCaption"])
        cap_w, cap_h = caption.wrap(width - 26 * mm, 18 * mm)
        caption.drawOn(c, x + 13 * mm, y + 24 * mm)
        c.restoreState()
        return
    elif hid in {"H06", "H10", "H11"}:
        image = ImageReader(str(BELL_ETCHING))
        art_w = 43 * mm
        art_h = 62 * mm
        c.drawImage(image, x + width - art_w - 9 * mm, y + 18 * mm, width=art_w, height=art_h, mask="auto", preserveAspectRatio=True, anchor="c")
        body_width -= 49 * mm
    elif hid == "H07":
        c.setStrokeColor(PARCHMENT_DARK)
        c.setLineWidth(0.35)
        for row in range(11):
            c.line(body_x, body_top - (8 + row * 11) * mm, x + width - 9 * mm, body_top - (8 + row * 11) * mm)
        c.setStrokeColor(RED)
        c.setLineWidth(1.0)
        c.line(x + 18 * mm, y + 9 * mm, x + 18 * mm, y + height - 29 * mm)
    elif hid == "H08":
        c.setStrokeColor(INK)
        c.setLineWidth(1.2)
        c.line(x + width - 49 * mm, y + 44 * mm, x + width - 20 * mm, y + 44 * mm)
        c.line(x + width - 49 * mm, y + 44 * mm, x + width - 37 * mm, y + 66 * mm)
        c.line(x + width - 49 * mm, y + 44 * mm, x + width - 36 * mm, y + 24 * mm)
        c.setDash(2, 2)
        c.line(x + width - 20 * mm, y + 44 * mm, x + width - 13 * mm, y + 44 * mm)
        c.setDash()
        body_width -= 55 * mm
    elif hid == "H09":
        draw_bell_mark(c, x + width - 21 * mm, y + 31 * mm, 9 * mm, UMBER)

    body_para = Paragraph(body, styles["HandoutBody"])
    _, body_h = body_para.wrap(body_width, height - 46 * mm)
    body_para.drawOn(c, body_x, max(y + 12 * mm, body_top - body_h))
    c.setFillColor(UMBER)
    c.setFont(FONT_BOLD, 6.2)
    c.drawRightString(x + width - 8 * mm, y + 7 * mm, "Krähenfels · Spielerhinweis")
    c.restoreState()


def build_handouts(path: Path) -> None:
    width, height = landscape(A4)
    c = canvas.Canvas(str(path), pagesize=(width, height), pageCompression=1)
    c.setTitle("Kraehenfels Spielerhinweise")
    entries = list(HANDOUTS.items())
    for page_index in range(0, len(entries), 2):
        draw_parchment(c, width, height)
        c.setFillColor(INK)
        c.setFont(SERIF_BOLD, 16)
        c.drawString(10 * mm, height - 11 * mm, "Krähenfels · Spielerhinweise")
        c.setFillColor(UMBER)
        c.setFont(FONT_BOLD, 6.8)
        c.drawRightString(width - 10 * mm, height - 10 * mm, "A5-HANDOUTS · AUSSCHNEIDEN ODER EINZELN DRUCKEN")
        draw_ornament(c, 105 * mm, height - 11 * mm, 32 * mm)
        card_width = (width - 28 * mm) / 2
        card_height = height - 29 * mm
        for column, (hid, (title, body)) in enumerate(entries[page_index:page_index + 2]):
            card_x = 9 * mm + column * (card_width + 10 * mm)
            draw_handout_card(c, card_x, 9 * mm, card_width, card_height, hid, title, body)
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
        ("A01", "Kutschenpanne", "Loop leise, SFX01 beim Bruch", "Wind beschreiben, dann Holzknacken"),
        ("A03 / A04", "Dorf / Wirtshaus", "Atmosphäre wechseln, keine Musik nötig", "Stimmen absenken und Pausen setzen"),
        ("A06 / SFX08", "Kirche", "Glocke normal, dann falscher Ton", "3 – 1 – 2 – 4 auf Tisch klopfen"),
        ("A07 / SFX13", "Grube", "Wind, Stimmen ohne Worte, Boden", "Sätze der Spieler verzögert wiederholen"),
        ("A05 / M03", "Weiße Frau", "Musik erst nach der Stille starten", "Zwei hohe fallende Töne summen"),
        ("A08 / M04 / M05", "Finale", "Loop unter die Entscheidung, M04 nur einmal", "Liedblatt H06 sichtbar in die Mitte legen"),
        ("M06", "Epilog", "Einmal abspielen, danach Stille", "Fenster öffnen oder Wasser einschenken"),
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
