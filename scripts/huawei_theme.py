"""Huawei visual spec constants and MckEngine theme adapter."""

from typing import Dict, Any

HUAWEI_COLORS = {
    "red": "#C7000B",
    "title_black": "#231815",
    "body_gray": "#595757",
    "white": "#FFFFFF",
    "light_gray": "#DCDDDD",
    "orange": "#ED6D00",
    "yellow": "#FCC800",
    "green": "#62B230",
    "blue": "#30B5C5",
}

HUAWEI_FONTS = {
    "zh": "Microsoft YaHei",
    "en": "Arial",
}

# Huawei ICT Academy style: light background, red accent used sparingly
MCK_THEME = {
    "bg_color": HUAWEI_COLORS["white"],
    "text_color": HUAWEI_COLORS["body_gray"],
    "title_color": HUAWEI_COLORS["title_black"],
    "accent_color": HUAWEI_COLORS["red"],
    "secondary_accent": HUAWEI_COLORS["blue"],
    "title_font": HUAWEI_FONTS["zh"],
    "body_font": HUAWEI_FONTS["zh"],
    "en_font": HUAWEI_FONTS["en"],
}


def apply_to_mck_engine() -> Dict[str, Any]:
    """Return a dict that MckEngine code can use to override default theme."""
    return MCK_THEME.copy()


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert '#C7000B' to (199, 0, 11)."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
