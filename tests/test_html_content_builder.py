import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from html_content_builder import build_html_content

def test_build_html_content(tmp_path):
    output_dir = tmp_path / "ppt-project-demo"
    outline = {
        "brief": {"audience": "CTO", "goal": "review", "duration_minutes": 15},
        "framework": "seven-step",
        "slides": [
            {"idx": 1, "layout": "cover", "title": "Q3 招聘复盘", "key_point": ""},
            {"idx": 2, "layout": "executive_summary", "title": "核心结论", "key_point": "完成率低于目标"},
        ],
    }
    content = build_html_content(outline, output_dir)
    assert (output_dir / "content.html.json").exists()
    assert content["slides"][0]["slide_type"] == "cover"
    assert "animation" in content["slides"][0]
