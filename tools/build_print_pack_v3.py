"""Build the Krähenfels 3.3 printable player and GM pack."""

from __future__ import annotations

import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.utils import ImageReader


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "content" / "manifest.json"
ASSETS = ROOT / "print" / "assets"
OUTPUT = ROOT / "outputs"

INK = colors.HexColor("#090E17")
PANEL = colors.HexColor("#111826")
PANEL_RAISED = colors.HexColor("#172133")
FROST = colors.HexColor("#B5D6EA")
COBALT = colors.HexColor("#4A8FCE")
QUIET = colors.HexColor("#94AABC")
WARNING = colors.HexColor("#D17B6E")
PAPER = colors.HexColor("#EEE5D2")
PAPER_DARK = colors.HexColor("#CBBFA8")
RUST = colors.HexColor("#9C4D3E")
CHARCOAL = colors.HexColor("#202731")


def load() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def text_style(name: str, size: float, leading: float | None = None, color=INK, font="Helvetica", bold=False, align=TA_LEFT) -> ParagraphStyle:
    return ParagraphStyle(name, fontName=("Helvetica-Bold" if bold else font), fontSize=size, leading=leading or size * 1.25, textColor=color, alignment=align, spaceAfter=4)


STYLES = getSampleStyleSheet()
BODY = text_style("body", 9.2, 12, CHARCOAL)
SMALL = text_style("small", 7.6, 9.5, CHARCOAL)
TITLE = text_style("title", 25, 29, INK, bold=True)


def paragraph(c: canvas.Canvas, content: str, x: float, y: float, width: float, height: float, style: ParagraphStyle = BODY) -> float:
    p = Paragraph(content, style)
    _, h = p.wrap(width, height)
    p.drawOn(c, x, y + height - h)
    return h


def page_title(c: canvas.Canvas, title: str, subtitle: str, dark: bool = True) -> None:
    width, height = c._pagesize
    c.setFillColor(INK if dark else PAPER)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setFillColor(FROST if dark else INK)
    c.setFont("Helvetica-Bold", 25)
    c.drawString(18 * mm, height - 25 * mm, title)
    c.setFillColor(COBALT if dark else RUST)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(19 * mm, height - 33 * mm, subtitle.upper())
    c.setStrokeColor(COBALT if dark else RUST)
    c.setLineWidth(1)
    c.line(18 * mm, height - 38 * mm, width - 18 * mm, height - 38 * mm)


def image_cover(c: canvas.Canvas, path: Path, x: float, y: float, width: float, height: float) -> None:
    if not path.exists():
        c.setFillColor(PANEL_RAISED)
        c.rect(x, y, width, height, fill=1, stroke=0)
        return
    image = ImageReader(str(path))
    iw, ih = image.getSize()
    scale = max(width / iw, height / ih)
    dw, dh = iw * scale, ih * scale
    c.saveState()
    crop = c.beginPath()
    crop.rect(x, y, width, height)
    c.clipPath(crop, stroke=0, fill=0)
    c.drawImage(image, x + (width - dw) / 2, y + (height - dh) / 2, dw, dh, mask="auto")
    c.restoreState()


