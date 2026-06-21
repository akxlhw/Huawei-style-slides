"""S2: Build outline.json from brief."""

import json
from pathlib import Path
from typing import Dict, Any
from hr_scenarios import build_default_outline


def build_outline(
    scenario: str,
    audience: str,
    goal: str,
    duration_minutes: int,
    output_dir: Path,
    scenario_path: str | None = None,
) -> Dict[str, Any]:
    outline = build_default_outline(scenario, path=scenario_path)
    outline["scenario"] = scenario
    outline["brief"]["audience"] = audience
    outline["brief"]["goal"] = goal
    outline["brief"]["duration_minutes"] = duration_minutes

    # Trim slides if duration is short. Keep cover (first) + closing (last)
    # and drop from the middle; the executive_summary, if present as slide 2,
    # is preserved as part of the kept head.
    max_slides = int(duration_minutes * 1.2)
    if len(outline["slides"]) > max_slides and max_slides >= 3:
        head = outline["slides"][:2]   # cover + (executive_summary or 2nd)
        tail = outline["slides"][-1:]  # closing
        middle = outline["slides"][2:-1]
        remaining = max_slides - len(head) - len(tail)
        outline["slides"] = head + middle[:max(0, remaining)] + tail
        # Re-index
        for i, slide in enumerate(outline["slides"], start=1):
            slide["idx"] = i

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "outline.json"
    path.write_text(json.dumps(outline, ensure_ascii=False, indent=2), encoding="utf-8")
    return outline
