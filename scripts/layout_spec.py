"""Unified layout specification — the single source of truth for each layout's
data contract. Both the PPTX track (pptx_renderer) and HTML track
(html_content_builder) reference this to stay in sync.

Each layout entry defines:
  - fields: the data keys consumed by both tracks
  - constraints: gate quantity limits (enforced by gate_check_s3)
  - track: 'mckengine' (calls a built-in method) or 'native' (custom python-pptx)
"""
from typing import Any, Dict, List

LAYOUT_SPECS: Dict[str, Dict[str, Any]] = {
    "cover": {"fields": ["title","subtitle","author","date","cover_image"], "track": "mckengine"},
    "executive_summary": {"fields": ["title","headline","items","source"], "track": "mckengine",
                          "constraints": {"items_arity": 3}},
    "table_insight": {"fields": ["title","headers","rows","insights","source"], "track": "mckengine"},
    "funnel": {"fields": ["title","stages","source"], "track": "mckengine"},
    "data_table": {"fields": ["title","headers","rows","source"], "track": "mckengine"},
    "matrix_2x2": {"fields": ["title","quadrants","axis_labels","source"], "track": "mckengine",
                   "constraints": {"quadrants": 4, "quadrant_arity": 3}},
    "timeline": {"fields": ["title","milestones","source"], "track": "mckengine",
                 "constraints": {"last_label_max_chars": 6}},
    "action_items": {"fields": ["title","actions","source"], "track": "mckengine"},
    "closing": {"fields": ["title","message"], "track": "mckengine"},
    "big_number": {"fields": ["title","number","unit","description","detail_items","source"], "track": "mckengine"},
    "three_stat": {"fields": ["title","stats","detail_items","source"], "track": "mckengine"},
    "metric_cards": {"fields": ["title","cards","source"], "track": "mckengine"},
    "grouped_bar": {"fields": ["title","categories","series","data","y_ticks","summary","source"], "track": "mckengine",
                    "constraints": {"max_categories": 6, "max_series": 2}},
    "horizontal_bar": {"fields": ["title","items","summary","source"], "track": "mckengine"},
    "donut_chart": {"fields": ["title","segments","center_label","center_sub","summary","source"], "track": "mckengine",
                    "constraints": {"max_segments": 6, "segment_arity": 3}},
    "kpi_tracker": {"fields": ["title","kpis","summary","source"], "track": "mckengine"},
    "pyramid_steps": {"fields": ["title","levels","source"], "track": "mckengine"},
    "four_column": {"fields": ["title","items","source"], "track": "mckengine"},
    "scorecard": {"fields": ["title","items","source"], "track": "mckengine"},
    "checklist_status": {"fields": ["title","columns","col_widths","rows","source"], "track": "mckengine"},
    "value_chain": {"fields": ["title","stages","source"], "track": "mckengine"},
    "swot": {"fields": ["title","quadrants","source"], "track": "mckengine"},
    "icon_grid": {"fields": ["title","items","source"], "track": "mckengine"},
    "quote": {"fields": ["title","quote_text","attribution","source"], "track": "mckengine"},
    "cycle": {"fields": ["title","phases","right_panel","source"], "track": "native"},
    "side_by_side": {"fields": ["title","options","source"], "track": "mckengine"},
    "case_study": {"fields": ["title","sections","result_box","source"], "track": "mckengine"},
    "decision_tree": {"fields": ["title","root","branches","right_panel","source"], "track": "mckengine"},
    "ecosystem_ring": {"fields": ["title","rings","center","side_cards","source"], "track": "native"},
    "harvey_ball_compare": {"fields": ["title","criteria","options","scores","legend_text","summary","source"], "track": "mckengine"},
    "swim_lane": {"fields": ["title","lanes","phases","steps","source"], "track": "native"},
    "pyramid_triangle": {"fields": ["title","levels","source"], "track": "native"},
    "radar_chart": {"fields": ["title","axes","series","source"], "track": "native"},
    "gantt_chart": {"fields": ["title","phases","tasks","source"], "track": "native"},
    "icon_stat_grid": {"fields": ["title","items","source"], "track": "native"},
    # Framework-gallery layouts (PPTX fallback to icon_grid; HTML gallery)
    "fishbone": {"fields": ["title","items","source"], "track": "mckengine"},
    "five_w2h": {"fields": ["title","items","source"], "track": "mckengine"},
    "pest_grid": {"fields": ["title","items","source"], "track": "mckengine"},
    "porter_five": {"fields": ["title","items","source"], "track": "mckengine"},
    "bmc_canvas": {"fields": ["title","items","source"], "track": "mckengine"},
    "mckinsey_7s": {"fields": ["title","items","source"], "track": "mckengine"},
    "bcg_matrix": {"fields": ["title","items","source"], "track": "mckengine"},
    "grow_model": {"fields": ["title","items","source"], "track": "mckengine"},
    "prep_model": {"fields": ["title","items","source"], "track": "mckengine"},
    "fabe_model": {"fields": ["title","items","source"], "track": "mckengine"},
    "raci_matrix": {"fields": ["title","items","source"], "track": "mckengine"},
    "aida_funnel": {"fields": ["title","items","source"], "track": "mckengine"},
}


def get_spec(layout: str) -> Dict[str, Any]:
    """Return the layout spec, or empty dict if unknown."""
    return LAYOUT_SPECS.get(layout, {})


def all_layouts() -> List[str]:
    """All registered layout names."""
    return sorted(LAYOUT_SPECS.keys())


def validate_content(content: Dict[str, Any]) -> List[str]:
    """Validate a content.pptx.json against layout specs. Returns list of issues."""
    issues = []
    for slide in content.get("slides", []):
        layout = slide.get("layout", "")
        spec = get_spec(layout)
        if not spec:
            continue
        c = spec.get("constraints", {})
        if "max_segments" in c and len(slide.get("segments", [])) > c["max_segments"]:
            issues.append(f"slide {slide.get('idx')}: {layout} segments > {c['max_segments']}")
        if "max_series" in c and len(slide.get("series", [])) > c["max_series"]:
            issues.append(f"slide {slide.get('idx')}: {layout} series > {c['max_series']}")
    return issues
