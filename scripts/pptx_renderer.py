"""S4a: Render content.pptx.json to deck.pptx via MckEngine."""

import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

MCK_ROOT = Path(__file__).resolve().parents[2] / "Mck-ppt-design-skill"
if str(MCK_ROOT) not in sys.path:
    sys.path.insert(0, str(MCK_ROOT))

from mck_ppt import MckEngine  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402


def _hex_to_rgb(hex_color: str) -> RGBColor:
    """Convert '#C7000B' to python-pptx RGBColor."""
    hex_color = hex_color.lstrip("#")
    return RGBColor(
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
    )


def _apply_huawei_theme(eng: MckEngine) -> None:
    """No-op adapter: MckEngine does not expose a global theme setter.

    The renderer relies on MckEngine's internal styling; explicit
    Huawei colors/fonts are applied in the HTML track instead.
    """
    pass


def _convert_executive_items(items: List[Dict[str, str]]) -> List[Tuple[int, str, str]]:
    """Convert [{title, description}] -> [(num, title, description)]."""
    return [(i + 1, item["title"], item.get("description", "")) for i, item in enumerate(items)]


def _convert_funnel_stages(stages: List[Dict[str, Any]]) -> List[Tuple[str, str, float]]:
    """Convert [{label, value}] -> [(label, count_label, pct_of_max)]."""
    max_value = max(s.get("value", 0) for s in stages) if stages else 1
    if max_value == 0:
        max_value = 1
    return [
        (str(s.get("label", "")), str(s.get("value", "")), s.get("value", 0) / max_value)
        for s in stages
    ]


def _convert_matrix_quadrants(
    quadrants: List[Dict[str, Any]],
) -> List[Tuple[str, RGBColor, str]]:
    """Convert [{label, items, color}] -> [(label, RGBColor, description)]."""
    result = []
    for q in quadrants:
        items = q.get("items", [])
        desc = "\n".join(str(i) for i in items) if isinstance(items, list) else str(items)
        color = _hex_to_rgb(q.get("color", "#DCDDDD"))
        result.append((str(q.get("label", "")), color, desc))
    return result


def _convert_axis_labels(axis_labels: Dict[str, str]) -> Tuple[str, str]:
    """Convert {'x': ..., 'y': ...} -> (x_label, y_label)."""
    if not axis_labels:
        return ("", "")
    return (axis_labels.get("x", ""), axis_labels.get("y", ""))


def _convert_timeline_milestones(
    milestones: List[Dict[str, str]],
) -> List[Tuple[str, str]]:
    """Convert [{date, label, desc}] -> [(label, description)]."""
    result = []
    for m in milestones:
        date = m.get("date", "")
        label = m.get("label", "")
        full_label = f"{date} {label}".strip()
        result.append((full_label, m.get("desc", "")))
    return result


def _convert_action_items(
    actions: List[Dict[str, str]],
) -> List[Tuple[str, str, str, str]]:
    """Convert [{title, owner, timeline, desc}] -> [(title, timeline, desc, owner)]."""
    return [
        (
            str(a.get("title", "")),
            str(a.get("timeline", "")),
            str(a.get("desc", "")),
            str(a.get("owner", "")),
        )
        for a in actions
    ]


def render_pptx(content: Dict[str, Any], output_dir: Path) -> Path:
    """Render a content.pptx.json dict to deck.pptx using MckEngine."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    total = len(content["slides"])
    eng = MckEngine(total_slides=total)
    _apply_huawei_theme(eng)

    for slide in content["slides"]:
        layout = slide["layout"]
        if layout == "cover":
            eng.cover(
                title=slide["title"],
                subtitle=slide.get("subtitle", ""),
                author=slide.get("author", ""),
                date=slide.get("date", ""),
            )
        elif layout == "executive_summary":
            eng.executive_summary(
                title=slide["title"],
                headline=slide.get("headline", ""),
                items=_convert_executive_items(slide.get("items", [])),
                source=slide.get("source", ""),
            )
        elif layout == "table_insight":
            eng.table_insight(
                title=slide["title"],
                headers=slide["headers"],
                rows=slide["rows"],
                insights=slide.get("insights", []),
                source=slide.get("source", ""),
            )
        elif layout == "funnel":
            # funnel() is marked retired in MckEngine but still callable.
            eng.funnel(
                title=slide["title"],
                stages=_convert_funnel_stages(slide.get("stages", [])),
                source=slide.get("source", ""),
            )
        elif layout == "data_table":
            eng.data_table(
                title=slide["title"],
                headers=slide["headers"],
                rows=slide["rows"],
                source=slide.get("source", ""),
            )
        elif layout == "matrix_2x2":
            axis_labels = _convert_axis_labels(slide.get("axis_labels"))
            eng.matrix_2x2(
                title=slide["title"],
                quadrants=_convert_matrix_quadrants(slide.get("quadrants", [])),
                axis_labels=axis_labels if any(axis_labels) else None,
                source=slide.get("source", ""),
            )
        elif layout == "timeline":
            eng.timeline(
                title=slide["title"],
                milestones=_convert_timeline_milestones(slide.get("milestones", [])),
                source=slide.get("source", ""),
            )
        elif layout == "action_items":
            eng.action_items(
                title=slide["title"],
                actions=_convert_action_items(slide.get("actions", [])),
                source=slide.get("source", ""),
            )
        elif layout == "closing":
            eng.closing(
                title=slide["title"],
                message=slide.get("message", ""),
            )
        else:
            raise ValueError(f"Unsupported PPTX layout: {layout}")

    deck_path = output_dir / "deck.pptx"
    try:
        eng.save(str(deck_path))
    except UnicodeEncodeError:
        # MckEngine's success print uses emoji that can fail on GBK/ASCII
        # consoles. The file is already saved at this point, so verify it
        # exists and continue.
        if not deck_path.exists():
            raise
    return deck_path
