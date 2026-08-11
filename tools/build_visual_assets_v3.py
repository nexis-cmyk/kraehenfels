"""Create practical map variants from the generated village overview."""

from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "print" / "assets" / "map-v3-village-player.png"
TARGETS = [ROOT / "print" / "assets", ROOT / "app" / "Kraehenfels" / "Resources" / "Art", ROOT / "web" / "assets" / "maps"]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(Path("C:/Windows/Fonts") / name, size)


def save_all(image: Image.Image, name: str) -> None:
    for directory in TARGETS:
        directory.mkdir(parents=True, exist_ok=True)
        image.save(directory / name, optimize=True)


def label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill=(232, 239, 243, 255), size=24, box=(9, 17, 29, 210)) -> None:
    x, y = xy
    bbox = draw.textbbox((x, y), text, font=font(size, True))
    pad = 8
    draw.rounded_rectangle((bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad), radius=5, fill=box, outline=(181, 214, 234, 210), width=1)
    draw.text((x, y), text, font=font(size, True), fill=fill)


def village_gm() -> None:
    image = Image.open(BASE).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    label(draw, (215, 410), "KUTSCHENSTRASSE · C01/C02", size=22)
    label(draw, (690, 510), "SCHWARZER KEILER · C03/C04", size=22)
    label(draw, (750, 190), "KIRCHE · C05", size=22)
    label(draw, (1020, 520), "SCHMIEDE · C07", size=22)
    label(draw, (1130, 70), "ALTE EICHE · FINALE", size=22, box=(96, 35, 28, 225))
    draw.line((755, 610, 1270, 150), fill=(205, 123, 110, 220), width=5)
    draw.ellipse((1170, 60, 1270, 160), outline=(205, 123, 110, 230), width=5)
    result = Image.alpha_composite(image, overlay)
    save_all(result, "map-v3-village-gm.png")


def detail_map(name: str, title: str, rooms: list[tuple[int, int, int, int, str]], hidden: list[tuple[int, int, int, int, str]]) -> None:
    width, height = 1500, 1000
    image = Image.new("RGB", (width, height), (15, 25, 38))
    draw = ImageDraw.Draw(image)
    for y in range(0, height, 16):
        draw.line((0, y, width, y), fill=(20 + (y % 32) // 4, 31, 45), width=1)
    draw.rectangle((46, 40, width - 46, height - 50), outline=(181, 214, 234), width=3)
    draw.text((72, 64), title, font=font(36, True), fill=(181, 214, 234))
    draw.text((74, 112), "Krähenfels · November 1890 · Spielerkarte", font=font(18), fill=(148, 170, 188))
    for x1, y1, x2, y2, text in rooms:
        draw.rectangle((x1, y1, x2, y2), fill=(46, 59, 72), outline=(214, 226, 234), width=3)
        draw.text((x1 + 15, y1 + 15), text, font=font(23, True), fill=(232, 239, 243))
    for x1, y1, x2, y2, text in hidden:
        draw.rectangle((x1, y1, x2, y2), fill=(73, 33, 40), outline=(205, 123, 110), width=4)
        draw.text((x1 + 15, y1 + 15), text, font=font(21, True), fill=(255, 218, 209))
    draw.text((74, height - 92), "Wände und Wege sind schematisch. Die Karte dient der Orientierung, nicht dem Kampf-Raster.", font=font(17), fill=(148, 170, 188))
    save_all(image, name)


def main() -> None:
    village_gm()
    detail_map("map-v3-inn-player.png", "Zum schwarzen Keiler", [(110, 210, 650, 770, "Schankraum"), (700, 210, 1050, 460, "Küche"), (1100, 210, 1370, 460, "Treppenhaus"), (700, 520, 1370, 770, "Gästezimmer")], [])
    detail_map("map-v3-inn-gm.png", "Zum schwarzen Keiler · SL", [(110, 210, 650, 770, "Schankraum"), (700, 210, 1050, 460, "Küche"), (1100, 210, 1370, 460, "Treppenhaus"), (700, 520, 1370, 770, "Gästezimmer")], [(1050, 520, 1370, 770, "Grubers Büro · H05")])
    detail_map("map-v3-church-player.png", "Kirche und Friedhof", [(120, 210, 880, 760, "Kirchenschiff"), (930, 210, 1340, 470, "Archiv"), (930, 530, 1340, 760, "Sakristei")], [])
    detail_map("map-v3-church-gm.png", "Kirche und Friedhof · SL", [(120, 210, 880, 760, "Kirchenschiff"), (930, 210, 1340, 470, "Archiv · H04"), (930, 530, 1340, 760, "Sakristei")], [(460, 120, 690, 205, "Turmboden")])
    detail_map("map-v3-oak-player.png", "Alte Eiche", [(110, 210, 1370, 770, "Waldlichtung"), (580, 350, 900, 640, "Alte Eiche")], [])
    detail_map("map-v3-oak-gm.png", "Alte Eiche · SL", [(110, 210, 1370, 770, "Waldlichtung"), (580, 350, 900, 640, "Alte Eiche")], [(930, 250, 1250, 430, "Prozession"), (270, 580, 530, 730, "Fluchtweg")])
    print("Built V3 map variants")


if __name__ == "__main__":
    main()
