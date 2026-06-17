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
) -> Dict[str, Any]:
    outline = build_default_outline(scenario)
    outline["brief"]["audience"] = audience
    outline["brief"]["goal"] = goal
    outline["brief"]["duration_minutes"] = duration_minutes

    # Trim slides if duration is short
    max_slides = int(duration_minutes * 1.2)
    if len(outline["slides"]) > max_slides:
        # Always keep cover, executive_summary, and closing
        keep_indices = {0, 1, len(outline["slides"]) - 1}
        middle = outline["slides"][2:-1]
        remaining = max_slides - len(keep_indices)
        middle = middle[:remaining]
        outline["slides"] = [outline["slides"][0]] + middle + [outline["slides"][-1]]
        # Re-index
        for i, slide in enumerate(outline["slides"], start=1):
            slide["idx"] = i

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "outline.json"
    path.write_text(json.dumps(outline, ensure_ascii=False, indent=2), encoding="utf-8")
    return outline
