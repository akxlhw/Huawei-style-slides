"""Huawei visual spec constants and MckEngine theme adapter.

Colors and fonts are loaded from theme.yaml (editable, no code change needed
to re-brand). Falls back to hardcoded defaults if YAML is missing or unreadable.
"""
from pathlib import Path
from typing import Dict, Any

# ── Defaults (used if theme.yaml is unavailable) ─────────────────────────────
_DEFAULT_COLORS = {
    "red": "#CF0A2C", "title_black": "#231815", "body_gray": "#595757",
    "med_gray": "#999999", "white": "#FFFFFF", "light_gray": "#DCDDDD",
    "tech_blue": "#007DFF", "orange": "#FF9900", "yellow": "#FCC800",
    "green": "#669900", "ict_blue": "#30B5C5", "bg_gray": "#F5F5F5",
}
_DEFAULT_FONTS = {"zh": "Microsoft YaHei", "en": "Arial"}

_THEME_YAML = Path(__file__).resolve().parent.parent / "theme.yaml"

# Support dark theme via HUAWEI_THEME=dark env var.
import os as _os
_theme_name = _os.getenv("HUAWEI_THEME", "").lower()
if _theme_name in ("dark", "deep"):
    _dark = Path(__file__).resolve().parent.parent / "theme-dark.yaml"
    if _dark.is_file():
        _THEME_YAML = _dark


def _load_theme_yaml() -> Dict[str, Any]:
    """Load theme.yaml if available; return empty dict on failure."""
    try:
        import yaml
        if _THEME_YAML.is_file():
            return yaml.safe_load(_THEME_YAML.read_text(encoding="utf-8")) or {}
    except Exception:
        pass
    return {}


_theme = _load_theme_yaml()

HUAWEI_COLORS = _theme.get("colors", _DEFAULT_COLORS)
HUAWEI_FONTS = _theme.get("fonts", _DEFAULT_FONTS)
HUAWEI_BRAND = _theme.get("brand", {"zh": "华为 ICT", "en": "HUAWEI ICT"})

MCK_THEME = {
    "bg_color": HUAWEI_COLORS.get("white", "#FFFFFF"),
    "text_color": HUAWEI_COLORS.get("body_gray", "#595757"),
    "title_color": HUAWEI_COLORS.get("title_black", "#231815"),
    "accent_color": HUAWEI_COLORS.get("red", "#CF0A2C"),
    "secondary_accent": HUAWEI_COLORS.get("tech_blue", "#007DFF"),
    "title_font": HUAWEI_FONTS.get("zh", "Microsoft YaHei"),
    "body_font": HUAWEI_FONTS.get("zh", "Microsoft YaHei"),
    "en_font": HUAWEI_FONTS.get("en", "Arial"),
}


def apply_to_mck_engine() -> Dict[str, Any]:
    """Return a dict that MckEngine code can use to override default theme."""
    return MCK_THEME.copy()


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert '#CF0A2C' to (207, 10, 44)."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
