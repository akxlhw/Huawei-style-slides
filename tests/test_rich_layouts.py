"""Tests for V2 rich-chart layouts and the skill-report scenario.

These cover the builders added in Part 2 (big_number, grouped_bar, donut_chart,
metric_cards, four_column, etc.) and the skill-report acceptance scenario that
turns the two research reports into a 22-slide deck.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from pptx_content_builder import build_pptx_content, BUILDERS
from html_content_builder import build_html_content


# Layouts added in Part 2 (excluding the pre-existing 9).
RICH_LAYOUTS = [
    "big_number", "three_stat", "metric_cards", "grouped_bar", "horizontal_bar",
    "donut_chart", "kpi_tracker", "pyramid_steps", "four_column", "scorecard",
    "checklist_status", "value_chain", "swot", "icon_grid", "quote",
    # SmartArt-style logic diagrams (V2+)
    "cycle", "side_by_side", "case_study", "decision_tree", "ecosystem_ring",
    # Additional Huawei charts (iteration round 2)
    "harvey_ball_compare", "swim_lane", "pyramid_triangle", "radar_chart",
    "gantt_chart", "icon_stat_grid",
]


def _outline(layouts, scenario="skill-report"):
    slides = [
        {"idx": i, "layout": l, "title": "测试" + l + "的结论性标题", "key_point": "kp"}
        for i, l in enumerate(layouts, 1)
    ]
    return {
        "brief": {"audience": "评审", "goal": "review", "duration_minutes": 20},
        "framework": "pyramid", "scenario": scenario, "slides": slides,
    }


def test_all_rich_layouts_registered():
    for layout in RICH_LAYOUTS:
        assert layout in BUILDERS, f"missing builder for {layout}"


def test_rich_layouts_build_pptx_content(tmp_path):
    content = build_pptx_content(_outline(RICH_LAYOUTS), tmp_path / "out")
    assert len(content["slides"]) == len(RICH_LAYOUTS)
    # every content slide (non-cover/closing) must carry a non-empty source
    # so the S3 gate passes.
    for s in content["slides"]:
        if s["layout"] not in ("cover", "closing"):
            assert s.get("source"), f"{s['layout']} missing source"


def test_donut_segments_are_3tuples():
    s = {"title": "环形图测试标题", "key_point": ""}
    data = BUILDERS["donut_chart"](s, "skill-report")
    for seg in data["segments"]:
        assert len(seg) == 3  # (pct, color_hex, label)


def test_grouped_bar_respects_series_cap():
    """gate_check_s3 requires grouped_bar <= 3 series; skill-report uses 2."""
    s = {"title": "分组柱状图测试标题", "key_point": ""}
    data = BUILDERS["grouped_bar"](s, "skill-report")
    assert len(data["series"]) <= 3


def test_skill_report_scenario_outline_has_24_slides():
    from hr_scenarios import get_scenario
    sc = get_scenario("skill-report")
    assert len(sc["slides"]) == 24
    assert sc["slides"][0]["layout"] == "cover"
    assert sc["slides"][-1]["layout"] == "closing"
    # every non-cover/closing title must be >10 chars (gate rule)
    for sl in sc["slides"]:
        if sl["layout"] not in ("cover", "closing"):
            assert len(sl["title"]) > 10, sl["title"]


def test_skill_report_uses_smartart_logic_diagrams():
    """The acceptance deck must use SmartArt-style logic diagrams, not just
    tables/text, to convey frameworks visually."""
    from hr_scenarios import get_scenario
    sc = get_scenario("skill-report")
    layouts = {sl["layout"] for sl in sc["slides"]}
    smartart = {"cycle", "decision_tree", "side_by_side", "case_study",
                "ecosystem_ring", "pyramid_triangle", "radar_chart",
                "harvey_ball_compare", "gantt_chart"}
    assert smartart & layouts, "no SmartArt logic diagrams in skill-report"


def test_pyramid_steps_uses_3_levels_to_avoid_overflow():
    """MckEngine pyramid overflows the right edge at 4 levels; skill-report
    must use 3 levels (the pyramid principle's three sub-structures)."""
    s = {"title": "金字塔原理测试标题文字", "key_point": ""}
    data = BUILDERS["pyramid_steps"](s, "skill-report")
    assert len(data["levels"]) == 3


def test_skill_report_html_track_round_trips(tmp_path):
    """The full skill-report outline must render both content tracks."""
    from hr_scenarios import build_default_outline
    outline = build_default_outline("skill-report")
    outline["scenario"] = "skill-report"
    pc = build_pptx_content(outline, tmp_path / "out")
    hc = build_html_content(outline, tmp_path / "out", pptx_content=pc)
    assert len(pc["slides"]) == 24
    assert len(hc["slides"]) == 24
    # HTML slide_type must match a PPTX layout for every slide
    for p, h in zip(pc["slides"], hc["slides"]):
        assert p["layout"] == h["slide_type"]


def test_huawei_red_is_cf0a2c():
    """The cross-verified Huawei red must be #CF0A2C everywhere."""
    from huawei_theme import HUAWEI_COLORS
    assert HUAWEI_COLORS["red"] == "#CF0A2C"


def test_agent_mode_writes_prompt(tmp_path):
    """content_source='agent' must emit a content_prompt.md for a Code Agent."""
    from hr_scenarios import build_default_outline
    outline = build_default_outline("skill-report")
    outline["scenario"] = "skill-report"
    build_pptx_content(outline, tmp_path / "out", content_source="agent")
    prompt = tmp_path / "out" / "content_prompt.md"
    assert prompt.is_file()
    text = prompt.read_text(encoding="utf-8")
    assert "outline.json" in text
    assert "数据契约" in text
    assert "skill-report" in text


def test_file_mode_round_trips(tmp_path):
    """content_source='file' loads a pre-written content.pptx.json."""
    from hr_scenarios import build_default_outline
    outline = build_default_outline("skill-report")
    outline["scenario"] = "skill-report"
    # First write sample content
    pc = build_pptx_content(outline, tmp_path / "out")
    # Then reload it via file mode
    pc2 = build_pptx_content(outline, tmp_path / "out", content_source="file")
    assert len(pc2["slides"]) == len(pc["slides"])


def test_radar_chart_axes_within_bounds():
    s = {"title": "雷达图测试标题文字", "key_point": ""}
    data = BUILDERS["radar_chart"](s, "skill-report")
    axes = data["axes"]
    assert 3 <= len(axes) <= 6
    for ser in data["series"]:
        assert all(0 <= v <= 100 for v in ser["values"])


def test_gantt_task_indices_within_phases():
    s = {"title": "甘特图测试标题文字", "key_point": ""}
    data = BUILDERS["gantt_chart"](s, "skill-report")
    n_phases = len(data["phases"])
    for name, start, end, color in data["tasks"]:
        assert 0 <= start < end <= n_phases


def test_cover_carries_image_field_when_set():
    """cover_image override flows through to the cover content."""
    s = {"title": "封面测试", "key_point": "", "cover_image": "/tmp/x.png"}
    data = BUILDERS["cover"](s, "skill-report")
    assert data["cover_image"] == "/tmp/x.png"


def test_agent_mode_full_pipeline(tmp_path):
    """agent mode: generates prompt + falls back to sample deck."""
    from hr_scenarios import build_default_outline
    import pptx_renderer
    outline = build_default_outline("recruitment-review")
    outline["scenario"] = "recruitment-review"
    # agent mode should write content_prompt.md AND produce sample content
    pc = build_pptx_content(outline, tmp_path / "out", content_source="agent")
    assert (tmp_path / "out" / "content_prompt.md").is_file()
    assert len(pc["slides"]) >= 5  # sample fallback produced content
    # And the sample content should render to a valid PPTX
    deck = pptx_renderer.render_pptx(pc, tmp_path / "out")
    assert deck.is_file()


def test_file_mode_loads_existing(tmp_path):
    """file mode loads a pre-existing content.pptx.json."""
    from hr_scenarios import build_default_outline
    outline = build_default_outline("allocation-plan")
    outline["scenario"] = "allocation-plan"
    pc1 = build_pptx_content(outline, tmp_path / "out")
    pc2 = build_pptx_content(outline, tmp_path / "out", content_source="file")
    assert len(pc2["slides"]) == len(pc1["slides"])


def test_layout_spec_covers_all_builders():
    """layout_spec.py should register every BUILDERS layout."""
    import sys; sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from layout_spec import LAYOUT_SPECS
    missing = set(BUILDERS) - set(LAYOUT_SPECS)
    assert not missing, f"layouts missing from layout_spec: {missing}"
