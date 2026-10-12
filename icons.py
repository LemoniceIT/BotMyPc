"""
Icon management module for BotMyPC.

Provides pre-rendered, high-resolution icons as CTkImage objects
for CustomTkinter buttons, ensuring crisp high-DPI rendering and
exact vertical alignment with button text.
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional

from PIL import Image, ImageDraw, ImageFont
import customtkinter as ctk

from config import APP_NAME, ICONS_DIR
from i18n import t

logger = logging.getLogger(APP_NAME)

_ICON_CACHE: Dict[Tuple[str, int, int], ctk.CTkImage] = {}

# Fallback emoji map used if an icon file needs to be dynamically generated
ICON_EMOJI_MAP: Dict[str, str] = {
    "token": "🔑",
    "master": "👑",
    "background": "🗂️",
    "mail": "📧",
    "language": "🌐",
    "credits": "ℹ️",
    "play": "▶",
    "stop": "⏹",
    "save": "💾",
}


def _ensure_icon_exists(name: str, out_path: Path) -> bool:
    """Generates an icon image if missing on disk using Pillow and system fonts."""
    char = ICON_EMOJI_MAP.get(name)
    if not char:
        return False

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas_size = 48
    font_size = 38

    # Try standard Windows Emoji font
    font = None
    for font_name in ("seguiemj.ttf", "Segoe UI Emoji", "Arial"):
        try:
            font = ImageFont.truetype(font_name, font_size)
            break
        except Exception:
            continue

    if font is None:
        font = ImageFont.load_default()

    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        bbox = font.getbbox(char)
        bw = bbox[2] - bbox[0]
        bh = bbox[3] - bbox[1]
        x = (canvas_size - bw) // 2 - bbox[0]
        y = (canvas_size - bh) // 2 - bbox[1]
        draw.text((x, y), char, font=font, embedded_color=True)
    except Exception:
        # Fallback text draw
        draw.text((8, 8), char, fill=(0, 255, 102, 255))

    try:
        img.save(out_path, format="PNG")
        return True
    except Exception as e:
        logger.error(t("log_icon_generate_error", name=name, e=e))
        return False


def get_button_icon(name: str, size: Tuple[int, int] = (16, 16)) -> Optional[ctk.CTkImage]:
    """
    Returns a cached CTkImage for the specified icon name and pixel dimensions.
    Ensures transparent background and sharp scaling across High-DPI monitors.
    """
    cache_key = (name, size[0], size[1])
    if cache_key in _ICON_CACHE:
        return _ICON_CACHE[cache_key]

    icon_file = ICONS_DIR / f"{name}.png"
    if not icon_file.exists():
        _ensure_icon_exists(name, icon_file)

    if not icon_file.exists():
        logger.warning(t("log_icon_not_found", path=icon_file))
        return None

    try:
        pil_img = Image.open(icon_file).convert("RGBA")
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
        _ICON_CACHE[cache_key] = ctk_img
        return ctk_img
    except Exception as e:
        logger.error(t("log_icon_load_error", name=name, path=icon_file, e=e))
        return None
