import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from html_renderer import render_html


def test_render_html_creates_file(tmp_path):
    output_dir = tmp_path / "ppt-project-demo"
    content = {
        "brief": {"audience": "CTO", "goal": "review", "duration_minutes": 15},
        "slides": [
            {
                "idx": 1,
                "slide_type": "cover",
                "title": "Q3 招聘复盘",
                "subtitle": "HR",
                "author": "Team",
                "date": "2026",
            },
            {
                "idx": 2,
                "slide_type": "executive_summary",
                "title": "核心结论",
                "headline": "完成率低于目标",
                "items": [{"title": "A", "description": "B"}],
                "source": "HR",
            },
            {
                "idx": 3,
                "slide_type": "closing",
                "title": "谢谢",
                "message": "期待交流",
            },
        ],
    }
    html_path = render_html(content, output_dir)
    assert html_path.exists()
    text = html_path.read_text(encoding="utf-8")
    assert "Q3 招聘复盘" in text
    assert "<deck-stage" in text
    assert "deck-stage.js" not in text  # JS should be inlined
