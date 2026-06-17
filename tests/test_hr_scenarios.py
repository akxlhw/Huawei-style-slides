import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from hr_scenarios import SCENARIOS, get_scenario, build_default_outline

def test_list_scenarios():
    assert "recruitment-review" in SCENARIOS
    assert "channel-roi" in SCENARIOS
    assert "allocation-plan" in SCENARIOS

def test_get_scenario():
    s = get_scenario("recruitment-review")
    assert s["framework"] == "seven-step"

def test_default_outline_has_slides():
    outline = build_default_outline("recruitment-review")
    assert len(outline["slides"]) >= 5
    assert outline["slides"][0]["layout"] == "cover"
