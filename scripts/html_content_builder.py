"""S3b: Build content.html.json from outline.

Reuses the PPTX builders then converts MckEngine tuple API format into the
dict format expected by the HTML Jinja2 templates.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from pptx_content_builder import BUILDERS as PPTX_BUILDERS


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
            "color": str(q[1]),
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
            "desc": desc,
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
            "desc": str(a[2]),
            "owner": str(a[3]),
        }
        for a in actions
    ]


def _convert_to_html_slide(data: Dict[str, Any]) -> Dict[str, Any]:
    layout = data.pop("layout", "")
    data["slide_type"] = layout

    if layout == "executive_summary":
        data["items"] = _to_html_executive_items(data.get("items", []))
    elif layout == "matrix_2x2":
        data["quadrants"] = _to_html_matrix_quadrants(data.get("quadrants", []))
    elif layout == "funnel":
        data["stages"] = _to_html_funnel_stages(data.get("stages", []))
    elif layout == "timeline":
        data["milestones"] = _to_html_timeline_milestones(data.get("milestones", []))
    elif layout == "action_items":
        data["actions"] = _to_html_action_items(data.get("actions", []))

    return data


def build_html_content(outline: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    slides: List[Dict[str, Any]] = []
    for slide in outline["slides"]:
        layout = slide["layout"]
        builder = PPTX_BUILDERS.get(layout)
        if not builder:
            raise ValueError(f"Unsupported HTML slide_type: {layout}")
        data = builder(slide)
        data["idx"] = slide["idx"]
        data["key_point"] = slide.get("key_point", "")
        data["animation"] = "fade-up" if layout != "cover" else "none"
        slides.append(_convert_to_html_slide(data))

    content = {
        "brief": outline["brief"],
        "framework": outline.get("framework", "pyramid"),
        "slides": slides,
    }

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "content.html.json"
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    return content
