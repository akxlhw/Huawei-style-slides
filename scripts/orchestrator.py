"""Main driver for huawei-hr-ppt skill: S1 -> S5."""

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from brief_builder import build_brief
from outline_builder import build_outline
from pptx_content_builder import build_pptx_content
from html_content_builder import build_html_content
from pptx_renderer import render_pptx
from html_renderer import render_html
from html_validator import validate_html
from qa_runner import run_gate_check_s3, run_gate_check, assert_passed


def run(
    scenario: str,
    audience: str,
    goal: str,
    duration_minutes: int,
    output_dir: Path,
    skip_qa: bool = False,
) -> Dict[str, Any]:
    """Run the full S1-S5 pipeline for a given scenario."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # S1 Requirements
    build_brief(scenario, audience, goal, duration_minutes, output_dir)

    # S2 Structure
    outline = build_outline(scenario, audience, goal, duration_minutes, output_dir)

    # S3 Content
    pptx_content = build_pptx_content(outline, output_dir)
    html_content = build_html_content(outline, output_dir)

    if not skip_qa:
        s3_result = run_gate_check_s3(output_dir / "content.pptx.json", output_dir)
        assert_passed(s3_result, "S3 gate_check_s3")

    # S4 Render
    deck_path = render_pptx(pptx_content, output_dir)
    html_path = render_html(html_content, output_dir)

    html_validation = validate_html(
        html_path, expected_slides=len(html_content["slides"])
    )
    if not html_validation["ok"]:
        raise SystemExit(f"HTML validation failed: {html_validation['errors']}")

    # S5 QA
    if not skip_qa:
        s4_result = run_gate_check(deck_path, output_dir)
        assert_passed(s4_result, "S4 gate_check")

    return {
        "brief": str(output_dir / "brief.md"),
        "outline": str(output_dir / "outline.json"),
        "content_pptx": str(output_dir / "content.pptx.json"),
        "content_html": str(output_dir / "content.html.json"),
        "deck": str(deck_path),
        "html": str(html_path),
    }


def main():
    parser = argparse.ArgumentParser(description="Generate Huawei HR PPT")
    parser.add_argument(
        "--scenario",
        required=True,
        choices=["recruitment-review", "channel-roi", "allocation-plan"],
    )
    parser.add_argument("--audience", default="HRD")
    parser.add_argument("--goal", default="review")
    parser.add_argument("--duration", type=int, default=15)
    parser.add_argument("--output", default="ppt-project-output")
    parser.add_argument("--skip-qa", action="store_true")
    args = parser.parse_args()

    result = run(
        scenario=args.scenario,
        audience=args.audience,
        goal=args.goal,
        duration_minutes=args.duration,
        output_dir=Path(args.output),
        skip_qa=args.skip_qa,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
