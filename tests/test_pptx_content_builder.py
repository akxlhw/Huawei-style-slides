import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from pptx_content_builder import build_pptx_content

def test_build_pptx_content(tmp_path):
    output_dir = tmp_path / "ppt-project-demo"
    outline = {
        "brief": {"audience": "CTO", "goal": "review", "duration_minutes": 15},
        "framework": "seven-step",
        "slides": [
            {"idx": 1, "layout": "cover", "title": "Q3 招聘复盘", "key_point": ""},
            {"idx": 2, "layout": "executive_summary", "title": "核心结论", "key_point": "完成率低于目标"},
        ],
    }
    content = build_pptx_content(outline, output_dir)
    assert (output_dir / "content.pptx.json").exists()
    assert content["slides"][0]["layout"] == "cover"
    assert "headline" in content["slides"][1]
    assert "items" in content["slides"][1]
