"""Load scenario outlines from YAML files in the scenarios/ directory.

Replaces the previously hardcoded SCENARIOS dict in hr_scenarios.py. New
scenarios can be added by dropping a `scenarios/<name>.yaml` file — no Python
code changes required.

YAML schema:
    name: <display name>
    framework: <primary framework: pyramid|scqa|mece|seven-step|...>
    secondary: [<framework>, ...]
    audience: <target audience>
    goal: <review|decision|proposal|...>
    duration_minutes: <int>
    slides:
      - idx: <int>
        layout: <one of the 35 layouts>
        title: <conclusion sentence, >10 chars for content slides>
        key_point: <optional seed for content generation>
        cover_image: <optional: file path or 'auto'>   # cover slides only
        show_arc: <optional: true|false>                # optional title decoration

Usage:
    from scenario_loader import load_scenario, list_scenarios
    sc = load_scenario("skill-report")
    sc = load_scenario("my-custom", path="/abs/path/to/my-custom.yaml")
    all_names = list_scenarios()
"""
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

_SCENARIOS_DIR = Path(__file__).resolve().parent.parent / "scenarios"

# Required top-level keys in a scenario YAML.
_REQUIRED_KEYS = {"name", "framework", "audience", "goal", "duration_minutes", "slides"}
# Required keys per slide.
_REQUIRED_SLIDE_KEYS = {"idx", "layout", "title"}


def list_scenarios(scenarios_dir: Optional[Path] = None) -> List[str]:
    """Return the names (file stems) of all available scenario YAMLs."""
    d = Path(scenarios_dir) if scenarios_dir else _SCENARIOS_DIR
    if not d.is_dir():
        return []
    return sorted(p.stem for p in d.glob("*.yaml"))


def load_scenario(name: str, path: Optional[str] = None) -> Dict[str, Any]:
    """Load a scenario by name (looks up scenarios/<name>.yaml) or by explicit
    path. Returns a dict identical in shape to the old SCENARIOS[name].
    """
    if path:
        p = Path(path)
    else:
        p = _SCENARIOS_DIR / f"{name}.yaml"
    if not p.is_file():
        available = list_scenarios()
        raise FileNotFoundError(
            f"Scenario '{name}' not found at {p}. "
            f"Available: {available}. You can also pass an explicit path=..."
        )
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{p}: top level must be a mapping, got {type(data)}")
    _validate(data, p)
    return data


def _validate(data: Dict[str, Any], source: Path) -> None:
    """Validate required keys and per-slide structure. Raises ValueError."""
    missing = _REQUIRED_KEYS - set(data.keys())
    if missing:
        raise ValueError(f"{source}: missing required keys {sorted(missing)}")
    slides = data["slides"]
    if not isinstance(slides, list) or not slides:
        raise ValueError(f"{source}: 'slides' must be a non-empty list")
    for i, sl in enumerate(slides):
        if not isinstance(sl, dict):
            raise ValueError(f"{source}: slide #{i+1} must be a mapping")
        missing_s = _REQUIRED_SLIDE_KEYS - set(sl.keys())
        if missing_s:
            raise ValueError(f"{source}: slide #{i+1} missing {sorted(missing_s)}")
        # secondary is optional but if present must be a list
    if "secondary" in data and not isinstance(data["secondary"], list):
        data["secondary"] = [data["secondary"]]  # coerce scalar to list
    data.setdefault("secondary", [])
