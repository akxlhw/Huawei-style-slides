"""S5: Run MckEngine gate checks and parse results."""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

MCK_ROOT = Path(__file__).resolve().parents[2] / "Mck-ppt-design-skill"
GATE_S3 = MCK_ROOT / "references" / "scripts" / "gate_check_s3.py"
GATE_S4 = MCK_ROOT / "references" / "scripts" / "gate_check.py"


def _env_with_mck_root() -> Dict[str, str]:
    """Return a copy of os.environ with MCK_ROOT added to PYTHONPATH.

    gate_check.py expects to import mck_ppt.qa from a path on sys.path.
    We keep the dependency local to this workspace by prepending MCK_ROOT
    instead of relying on ~/.workbuddy/skills/.
    """
    env = os.environ.copy()
    sep = os.pathsep
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = sep.join([str(MCK_ROOT), existing]) if existing else str(MCK_ROOT)
    return env


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
    subprocess.run(cmd, check=True, env=_env_with_mck_root())
    result_path = Path(project_dir) / "gate_result.json"
    return json.loads(result_path.read_text(encoding="utf-8"))


def assert_passed(result: Dict[str, Any], gate_name: str) -> None:
    """Exit if a gate check did not pass."""
    if not result.get("passed"):
        raise SystemExit(f"{gate_name} failed: {result}")
