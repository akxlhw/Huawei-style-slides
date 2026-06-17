"""S5: Run MckEngine gate checks and parse results."""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

MCK_ROOT = Path(__file__).resolve().parents[2] / "Mck-ppt-design-skill"
GATE_S3 = MCK_ROOT / "references" / "scripts" / "gate_check_s3.py"
GATE_S4 = MCK_ROOT / "references" / "scripts" / "gate_check.py"


def run_gate_check_s3(
    content_json: Path, project_dir: Path, script_path: Path = None
) -> Dict[str, Any]:
    """Run MckEngine S3 content gate check and return parsed gate_s3.json."""
    script = Path(script_path) if script_path else GATE_S3
    cmd = [sys.executable, str(script), str(content_json), str(project_dir)]
    subprocess.run(cmd, check=True)
    result_path = Path(project_dir) / "gate_s3.json"
    return json.loads(result_path.read_text(encoding="utf-8"))


def run_gate_check(
    pptx_path: Path, project_dir: Path, script_path: Path = None
) -> Dict[str, Any]:
    """Run MckEngine S4 QA gate check and return parsed gate_result.json."""
    script = Path(script_path) if script_path else GATE_S4
    cmd = [sys.executable, str(script), str(pptx_path), str(project_dir)]
    subprocess.run(cmd, check=True)
    result_path = Path(project_dir) / "gate_result.json"
    return json.loads(result_path.read_text(encoding="utf-8"))


def assert_passed(result: Dict[str, Any], gate_name: str) -> None:
    """Exit if a gate check did not pass."""
    if not result.get("passed"):
        raise SystemExit(f"{gate_name} failed: {result}")
