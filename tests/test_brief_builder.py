import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from brief_builder import build_brief, parse_natural_language

def test_parse_natural_language():
    text = "帮我做一份 Q3 技术岗招聘复盘汇报，面向 CTO 和技术总监。"
    result = parse_natural_language(text)
    assert result["scenario"] == "recruitment-review"
    assert "CTO" in result["audience"]

def test_build_brief_creates_file(tmp_path):
    output_dir = tmp_path / "ppt-project-demo"
    brief = build_brief("recruitment-review", "CTO", "review", 15, output_dir)
    assert (output_dir / "brief.md").exists()
    assert "CTO" in brief
