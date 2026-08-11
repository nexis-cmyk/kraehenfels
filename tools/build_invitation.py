#!/usr/bin/env python3
"""Build the player invitation for the Kraehenfels one-shot.

The illustration is kept text-free so the invitation remains editable and the
PDF text stays crisp when printed.  Re-running this script replaces only the
invitation output and its preview image.
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs"
OUTPUT.mkdir(exist_ok=True)
BACKGROUND = ROOT / "print" / "assets" / "einladung-kraehenfels-bg.png"
PDF_PATH = OUTPUT / "Einladung_Kraehenfels.pdf"


def register_fonts() -> tuple[str, str, str, str]:
    """Prefer the same Windows fonts as the existing print-pack builder."""
    sans = Path("C:/Windows/Fonts/arial.ttf")
    sans_bold = Path("C:/Windows/Fonts/arialbd.ttf")
    serif = Path("C:/Windows/Fonts/georgia.ttf")
    serif_bold = Path("C:/Windows/Fonts/georgiab.ttf")
    if sans.exists() and sans_bold.exists():
        pdfmetrics.registerFont(TTFont("KraehenSansInvite", str(sans)))
        pdfmetrics.registerFont(TTFont("KraehenSansInviteBold", str(sans_bold)))
        if serif.exists() and serif_bold.exists():
            pdfmetrics.registerFont(TTFont("KraehenSerifInvite", str(serif)))
            pdfmetrics.registerFont(TTFont("KraehenSerifInviteBold", str(serif_bold)))
            return (
                "KraehenSansInvite",
                "KraehenSansInviteBold",
                "KraehenSerifInvite",
                "KraehenSerifInviteBold",
            )
        return "KraehenSansInvite", "KraehenSansInviteBold", "Times-Roman", "Times-Bold"
    return "Helvetica", "Helvetica-Bold", "Times-Roman", "Times-Bold"


FONT, FONT_BOLD, SERIF, SERIF_BOLD = register_fonts()
INK = colors.HexColor("#172524")
PINE = colors.HexColor("#233D39")
BLUE = colors.HexColor("#315F67")
FROST = colors.HexColor("#DCEAF0")
PARCHMENT = colors.HexColor("#F1E5CF")
PARCHMENT_EDGE = colors.HexColor("#C3A879")
RED = colors.HexColor("#7D392C")
MUTED = colors.HexColor("#526762")


def draw_cover_image(c: canvas.Canvas, path: Path, width: float, height: float) -> None:
    """Scale the portrait illustration to cover the complete A4 page."""
    image = ImageReader(str(path))
    source_width, source_height = image.getSize()
    scale = max(width / source_width, height / source_height)
    draw_width = source_width * scale
    draw_height = source_height * scale
    c.drawImage(
        image,
        (width - draw_width) / 2,
        (height - draw_height) / 2,
        width=draw_width,
        height=draw_height,
        mask="auto",
    )


def set_alpha(c: canvas.Canvas, alpha: float) -> None:
    """Use transparency where supported, with a safe fallback for old ReportLab."""
    try:
        c.setFillAlpha(alpha)
    except AttributeError:
        pass


def draw_para(
    c: canvas.Canvas,
    text: str,
    x: float,
    top: float,
    width: float,
    style: ParagraphStyle,
) -> float:
    """Draw a wrapped paragraph and return the y coordinate below it."""
    paragraph = Paragraph(text, style)
    _, height = paragraph.wrap(width, 500 * mm)
    paragraph.drawOn(c, x, top - height)
    return top - height


def draw_rule(c: canvas.Canvas, x: float, y: float, width: float, color=RED) -> None:
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(0.75)
    c.line(x, y, x + width, y)
    c.restoreState()


def draw_bell(c: canvas.Canvas, x: float, y: float, size: float) -> None:
    """Small line-art bell used as a quiet visual signature."""
    c.saveState()
    c.setStrokeColor(RED)
    c.setFillColor(RED)
    c.setLineWidth(1.15)
    c.arc(x - size * 0.42, y - size * 0.05, x + size * 0.42, y + size * 0.70, 0, 180)
    c.line(x - size * 0.42, y + size * 0.30, x - size * 0.30, y - size * 0.22)
    c.line(x + size * 0.42, y + size * 0.30, x + size * 0.30, y - size * 0.22)
    c.line(x - size * 0.30, y - size * 0.22, x + size * 0.30, y - size * 0.22)
    c.circle(x, y - size * 0.30, size * 0.075, stroke=0, fill=1)
    c.line(x, y + size * 0.02, x, y - size * 0.30)
    c.restoreState()


def build_invitation() -> Path:
    if not BACKGROUND.exists():
        raise FileNotFoundError(f"Missing invitation background: {BACKGROUND}")

    width, height = A4
    c = canvas.Canvas(str(PDF_PATH), pagesize=A4)
    c.setTitle("Einladung - Die Weiße Frau schweigt")
    c.setAuthor("Kraehenfels Spielleitung")

    draw_cover_image(c, BACKGROUND, width, height)

    # A quiet blue veil makes the illustration print-friendly without hiding it.
    c.saveState()
    c.setFillColor(colors.HexColor("#091417"))
    set_alpha(c, 0.30)
    c.rect(0, 0, width, height, stroke=0, fill=1)
    set_alpha(c, 1)
    c.restoreState()

    margin = 14 * mm
    panel_x = margin
    panel_y = 13 * mm
    panel_width = width - 2 * margin
    panel_height = height - 27 * mm

    # Paper card: a tangible invitation over the cold village image.
    c.saveState()
    c.setFillColor(PARCHMENT)
    set_alpha(c, 0.965)
    c.roundRect(panel_x, panel_y, panel_width, panel_height, 4 * mm, stroke=0, fill=1)
    set_alpha(c, 1)
    c.setStrokeColor(PARCHMENT_EDGE)
    c.setLineWidth(0.9)
    c.roundRect(panel_x, panel_y, panel_width, panel_height, 4 * mm, stroke=1, fill=0)
    c.restoreState()

    inner_x = panel_x + 11 * mm
    inner_width = panel_width - 22 * mm
    current = panel_y + panel_height - 11 * mm

    draw_bell(c, panel_x + panel_width - 15 * mm, current - 1 * mm, 9 * mm)
    kicker_style = ParagraphStyle(
        "InviteKicker",
        fontName=FONT_BOLD,
        fontSize=8.2,
        leading=10,
        textColor=RED,
        tracking=1.2,
        alignment=TA_LEFT,
    )
    title_style = ParagraphStyle(
        "InviteTitle",
        fontName=SERIF_BOLD,
        fontSize=24,
        leading=26,
        textColor=INK,
        alignment=TA_LEFT,
        spaceAfter=0,
    )
    sub_style = ParagraphStyle(
        "InviteSub",
        fontName=FONT,
        fontSize=9.8,
        leading=12.2,
        textColor=BLUE,
        alignment=TA_LEFT,
    )
    body_style = ParagraphStyle(
        "InviteBody",
        fontName=FONT,
        fontSize=9.35,
        leading=13.4,
        textColor=INK,
        alignment=TA_LEFT,
        spaceAfter=0,
    )
    small_style = ParagraphStyle(
        "InviteSmall",
        fontName=FONT,
        fontSize=8.1,
        leading=10.5,
        textColor=MUTED,
        alignment=TA_LEFT,
    )
    section_style = ParagraphStyle(
        "InviteSection",
        fontName=FONT_BOLD,
        fontSize=8.5,
        leading=10,
        textColor=RED,
        tracking=0.7,
        alignment=TA_LEFT,
    )
    info_style = ParagraphStyle(
        "InviteInfo",
        fontName=FONT,
        fontSize=7.7,
        leading=9.5,
        textColor=INK,
        alignment=TA_LEFT,
    )
    footer_style = ParagraphStyle(
        "InviteFooter",
        fontName=FONT_BOLD,
        fontSize=7.4,
        leading=9,
        textColor=RED,
        alignment=TA_CENTER,
    )

    current = draw_para(c, "EINLADUNG", inner_x, current, inner_width, kicker_style)
    current -= 2.4 * mm
    current = draw_para(c, "DIE WEISSE FRAU SCHWEIGT", inner_x, current, inner_width - 15 * mm, title_style)
    current -= 1.5 * mm
    current = draw_para(c, "Ein Folk-Horror-Abenteuer für <i>How to be a Hero</i>", inner_x, current, inner_width, sub_style)
    current -= 4.5 * mm
    draw_rule(c, inner_x, current, inner_width)
    current -= 6 * mm

    current = draw_para(
        c,
        "<b>Krähenfels, Schwarzwald - November 1890</b><br/><br/>"
        "Eine Kutsche bleibt im Schnee stecken. Vor euch liegt ein Dorf, das zu viel verschweigt: "
        "eine Glocke, die seit Jahrzehnten stumm sein sollte, ein verschlossener Grubenweg "
        "und eine Frau in Weiß, die niemand sprechen hört.<br/><br/>"
        "Ihr seid drei Reisende. Was als unfreiwillige Nacht in Krähenfels beginnt, führt euch "
        "zu einem alten Pakt, einer falschen Glocke und einer Entscheidung, die das Dorf "
        "nicht vergessen wird.",
        inner_x,
        current,
        inner_width,
        body_style,
    )
    current -= 6 * mm
    draw_rule(c, inner_x, current, inner_width, color=colors.HexColor("#B99C6B"))
    current -= 6 * mm

    current = draw_para(c, "VORBEREITUNG VOR DEM SPIEL", inner_x, current, inner_width, section_style)
    current -= 2 * mm
    current = draw_para(
        c,
        "Bitte erstellt vorab euren Charakter für <i>How to be a Hero</i>. Ihr könnt euch dabei "
        "an einer echten Person, einem Beruf oder einer ganz eigenen Idee orientieren. "
        "Die Charakter-Dossiers werden am Tisch gemeinsam fertig ausgefuellt.",
        inner_x,
        current,
        inner_width,
        body_style,
    )
    current -= 2.5 * mm
    current = draw_para(
        c,
        "<b>Dafuer braucht ihr:</b><br/>"
        "• Name, Alter und einen kurzen Charakterbegriff<br/>"
        "• Werte für Handeln, Wissen und Soziales<br/>"
        "• eigene Fähigkeiten, HP, mentale Stabilität und 1-2 Macken",
        inner_x,
        current,
        inner_width,
        body_style,
    )
    current -= 5 * mm

    # Compact practical details block.
    box_y = current - 18 * mm
    box_height = 18 * mm
    c.saveState()
    c.setFillColor(colors.HexColor("#E4D4B7"))
    c.roundRect(inner_x, box_y, inner_width, box_height, 2 * mm, stroke=0, fill=1)
    c.setStrokeColor(colors.HexColor("#C2A979"))
    c.setLineWidth(0.55)
    c.roundRect(inner_x, box_y, inner_width, box_height, 2 * mm, stroke=1, fill=0)
    c.restoreState()
    columns = [
        ("SPIELER", "3"),
        ("SPIELLEITUNG", "1"),
        ("DAUER", "ca. 3-4 Stunden\noder mehrere Abende"),
        ("REGELWERK", "How to be a Hero"),
    ]
    col_width = inner_width / len(columns)
    for index, (label, value) in enumerate(columns):
        x = inner_x + index * col_width + 3.2 * mm
        c.setFont(FONT_BOLD, 6.8)
        c.setFillColor(RED)
        c.drawString(x, box_y + box_height - 5.5 * mm, label)
        c.setFont(FONT, 7.3)
        c.setFillColor(INK)
        lines = value.split("\n")
        for line_index, line in enumerate(lines):
            c.drawString(x, box_y + box_height - (10 + line_index * 3.3) * mm, line)
    current = box_y - 7 * mm

    current = draw_para(
        c,
        "<b>Mitbringen:</b> Lust auf Ermittlungen, Entscheidungen und eine unheimliche Dorfatmosphäre. "
        "Bitte keine Spoiler suchen - die wichtigsten Geheimnisse warten am Tisch.",
        inner_x,
        current,
        inner_width,
        small_style,
    )
    current -= 4.5 * mm
    draw_rule(c, inner_x, current, inner_width, color=colors.HexColor("#B99C6B"))
    current -= 7 * mm

    c.setFont(FONT_BOLD, 7.2)
    c.setFillColor(RED)
    c.drawString(inner_x, current, "DATUM:")
    c.setStrokeColor(MUTED)
    c.setLineWidth(0.45)
    c.line(inner_x + 15 * mm, current - 0.8 * mm, inner_x + 58 * mm, current - 0.8 * mm)
    c.drawString(inner_x + 68 * mm, current, "BEGINN:")
    c.setStrokeColor(MUTED)
    c.line(inner_x + 84 * mm, current - 0.8 * mm, inner_x + 116 * mm, current - 0.8 * mm)
    c.drawString(inner_x + 126 * mm, current, "ORT:")
    c.line(inner_x + 137 * mm, current - 0.8 * mm, inner_x + inner_width, current - 0.8 * mm)

    c.setFont(FONT_BOLD, 7.2)
    c.setFillColor(RED)
    c.drawCentredString(width / 2, panel_y + 7 * mm, "KRÄHENFELS  /  DIE WEISSE FRAU SCHWEIGT")
    c.showPage()
    c.save()
    return PDF_PATH


if __name__ == "__main__":
    path = build_invitation()
    print(path)