def image_contain(c: canvas.Canvas, path: Path, x: float, y: float, width: float, height: float, background=PANEL) -> None:
    """Place an image fully inside a box without cropping its map legend."""
    c.setFillColor(background)
    c.roundRect(x, y, width, height, 2 * mm, fill=1, stroke=0)
    if not path.exists():
        return
    image = ImageReader(str(path))
    iw, ih = image.getSize()
    scale = min(width / iw, height / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(image, x + (width - dw) / 2, y + (height - dh) / 2, dw, dh, mask="auto")


def build_start(path: Path, data: dict) -> None:
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    image_cover(c, ASSETS / "scene-v3-coach.png", 0, height * 0.36, width, height * 0.64)
    c.setFillColor(INK)
    c.rect(0, 0, width, height * 0.44, fill=1, stroke=0)
    c.setFillColor(FROST)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(18 * mm, height * 0.32, "KRÄHENFELS")
    c.setFillColor(WARNING)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(18 * mm, height * 0.275, "DIE LETZTE KUTSCHE")
    paragraph(c, "Ein detektivischer Folk-Horror für drei Reisende und eine Spielleitung. Schwarzwald, November 1890. Eure Kutsche hat die Straße verlassen. Das Dorf wartet bereits.", 18 * mm, 22 * mm, width - 36 * mm, 55 * mm, text_style("start", 12, 16, FROST))
    c.setFillColor(QUIET)
    c.setFont("Helvetica", 8)
    c.drawString(18 * mm, 12 * mm, "How to be a Hero · W100 · Version 3.3.0")
    c.showPage()
    page_title(c, "Spielstart", "Für die Spielleitung · 20 Minuten Vorbereitung")
    y = height - 55 * mm
    steps = [
        ("Tisch", "Lege die Spielerkarte, drei eigene Figurenbögen, die sechs Gegenstandskarten sowie H01 bis H08 und H10 verdeckt bereit. H09 bleibt bei dir."),
        ("Figuren", "Jede Person bringt einen eigenen Charakter mit. Tragt die drei Namen ein und verteilt die sechs Gegenstände nach der Kutschenpanne untereinander."),
        ("Einstieg", "Starte M01 leise. Lies S01 vor. Frage nur: Was tut ihr? Gib H01 unabhängig vom Würfelwurf. A01 beginnt erst beim Aufbruch."),
        ("Leitung", "Setze die Dorfspannung manuell. Die App zeigt Empfehlungen, entscheidet aber nie an deiner Stelle."),
        ("Grenzen", "Kinder bleiben sicher. Gewalt bleibt unheimlich und dosiert. Sprich vor Beginn kurz über Stoppsignale."),
    ]
    for title, body in steps:
        c.setFillColor(COBALT)
        c.circle(23 * mm, y + 2 * mm, 3 * mm, fill=1, stroke=0)
        c.setFillColor(FROST)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(33 * mm, y, title)
        paragraph(c, body, 33 * mm, y - 16 * mm, width - 52 * mm, 14 * mm, text_style("step" + title, 9.5, 12, colors.white))
        y -= 28 * mm
    c.showPage()
    c.save()


def build_characters(path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    for page in range(3):
        page_title(c, "Eigener Charakter", f"Figurenbogen {page + 1} · für eine Person")
        c.setFillColor(INK)
        c.roundRect(18 * mm, height - 85 * mm, width - 36 * mm, 32 * mm, 5 * mm, fill=1, stroke=0)
        c.setFillColor(FROST)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(25 * mm, height - 67 * mm, "Name der Figur:")
        c.line(62 * mm, height - 68 * mm, 125 * mm, height - 68 * mm)
        c.drawString(135 * mm, height - 67 * mm, "Spieler/in:")
        c.line(161 * mm, height - 68 * mm, 190 * mm, height - 68 * mm)
        c.setFont("Helvetica", 8)
        c.drawString(25 * mm, height - 77 * mm, "Beruf / Idee / Grund für die Reise:")
        c.line(76 * mm, height - 78 * mm, 190 * mm, height - 78 * mm)
        y = height - 105 * mm
        headings = ["Handeln · Körper und Kampf", "Wissen · Gehirn und Planung", "Soziales · Reden und Macht"]
        for heading in headings:
            c.setFillColor(PANEL)
            c.roundRect(18 * mm, y, width - 36 * mm, 19 * mm, 4 * mm, fill=1, stroke=0)
            c.setFillColor(FROST)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(24 * mm, y + 11 * mm, heading)
            c.setFillColor(QUIET)
            c.setFont("Helvetica", 8)
            c.drawString(24 * mm, y + 4 * mm, "Begabung:")
            c.line(48 * mm, y + 4 * mm, 72 * mm, y + 4 * mm)
            c.drawString(82 * mm, y + 4 * mm, "Fähigkeiten und Werte:")
            c.line(122 * mm, y + 4 * mm, 190 * mm, y + 4 * mm)
            y -= 27 * mm
        c.setFillColor(PAPER)
        c.roundRect(18 * mm, 55 * mm, width - 36 * mm, 58 * mm, 5 * mm, fill=1, stroke=0)
        c.setFillColor(CHARCOAL)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(25 * mm, 101 * mm, "HTBAH-Kurzregel")
        paragraph(c, "Würfle W100. Gleich oder kleiner als dein Wert ist ein Erfolg. Eine sehr niedrige Zahl ist kritisch, eine sehr hohe Zahl ein Patzer. Ein Fehlschlag verschärft die Lage, blockiert aber keine Pflichtspur.", 25 * mm, 63 * mm, width - 50 * mm, 30 * mm, SMALL)
        c.setFillColor(QUIET)
        c.setFont("Helvetica", 8)
        c.drawString(18 * mm, 15 * mm, f"Figurenbogen {page + 1} · Krähenfels: Die letzte Kutsche")
        c.showPage()
    c.save()


def build_item_cards(path: Path, data: dict) -> None:
    """Build six cut-out equipment cards from the shared guided-flow source."""
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    locations = {location["id"]: location["title"] for location in data.get("guide", {}).get("itemFindLocations", [])}
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
        c.setFillColor(PAPER)
        c.setStrokeColor(RUST if item.get("weapon") else COBALT)
        c.setLineWidth(1.2)
        c.roundRect(x, y, card_width, card_height, 3 * mm, fill=1, stroke=1)
        c.setFillColor(RUST if item.get("weapon") else COBALT)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(x + 7 * mm, y + card_height - 10 * mm, "GEGENSTAND · KUTSCHE")
        c.setFillColor(CHARCOAL)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x + 7 * mm, y + card_height - 20 * mm, item["title"])
        c.setFillColor(RUST if item.get("weapon") else COBALT)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(x + 7 * mm, y + card_height - 27 * mm, f"Fundort · {locations.get(item.get('locationID'), item.get('locationID', 'Kutsche'))}")
        c.setStrokeColor(PAPER_DARK)
        c.setLineWidth(0.6)
        c.line(x + 7 * mm, y + card_height - 31 * mm, x + card_width - 7 * mm, y + card_height - 31 * mm)
        body_y = y + 9 * mm
        body_height = card_height - 43 * mm
        detail = f"<b>Beschreibung:</b> {escape(item.get('detail', ''))}<br/><br/><b>Anwendungen:</b> {int(item.get('initialUses', 1))}"
        for effect in item.get("effects", []):
            timing = "Vor der Probe" if effect.get("timing") == "beforeRoll" else "Nach einem Fehlschlag"
            modifier = f" · Zielwert +{effect['modifier']}" if effect.get("modifier") else ""
            detail += f"<br/><br/><b>{escape(timing)} · {escape(effect.get('title', ''))}{escape(modifier)}:</b> {escape(effect.get('detail', ''))}"
        weapon = item.get("weapon")
        if weapon:
            detail += f"<br/><br/><b>Waffe:</b> {escape(weapon.get('skill', 'Schusswaffen'))} · {escape(weapon.get('damageDice', '7W10'))} Schaden · {int(weapon.get('ammunition', 0))} Patronen · nicht parierbar"
        paragraph(c, detail, x + 7 * mm, body_y, card_width - 14 * mm, body_height, text_style(f"item-card-{index}", 7.2, 8.8, CHARCOAL))
        c.setFillColor(QUIET)
        c.setFont("Helvetica-Oblique", 6.5)
        c.drawString(x + 7 * mm, y + 4 * mm, "Ausschneiden an der Kartenkante · Weitergeben erlaubt")
    c.showPage()
    c.save()


def draw_newspaper(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    c.setFillColor(PAPER)
    c.roundRect(x, y, w, h, 2 * mm, fill=1, stroke=0)
    c.setFillColor(CHARCOAL)
    c.setFont("Times-Bold", 24)
    c.drawCentredString(x + w / 2, y + h - 20 * mm, "DER KRÄHENFELSER BOTEN")
    c.setFont("Times-Roman", 7)
    c.drawCentredString(x + w / 2, y + h - 27 * mm, "Ausgabe vom 28. November 1890 · Preis 5 Pfennig")
    c.setStrokeColor(CHARCOAL)
    c.line(x + 10 * mm, y + h - 31 * mm, x + w - 10 * mm, y + h - 31 * mm)
    col = (w - 30 * mm) / 2
    paragraph(c, "<b>REISENDE NICHT ANGEKOMMEN</b><br/><br/>Drei Reisende, die über den alten Pass nach Krähenfels kamen, haben ihre Weiterfahrt nicht angetreten. Der Gemeinderat verweist auf die Witterung. Angehörige werden gebeten, Namen nicht unnötig zu wiederholen.<br/><br/><b>GASTHOF MELDET VOLLE BELEGUNG</b><br/><br/>Der schwarze Keiler nimmt bei Schnee weiterhin Gäste auf. Bürgermeister Gruber erinnert an die Pflicht jedes Hauses, Fremden bis zum Morgen Schutz zu gewähren.", x + 10 * mm, y + 22 * mm, col, h - 62 * mm, text_style("newsleft", 9.2, 11, CHARCOAL, "Times-Roman"))
    paragraph(c, "<b>WINTERDIENST VERSCHOBEN</b><br/><br/>Die Wege zur Alten Eiche bleiben bis auf Weiteres gesperrt. Eine private Prozession ist nicht genehmigt.<br/><br/><b>VOM WALDRAND</b><br/><br/>Ein Holzfäller berichtet von Spuren, die im Schnee als Hufe beginnen und in menschlichen Sohlen enden. Der Bericht wurde nicht bestätigt.", x + 20 * mm + col, y + 22 * mm, col, h - 62 * mm, text_style("newsright", 9.2, 11, CHARCOAL, "Times-Roman"))
    # A real broadsheet needs a lower news rail as well; it keeps the evidence
    # useful and prevents the page from reading like a sparse text mockup.
    rail_y = y + 26 * mm
    c.setStrokeColor(CHARCOAL)
    c.setLineWidth(0.8)
    c.line(x + 10 * mm, rail_y + 48 * mm, x + w - 10 * mm, rail_y + 48 * mm)
    c.setFont("Times-Bold", 9)
    c.setFillColor(CHARCOAL)
    c.drawString(x + 10 * mm, rail_y + 40 * mm, "AUS DEM GEMEINDERAT")
    paragraph(c, "Der Pass bleibt nach Einbruch der Dunkelheit gesperrt. Fremde melden sich beim Wirt.<br/><br/>Wer die alte Glocke hört, wartet bis zum ersten Hahnenschrei.", x + 10 * mm, rail_y + 20 * mm, w * .43, 19 * mm, text_style("newsrailleft", 8.2, 10, CHARCOAL, "Times-Roman"))
    c.setStrokeColor(PAPER_DARK)
    c.line(x + w * .58, rail_y + 18 * mm, x + w * .58, rail_y + 44 * mm)
    c.setFont("Times-Bold", 9)
    c.setFillColor(RUST)
    c.drawString(x + w * .61, rail_y + 40 * mm, "KLEINANZEIGE")
    paragraph(c, "<i>Gesucht: vermisster Reisender</i><br/><br/><i>Letzte Sichtung: Passstraße · 23. Nov.</i>", x + w * .61, rail_y + 20 * mm, w * .29, 19 * mm, text_style("newsrailright", 8.2, 10, CHARCOAL, "Times-Roman"))


def draw_guestbook(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    c.setFillColor(colors.HexColor("#B58C5F"))
    c.roundRect(x, y, w, h, 3 * mm, fill=1, stroke=0)
    c.setFillColor(CHARCOAL)
    c.setFont("Times-Bold", 18)
    c.drawString(x + 14 * mm, y + h - 18 * mm, "Gästebuch · Zum schwarzen Keiler")
    c.setFont("Times-Roman", 8)
    c.drawString(x + 14 * mm, y + h - 26 * mm, "November 1890 · Gäste bis zum Hahnenschrei unter Dach")
    top = y + h - 42 * mm
    rows = ["12. Nov. · Familie Renz · Weiterfahrt 06:00", "16. Nov. · Wilhelm K. · Zimmer 2", "20. Nov. · Marta und Paul S. · Zimmer 1", "23. Nov. · Unbekannter Herr · Zimmer 3", "28. Nov. · ___________________________", "28. Nov. · ___________________________", "28. Nov. · ___________________________"]
    for index, row in enumerate(rows):
        yy = top - index * 17 * mm
        c.setStrokeColor(colors.HexColor("#765337"))
        c.line(x + 14 * mm, yy, x + w - 14 * mm, yy)
        c.setFillColor(RUST if index < 4 else CHARCOAL)
        c.setFont("Times-Italic" if index < 4 else "Times-Roman", 10)
        c.drawString(x + 17 * mm, yy + 4 * mm, row)
        if index < 4:
            c.setStrokeColor(RUST)
            c.setLineWidth(1.7)
            c.line(x + 12 * mm, yy + 7 * mm, x + w - 10 * mm, yy - 6 * mm)
            c.setLineWidth(1)


def draw_ledger(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    c.setFillColor(PAPER)
    c.rect(x, y, w, h, fill=1, stroke=0)
    c.setStrokeColor(PAPER_DARK)
    for i in range(11):
        c.line(x + 10 * mm, y + 22 * mm + i * 12 * mm, x + w - 10 * mm, y + 22 * mm + i * 12 * mm)
    for i in range(1, 4):
        c.line(x + 10 * mm + i * (w - 20 * mm) / 4, y + 22 * mm, x + 10 * mm + i * (w - 20 * mm) / 4, y + h - 25 * mm)
    c.setFillColor(CHARCOAL)
    c.setFont("Courier-Bold", 12)
    c.drawString(x + 12 * mm, y + h - 15 * mm, "WINTERBUCHHALTUNG · GEMEINDE KRÄHENFELS")
    c.setFont("Courier", 8)
    headers = ["JAHR", "GÄSTE", "WINTER", "ANMERKUNG"]
    for i, head in enumerate(headers):
        c.drawString(x + 12 * mm + i * (w - 20 * mm) / 4, y + h - 28 * mm, head)
    rows = [("1887", "2", "mild", "Holzpreis steigt"), ("1888", "1", "mild", "keine Meldung"), ("1889", "3", "mild", "Eiche bleibt ruhig"), ("1890", "3", "?", "vor Mitternacht")]
    for r, row in enumerate(rows):
        for i, value in enumerate(row):
            c.setFillColor(RUST if r == 3 and i in (1, 3) else CHARCOAL)
            c.drawString(x + 12 * mm + i * (w - 20 * mm) / 4, y + h - 42 * mm - r * 12 * mm, value)


def handout_stamp(c: canvas.Canvas, text_value: str, x: float, y: float, color=RUST, angle: float = -8) -> None:
    c.saveState()
    c.translate(x, y)
    c.rotate(angle)
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.5)
    c.roundRect(-28 * mm, -7 * mm, 56 * mm, 14 * mm, 2 * mm, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(0, -3 * mm, text_value)
    c.restoreState()


def draw_order(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    c.setFillColor(colors.HexColor("#E8D9B9"))
    c.roundRect(x, y, w, h, 2 * mm, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor("#A78A61"))
    c.setLineWidth(0.7)
    c.rect(x + 7 * mm, y + 7 * mm, w - 14 * mm, h - 14 * mm, fill=0, stroke=1)
    c.setFillColor(CHARCOAL)
    c.setFont("Courier-Bold", 17)
    c.drawString(x + 15 * mm, y + h - 21 * mm, "POST- UND FRACHTAUFTRAG")
    c.setFont("Courier", 8)
    c.drawRightString(x + w - 15 * mm, y + h - 20 * mm, "Nr. 28/11-KF")
    c.setStrokeColor(colors.HexColor("#B79D76"))
    c.line(x + 15 * mm, y + h - 28 * mm, x + w - 15 * mm, y + h - 28 * mm)
    rows = [("ABFAHRT", "28. November 1890 · 21:10"), ("ROUTE", "Hauptstraße – Umleitung Krähenfels"), ("EMPFÄNGER", "Bürgermeister Konrad Gruber"), ("FÜR DIE GÄSTE", "Unter Dach bringen · bis zum Hahnenschrei"), ("ANWEISUNG", "Keine Rückkehr auf die Passstraße")]
    yy = y + h - 47 * mm
    for label, value in rows:
        c.setFillColor(RUST)
        c.setFont("Courier-Bold", 8)
        c.drawString(x + 15 * mm, yy, label)
        c.setFillColor(CHARCOAL)
        c.setFont("Courier", 10)
        c.drawString(x + 52 * mm, yy, value)
        c.setStrokeColor(colors.HexColor("#C7B994"))
        c.line(x + 15 * mm, yy - 3 * mm, x + w - 15 * mm, yy - 3 * mm)
        yy -= 17 * mm
    c.setStrokeColor(CHARCOAL)
    c.setLineWidth(1.1)
    c.line(x + 20 * mm, y + 42 * mm, x + 84 * mm, y + 42 * mm)
    c.line(x + 55 * mm, y + 26 * mm, x + 55 * mm, y + 59 * mm)
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(x + 18 * mm, y + 30 * mm, "Achse vor Abfahrt geprüft")
    c.setFillColor(colors.HexColor("#D7C7A2"))
    c.circle(x + w - 35 * mm, y + 37 * mm, 18 * mm, fill=1, stroke=0)
    handout_stamp(c, "RATHAUS KF", x + w - 35 * mm, y + 37 * mm, colors.HexColor("#7E3F35"), -13)
    c.setFillColor(RUST)
    c.setFont("Courier-Bold", 10)
    c.drawString(x + 98 * mm, y + 38 * mm, "NICHT ZURÜCK AUF DIE HAUPTSTRASSE")


def draw_oath(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    c.setFillColor(colors.HexColor("#E2D4B8"))
    c.roundRect(x, y, w, h, 2 * mm, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor("#9E8765"))
    c.setLineWidth(1)
    c.rect(x + 9 * mm, y + 9 * mm, w - 18 * mm, h - 18 * mm, fill=0, stroke=1)
    c.setFillColor(CHARCOAL)
    c.setFont("Times-Bold", 21)
    c.drawCentredString(x + w / 2, y + h - 28 * mm, "AUSZUG AUS DEM KIRCHENBUCH")
    c.setFont("Times-Italic", 10)
    c.drawCentredString(x + w / 2, y + h - 39 * mm, "Blatt 17 · abgeschrieben vor dem Winter 1764")
    c.setStrokeColor(RUST)
    c.line(x + 24 * mm, y + h - 47 * mm, x + w - 24 * mm, y + h - 47 * mm)
    paragraph(c, "<b>Der Gast unter unserem Dach</b><br/><br/>Wer bei Schnee und Nacht unter dem Dach von Krähenfels aufgenommen wird, bleibt bis zum ersten Hahnenschrei Gast. Kein Messer, kein Seil und kein Name soll ihn an den Wald zurückgeben.<br/><br/>Wer dieses Wort bricht, öffnet die Tür für das, was draußen wartet.", x + 28 * mm, y + 53 * mm, w - 56 * mm, h - 105 * mm, text_style("oath", 13, 18, CHARCOAL, "Times-Roman"))
    c.setFont("Times-Italic", 9)
    c.setFillColor(colors.HexColor("#665743"))
    c.drawString(x + 28 * mm, y + 33 * mm, "Randnotiz, fremde Hand: Nicht Gruber fragen.")
    handout_stamp(c, "PFARRAMT", x + w - 38 * mm, y + 31 * mm, colors.HexColor("#5D5145"), 9)


def draw_smithy(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    c.setFillColor(colors.HexColor("#D6C4A2"))
    c.rect(x, y, w, h, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor("#6F5B46"))
    c.setLineWidth(0.8)
    c.rect(x + 8 * mm, y + 8 * mm, w - 16 * mm, h - 16 * mm, fill=0, stroke=1)
    c.setFillColor(CHARCOAL)
    c.setFont("Courier-Bold", 16)
    c.drawString(x + 16 * mm, y + h - 21 * mm, "WERKBLATT · GEWEIHRELIQUIE")
    c.setFont("Courier", 8)
    c.drawRightString(x + w - 16 * mm, y + h - 20 * mm, "M. KERN · SCHMIEDE")
    cx, cy = x + w * 0.46, y + h * 0.56
    c.setStrokeColor(CHARCOAL)
    c.setLineWidth(2.2)
    c.arc(cx - 55 * mm, cy - 32 * mm, cx + 5 * mm, cy + 56 * mm, 80, 270)
    c.arc(cx - 5 * mm, cy - 32 * mm, cx + 55 * mm, cy + 56 * mm, -90, 100)
    c.line(cx, cy - 32 * mm, cx, cy + 50 * mm)
    for offset in (-38, 0, 38):
        c.setFillColor(colors.HexColor("#24272A"))
        c.circle(cx + offset * mm, cy - 47 * mm, 4 * mm, fill=1, stroke=0)
        c.setFillColor(RUST)
        c.setFont("Courier-Bold", 8)
        c.drawCentredString(cx + offset * mm, cy - 60 * mm, f"NAGEL {1 + ((offset + 38) // 38)}")
    c.setStrokeColor(RUST)
    c.setLineWidth(1)
    c.line(x + 26 * mm, y + 43 * mm, x + w - 25 * mm, y + 43 * mm)
    c.setFillColor(CHARCOAL)
    c.setFont("Courier", 10)
    c.drawString(x + 27 * mm, y + 30 * mm, "Drei schwarze Nägel · altes Eisen · Feuer")
    c.setFont("Courier-Oblique", 9)
    c.drawString(x + 27 * mm, y + 18 * mm, "Feuer löst die Bindung. Ein Eid kann sie wenden.")


def draw_child_drawing(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    c.setFillColor(colors.HexColor("#F4EBD6"))
    c.rect(x, y, w, h, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor("#D2B47A"))
    c.setLineWidth(0.6)
    for yy in range(int(y + 12 * mm), int(y + h - 8 * mm), 22): c.line(x + 10 * mm, yy, x + w - 10 * mm, yy)
    c.setStrokeColor(colors.HexColor("#1A2028"))
    c.setLineWidth(2.8)
    cx, cy = x + w * 0.55, y + h * 0.59
    c.circle(cx, cy + 44 * mm, 11 * mm, fill=0, stroke=1)
    c.line(cx, cy + 33 * mm, cx, cy - 6 * mm)
    c.line(cx, cy + 20 * mm, cx - 30 * mm, cy + 2 * mm)
    c.line(cx, cy + 20 * mm, cx + 30 * mm, cy + 2 * mm)
    c.line(cx, cy - 6 * mm, cx - 17 * mm, cy - 38 * mm)
    c.line(cx, cy - 6 * mm, cx + 17 * mm, cy - 38 * mm)
    c.setStrokeColor(RUST)
    c.setLineWidth(3.8)
    c.arc(cx - 53 * mm, cy + 47 * mm, cx - 5 * mm, cy + 96 * mm, 45, 135)
    c.arc(cx + 5 * mm, cy + 47 * mm, cx + 53 * mm, cy + 96 * mm, 45, 135)
    c.setStrokeColor(colors.HexColor("#3A8C61"))
    c.setLineWidth(2)
    for px in (x + 45 * mm, x + 75 * mm, x + 105 * mm, x + 135 * mm):
        c.circle(px, y + 54 * mm, 4 * mm, fill=0, stroke=1)
        c.line(px, y + 50 * mm, px, y + 32 * mm)
        c.line(px, y + 44 * mm, px - 7 * mm, y + 37 * mm)
        c.line(px, y + 44 * mm, px + 7 * mm, y + 37 * mm)
    c.setFillColor(CHARCOAL)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x + 18 * mm, y + 20 * mm, "ER KOMMT, WENN DAS FEUER ERLISCHT")
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(x + 18 * mm, y + 9 * mm, "Leni · Dachfenster · nicht für Erwachsene")


def draw_rubbing(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    c.setFillColor(colors.HexColor("#CFC0A3"))
    c.rect(x, y, w, h, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor("#8D765D"))
    c.setLineWidth(1.5)
    c.rect(x + 7 * mm, y + 7 * mm, w - 14 * mm, h - 14 * mm, fill=0, stroke=1)
    c.setFillColor(colors.HexColor("#4B4540"))
    c.setFont("Courier-Bold", 14)
    c.drawString(x + 17 * mm, y + h - 23 * mm, "HOLZABRIEBUNG · ELIAS RENK")
    c.setStrokeColor(colors.HexColor("#292B2D"))
    c.setLineWidth(5)
    cx, cy = x + w * .5, y + h * .55
    c.circle(cx, cy, 62 * mm, fill=0, stroke=1)
    c.line(cx - 48 * mm, cy + 5 * mm, cx + 28 * mm, cy + 30 * mm)
    c.line(cx + 28 * mm, cy + 30 * mm, cx + 63 * mm, cy - 7 * mm)
    c.setFillColor(colors.HexColor("#4B4540"))
    c.setFont("Courier-Bold", 16)
    c.drawCentredString(cx, y + 28 * mm, "ÖFFNEN · ERINNERN · BRECHEN")
    c.setFont("Courier-Oblique", 9)
    c.drawString(x + 17 * mm, y + 14 * mm, "Nicht laut lesen, wenn Gruber im Raum ist.")


def draw_handout(c: canvas.Canvas, hid: str, title: str, spoiler: bool = False) -> None:
    width, height = A4
    c.setFillColor(PAPER if not spoiler else colors.HexColor("#25191D"))
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setStrokeColor(RUST if spoiler else CHARCOAL)
    c.setLineWidth(1.1)
    c.setDash(3, 2)
    c.rect(10 * mm, 10 * mm, width - 20 * mm, height - 20 * mm, fill=0, stroke=1)
    c.setDash()
    c.setFillColor(RUST if spoiler else CHARCOAL)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(18 * mm, height - 19 * mm, f"{hid} · BEWEISSTÜCK")
    c.setFont("Helvetica-Bold", 17)
    c.drawString(18 * mm, height - 31 * mm, title)
    c.setStrokeColor(RUST if spoiler else PAPER_DARK)
    c.line(18 * mm, height - 37 * mm, width - 18 * mm, height - 37 * mm)
    groups = {
        "H01": "FUNDORT · KUTSCHE  /  SPUR A",
        "H02": "FUNDORT · GASTHAUS  /  SPUR B",
        "H03": "FUNDORT · GASTHAUS  /  SPUR B",
        "H04": "FUNDORT · KIRCHE  /  SPUR C",
        "H05": "FUNDORT · RATHAUS  /  SPUR C",
        "H06": "FUNDORT · SCHMIEDE  /  SPUR D",
        "H07": "FUNDORT · DACHFENSTER  /  SPUR D",
        "H08": "FUNDORT · WALDRAND  /  SPUR D",
        "H09": "SL-ARCHIV · SPOILER  /  SPUR D",
        "H10": "FUNDORT · FORSTWEG  /  ORIENTIERUNG",
    }
    c.setFillColor(RUST if spoiler else COBALT)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(18 * mm, height - 45 * mm, groups.get(hid, "KRÄHENFELS · BEWEISARCHIV"))
    x, y, w, h = 22 * mm, 25 * mm, width - 44 * mm, height - 72 * mm
    if hid == "H01":
        draw_order(c, x, y, w, h)
    elif hid == "H02":
        draw_newspaper(c, x, y, w, h)
    elif hid == "H03":
        draw_guestbook(c, x, y, w, h)
    elif hid == "H05":
        draw_ledger(c, x, y, w, h)
    elif hid == "H07":
        image_contain(c, ASSETS / "ai_handouts" / "h07-child.png", x, y, w, h, colors.HexColor("#F4EBD6"))
        c.setFillColor(CHARCOAL)
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(x + w / 2, y + 17 * mm, "ER KOMMT, WENN DAS FEUER ERLISCHT")
    elif hid == "H08":
        image_contain(c, ASSETS / "ai_handouts" / "h08-rubbing.png", x, y, w, h, colors.HexColor("#CFC0A3"))
        c.setFillColor(CHARCOAL)
        c.setFont("Courier-Bold", 16)
        c.drawCentredString(x + w / 2, y + 17 * mm, "ÖFFNEN · ERINNERN · BRECHEN")
    elif hid == "H06":
        image_contain(c, ASSETS / "ai_handouts" / "h06-smithy.png", x, y, w, h, colors.HexColor("#D6C4A2"))
        c.setFillColor(CHARCOAL)
        c.setFont("Courier", 10)
        c.drawString(x + 20 * mm, y + 17 * mm, "Drei schwarze Nägel · altes Eisen · Feuer")
    elif hid == "H04":
        draw_oath(c, x, y, w, h)
    elif hid == "H10":
        image_contain(c, ASSETS / "map-v3-oak-player.png", x, y, w, h, colors.HexColor("#E2D4B8"))
    else:
        c.setFillColor(colors.HexColor("#E7DDC8"))
        c.rect(x, y, w, h, fill=1, stroke=0)
        c.setFillColor(CHARCOAL)
        c.setFont("Times-Roman", 11)
        body = {
            "H09": "<b>FRAGMENT DES ALTEN RITUALS</b><br/><br/><b>ÖFFNEN:</b> Das Dorf verweigert dem Eidbrecher seine Stimmen.<br/><br/><b>ERINNERN:</b> Die Namen der Gäste werden an der Eiche zurückgegeben.<br/><br/><b>BRECHEN:</b> Feuer und altes Eisen lösen die Geweihreliquie.",
        }.get(hid, "Ein Beweisstück aus Krähenfels.")
        paragraph(c, body, x + 18 * mm, y + 32 * mm, w - 36 * mm, h - 58 * mm, text_style(f"handout-{hid}", 11, 15, CHARCOAL, "Times-Roman"))
        c.setStrokeColor(PAPER_DARK)
        c.setLineWidth(0.7)
        c.line(x + 18 * mm, y + 24 * mm, x + w - 18 * mm, y + 24 * mm)
        c.setFont("Helvetica-Oblique", 7)
        c.setFillColor(RUST if spoiler else QUIET)
        c.drawString(x + 18 * mm, y + 15 * mm, f"Ausschneiden an der gestrichelten Außenlinie · {groups.get(hid, 'Beweisstück')}" )
    c.setFillColor(RUST if spoiler else QUIET)
    c.setFont("Helvetica", 7)
    c.drawRightString(width - 18 * mm, 15 * mm, "Krähenfels · Die letzte Kutsche")


def build_handouts(path: Path, ids: list[str], data: dict, spoiler: bool = False) -> None:
    c = canvas.Canvas(str(path), pagesize=A4)
    entries = {item["id"]: item for item in data["handouts"]}
    for hid in ids:
        entry = entries[hid]
        draw_handout(c, hid, entry["title"], spoiler or entry.get("spoiler", False))
        c.showPage()
    c.save()


def build_maps(data: dict) -> None:
    map_entries = {item["id"]: item for item in data["maps"]}
    for gm in (False, True):
        filename = OUTPUT / ("01_Karte_SL.pdf" if gm else "01_Karte_Spieler.pdf")
        c = canvas.Canvas(str(filename), pagesize=landscape(A4))
        width, height = landscape(A4)
        for map_id in ("MAP01", "MAP02", "MAP03", "MAP04", "MAP05", "MAP06"):
            entry = map_entries[map_id]
            page_title(c, entry["title"], "SL-Karte · Spoiler" if gm else "Spielerkarte · ohne Spoiler")
            image_name = entry["gmAsset"] if gm else entry["playerAsset"]
            image_cover(c, ASSETS / image_name, 18 * mm, 18 * mm, width - 36 * mm, height - 78 * mm)
            c.setFillColor(WARNING if gm else FROST)
            c.setFont("Helvetica-Bold", 8)
            c.drawString(20 * mm, 10 * mm, "SL-OVERLAY: Hinweis-IDs, geheime Räume und Prozession" if gm else "Spielerkarte: Wege, Gelände und sichtbare Gebäude")
            c.showPage()
        c.save()


def build_detail_maps(data: dict) -> None:
    path = OUTPUT / "01_Karten_Detail.pdf"
    c = canvas.Canvas(str(path), pagesize=landscape(A4))
    width, height = landscape(A4)
    for title, name in [("Gasthaus", "map-v3-inn-player.png"), ("Kirche und Friedhof", "map-v3-church-player.png"), ("Schmiede", "map-v3-smithy-player.png"), ("Rathaus und Archiv", "map-v3-archive-player.png"), ("Waldheiligtum", "map-v3-oak-player.png")]:
        page_title(c, title, "Detailkarte · Spielerfassung")
        image_cover(c, ASSETS / name, 18 * mm, 18 * mm, width - 36 * mm, height - 78 * mm)
        c.showPage()
    c.save()


def build_sl_adventure(path: Path, data: dict) -> None:
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=18 * mm, bottomMargin=16 * mm)
    story = [Paragraph("SL-Abenteuer", TITLE), Paragraph("Krähenfels: Die letzte Kutsche · spoilerhaltig", text_style("subtitle", 11, 14, RUST, bold=True)), Spacer(1, 8 * mm)]
    story.append(Paragraph("Wahrheit", text_style("truth", 15, 18, INK, bold=True)))
    story.append(Paragraph("Konrad Gruber verdreht das alte Gastrecht. Die Reisenden sollen als Gäste aufgenommen, eingeschlossen und an der Alten Eiche geopfert werden. Der Knochenhirsch ist der gebundene Waldgeist in seiner verdorbenen Form.", BODY))
    story.append(Spacer(1, 6 * mm))
    for scene in data["scenes"]:
        audio_line = " · ".join(f"<b>{entry['cueId']}</b>: {entry['playWhen']}" for entry in scene.get("audioPlan", []))
        story.extend([Paragraph(f"{scene['id']} · {scene['title']}", text_style(scene["id"], 15, 18, COBALT, bold=True)), Paragraph(f"<b>Ziel:</b> {scene['goal']}", BODY), Paragraph(f"<b>Vorlesen:</b> {scene['readAloud']}", BODY), Paragraph("<b>SL-Notizen:</b> " + " · ".join(scene["gmNotes"]), SMALL), Paragraph(f"<b>Hinweise:</b> {', '.join(scene['clueIds']) or 'keine'} · <b>Handouts:</b> {', '.join(scene['handoutIds']) or 'keine'}", SMALL), Paragraph(f"<b>Sound-Regie:</b> {audio_line}", SMALL), Spacer(1, 4 * mm)])
    doc.build(story)


def build_reference(path: Path, data: dict, mode: str) -> None:
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=14 * mm, leftMargin=14 * mm, topMargin=14 * mm, bottomMargin=14 * mm)
    if mode == "quick":
        story = [Paragraph("SL-Schnellreferenz", TITLE), Paragraph("Pflichtspuren, NPCs und Eskalation", text_style("qsub", 11, 14, RUST, bold=True))]
        rows = [["Fakt", "Hinweise", "Fallback"]] + [[fact["title"], ", ".join(fact["clueIds"]), fact["fallback"]] for fact in data["facts"]]
        table = Table(rows, colWidths=[43 * mm, 31 * mm, 100 * mm], repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), PANEL), ("TEXTCOLOR", (0, 0), (-1, 0), FROST), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 7.4), ("LEADING", (0, 0), (-1, -1), 9), ("GRID", (0, 0), (-1, -1), 0.3, PAPER_DARK), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2EEE4")])]))
        story.extend([Spacer(1, 6 * mm), table, Spacer(1, 8 * mm), Paragraph("Eskalation 0 bis 5", text_style("esc", 14, 17, INK, bold=True))])
        for level in data["threatLevels"]:
            story.append(Paragraph(f"<b>{level['level']} · {level['title']}</b> · {level['detail']} · Auslöser: {level['trigger']}", SMALL))
    else:
        compact = text_style("table_compact", 6.8, 8.2, INK)
        compact_bold = text_style("table_compact_bold", 6.8, 8.2, INK, bold=True)
        compact_head = text_style("table_compact_head", 6.8, 8.2, FROST, bold=True)
        story = [Paragraph("Am Tisch", TITLE), Paragraph("Was jetzt wichtig ist", text_style("atsub", 11, 14, RUST, bold=True))]
        story.extend([Paragraph("Vorlesen, nach einer Handlung fragen und Pflichtspuren auch bei einem misslungenen Wurf geben. Dorfspannung nur erhöhen, wenn eine Wahrheit offen ausgesprochen wird oder Gruber handeln muss.", BODY), Spacer(1, 4 * mm)])
        rows = [[Paragraph("Szene", compact_head), Paragraph("Gerade wichtig", compact_head), Paragraph("Nächster Hinweis", compact_head), Paragraph("Nächster Sound", compact_head), Paragraph("Stufe", compact_head)]]
        for scene in data["scenes"]:
            shock = next((entry for entry in scene.get("audioPlan", []) if entry["cueId"].startswith("SFX")), None)
            sound = f"{shock['cueId']}: {shock['playWhen']}" if shock else f"{scene['audioPlan'][0]['cueId']}: {scene['audioPlan'][0]['playWhen']}"
            rows.append([
                Paragraph(f"<b>{scene['id']}</b><br/>{scene['shortTitle']}", compact),
                Paragraph(scene["recommendation"], compact),
                Paragraph(", ".join(scene["clueIds"]) or "Nachhall statt Hinweis", compact),
                Paragraph(sound, compact),
                Paragraph(str(scene["escalation"]), compact_bold),
            ])
        table = Table(rows, colWidths=[22 * mm, 59 * mm, 31 * mm, 56 * mm, 12 * mm], repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), PANEL), ("GRID", (0, 0), (-1, -1), 0.25, PAPER_DARK), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3), ("TOPPADDING", (0, 1), (-1, -1), 4), ("BOTTOMPADDING", (0, 1), (-1, -1), 4), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2EEE4")])]))
        story.extend([table, Spacer(1, 5 * mm), Paragraph("Drei Finale", text_style("endings", 14, 17, INK, bold=True))])
        for ending in data["endings"]:
            story.append(Paragraph(f"<b>{ending['title']}</b> · {ending['summary']} Preis: {ending['cost']}", BODY))
    doc.build(story)


def build_audio_sheet(path: Path, data: dict) -> None:
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=15 * mm, leftMargin=15 * mm, topMargin=15 * mm, bottomMargin=15 * mm)
    cell = text_style("audio_cell", 7.1, 8.6, INK)
    cell_bold = text_style("audio_cell_bold", 7.1, 8.6, INK, bold=True)
    header_cell = text_style("audio_header", 7.1, 8.6, FROST, bold=True)
    layer_labels = {"musicBed": "Grundmusik", "musicLayer": "Musik-Layer", "ambient": "Atmosphäre", "sfx": "Effekt"}
    story = [
        Paragraph("Sound-Regie", TITLE),
        Paragraph("Wann du welchen Cue spielst", text_style("audsub", 11, 14, RUST, bold=True)),
        Paragraph("M01 vor dem ersten Vorlesetext starten und durch den ganzen Abend laufen lassen. Mit VORLESEN in der App absenken. STOP beendet im Notfall alle vier Audio-Layer sofort.", BODY),
        Spacer(1, 5 * mm),
    ]
    cues = {cue["id"]: cue for cue in data["audioCues"]}
    rows = [[Paragraph("Szene", header_cell), Paragraph("Cue", header_cell), Paragraph("Wann abspielen?", header_cell), Paragraph("Dein Einsatz", header_cell)]]
    for scene in data["scenes"]:
        for plan in scene.get("audioPlan", []):
            cue = cues[plan["cueId"]]
            optional = " · OPTIONAL" if plan.get("optional") else ""
            rows.append([
                Paragraph(f"<b>{scene['id']}</b><br/>{scene['shortTitle']}", cell),
                Paragraph(f"<b>{cue['id']} · {cue['title']}</b><br/>{layer_labels[cue['layer']]}{optional}", cell),
                Paragraph(plan["playWhen"], cell),
                Paragraph(plan["gmInstruction"], cell),
            ])
    table = Table(rows, colWidths=[25 * mm, 42 * mm, 54 * mm, 54 * mm], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), PANEL), ("TEXTCOLOR", (0, 0), (-1, 0), FROST), ("GRID", (0, 0), (-1, -1), 0.25, PAPER_DARK), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 1), (-1, -1), 5), ("BOTTOMPADDING", (0, 1), (-1, -1), 5), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2EEE4")])]))
    story.append(table)
    doc.build(story)


def main() -> None:
    data = load()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    build_start(OUTPUT / "00_Spielstart.pdf", data)
    build_characters(OUTPUT / "03_Figurenbau.pdf")
    build_item_cards(OUTPUT / "04_Gegenstandskarten.pdf", data)
    build_maps(data)
    build_detail_maps(data)
    build_handouts(OUTPUT / "02_Handouts.pdf", ["H01", "H02", "H03", "H04", "H05", "H06", "H07", "H08", "H10"], data)
    build_handouts(OUTPUT / "13_SL_Spoiler-Handouts.pdf", ["H09"], data, spoiler=True)
    build_sl_adventure(OUTPUT / "10_SL_Abenteuer.pdf", data)
    build_reference(OUTPUT / "11_SL_Schnellreferenz.pdf", data, "quick")
    build_reference(OUTPUT / "12_SL_Am_Tisch.pdf", data, "table")
    build_audio_sheet(OUTPUT / "14_Soundboard-Cues.pdf", data)
    print(f"Wrote V3 print pack to {OUTPUT}")


if __name__ == "__main__":
    main()
