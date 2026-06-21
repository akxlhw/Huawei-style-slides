import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from hr_scenarios import available_scenarios, get_scenario, build_default_outline


def test_list_scenarios():
    names = available_scenarios()
    assert "recruitment-review" in names
    assert "channel-roi" in names
    assert "allocation-plan" in names
    assert "skill-report" in names


def test_get_scenario():
    s = get_scenario("recruitment-review")
    assert s["framework"] == "seven-step"


def test_default_outline_has_slides():
    outline = build_default_outline("recruitment-review")
    assert len(outline["slides"]) >= 5
    assert outline["slides"][0]["layout"] == "cover"


def test_yaml_loader_custom_path(tmp_path):
    """A custom YAML outside scenarios/ must load via path=."""
    from scenario_loader import load_scenario
    yaml_text = """
name: Custom Test
framework: pyramid
secondary: [mece]
audience: testers
goal: review
duration_minutes: 10
slides:
  - {idx: 1, layout: cover, title: "测试封面标题", key_point: ""}
  - {idx: 2, layout: closing, title: "谢谢", key_point: ""}
"""
    p = tmp_path / "custom.yaml"
    p.write_text(yaml_text, encoding="utf-8")
    sc = load_scenario("custom", path=str(p))
    assert sc["name"] == "Custom Test"
    assert len(sc["slides"]) == 2


def test_yaml_validation_rejects_missing_keys(tmp_path):
    """A YAML missing required keys must raise ValueError."""
    import pytest
    from scenario_loader import load_scenario
    p = tmp_path / "bad.yaml"
    p.write_text("name: Bad\nframework: pyramid\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_scenario("bad", path=str(p))
