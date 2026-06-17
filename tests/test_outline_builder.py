import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from outline_builder import build_outline

def test_build_outline(tmp_path):
    output_dir = tmp_path / "ppt-project-demo"
    outline = build_outline("recruitment-review", "CTO", "review", 15, output_dir)
    assert (output_dir / "outline.json").exists()
    assert outline["brief"]["audience"] == "CTO"
    assert outline["slides"][0]["layout"] == "cover"
