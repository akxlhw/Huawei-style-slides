import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from qa_runner import run_gate_check_s3, run_gate_check


def test_run_gate_check_s3_parses(tmp_path, monkeypatch):
    # Patch gate_check_s3.py by creating a fake script
    fake_script = tmp_path / "fake_gate_check_s3.py"
    fake_script.write_text(
        "import json, sys\n"
        'out = {"passed": True, "fail_items": []}\n'
        'open(sys.argv[2] + "/gate_s3.json", "w").write(json.dumps(out))\n',
        encoding="utf-8",
    )
    result = run_gate_check_s3(tmp_path / "content.json", tmp_path, fake_script)
    assert result["passed"] is True
