import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from pptx_renderer import render_pptx


def test_render_pptx_creates_file(tmp_path):
    output_dir = tmp_path / "ppt-project-demo"
    content = {
        "brief": {"audience": "CTO", "goal": "review", "duration_minutes": 15},
        "slides": [
            {
                "idx": 1,
                "layout": "cover",
                "title": "Q3 招聘复盘",
                "subtitle": "HR",
                "author": "Team",
                "date": "2026",
            },
            {
                "idx": 2,
                "layout": "executive_summary",
                "title": "核心结论",
                "headline": "完成率低于目标",
                "items": [{"title": "A", "description": "B"}],
                "source": "HR",
            },
            {
                "idx": 3,
                "layout": "closing",
                "title": "谢谢",
                "message": "期待交流",
            },
        ],
    }
    deck_path = render_pptx(content, output_dir)
    assert deck_path.exists()
    assert deck_path.stat().st_size > 0
