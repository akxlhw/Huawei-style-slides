import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from html_validator import validate_html


def test_validate_html_passes_good_file(tmp_path):
    html = tmp_path / "slides.html"
    html.write_text(
        "<html><body><div class='deck-stage'><section class='slide'>x</section></div></body></html>",
        encoding="utf-8",
    )
    result = validate_html(html, expected_slides=1)
    assert result["ok"] is True


def test_validate_html_counts_slides(tmp_path):
    html = tmp_path / "slides.html"
    html.write_text(
        "<html><body><div class='deck-stage'><section class='slide'></section><section class='slide'></section></div></body></html>",
        encoding="utf-8",
    )
    result = validate_html(html, expected_slides=2)
    assert result["ok"] is True
    result2 = validate_html(html, expected_slides=3)
    assert result2["ok"] is False
