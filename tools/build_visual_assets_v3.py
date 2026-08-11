"""Build practical, illustrated top-down maps for the Krähenfels print pack.

The village overview is an atmospheric aerial plate. The location maps are
drawn deterministically so doors, furniture and clue locations stay readable
and consistent between the player and GM versions.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "print" / "assets" / "map-v3-village-player.png"
AI_MAPS = ROOT / "print" / "assets" / "ai_maps"
TARGETS = [ROOT / "print" / "assets", ROOT / "app" / "Kraehenfels" / "Resources" / "Art", ROOT / "web" / "assets" / "maps"]

W, H = 1800, 1200
NAVY = (11, 20, 31, 255)
INK = (22, 29, 35, 255)
FROST = (218, 231, 234, 255)
QUIET = (147, 169, 181, 255)
RUST = (193, 91, 70, 255)
AMBER = (204, 150, 75, 255)
PAPER = (221, 208, 176, 255)
WOOD = (111, 71, 45, 255)
WOOD_DARK = (65, 43, 33, 255)
STONE = (105, 113, 113, 255)
SNOW = (218, 226, 224, 255)
PINE = (37, 66, 56, 255)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(Path("C:/Windows/Fonts") / name, size)


def save_all(image: Image.Image, name: str) -> None:
    for directory in TARGETS:
        directory.mkdir(parents=True, exist_ok=True)
        image.save(directory / name, optimize=True)


def text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, size: int = 24, fill=FROST, bold: bool = False, anchor=None) -> None:
    draw.text(xy, value, font=font(size, bold), fill=fill, anchor=anchor)


def rounded_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, size: int = 20, fill=FROST, bg=(13, 24, 35, 230), outline=(181, 214, 234, 220)) -> None:
    x, y = xy
    box = draw.textbbox((x, y), value, font=font(size, True))
    pad_x, pad_y = 12, 7
    draw.rounded_rectangle((box[0] - pad_x, box[1] - pad_y, box[2] + pad_x, box[3] + pad_y), radius=8, fill=bg, outline=outline, width=2)
    draw.text((x, y), value, font=font(size, True), fill=fill)


def wood_texture(image: Image.Image, box: tuple[int, int, int, int], dark: bool = False) -> None:
    draw = ImageDraw.Draw(image)
    x1, y1, x2, y2 = box
    base = WOOD_DARK if dark else WOOD
    draw.rectangle(box, fill=base)
    for y in range(y1 + 12, y2, 24):
        draw.line((x1, y, x2, y), fill=(150, 99, 61, 145) if not dark else (95, 63, 48, 160), width=2)
        if y + 8 < y2:
            draw.line((x1, y + 8, x2, y + 8), fill=(53, 39, 34, 100), width=1)
    for x in range(x1 + 70, x2, 150):
        draw.line((x, y1, x + 30, y2), fill=(55, 41, 33, 85), width=2)


def stone_texture(image: Image.Image, box: tuple[int, int, int, int]) -> None:
    draw = ImageDraw.Draw(image)
    x1, y1, x2, y2 = box
    draw.rectangle(box, fill=STONE)
    for y in range(y1 + 20, y2, 42):
        draw.line((x1, y, x2, y), fill=(62, 72, 74, 170), width=2)
        offset = 0 if ((y - y1) // 42) % 2 else 38
        for x in range(x1 + offset, x2, 88):
            draw.line((x, y - 42, x - 8, y), fill=(66, 76, 77, 150), width=2)


def snow_texture(image: Image.Image, box: tuple[int, int, int, int]) -> None:
    draw = ImageDraw.Draw(image)
    x1, y1, x2, y2 = box
    draw.rectangle(box, fill=SNOW)
    for y in range(y1 + 12, y2, 20):
        draw.line((x1, y, x2, y + 2), fill=(181, 198, 200, 100), width=1)
    for x in range(x1 + 10, x2, 42):
        draw.ellipse((x, y1 + (x * 7) % max(1, y2 - y1), x + 3, y1 + (x * 7) % max(1, y2 - y1) + 3), fill=(255, 255, 255, 150))


def frame(image: Image.Image, title: str, subtitle: str, gm: bool, theme: str = "dark") -> ImageDraw.ImageDraw:
    draw = ImageDraw.Draw(image)
    if theme == "wood":
        wood_texture(image, (0, 0, W, H), dark=True)
    elif theme == "stone":
        stone_texture(image, (0, 0, W, H))
    elif theme == "snow":
        snow_texture(image, (0, 0, W, H))
    else:
        draw.rectangle((0, 0, W, H), fill=NAVY)
        for y in range(0, H, 18):
            draw.line((0, y, W, y + 1), fill=(28, 43, 56, 120), width=1)
    draw.rectangle((42, 36, W - 42, H - 38), outline=RUST if gm else FROST, width=4)
    text(draw, (74, 58), title, 42, RUST if gm else FROST, True)
    text(draw, (76, 112), subtitle, 19, QUIET if not gm else (244, 170, 155, 255), False)
    if gm:
        draw.rounded_rectangle((W - 360, 54, W - 74, 106), radius=10, fill=(71, 26, 30, 235), outline=RUST, width=2)
        text(draw, (W - 217, 80), "SL · SPOILER", 21, (255, 221, 211, 255), True, "mm")
    else:
        draw.rounded_rectangle((W - 360, 54, W - 74, 106), radius=10, fill=(19, 38, 55, 240), outline=FROST, width=2)
        text(draw, (W - 217, 80), "SPIELERKARTE", 21, FROST, True, "mm")
    return draw


def wall(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill=(46, 52, 52, 255), width: int = 12) -> None:
    draw.rectangle(box, fill=fill, outline=(215, 220, 211, 255), width=3)
    x1, y1, x2, y2 = box
    draw.line((x1, y1, x2, y1), fill=(32, 37, 38, 255), width=width)
    draw.line((x1, y1, x1, y2), fill=(32, 37, 38, 255), width=width)
    draw.line((x2, y1, x2, y2), fill=(32, 37, 38, 255), width=width)
    draw.line((x1, y2, x2, y2), fill=(32, 37, 38, 255), width=width)


def room(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], name: str, fill=(82, 75, 63, 255), label_fill=FROST) -> None:
    x1, y1, x2, y2 = box
    draw.rectangle(box, fill=fill)
    wall(draw, box, fill=fill, width=10)
    text(draw, (x1 + 20, y1 + 18), name, 23, label_fill, True)


def door(draw: ImageDraw.ImageDraw, xy: tuple[int, int], horizontal: bool = True, color=(238, 199, 129, 255)) -> None:
    x, y = xy
    if horizontal:
        draw.line((x - 30, y, x + 30, y), fill=color, width=9)
        draw.arc((x - 30, y - 30, x + 30, y + 30), 180, 270, fill=color, width=2)
    else:
        draw.line((x, y - 30, x, y + 30), fill=color, width=9)
        draw.arc((x - 30, y - 30, x + 30, y + 30), 270, 360, fill=color, width=2)


def window(draw: ImageDraw.ImageDraw, xy: tuple[int, int], horizontal: bool = True) -> None:
    x, y = xy
    if horizontal:
        draw.rectangle((x - 30, y - 7, x + 30, y + 7), fill=(111, 166, 184, 255), outline=(228, 237, 232, 255), width=2)
        draw.line((x, y - 7, x, y + 7), fill=(41, 67, 78, 255), width=2)
    else:
        draw.rectangle((x - 7, y - 30, x + 7, y + 30), fill=(111, 166, 184, 255), outline=(228, 237, 232, 255), width=2)
        draw.line((x - 7, y, x + 7, y), fill=(41, 67, 78, 255), width=2)


def table(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill=(126, 83, 52, 255)) -> None:
    draw.rounded_rectangle(box, radius=12, fill=fill, outline=(46, 32, 27, 255), width=3)
    x1, y1, x2, y2 = box
    draw.ellipse((x1 + 12, y1 + 8, x1 + 26, y1 + 22), fill=(215, 189, 134, 255))
    draw.ellipse((x2 - 26, y2 - 22, x2 - 12, y2 - 8), fill=(215, 189, 134, 255))


def bed(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = box
    draw.rectangle(box, fill=(108, 71, 53, 255), outline=(40, 32, 30, 255), width=3)
    draw.rectangle((x1 + 9, y1 + 9, x2 - 9, y2 - 9), fill=(177, 187, 178, 255))
    draw.rectangle((x1 + 12, y1 + 12, x2 - 12, y1 + 32), fill=(222, 215, 189, 255))


def hearth(draw: ImageDraw.ImageDraw, xy: tuple[int, int]) -> None:
    x, y = xy
    draw.ellipse((x - 42, y - 28, x + 42, y + 28), fill=(50, 37, 30, 255), outline=(230, 166, 81, 255), width=5)
    draw.polygon([(x, y - 21), (x + 17, y + 18), (x - 18, y + 18)], fill=(245, 115, 52, 255))


def marker(draw: ImageDraw.ImageDraw, xy: tuple[int, int], label: str, gm: bool) -> None:
    x, y = xy
    if gm:
        draw.ellipse((x - 26, y - 26, x + 26, y + 26), fill=(104, 33, 38, 240), outline=(255, 191, 167, 255), width=3)
        text(draw, (x, y), label, 17, (255, 231, 221, 255), True, "mm")


def legend(draw: ImageDraw.ImageDraw, lines: list[str], gm: bool) -> None:
    x1, y1, x2, y2 = 76, H - 154, 760, H - 68
    draw.rounded_rectangle((x1, y1, x2, y2), radius=10, fill=(8, 15, 24, 225), outline=RUST if gm else FROST, width=2)
    text(draw, (x1 + 18, y1 + 12), "LEGENDE", 15, RUST if gm else FROST, True)
    xx = x1 + 125
    for i, value in enumerate(lines):
        text(draw, (xx, y1 + 12 + (i % 2) * 30), value, 14, (247, 226, 191, 255) if gm else QUIET, False)
        if i % 2 == 1:
            xx += 290


def compass(draw: ImageDraw.ImageDraw, xy: tuple[int, int]) -> None:
    x, y = xy
    draw.ellipse((x - 36, y - 36, x + 36, y + 36), outline=FROST, width=2)
    draw.polygon([(x, y - 26), (x - 8, y + 7), (x + 8, y + 7)], fill=RUST)
    draw.polygon([(x, y + 26), (x - 8, y - 7), (x + 8, y - 7)], fill=QUIET)
    text(draw, (x, y - 55), "N", 16, FROST, True, "mm")


def village_gm() -> None:
    base = Image.open(BASE).convert("RGBA")
    player = base.copy()
    over = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(over)
    draw.rectangle((38, 35, 1498, 114), fill=(8, 17, 28, 228), outline=(181, 214, 234, 220), width=2)
    text(draw, (68, 50), "KRÄHENFELS", 34, FROST, True)
    text(draw, (68, 86), "Spielerkarte · November 1890 · Wege und sichtbare Gebäude", 16, QUIET)
    compass(draw, (1414, 81))
    points = [(286, 822, "1", "Kutschenstraße"), (935, 386, "2", "Zum schwarzen Keiler"), (760, 404, "3", "Kirche"), (1118, 566, "4", "Schmiede"), (1283, 158, "5", "Waldweg zur Alten Eiche")]
    for x, y, number, label in points:
        draw.ellipse((x - 18, y - 18, x + 18, y + 18), fill=(16, 39, 55, 235), outline=FROST, width=2)
        text(draw, (x, y), number, 18, FROST, True, "mm")
        rounded_label(draw, (x + 26, y - 13), label, 15)
    player = Image.alpha_composite(player, over)
    save_all(player, "map-v3-village-player.png")

    gm_over = over.copy()
    gm_draw = ImageDraw.Draw(gm_over)
    for x, y, number, _ in points:
        gm_draw.ellipse((x - 23, y - 23, x + 23, y + 23), outline=RUST, width=4)
    rounded_label(gm_draw, (1030, 870), "SL: C01/C02 · C03/C04 · C05 · C07 · FINALE", 17, (255, 226, 216, 255), (71, 26, 30, 235), RUST)
    gm = Image.alpha_composite(base, gm_over)
    save_all(gm, "map-v3-village-gm.png")


def make_inn(gm: bool) -> Image.Image:
    image = Image.new("RGBA", (W, H), (18, 25, 31, 255))
    draw = frame(image, "Zum schwarzen Keiler", "Krähenfels · Erdgeschoss · Orientierungskarte", gm, "wood")
    room(draw, (110, 220, 840, 1000), "Schankraum", (101, 71, 48, 255))
    room(draw, (890, 220, 1245, 490), "Küche", (94, 72, 54, 255))
    room(draw, (1285, 220, 1650, 490), "Treppenhaus", (72, 60, 53, 255))
    room(draw, (890, 550, 1650, 1000), "Gästezimmer", (91, 68, 54, 255))
    room(draw, (1285, 220, 1650, 490), "Treppenhaus", (72, 60, 53, 255))
    # Schankraum furniture
    draw.rectangle((150, 270, 800, 355), fill=(52, 34, 27, 255), outline=AMBER, width=3)
    text(draw, (174, 294), "THEKE", 18, (243, 210, 154, 255), True)
    for box in [(200, 455, 390, 550), (500, 455, 690, 550), (200, 665, 390, 760), (500, 665, 690, 760)]:
        table(draw, box)
    hearth(draw, (730, 875))
    for y in (285, 390, 610, 820): window(draw, (110, y), False)
    window(draw, (500, 1000), True)
    # kitchen details
    hearth(draw, (1045, 372))
    draw.rectangle((1140, 275, 1200, 450), fill=(126, 97, 66, 255), outline=(38, 31, 29, 255), width=3)
    text(draw, (1150, 292), "Herd", 16, FROST, True)
    # stairs and rooms
    for y in range(270, 450, 32): draw.line((1340, y, 1580, y), fill=(180, 161, 130, 255), width=3)
    bed(draw, (950, 640, 1190, 820)); bed(draw, (1340, 650, 1590, 830))
    draw.rectangle((950, 875, 1130, 940), fill=(71, 46, 33, 255), outline=AMBER, width=2)
    text(draw, (970, 894), "Koffer", 15, FROST, True)
    door(draw, (840, 640), False); door(draw, (890, 420), True); door(draw, (1245, 360), False); door(draw, (1285, 670), True)
    for xy in [(240, 220), (525, 220), (1000, 220), (1425, 220), (1650, 320), (1650, 760)]: window(draw, xy, True if xy[1] in (220,) else False)
    text(draw, (1140, 575), "Gästezimmer", 16, (213, 192, 161, 255), True)
    if gm:
        marker(draw, (625, 312), "H03", True)
        marker(draw, (1505, 930), "H05", True)
        rounded_label(draw, (1050, 1032), "SL: Büro hinter dem Gästezimmer · H05", 17, (255, 226, 216, 255), (71, 26, 30, 235), RUST)
    legend(draw, ["Tür", "Fenster", "Treppen", "Möbel"], gm)
    compass(draw, (1610, 1090))
    return image


def make_church(gm: bool) -> Image.Image:
    image = Image.new("RGBA", (W, H), (18, 25, 31, 255))
    draw = frame(image, "Kirche und Friedhof", "Krähenfels · Hauptschiff, Archiv und Turm", gm, "stone")
    room(draw, (120, 230, 1110, 1005), "Kirchenschiff", (127, 132, 128, 255))
    room(draw, (1180, 230, 1640, 550), "Archiv", (109, 110, 105, 255))
    room(draw, (1180, 620, 1640, 1005), "Sakristei", (98, 104, 100, 255))
    # nave and altar
    draw.rectangle((460, 280, 770, 360), fill=(88, 72, 59, 255), outline=(245, 222, 170, 255), width=3)
    text(draw, (615, 307), "ALTAR", 22, (248, 226, 175, 255), True, "mm")
    for row in range(4):
        for col in range(3):
            x = 250 + col * 210
            y = 470 + row * 120
            draw.rounded_rectangle((x, y, x + 140, y + 68), radius=8, fill=(86, 79, 67, 255), outline=(214, 219, 210, 255), width=2)
            draw.line((x + 20, y + 34, x + 120, y + 34), fill=(41, 46, 45, 255), width=3)
    draw.ellipse((870, 430, 1010, 570), fill=(88, 79, 64, 255), outline=(230, 206, 150, 255), width=4)
    text(draw, (940, 500), "Taufstein", 16, FROST, True, "mm")
    # archive shelves and desk
    for y in (300, 390, 480): draw.rectangle((1230, y, 1590, y + 35), fill=(83, 58, 43, 255), outline=(42, 31, 27, 255), width=2)
    table(draw, (1280, 720, 1530, 850), (99, 68, 46, 255))
    draw.rectangle((1240, 880, 1590, 950), fill=(73, 50, 40, 255), outline=AMBER, width=2)
    text(draw, (1415, 915), "Schrank", 16, FROST, True, "mm")
    # tower stairs
    for y in range(660, 960, 42): draw.line((1020, y, 1100, y), fill=(222, 216, 197, 255), width=3)
    text(draw, (1060, 585), "Turm", 17, FROST, True, "mm")
    door(draw, (1110, 650), False); door(draw, (1180, 760), True); door(draw, (1180, 390), True)
    for xy in [(120, 440), (120, 730), (1110, 490), (1380, 230), (1640, 390), (1640, 820)]: window(draw, xy, False if xy[0] in (120, 1640) else True)
    # cemetery outside strip
    draw.rectangle((120, 1050, 1640, 1090), fill=(49, 70, 64, 255))
    for x in range(180, 1600, 100): draw.rectangle((x, 1060, x + 28, 1085), fill=(180, 187, 177, 255))
    if gm:
        marker(draw, (1400, 335), "H04", True)
        marker(draw, (1060, 845), "H09", True)
        rounded_label(draw, (1040, 1032), "SL: ausgeschnittene Eidseite im Archiv · C05", 17, (255, 226, 216, 255), (71, 26, 30, 235), RUST)
    legend(draw, ["Pew", "Altar", "Archiv", "Turmaufgang"], gm)
    compass(draw, (1610, 1090))
    return image


def make_smithy(gm: bool) -> Image.Image:
    image = Image.new("RGBA", (W, H), (18, 25, 31, 255))
    draw = frame(image, "Schmiede Kern", "Krähenfels · Werkstatt und Eisenlager", gm, "wood")
    room(draw, (120, 235, 1110, 1000), "Werkstatt", (91, 67, 48, 255))
    room(draw, (1180, 235, 1640, 620), "Kohlenschuppen", (66, 56, 48, 255))
    room(draw, (1180, 690, 1640, 1000), "Eisenlager", (76, 62, 49, 255))
    hearth(draw, (360, 460))
    text(draw, (360, 535), "Esse", 19, (246, 218, 160, 255), True, "mm")
    draw.rectangle((540, 420, 760, 560), fill=(62, 53, 46, 255), outline=(225, 201, 153, 255), width=4)
    text(draw, (650, 488), "AMBOSS", 20, FROST, True, "mm")
    table(draw, (250, 700, 470, 830), (91, 61, 43, 255))
    for x in (560, 650, 740, 830):
        draw.line((x, 260, x, 360), fill=(224, 188, 120, 255), width=8)
        draw.line((x - 18, 335, x + 18, 335), fill=(224, 188, 120, 255), width=4)
    text(draw, (700, 285), "Werkzeugwand", 17, (243, 210, 156, 255), True, "mm")
    for x in (1240, 1340, 1440, 1540):
        draw.rectangle((x, 310, x + 54, 520), fill=(82, 60, 43, 255), outline=(30, 27, 25, 255), width=2)
        draw.ellipse((x + 14, 350, x + 40, 376), fill=(50, 49, 44, 255))
    for x in (1230, 1320, 1410, 1500):
        draw.rectangle((x, 760, x + 60, 925), fill=(105, 74, 46, 255), outline=(40, 28, 24, 255), width=2)
    door(draw, (1110, 500), False); door(draw, (1180, 790), True); door(draw, (1180, 410), True)
    for xy in [(120, 330), (120, 720), (570, 235), (880, 235), (1640, 350), (1640, 820)]: window(draw, xy, False if xy[0] in (120, 1640) else True)
    if gm:
        marker(draw, (650, 490), "H06", True)
        marker(draw, (1330, 840), "EISEN", True)
        rounded_label(draw, (1050, 1032), "SL: drei Nägel · altes Eisen für Finale E03", 17, (255, 226, 216, 255), (71, 26, 30, 235), RUST)
    legend(draw, ["Esse", "Amboss", "Werkzeugwand", "Lager"], gm)
    compass(draw, (1610, 1090))
    return image


def make_archive(gm: bool) -> Image.Image:
    image = Image.new("RGBA", (W, H), (18, 25, 31, 255))
    draw = frame(image, "Rathaus · Gemeindearchiv", "Krähenfels · Aktenraum hinter dem Sitzungssaal", gm, "wood")
    room(draw, (120, 235, 1060, 1000), "Sitzungssaal", (92, 75, 59, 255))
    room(draw, (1120, 235, 1640, 560), "Archiv", (76, 65, 56, 255))
    room(draw, (1120, 625, 1640, 1000), "Bürgermeisterzimmer", (83, 62, 52, 255))
    table(draw, (310, 470, 820, 700), (102, 69, 47, 255))
    for x in (390, 520, 650, 780):
        draw.ellipse((x - 16, 430, x + 16, 462), fill=(50, 39, 34, 255), outline=(221, 192, 142, 255), width=2)
    draw.rectangle((172, 300, 990, 380), fill=(61, 46, 39, 255), outline=AMBER, width=3)
    text(draw, (580, 337), "RATHAUS · 1890", 21, (241, 209, 156, 255), True, "mm")
    for y in (295, 390, 485): draw.rectangle((1200, y, 1580, y + 45), fill=(88, 58, 43, 255), outline=(37, 30, 27, 255), width=2)
    draw.rectangle((1210, 720, 1510, 870), fill=(95, 63, 45, 255), outline=(224, 188, 125, 255), width=3)
    text(draw, (1360, 785), "Schreibtisch", 19, FROST, True, "mm")
    draw.rectangle((1510, 720, 1590, 870), fill=(65, 45, 38, 255), outline=RUST, width=3)
    text(draw, (1550, 795), "Schubfach", 14, (255, 220, 205, 255), True, "mm")
    door(draw, (1060, 450), False); door(draw, (1120, 770), True); door(draw, (1120, 385), True)
    for xy in [(120, 350), (120, 800), (550, 235), (850, 235), (1640, 340), (1640, 820)]: window(draw, xy, False if xy[0] in (120, 1640) else True)
    if gm:
        marker(draw, (1330, 785), "H05", True)
        marker(draw, (1550, 795), "H09", True)
        rounded_label(draw, (1040, 1032), "SL: Buchhaltung · Ritualfragment im Schubfach", 17, (255, 226, 216, 255), (71, 26, 30, 235), RUST)
    legend(draw, ["Sitzungssaal", "Archiv", "Schreibtisch", "Schubfach"], gm)
    compass(draw, (1610, 1090))
    return image


def tree(draw: ImageDraw.ImageDraw, xy: tuple[int, int], scale: int = 1, dark: bool = False) -> None:
    x, y = xy
    trunk = (55, 49, 42, 255)
    crown = (27, 55, 45, 255) if not dark else (21, 42, 38, 255)
    draw.rectangle((x - 5 * scale, y, x + 5 * scale, y + 28 * scale), fill=trunk)
    draw.polygon([(x, y - 38 * scale), (x - 24 * scale, y + 8 * scale), (x + 24 * scale, y + 8 * scale)], fill=crown, outline=(19, 36, 33, 255))
    draw.polygon([(x, y - 18 * scale), (x - 30 * scale, y + 24 * scale), (x + 30 * scale, y + 24 * scale)], fill=crown, outline=(19, 36, 33, 255))


def make_oak(gm: bool) -> Image.Image:
    image = Image.new("RGBA", (W, H), (18, 25, 31, 255))
    draw = frame(image, "Waldheiligtum · Alte Eiche", "Krähenfels · Spielerkarte mit sichtbaren Wegen", gm, "snow")
    # clearing
    draw.ellipse((135, 230, 1660, 1020), fill=(205, 219, 216, 255), outline=(50, 76, 67, 255), width=8)
    # paths
    draw.line((155, 905, 420, 760, 670, 640), fill=(162, 132, 98, 255), width=66)
    draw.line((1660, 300, 1320, 430, 1090, 550), fill=(162, 132, 98, 255), width=66)
    draw.line((1090, 550, 910, 630), fill=(162, 132, 98, 255), width=46)
    # tree ring
    draw.ellipse((650, 420, 1130, 910), fill=(157, 166, 152, 255), outline=(54, 61, 54, 255), width=10)
    draw.ellipse((730, 495, 1050, 835), fill=(79, 61, 42, 255), outline=(40, 35, 30, 255), width=8)
    draw.ellipse((795, 560, 985, 770), fill=(102, 71, 42, 255), outline=(194, 136, 72, 255), width=5)
    text(draw, (890, 665), "ALTE\nEICHE", 25, (250, 226, 177, 255), True, "mm")
    # shrine and stones
    draw.rectangle((1080, 545, 1260, 675), fill=(58, 51, 45, 255), outline=(224, 214, 188, 255), width=5)
    draw.polygon([(1060, 545), (1170, 480), (1280, 545)], fill=(74, 63, 52, 255), outline=(224, 214, 188, 255))
    text(draw, (1170, 610), "SCHREIN", 17, FROST, True, "mm")
    for xy in [(380, 430), (510, 360), (1380, 340), (1470, 720), (400, 720), (1320, 880), (580, 910), (1450, 500)]: tree(draw, xy, 2 if xy[0] % 2 else 1)
    for xy in [(520, 560), (600, 720), (1310, 760), (1410, 590), (300, 650), (1500, 390)]:
        draw.ellipse((xy[0] - 18, xy[1] - 10, xy[0] + 18, xy[1] + 10), fill=(132, 137, 131, 255), outline=(76, 80, 76, 255), width=2)
    rounded_label(draw, (170, 285), "vom Dorf", 18)
    rounded_label(draw, (1460, 275), "Forstweg", 18)
    door(draw, (1080, 610), True)
    if gm:
        marker(draw, (1170, 610), "H06", True)
        marker(draw, (1365, 465), "E01", True)
        marker(draw, (470, 820), "Flucht", True)
        draw.arc((1170, 400, 1540, 770), 205, 325, fill=RUST, width=8)
        rounded_label(draw, (1020, 1032), "SL: Reliquie · Prozessionsweg · Fluchtweg", 17, (255, 226, 216, 255), (71, 26, 30, 235), RUST)
    legend(draw, ["Weg", "Baum", "Schrein", "Fels"], gm)
    compass(draw, (1610, 1090))
    return image


def annotate_ai_map(source: Path, title: str, subtitle: str, gm: bool, pins: list[tuple[float, float, str]], footer: str) -> Image.Image:
    """Add clean, typeset labels to a generated map without changing its art."""
    image = Image.open(source).convert("RGBA")
    draw = ImageDraw.Draw(image)
    width, height = image.size
    scale = max(0.65, min(width, height) / 1100)
    title_font = max(24, int(34 * scale))
    small_font = max(13, int(17 * scale))
    # The generated plates have a clear parchment margin. Keep type there.
    draw.rounded_rectangle((int(width * .055), int(height * .035), int(width * .945), int(height * .115)), radius=int(8 * scale), fill=(11, 20, 31, 205), outline=RUST if gm else FROST, width=max(2, int(2 * scale)))
    text(draw, (int(width * .075), int(height * .055)), title, title_font, (255, 225, 205, 255) if gm else FROST, True)
    map_subtitle = subtitle
    if gm:
        map_subtitle = map_subtitle.replace("Spielerkarte", "Spielleiterkarte · Spoiler")
        if map_subtitle == subtitle:
            map_subtitle = f"{map_subtitle} · Spielleiterkarte · Spoiler"
    text(draw, (int(width * .075), int(height * .091)), map_subtitle, small_font, (243, 173, 154, 255) if gm else QUIET, False)
    badge = "SL · SPOILER" if gm else "SPIELERKARTE"
    draw.rounded_rectangle((int(width * .76), int(height * .052), int(width * .915), int(height * .103)), radius=int(7 * scale), fill=(75, 26, 31, 225) if gm else (19, 38, 55, 230), outline=RUST if gm else FROST, width=max(2, int(2 * scale)))
    text(draw, (int(width * .8375), int(height * .077)), badge, max(13, int(17 * scale)), (255, 228, 218, 255) if gm else FROST, True, "mm")
    for nx, ny, label in pins:
        x, y = int(width * nx), int(height * ny)
        if gm:
            draw.ellipse((x - int(20 * scale), y - int(20 * scale), x + int(20 * scale), y + int(20 * scale)), fill=(104, 33, 38, 230), outline=(255, 207, 191, 255), width=max(2, int(2 * scale)))
            text(draw, (x, y), label, max(12, int(15 * scale)), (255, 231, 221, 255), True, "mm")
    draw.rounded_rectangle((int(width * .055), int(height * .91), int(width * .58), int(height * .965)), radius=int(7 * scale), fill=(9, 17, 27, 215), outline=RUST if gm else FROST, width=max(2, int(2 * scale)))
    text(draw, (int(width * .075), int(height * .927)), footer, small_font, (255, 224, 212, 255) if gm else QUIET, False)
    return image


def build_ai_maps() -> None:
    entries = [
        ("village.png", "map-v3-village-player.png", "map-v3-village-gm.png", "Krähenfels", "Krähenfels · Übersicht · sichtbare Wege und Gebäude", [(0.43, 0.37, "H01"), (0.78, 0.40, "H04"), (0.17, 0.64, "H06"), (0.79, 0.18, "H10")], "Dorfplatz, Kutschenstraße, Kirche, Schmiede, Bach und Waldheiligtum"),
        ("inn.png", "map-v3-inn-player.png", "map-v3-inn-gm.png", "Zum schwarzen Keiler", "Krähenfels · Erdgeschoss · Spielerkarte", [(0.38, 0.29, "H03"), (0.75, 0.57, "C04")], "Bar, Küche, Treppe und Gästezimmer · keine SL-Fundstellen"),
        ("church.png", "map-v3-church-player.png", "map-v3-church-gm.png", "Kirche und Friedhof", "Krähenfels · Kirchenschiff, Archiv und Turm", [(0.76, 0.72, "H04")], "Kirchenschiff, Archiv, Sakristei und Friedhof · C05 im Kirchenbuch"),
        ("smithy.png", "map-v3-smithy-player.png", "map-v3-smithy-gm.png", "Schmiede Kern", "Krähenfels · Werkstatt und Eisenlager", [(0.53, 0.50, "H06")], "Esse, Amboss, Werkzeugwand und Eisenlager · Fundstück bleibt sichtbar"),
        ("archive.png", "map-v3-archive-player.png", "map-v3-archive-gm.png", "Rathaus und Gemeindearchiv", "Krähenfels · Sitzungssaal, Archiv und Bürgermeisterzimmer", [(0.78, 0.72, "H05"), (0.80, 0.51, "H09")], "Sitzungssaal, Archiv und Büro · SL-Fundstellen markiert"),
        ("oak.png", "map-v3-oak-player.png", "map-v3-oak-gm.png", "Waldheiligtum · Alte Eiche", "Krähenfels · Forstweg, Lichtung und Schrein", [(0.58, 0.55, "H10"), (0.65, 0.61, "E")], "Forstweg, Alte Eiche, Schrein und Spuren · keine Kampfraster"),
    ]
    for source_name, player_name, gm_name, title, subtitle, pins, footer in entries:
        source = AI_MAPS / source_name
        if not source.exists():
            continue
        player = annotate_ai_map(source, title, subtitle, False, pins, footer)
        gm = annotate_ai_map(source, title, subtitle, True, pins, footer.replace("keine SL-Fundstellen", "SL-Markierungen: H03/C04").replace("Fundstück bleibt sichtbar", "SL-Markierung: H06").replace("SL-Fundstellen markiert", "SL-Markierungen: H05/H09").replace("keine Kampfraster", "SL-Markierungen: E01/E02/E03"))
        save_all(player, player_name)
        save_all(gm, gm_name)


def main() -> None:
    village_gm()
    save_all(make_inn(False), "map-v3-inn-player.png")
    save_all(make_inn(True), "map-v3-inn-gm.png")
    save_all(make_church(False), "map-v3-church-player.png")
    save_all(make_church(True), "map-v3-church-gm.png")
    save_all(make_smithy(False), "map-v3-smithy-player.png")
    save_all(make_smithy(True), "map-v3-smithy-gm.png")
    save_all(make_archive(False), "map-v3-archive-player.png")
    save_all(make_archive(True), "map-v3-archive-gm.png")
    save_all(make_oak(False), "map-v3-oak-player.png")
    save_all(make_oak(True), "map-v3-oak-gm.png")
    build_ai_maps()
    print("Built illustrated V3 map variants")


if __name__ == "__main__":
    main()
