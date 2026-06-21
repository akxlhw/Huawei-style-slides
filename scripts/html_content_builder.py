"""S3b: Build content.html.json from outline.

Reuses the PPTX builders then converts MckEngine tuple API format into the
dict format expected by the HTML Jinja2 templates.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from pptx_content_builder import BUILDERS as PPTX_BUILDERS


# Huawei palette name used by CSS classes / CSS variables.
_HEX_TO_COLOR_NAME = {
    "#CF0A2C": "red",
    "#007DFF": "blue",
    "#30B5C5": "ictblue",
    "#FCC800": "yellow",
    "#FF9900": "orange",
    "#ED6D00": "orange",
    "#669900": "green",
    "#62B230": "green",
    "#DCDDDD": "gray",
}

_SCENARIO_LABEL = {
    "recruitment-review": "招聘复盘",
    "channel-roi": "渠道 ROI 分析",
    "allocation-plan": "人员调配方案",
    "skill-report": "Skill 研究报告",
}

# Huawei-style left-nav chapters per scenario. The nav rail highlights the
# chapter the current slide belongs to. Each chapter covers a page range.
_SCENARIO_CHAPTERS = {
    "skill-report": ["研究概览", "架构设计", "视觉规范", "V2 升级", "实施落地"],
    "recruitment-review": ["执行摘要", "漏斗分析", "渠道 ROI", "追赶计划"],
    "channel-roi": ["执行摘要", "渠道分类", "ROI 对比", "预算调整"],
    "allocation-plan": ["执行摘要", "调配背景", "决策矩阵", "实施计划"],
}

_SCENARIO_BRAND = {
    "skill-report": {"zh": "Slide Skill", "en": "HUAWEI SLIDE"},
    "recruitment-review": {"zh": "招聘复盘", "en": "HR REVIEW"},
    "channel-roi": {"zh": "渠道分析", "en": "CHANNEL ROI"},
    "allocation-plan": {"zh": "人员调配", "en": "ALLOCATION"},
}


def _chapter_for(scenario: str, page_no: int, total: int) -> str:
    """Map a 1-based page number to its chapter name for the left nav rail."""
    chapters = _SCENARIO_CHAPTERS.get(scenario)
    if not chapters:
        return ""
    n = len(chapters)
    # Evenly distribute pages across chapters by index.
    idx = min(n - 1, (page_no - 1) * n // total)
    return chapters[idx]

_SECTION_LABEL = {
    "executive_summary": "执行摘要",
    "data_table": "数据洞察",
    "table_insight": "数据洞察",
    "matrix_2x2": "分析矩阵",
    "timeline": "时间规划",
    "action_items": "行动计划",
    "funnel": "漏斗分析",
    "big_number": "核心指标",
    "three_stat": "指标对比",
    "metric_cards": "能力卡片",
    "grouped_bar": "数据图表",
    "horizontal_bar": "数据图表",
    "donut_chart": "占比分析",
    "kpi_tracker": "KPI 看板",
    "pyramid_steps": "架构演进",
    "four_column": "架构演进",
    "scorecard": "评分体系",
    "checklist_status": "检查清单",
    "value_chain": "流程闭环",
    "swot": "对比分析",
    "icon_grid": "评估矩阵",
    "quote": "核心理念",
    "cycle": "闭环流程",
    "side_by_side": "对比分析",
    "case_study": "案例叙事",
    "decision_tree": "决策路由",
    "ecosystem_ring": "架构总览",
    "harvey_ball_compare": "评估矩阵",
    "swim_lane": "流程泳道",
    "pyramid_triangle": "层级金字塔",
    "radar_chart": "雷达对比",
    "gantt_chart": "进度甘特",
    "icon_stat_grid": "数据总览",
}


def _split_timeline_label(label: str, desc: str) -> Tuple[str, str, str]:
    """Split '10 月 W1' into (date, label_text, desc).

    If the label has no label_text after the date, try to extract the label
    from the first segment of desc separated by '：'.
    """
    parts = label.split(" ", 1)
    date = parts[0]
    label_text = parts[1] if len(parts) == 2 else ""

    if not label_text and "：" in desc:
        label_text, _, desc = desc.partition("：")

    return date, label_text, desc


def _to_html_executive_items(items: List[Tuple[Any, str, str]]) -> List[Dict[str, str]]:
    return [
        {"title": str(item[1]), "description": str(item[2])}
        for item in items
    ]


def _to_html_matrix_quadrants(
    quadrants: List[Tuple[str, str, str]],
) -> List[Dict[str, Any]]:
    return [
        {
            "label": str(q[0]),
            "color": _HEX_TO_COLOR_NAME.get(str(q[1]).upper(), "red"),
            "items": [line for line in str(q[2]).split("\n") if line.strip()],
        }
        for q in quadrants
    ]


def _to_html_funnel_stages(stages: List[Tuple[str, str, float]]) -> List[Dict[str, Any]]:
    return [
        {"label": str(s[0]), "value": int(str(s[1]).replace(",", ""))}
        for s in stages
    ]


def _to_html_timeline_milestones(
    milestones: List[Tuple[str, str]],
) -> List[Dict[str, str]]:
    return [
        {
            "date": date,
            "label": label_text,
            "description": desc,
        }
        for date, label_text, desc in (
            _split_timeline_label(str(m[0]), str(m[1])) for m in milestones
        )
    ]


def _to_html_action_items(
    actions: List[Tuple[str, str, str, str]],
) -> List[Dict[str, str]]:
    return [
        {
            "title": str(a[0]),
            "timeline": str(a[1]),
            "description": str(a[2]),
            "owner": str(a[3]),
        }
        for a in actions
    ]


# ── V2 rich-chart converters ──────────────────────────────────────────────────


def _color_name(hex_color: str, default: str = "red") -> str:
    return _HEX_TO_COLOR_NAME.get(str(hex_color).upper(), default)


def _to_html_three_stat(stats: List[Tuple[Any, ...]]) -> List[Dict[str, Any]]:
    out = []
    for s in stats:
        out.append({
            "value": str(s[0]),
            "label": str(s[1]),
            "highlight": bool(s[2]) if len(s) > 2 else False,
        })
    return out


def _to_html_metric_cards(cards: List[Tuple[Any, ...]]) -> List[Dict[str, Any]]:
    out = []
    for c in cards:
        out.append({
            "letter": str(c[0]),
            "title": str(c[1]),
            "description": str(c[2]),
            "color": _color_name(c[3]) if len(c) > 3 else "red",
        })
    return out


def _to_html_grouped_bar(
    categories: List[str],
    series: List[Tuple[str, str]],
    data: List[List[int]],
) -> Dict[str, Any]:
    max_val = max((max(row) for row in data), default=1) or 1
    # Flatten into per-category groups so the template needs no double indexing.
    groups = []
    for ci, cat in enumerate(categories):
        bars = []
        for si, s in enumerate(series):
            bars.append({
                "value": int(data[ci][si]) if ci < len(data) and si < len(data[ci]) else 0,
                "color": _color_name(s[1]),
                "height_pct": int(round(
                    (int(data[ci][si]) if ci < len(data) and si < len(data[ci]) else 0)
                    / max_val * 100)),
            })
        groups.append({"category": str(cat), "bars": bars})
    return {
        "series": [{"name": str(s[0]), "color": _color_name(s[1])} for s in series],
        "groups": groups,
    }


def _to_html_horizontal_bar(items: List[Tuple[str, int, str]]) -> List[Dict[str, Any]]:
    max_val = max((p for _, p, _ in items), default=100) or 100
    return [
        {"label": str(n), "pct": min(100, int(round(p / max_val * 100))),
         "raw": int(p), "color": _color_name(c)}
        for n, p, c in items
    ]


def _to_html_donut(segments: List[Tuple[float, str, str]]) -> List[Dict[str, Any]]:
    return [
        {"pct": round(float(s[0]) * 100), "color": _color_name(s[1]), "label": str(s[2])}
        for s in segments
    ]


def _to_html_kpi_tracker(kpis: List[Tuple[Any, ...]]) -> List[Dict[str, Any]]:
    return [
        {"name": str(k[0]), "pct": round(float(k[1]) * 100),
         "detail": str(k[2]), "status": str(k[3])}
        for k in kpis
    ]


def _to_html_pyramid(levels: List[Tuple[str, str, str]]) -> List[Dict[str, str]]:
    return [{"label": str(l[0]), "description": str(l[1]), "icon": str(l[2])}
            for l in levels]


def _to_html_four_column(items: List[Tuple[Any, ...]]) -> List[Dict[str, Any]]:
    out = []
    for it in items:
        num, title, desc = it[0], it[1], it[2]
        if isinstance(desc, (list, tuple)):
            points = [str(x) for x in desc]
        else:
            points = [str(desc)]
        out.append({"num": str(num), "title": str(title), "points": points})
    return out


def _to_html_scorecard(items: List[Tuple[str, str, float]]) -> List[Dict[str, Any]]:
    return [
        {"name": str(i[0]), "stars": str(i[1]), "pct": round(float(i[2]) * 100)}
        for i in items
    ]


def _to_html_value_chain(stages: List[Tuple[str, str, str]]) -> List[Dict[str, str]]:
    return [
        {"title": str(s[0]), "description": str(s[1]), "color": _color_name(s[2])}
        for s in stages
    ]


def _to_html_swot(quadrants: List[Tuple[str, str, str, Any]]) -> List[Dict[str, Any]]:
    return [
        {"label": str(q[0]), "color": _color_name(q[1]),
         "points": [str(p) for p in q[3]] if len(q) > 3 else []}
        for q in quadrants
    ]


def _to_html_icon_grid(items: List[Tuple[str, str, str]]) -> List[Dict[str, str]]:
    return [
        {"title": str(i[0]), "description": str(i[1]), "color": _color_name(i[2])}
        for i in items
    ]


def _to_html_cycle(phases: List[Tuple[Any, ...]]) -> List[Dict[str, Any]]:
    import math
    n = len(phases)
    out = []
    cx, cy, r = 50, 50, 36  # percentage positions within the ring container
    for i, p in enumerate(phases):
        angle = math.radians(-90 + i * (360 / n))
        out.append({
            "label": str(p[0]),
            "x": round(cx + r * math.cos(angle), 1),
            "y": round(cy + r * math.sin(angle), 1),
            "num": i + 1,
        })
    return out


def _to_html_side_by_side(options: List[Tuple[str, Any]]) -> List[Dict[str, Any]]:
    return [{"title": str(o[0]),
             "points": [str(p) for p in o[1]] if isinstance(o[1], (list, tuple)) else [str(o[1])]}
            for o in options]


def _to_html_case_study(sections: List[Tuple[str, str, str]]) -> List[Dict[str, str]]:
    return [{"letter": str(s[0]), "title": str(s[1]), "description": str(s[2])}
            for s in sections]


def _to_html_decision_tree(
    root: Tuple[str], branches: List[Tuple[Any, ...]]
) -> Dict[str, Any]:
    return {
        "root": str(root[0]) if root else "",
        "branches": [
            {"title": str(b[0]), "metric": str(b[1]),
             "color": _color_name(b[2]),
             "children": [{"name": str(c[0]), "metric": str(c[1])}
                          for c in b[3]]}
            for b in branches
        ],
    }


def _to_html_ecosystem_ring(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert ecosystem_ring data for the concentric-ring SVG template."""
    import math
    rings = []
    for r in data.get("rings", []):
        rings.append({
            "label": str(r.get("label", "")),
            "color": _color_name(r.get("color", "#CF0A2C")),
            "items": [str(x) for x in r.get("items", [])],
        })
    # Node positions on each ring (evenly distributed by angle).
    for ri, ring in enumerate(rings):
        n = len(ring["items"])
        nodes = []
        for i, it in enumerate(ring["items"]):
            ang = math.radians(-90 + i * (360 / max(n, 1)))
            nodes.append({"label": it, "x": round(50 + 42 * math.cos(ang), 1),
                          "y": round(50 + 42 * math.sin(ang), 1)})
        ring["nodes"] = nodes
    center = data.get("center", {})
    side_cards = [
        {"title": str(c[0]), "color": _color_name(c[1]), "desc": str(c[2])}
        for c in data.get("side_cards", [])
    ]
    return {"rings": rings,
            "center_label": str(center.get("label", "")),
            "center_sub": str(center.get("sub", "")),
            "side_cards": side_cards}


