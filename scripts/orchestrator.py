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
    content_source: str = "sample",
    scenario_path: str | None = None,
) -> Dict[str, Any]:
    """Run the full S1-S5 pipeline for a given scenario.

    content_source: 'sample' (hardcoded), 'agent' (emit content_prompt.md for a
    Code Agent to fill), or 'file' (load an agent-filled content.pptx.json).
    scenario_path: optional explicit path to a scenario YAML (for custom
    scenarios outside scenarios/).
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # S1 Requirements
    build_brief(scenario, audience, goal, duration_minutes, output_dir,
                scenario_path=scenario_path)

    # S2 Structure
    outline = build_outline(scenario, audience, goal, duration_minutes, output_dir,
                            scenario_path=scenario_path)

    # S3 Content
    pptx_content = build_pptx_content(outline, output_dir, content_source=content_source)
    if content_source == "agent":
        print(f"[S3] content_prompt.md written to {output_dir} — fill it, then "
              f"re-run with --content-source file to render the agent's content.")
    html_content = build_html_content(outline, output_dir, pptx_content=pptx_content)

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
    from hr_scenarios import get_scenario, available_scenarios

    parser = argparse.ArgumentParser(description="Generate Huawei HR PPT")
    subparsers = parser.add_subparsers(dest="command")

    # ── Corpus Learning subcommands ────────────────────────────────────────
    p_ingest = subparsers.add_parser("corpus-ingest", help="Extract objects from historical PPTs")
    p_ingest.add_argument("--ppt-dir", required=True)
    p_ingest.add_argument("--output", default="corpus_output")

    p_learn = subparsers.add_parser("learn", help="One-click learn PPT style (ingest+VLM+aggregate)")
    p_learn.add_argument("--ppt-dir", required=True)
    p_learn.add_argument("--output", default="corpus_output")
    p_learn.add_argument("--model", default=None)

    # ── Default generate command (original behavior) ──────────────────────
    # --scenario accepts any name resolvable in scenarios/, OR a custom YAML
    # path via --scenario-yaml. We don't hardcode choices so new YAML scenarios
    # work without code changes.
    parser.add_argument(
        "--scenario",
        help="scenario name (a scenarios/<name>.yaml file). "
             "Available: " + ", ".join(available_scenarios()),
    )
    parser.add_argument(
        "--scenario-yaml", default=None,
        help="explicit path to a custom scenario YAML file (alternative to --scenario)",
    )
    parser.add_argument("--audience", default=None,
                        help="audience; defaults to the scenario's audience")
    parser.add_argument("--goal", default=None,
                        help="goal; defaults to the scenario's goal")
    parser.add_argument("--duration", type=int, default=None,
                        help="duration in minutes; defaults to the scenario's duration")
    parser.add_argument("--output", default="ppt-project-output")
    parser.add_argument("--skip-qa", action="store_true")
    parser.add_argument(
        "--content-source", default="sample",
        choices=["sample", "agent", "file"],
        help="sample=hardcoded data (default); agent=write content_prompt.md for "
             "a Code Agent to fill; file=load an agent-filled content.pptx.json",
    )
    # ── Smart Planner mode: input.txt → LLM → outline → render ────────────
    parser.add_argument(
        "--input", default=None,
        help="raw source material file (input.txt). When set, uses Smart Planner "
             "(LLM) to auto-generate the outline instead of a YAML scenario. "
             "Requires GLM_API_KEY or OPENAI_API_KEY.",
    )
    parser.add_argument("--title", default="", help="deck title (with --input)")
    parser.add_argument("--page-count", type=int, default=8,
                        help="target page count (with --input)")
    args = parser.parse_args()

    # Smart Planner mode: input.txt → LLM → outline
    if args.input:
        from smart_planner import plan_from_input
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"[Smart Planner] Reading {args.input}...")
        outline = plan_from_input(
            args.input, title=args.title, page_count=args.page_count,
            output_dir=output_dir,
        )
        print(f"[Smart Planner] Generated {len(outline['slides'])}-slide outline.")
        # Now run the pipeline with the LLM-generated outline
        from pptx_content_builder import build_pptx_content
        from html_content_builder import build_html_content
        from pptx_renderer import render_pptx
        from html_renderer import render_html
        from html_validator import validate_html
        pc = build_pptx_content(outline, output_dir)
        hc = build_html_content(outline, output_dir, pptx_content=pc)
        deck = render_pptx(pc, output_dir)
        html = render_html(hc, output_dir)
        val = validate_html(html, expected_slides=len(hc["slides"]))
        if not val["ok"]:
            raise SystemExit(f"HTML validation failed: {val['errors']}")
        # Grounding check
        from grounding_checker import check_grounding
        input_text = Path(args.input).read_text(encoding="utf-8")
        report = check_grounding(pc, input_text)
        (output_dir / "grounding_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[Grounding] support rate: {report['support_rate']:.0%} "
              f"({report['supported_claims']}/{report['checked_claims']})")
        if report["unsupported_claims"]:
            print(f"  ⚠ {len(report['unsupported_claims'])} unsupported claims")
        print(json.dumps({
            "outline": str(output_dir / "outline.json"),
            "deck": str(deck), "html": str(html),
            "grounding": str(output_dir / "grounding_report.json"),
        }, ensure_ascii=False, indent=2))
        return

    if not args.scenario and not args.scenario_yaml:
        parser.error("one of --scenario, --scenario-yaml, or --input is required")

    # Fall back to scenario-defined defaults when the CLI flag is omitted.
    sc = get_scenario(args.scenario, path=args.scenario_yaml)
    scenario_name = args.scenario or Path(args.scenario_yaml).stem
    audience = args.audience if args.audience is not None else sc["audience"]
    goal = args.goal if args.goal is not None else sc["goal"]
    duration = args.duration if args.duration is not None else sc["duration_minutes"]

    result = run(
        scenario=scenario_name,
        audience=audience,
        goal=goal,
        duration_minutes=duration,
        output_dir=Path(args.output),
        skip_qa=args.skip_qa,
        content_source=args.content_source,
        scenario_path=args.scenario_yaml,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # ── Corpus Learning command dispatch ──────────────────────────────────
    args = parser.parse_args()
    if args.command == "corpus-ingest":
        import sys; sys.path.insert(0, str(Path(__file__).parent / "corpus_learning"))
        from ingest_pptx import ingest_pptx_directory
        ingest_pptx_directory(args.ppt_dir, args.output)
        return
    if args.command == "learn":
        import sys; sys.path.insert(0, str(Path(__file__).parent / "corpus_learning"))
        from ingest_pptx import ingest_pptx_directory
        from summarize_slide_with_vlm import summarize_all_slides
        from aggregate_slide_summaries import aggregate_summaries
        from build_generation_requirements import build_requirements
        print("=== Phase 1: Ingest ===")
        ingest_pptx_directory(args.ppt_dir, args.output)
        if args.model:
            print("\n=== Phase 2: VLM Summarize ===")
            summarize_all_slides(args.output, args.model)
            print("\n=== Phase 3: Aggregate ===")
            aggregate_summaries(args.output)
        print("\n=== Phase 4: Build Requirements ===")
        build_requirements(args.output, str(Path(args.output) / "ppt_generation_requirements.md"))
        print(f"\n=== Done → {args.output}/ ===")
        return


if __name__ == "__main__":
    main()
