import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from orchestrator import run


def test_run_creates_outputs(tmp_path):
    output_dir = tmp_path / "ppt-project-demo"
    result = run(
        scenario="recruitment-review",
        audience="CTO",
        goal="review",
        duration_minutes=15,
        output_dir=output_dir,
        skip_qa=True,
    )
    assert (output_dir / "brief.md").exists()
    assert (output_dir / "outline.json").exists()
    assert (output_dir / "content.pptx.json").exists()
    assert (output_dir / "content.html.json").exists()
    assert (output_dir / "slides.html").exists()
    assert (output_dir / "deck.pptx").exists()
    assert "deck" in result
    assert "html" in result
