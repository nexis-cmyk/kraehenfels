#!/usr/bin/env python3
"""Export the player-facing raster previews bundled with the native app."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RENDER_DIR = ROOT / "tmp" / "pdfs" / "session-materials" / "render-player"
HANDOUT_DIR = ROOT / "app" / "Kraehenfels" / "Resources" / "Materials" / "Handouts"
ITEM_DIR = ROOT / "app" / "Kraehenfels" / "Resources" / "Materials" / "Items"
ENDING_DIR = ROOT / "app" / "Kraehenfels" / "Resources" / "Materials" / "Endings"

HANDOUT_PAGES = {
    "handout-h01.png": "page-03.png",
    "handout-h02.png": "page-07.png",
    "handout-h03.png": "page-08.png",
    "handout-h04.png": "page-10.png",
    "handout-h05.png": "page-17.png",
    "handout-h06.png": "page-12.png",
    "handout-h07.png": "page-13.png",
    "handout-h08.png": "page-14.png",
    "handout-h10.png": "page-15.png",
}

# Coordinates are the six rounded cards on the A4 item-card sheet at 993 x 1404 px.
ITEM_CROPS = {
    "item-wool-blanket.png": (55, 56, 486, 472),
    "item-bandage-pouch.png": (507, 56, 936, 472),
    "item-hemp-rope.png": (55, 494, 486, 911),
    "item-storm-lantern.png": (507, 494, 936, 911),
    "item-tool-roll.png": (55, 932, 486, 1345),
    "item-revolver.png": (507, 932, 936, 1345),
}


def export_handouts() -> None:
    HANDOUT_DIR.mkdir(parents=True, exist_ok=True)
    for target_name, source_name in HANDOUT_PAGES.items():
        source_path = RENDER_DIR / source_name
        if not source_path.exists():
            raise FileNotFoundError(f"Missing rendered handout page: {source_path}")
        with Image.open(source_path) as image:
            image.convert("RGB").save(HANDOUT_DIR / target_name, format="PNG", optimize=True)


def export_item_cards() -> None:
    source_path = RENDER_DIR / "page-04.png"
    if not source_path.exists():
        raise FileNotFoundError(f"Missing rendered item-card page: {source_path}")
    ITEM_DIR.mkdir(parents=True, exist_ok=True)
    with Image.open(source_path) as image:
        if image.size != (993, 1404):
            raise ValueError(f"Unexpected item-card page size: {image.size}")
        for target_name, box in ITEM_CROPS.items():
            image.crop(box).convert("RGB").save(ITEM_DIR / target_name, format="PNG", optimize=True)


def export_ending_cards() -> None:
    source_path = RENDER_DIR / "page-19.png"
    if not source_path.exists():
        raise FileNotFoundError(f"Missing rendered ending-card page: {source_path}")
    ENDING_DIR.mkdir(parents=True, exist_ok=True)
    with Image.open(source_path) as image:
        image.convert("RGB").save(ENDING_DIR / "ending-cards.png", format="PNG", optimize=True)


def main() -> None:
    export_handouts()
    export_item_cards()
    export_ending_cards()
    print(f"Exported {len(HANDOUT_PAGES)} handout previews, {len(ITEM_CROPS)} item-card previews, and one ending-card sheet.")


if __name__ == "__main__":
    main()
