"""Build the Krähenfels 3.0 printable player and GM pack."""

from __future__ import annotations

import json
import math
from pathlib import Path

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
    c.drawString(18 * mm, 12 * mm, "How to be a Hero · W100 · Version 3.0.0")
    c.showPage()
    page_title(c, "Spielstart", "Für die Spielleitung · 20 Minuten Vorbereitung")
    y = height - 55 * mm
    steps = [
        ("Tisch", "Lege die Spielerkarte, Figurenbögen und H01 bis H08 verdeckt bereit. H09 bleibt bei dir."),
        ("Figuren", "Die drei Spieler erstellen eigene HTBAH-Figuren und wählen je einen Reisehaken aus der Akte."),
        ("Einstieg", "Starte A01 leise. Lies S01 vor. Frage nur: Was tut ihr? Gib H01 unabhängig vom Würfelwurf."),
        ("Leitung", "Setze die Dorfspannung manuell. Die App zeigt Empfehlungen, entscheidet aber nie an deiner Stelle."),
        ("Grenzen", "Kinder bleiben sicher. Gewalt bleibt unheimlich und dosiert. Sprich vor Beginn kurz über Stoppsignale."),
    ]
    for title, body in steps:
        c.setFillColor(COBALT)
        c.circle(23 * mm, y + 2 * mm, 3 * mm, fill=1, stroke=0)
        c.setFillColor(FROST)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(33 * mm, y, title)
        paragraph(c, body, 33 * mm, y - 15 * mm, width - 52 * mm, 18 * mm, text_style("step" + title, 9.5, 12, colors.white))
        y -= 28 * mm
    c.showPage()
    c.save()


