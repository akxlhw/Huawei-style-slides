"""HR scenario templates — now loaded from scenarios/*.yaml.

The scenario definitions live in YAML files under scenarios/. This module
keeps the same public API (get_scenario, build_default_outline) so the rest of
the pipeline is unaffected, but delegates to scenario_loader for the actual
data. New scenarios are added by dropping a YAML file — no code change here.
"""
from typing import Dict, Any, List

from scenario_loader import load_scenario, list_scenarios


def get_scenario(name: str, path: str | None = None) -> Dict[str, Any]:
    """Return the scenario dict (same shape as the old hardcoded SCENARIOS)."""
    return load_scenario(name, path=path)


def available_scenarios() -> List[str]:
    """Names of all scenario YAMLs in scenarios/."""
    return list_scenarios()


def build_default_outline(name: str, path: str | None = None) -> Dict[str, Any]:
    s = get_scenario(name, path=path)
    return {
        "brief": {
            "audience": s["audience"],
            "goal": s["goal"],
            "duration_minutes": s["duration_minutes"],
        },
        "framework": s["framework"],
        "secondary_frameworks": s.get("secondary", []),
        "slides": s["slides"],
    }