def _to_html_radar(axes: List[str], series: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Pre-compute radar chart coordinates so the template needs no trig."""
    import math
    n = len(axes)
    cx, cy, R = 250, 250, 200
    # Axis label positions (just outside the outer ring).
    axis_pts = []
    for i in range(n):
        ang = math.radians(-90 + i * (360 / n))
        axis_pts.append({
            "label": str(axes[i]),
            "x": round(cx + (R + 28) * math.cos(ang), 1),
            "y": round(cy + (R + 28) * math.sin(ang), 1),
        })
    # Grid polygons (3 concentric levels).
    grids = []
    for frac in (0.33, 0.66, 1.0):
        pts = []
        for i in range(n):
            ang = math.radians(-90 + i * (360 / n))
            pts.append((round(cx + R * frac * math.cos(ang), 1),
                        round(cy + R * frac * math.sin(ang), 1)))
        grids.append(" ".join(f"{x},{y}" for x, y in pts))
    # Series polygons.
    ser_out = []
    for s in series:
        vals = s.get("values", [])
        pts = []
        for i in range(min(n, len(vals))):
            ang = math.radians(-90 + i * (360 / n))
            r = R * (vals[i] / 100.0)
            pts.append((round(cx + r * math.cos(ang), 1),
                        round(cy + r * math.sin(ang), 1)))
        ser_out.append({
            "name": str(s.get("name", "")),
            "color": _color_name(s.get("color", "#CF0A2C")),
            "points": " ".join(f"{x},{y}" for x, y in pts),
        })
    return {"axes": axis_pts, "grids": grids, "series": ser_out}


def _convert_to_html_slide(data: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    layout = data.pop("layout", "")
    data["slide_type"] = layout

    if layout == "cover":
        data["context"] = _SCENARIO_LABEL.get(scenario, "HR 数据汇报")
    elif layout == "executive_summary":
        data["items"] = _to_html_executive_items(data.get("items", []))
    elif layout == "matrix_2x2":
        data["quadrants"] = _to_html_matrix_quadrants(data.get("quadrants", []))
    elif layout == "funnel":
        data["stages"] = _to_html_funnel_stages(data.get("stages", []))
    elif layout == "timeline":
        data["milestones"] = _to_html_timeline_milestones(data.get("milestones", []))
    elif layout == "action_items":
        data["actions"] = _to_html_action_items(data.get("actions", []))
    elif layout == "three_stat":
        data["stats"] = _to_html_three_stat(data.get("stats", []))
    elif layout == "metric_cards":
        data["cards"] = _to_html_metric_cards(data.get("cards", []))
    elif layout == "grouped_bar":
        data["chart"] = _to_html_grouped_bar(
            data.get("categories", []), data.get("series", []), data.get("data", []))
    elif layout == "horizontal_bar":
        data["bars"] = _to_html_horizontal_bar(data.get("items", []))
    elif layout == "donut_chart":
        data["segments"] = _to_html_donut(data.get("segments", []))
    elif layout == "kpi_tracker":
        data["kpis"] = _to_html_kpi_tracker(data.get("kpis", []))
    elif layout == "pyramid_steps":
        data["levels"] = _to_html_pyramid(data.get("levels", []))
    elif layout == "four_column":
        data["columns"] = _to_html_four_column(data.get("items", []))
    elif layout == "scorecard":
        data["score_items"] = _to_html_scorecard(data.get("items", []))
    elif layout == "value_chain":
        data["stages"] = _to_html_value_chain(data.get("stages", []))
    elif layout == "swot":
        data["quadrants"] = _to_html_swot(data.get("quadrants", []))
    elif layout == "icon_grid":
        data["grid_items"] = _to_html_icon_grid(data.get("items", []))
    elif layout == "cycle":
        data["phases"] = _to_html_cycle(data.get("phases", []))
    elif layout == "side_by_side":
        data["options"] = _to_html_side_by_side(data.get("options", []))
    elif layout == "case_study":
        data["sections"] = _to_html_case_study(data.get("sections", []))
    elif layout == "decision_tree":
        data["tree"] = _to_html_decision_tree(data.get("root", ("",)),
                                              data.get("branches", []))
    elif layout == "ecosystem_ring":
        data["ring"] = _to_html_ecosystem_ring(data)
    elif layout == "harvey_ball_compare":
        # scores already list[list[int]]; pass through, legend_text too.
        pass
    elif layout == "swim_lane":
        # lanes/phases/steps are already plain lists; pass through.
        pass
    elif layout == "pyramid_triangle":
        data["levels"] = [
            {"label": str(l[0]), "desc": str(l[1]), "color": _color_name(l[2])}
            for l in data.get("levels", [])
        ]
    elif layout == "radar_chart":
        data["radar"] = _to_html_radar(data.get("axes", []), data.get("series", []))
    elif layout == "gantt_chart":
        data["gantt_phases"] = [str(p) for p in data.get("phases", [])]
        data["gantt_tasks"] = [
            {"name": str(t[0]), "start": t[1], "end": t[2], "color": _color_name(t[3])}
            for t in data.get("tasks", [])
        ]
    elif layout == "icon_stat_grid":
        data["stat_items"] = [
            {"num": str(it[0]), "label": str(it[1]), "desc": str(it[2]),
             "color": _color_name(it[3])}
            for it in data.get("items", [])
        ]
    elif layout == "big_number":
        # 'number' collides with the page-number key; rename to big_value.
        data["big_value"] = data.pop("number", "")
    elif layout == "checklist_status":
        # rows arrive as tuples; expose as lists for Jinja2.
        data["rows"] = [list(r) for r in data.get("rows", [])]
    # quote / data_table / table_insight: fields are scalars/templates read directly.

    data["section_title"] = _SECTION_LABEL.get(layout)
    return data


def build_html_content(
    outline: Dict[str, Any],
    output_dir: Path,
    pptx_content: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Build content.html.json.

    If ``pptx_content`` is provided, reuse it so the HTML track exactly matches
    the PPTX track. Otherwise build fresh from outline.
    """
    scenario = outline.get("scenario", "recruitment-review")

    if pptx_content is not None:
        pptx_slides = pptx_content["slides"]
    else:
        # Build from the same scenario-aware builders used by the PPTX track.
        from pptx_content_builder import build_pptx_content
        pptx_slides = build_pptx_content(outline, output_dir)["slides"]

    total = len(pptx_slides)
    chapters = _SCENARIO_CHAPTERS.get(scenario, [])
    slides: List[Dict[str, Any]] = []
    for i, data in enumerate(pptx_slides):
        # Work on a copy so the original pptx_content dict is not mutated.
        html_data = _convert_to_html_slide(data.copy(), scenario)
        html_data["idx"] = data["idx"]
        html_data["number"] = i + 1
        html_data["total"] = total
        html_data["key_point"] = data.get("key_point", "")
        html_data["animation"] = "fade-up" if html_data["slide_type"] != "cover" else "none"
        html_data["chapter"] = _chapter_for(scenario, i + 1, total)
        # Image support: pass through cover_image / image / bg_image fields.
        # For covers, auto-resolve a per-scenario asset for the HTML track
        # (the PPTX track keeps cover images opt-in to avoid a QA false
        # positive — see pptx_content_builder._make_cover).
        if data.get("cover_image"):
            html_data["bg_image"] = data["cover_image"]
        elif html_data["slide_type"] == "cover" and not html_data.get("bg_image"):
            from pathlib import Path as _P
            _skill_root = _P(__file__).resolve().parent.parent
            _candidate = _skill_root / "assets" / "covers" / f"{scenario}-cover.png"
            if _candidate.is_file():
                html_data["bg_image"] = str(_candidate)
        if data.get("image"):
            html_data["bg_image"] = data["image"]
        if data.get("image_url"):
            html_data["image_url"] = data["image_url"]
        slides.append(html_data)

    brand = _SCENARIO_BRAND.get(scenario, {"zh": "华为 ICT", "en": "HUAWEI ICT"})
    content = {
        "brief": outline["brief"],
        "framework": outline.get("framework", "pyramid"),
        "scenario": scenario,
        "slides": slides,
        "brand": brand["zh"],
        "brand_en": brand["en"],
        "chapters": chapters,
    }

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "content.html.json"
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    return content
