"""S1: Build brief.md from scenario + user intent."""

from pathlib import Path
from typing import Dict, Any
from hr_scenarios import get_scenario


def parse_natural_language(text: str) -> Dict[str, Any]:
    """Heuristic parse of user request. In production this is delegated to LLM."""
    text_lower = text.lower()
    scenario = "recruitment-review"
    if "渠道" in text or "roi" in text_lower:
        scenario = "channel-roi"
    elif "调配" in text or "allocate" in text_lower:
        scenario = "allocation-plan"

    audience = "HRD"
    if "cto" in text_lower:
        audience = "CTO / 技术总监"

    goal = "review"
    if "申请" in text or "预算" in text:
        goal = "proposal"

    return {
        "scenario": scenario,
        "audience": audience,
        "goal": goal,
        "duration_minutes": 15,
        "raw_request": text,
    }


def build_brief(
    scenario: str,
    audience: str,
    goal: str,
    duration_minutes: int,
    output_dir: Path,
    scenario_path: str | None = None,
) -> str:
    s = get_scenario(scenario, path=scenario_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    brief = f"""# Brief: {s['name']}

## Audience
{audience}

## Goal
{goal}

## Duration
{duration_minutes} minutes (~{duration_minutes} slides)

## Scenario
{scenario}

## Key Messages (to be refined)
- 待补充
- 待补充
- 待补充

## Data Available
- 待补充

## Source
{output_dir / 'brief.md'}
"""
    path = output_dir / "brief.md"
    path.write_text(brief, encoding="utf-8")
    return brief