def build_characters(path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    for page in range(2):
        page_title(c, "Figurenbau", "How to be a Hero · W100")
        c.setFillColor(INK)
        c.roundRect(18 * mm, height - 85 * mm, width - 36 * mm, 32 * mm, 5 * mm, fill=1, stroke=0)
        c.setFillColor(FROST)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(25 * mm, height - 67 * mm, "Name der Figur:")
        c.line(62 * mm, height - 68 * mm, 125 * mm, height - 68 * mm)
        c.drawString(135 * mm, height - 67 * mm, "Reisehaken:")
        c.line(170 * mm, height - 68 * mm, 190 * mm, height - 68 * mm)
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
        c.drawString(18 * mm, 15 * mm, f"Seite {page + 1} · Krähenfels: Die letzte Kutsche")
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
    x, y, w, h = 22 * mm, 25 * mm, width - 44 * mm, height - 72 * mm
    if hid == "H02":
        draw_newspaper(c, x, y, w, h)
    elif hid == "H03":
        draw_guestbook(c, x, y, w, h)
    elif hid == "H05":
        draw_ledger(c, x, y, w, h)
    elif hid == "H07":
        c.setFillColor(colors.HexColor("#F5EEDA"))
        c.rect(x, y, w, h, fill=1, stroke=0)
        c.setStrokeColor(colors.HexColor("#5D5145"))
        c.setLineWidth(3)
        c.circle(x + w / 2, y + h / 2 + 10 * mm, 58 * mm, fill=0, stroke=1)
        c.line(x + w / 2, y + h / 2 + 10 * mm, x + w / 2 - 45 * mm, y + h / 2 - 45 * mm)
        c.line(x + w / 2, y + h / 2 + 10 * mm, x + w / 2 + 45 * mm, y + h / 2 - 45 * mm)
        for angle in range(0, 360, 60):
            xx = x + w / 2 + math.cos(math.radians(angle)) * 84 * mm
            yy = y + h / 2 + 10 * mm + math.sin(math.radians(angle)) * 84 * mm
            c.line(x + w / 2, y + h / 2 + 10 * mm, xx, yy)
        c.setFont("Courier", 13)
        c.drawCentredString(x + w / 2, y + 25 * mm, "öffnen   erinnern   brechen")
    elif hid == "H08":
        c.setFillColor(colors.HexColor("#D5C7AA"))
        c.rect(x, y, w, h, fill=1, stroke=0)
        c.setStrokeColor(CHARCOAL)
        c.setLineWidth(4)
        c.circle(x + w / 2, y + h / 2, 70 * mm, fill=0, stroke=1)
        c.line(x + w / 2 - 55 * mm, y + h / 2, x + w / 2 + 35 * mm, y + h / 2 + 25 * mm)
        c.line(x + w / 2 + 35 * mm, y + h / 2 + 25 * mm, x + w / 2 + 70 * mm, y + h / 2 - 10 * mm)
        c.setFont("Courier-Bold", 19)
        c.drawString(x + 18 * mm, y + 25 * mm, "ÖFFNEN · ERINNERN · BRECHEN")
    elif hid == "H06":
        c.setFillColor(colors.HexColor("#E3D4B8"))
        c.rect(x, y, w, h, fill=1, stroke=0)
        c.setStrokeColor(CHARCOAL)
        c.setLineWidth(2)
        c.line(x + 30 * mm, y + 55 * mm, x + w - 30 * mm, y + 55 * mm)
        c.line(x + w / 2, y + 55 * mm, x + w / 2, y + h - 40 * mm)
        c.setFillColor(CHARCOAL)
        c.setFont("Helvetica-Bold", 19)
        c.drawString(x + 28 * mm, y + h - 32 * mm, "GEWEIHRELIQUIE")
        c.setFont("Helvetica", 12)
        c.drawString(x + 28 * mm, y + h - 48 * mm, "drei schwarze Nägel · Eisenstange · Feuer")
        c.setFont("Courier", 10)
        c.drawString(x + 28 * mm, y + 34 * mm, "Feuer löst die Bindung. Ein Eid kann sie wenden.")
    elif hid == "H10":
        image_cover(c, ASSETS / "map-v3-oak-player.png", x, y, w, h)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x + 12 * mm, y + 12 * mm, "Alter Forstweg zur Alten Eiche")
    else:
        c.setFillColor(colors.HexColor("#E7DDC8"))
        c.rect(x, y, w, h, fill=1, stroke=0)
        c.setFillColor(CHARCOAL)
        c.setFont("Times-Roman", 11)
        body = {
            "H01": "<b>POST- UND FRACHTAUFTRAG</b><br/><br/>Umleitung über Krähenfels. Zahlung bestätigt durch K. Gruber.<br/><br/>Gäste vor Mitternacht unter Dach bringen.<br/><br/>Die Achse ist vor Abfahrt geprüft worden.<br/><br/><font name='Courier'>Stempel: K. GRUBER · 28. NOVEMBER 1890</font>",
            "H04": "<b>KIRCHENBUCH · AUSZUG</b><br/><br/>Wer unter Dach aufgenommen ist, bleibt bis zum ersten Hahnenschrei Gast.<br/><br/>Kein Messer, kein Seil und kein Name soll ihn an den Wald zurückgeben.",
            "H09": "<b>FRAGMENT DES ALTEN RITUALS</b><br/><br/><b>ÖFFNEN:</b> Das Dorf verweigert dem Eidbrecher seine Stimmen.<br/><br/><b>ERINNERN:</b> Die Namen der Gäste werden an der Eiche zurückgegeben.<br/><br/><b>BRECHEN:</b> Feuer und altes Eisen lösen die Geweihreliquie.",
        }.get(hid, "Ein Beweisstück aus Krähenfels.")
        paragraph(c, body, x + 18 * mm, y + 32 * mm, w - 36 * mm, h - 58 * mm, text_style(f"handout-{hid}", 11, 15, CHARCOAL, "Times-Roman"))
        c.setStrokeColor(PAPER_DARK)
        c.setLineWidth(0.7)
        c.line(x + 18 * mm, y + 24 * mm, x + w - 18 * mm, y + 24 * mm)
        c.setFont("Helvetica-Oblique", 7)
        c.setFillColor(RUST if spoiler else QUIET)
        c.drawString(x + 18 * mm, y + 15 * mm, "Ausschneiden an der gestrichelten Außenlinie · als Beweisstück ausgeben")
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
        for map_id in ("MAP01", "MAP02", "MAP03", "MAP04"):
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
    for title, name in [("Gasthaus", "map-v3-inn-player.png"), ("Kirche und Friedhof", "map-v3-church-player.png"), ("Alte Eiche", "map-v3-oak-player.png")]:
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
        story.extend([Paragraph(f"{scene['id']} · {scene['title']}", text_style(scene["id"], 15, 18, COBALT, bold=True)), Paragraph(f"<b>Ziel:</b> {scene['goal']}", BODY), Paragraph(f"<b>Vorlesen:</b> {scene['readAloud']}", BODY), Paragraph("<b>SL-Notizen:</b> " + " · ".join(scene["gmNotes"]), SMALL), Paragraph(f"<b>Hinweise:</b> {', '.join(scene['clueIds']) or 'keine'} · <b>Handouts:</b> {', '.join(scene['handoutIds']) or 'keine'} · <b>Sound:</b> {scene['soundPreset']}", SMALL), Spacer(1, 4 * mm)])
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
        story = [Paragraph("Am Tisch", TITLE), Paragraph("Die eine Seite für den Abend", text_style("atsub", 11, 14, RUST, bold=True))]
        story.extend([Paragraph("1. Vorlesen, dann fragen: Was tut ihr?", BODY), Paragraph("2. Pflichtspur geben, auch wenn der Wurf misslingt.", BODY), Paragraph("3. Eskalation manuell erhöhen, wenn die Gruppe einen Fakt offen ausspricht.", BODY), Paragraph("4. Bei Stillstand den Fallback des nächsten Faktums verwenden.", BODY), Paragraph("5. Vor dem Finale die drei Wege sichtbar benennen.", BODY), Spacer(1, 6 * mm), Paragraph("Drei Finale", text_style("endings", 14, 17, INK, bold=True))])
        for ending in data["endings"]:
            story.append(Paragraph(f"<b>{ending['title']}</b> · {ending['summary']} Preis: {ending['cost']}", BODY))
    doc.build(story)


def build_audio_sheet(path: Path, data: dict) -> None:
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=15 * mm, leftMargin=15 * mm, topMargin=15 * mm, bottomMargin=15 * mm)
    story = [Paragraph("Soundboard-Cues", TITLE), Paragraph("Kompakt filmisch · Keine plötzlichen Spitzen", text_style("audsub", 11, 14, RUST, bold=True))]
    rows = [["ID", "Cue", "Einsatz", "Beschreibung"]]
    for cue in data["audioCues"]:
        rows.append([cue["id"], cue["title"], cue["category"], cue.get("description", "")])
    table = Table(rows, colWidths=[14 * mm, 44 * mm, 23 * mm, 92 * mm], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), PANEL), ("TEXTCOLOR", (0, 0), (-1, 0), FROST), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 7.3), ("LEADING", (0, 0), (-1, -1), 9), ("GRID", (0, 0), (-1, -1), 0.25, PAPER_DARK), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2EEE4")])]))
    story.extend([Spacer(1, 6 * mm), table])
    doc.build(story)


def main() -> None:
    data = load()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    build_start(OUTPUT / "00_Spielstart.pdf", data)
    build_characters(OUTPUT / "03_Figurenbau.pdf")
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
