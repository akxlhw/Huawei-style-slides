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


def _convert_matrix_quadrants(
    quadrants: List[Tuple[str, str, str]],
) -> List[Tuple[str, RGBColor, str]]:
    """Convert (label, hex_color, desc) -> (label, RGBColor, desc)."""
    return [
        (str(q[0]), _hex_to_rgb(q[1]), str(q[2]))
        for q in quadrants
    ]


def _convert_axis_labels(axis_labels: Dict[str, str]) -> Tuple[str, str]:
    """Convert {'x': ..., 'y': ...} -> (x_label, y_label)."""
    if not axis_labels:
        return ("", "")
    return (axis_labels.get("x", ""), axis_labels.get("y", ""))


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
                items=slide.get("items", []),
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
            # The retired eng.funnel() overflows; use process_chevron instead.
            steps = [
                (str(i + 1), str(label), f"{count} ({int(pct * 100)}%)")
                for i, (label, count, pct) in enumerate(slide.get("stages", []))
            ]
            eng.process_chevron(
                title=slide["title"],
                steps=steps,
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
                milestones=slide.get("milestones", []),
                source=slide.get("source", ""),
            )
        elif layout == "action_items":
            eng.action_items(
                title=slide["title"],
                actions=slide.get("actions", []),
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
