import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from huawei_theme import HUAWEI_COLORS, HUAWEI_FONTS, apply_to_mck_engine

def test_huawei_colors():
    assert HUAWEI_COLORS["red"] == "#C7000B"
    assert HUAWEI_COLORS["title_black"] == "#231815"
    assert HUAWEI_COLORS["body_gray"] == "#595757"

def test_huawei_fonts():
    assert HUAWEI_FONTS["zh"] == "Microsoft YaHei"
    assert HUAWEI_FONTS["en"] == "Arial"

def test_apply_to_mck_engine_returns_dict():
    result = apply_to_mck_engine()
    assert "bg_color" in result
    assert "title_font" in result
    assert result["accent_color"] == HUAWEI_COLORS["red"]
