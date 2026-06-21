---
name: huawei-style-slides
description: >-
  Generate Huawei-style presentations (PPTX + HTML dual-track) from scenarios,
  raw material, or LLM planning. 47 layouts, 25 framework gallery, 7 built-in
  scenarios. Supports Smart Planner (input→LLM→deck), Grounding Checker
  (anti-fabrication), and Corpus Learning (learn from historical PPTs).
  Trigger when the user asks for any Huawei-style or business presentation.
license: MIT
metadata:
  version: "0.5.0"
  category: productivity
  sources:
    - https://github.com/likaku/Mck-ppt-design-skill
    - ./Mck-ppt-design-skill
---

# Huawei Style Slides

## Overview

Generate presentations in Huawei official visual style.
- **Visual style**: Huawei Red #CF0A2C (Pantone 185C), title black, body gray,
  Microsoft YaHei/Arial, light backgrounds. Optional dark theme.
- **47 layouts**: PPTX + HTML dual-track, fully aligned.
- **25 framework gallery**: Ishikawa, BMC, 7S, BCG, Porter's Five Forces, etc.
- **Outputs**: `deck.pptx` (editable) + `slides.html` (browser-presentable).

## Three Generation Modes

### 1. YAML Scenario (structured outline)
```bash
python scripts/orchestrator.py --scenario skill-report --output ppt-project-foo
```
7 built-in scenarios, or drop a `scenarios/my-report.yaml` for custom.

### 2. Smart Planner (raw material → LLM → deck)
```bash
export GLM_API_KEY=...   # or OPENAI_API_KEY
python scripts/orchestrator.py --input material.txt --title "Q3汇报" --output ppt-foo
```
LLM reads the material, plans the outline, fills content, then grounding-checks
for fabrication. Outputs `grounding_report.json`.

### 3. Agent Fill (prompt for external Code Agent)
```bash
python scripts/orchestrator.py --scenario my-report --content-source agent --output ppt-foo
# → generates content_prompt.md, Code Agent fills it, then:
python scripts/orchestrator.py --scenario my-report --content-source file --output ppt-foo
```

## Corpus Learning (learn from real PPTs)
```bash
python scripts/orchestrator.py learn --ppt-dir /path/to/huawei-decks --model gpt-4o
```
Extracts coordinates/fonts/colors from historical PPTs, VLM analyzes layout
patterns, generates reusable style requirements.

## Scenarios (7 built-in + unlimited custom)

| Scenario | Framework | Pages |
|----------|-----------|-------|
| skill-report | pyramid | 24 |
| recruitment-review | seven-step | 9 |
| channel-roi | mece | 7 |
| allocation-plan | scqa | 8 |
| annual-review | star | 9 |
| risk-report | fis | 7 |
| proposal-review | bsbrp | 7 |

Custom: `cp scenarios/allocation-plan.yaml scenarios/my-report.yaml` → edit → run.
See `docs/scenario-guide.md`.

## Configuration (no code changes needed)

| File | Controls |
|------|----------|
| `theme.yaml` | Colors, fonts, brand (light theme) |
| `theme-dark.yaml` | Dark theme (`HUAWEI_THEME=dark` to activate) |
| `scenarios/*.yaml` | Deck outlines (titles, layouts, pages) |
| `slide.data` field | Per-slide content data override |

## Layouts (47 types)

| Category | Layouts |
|----------|---------|
| Logic diagrams | ecosystem_ring, cycle, decision_tree, value_chain, swot, matrix_2x2, side_by_side, case_study, pyramid_triangle, pyramid_steps, swim_lane |
| Data charts | grouped_bar, horizontal_bar, donut_chart, kpi_tracker, radar_chart, gantt_chart, harvey_ball_compare, scorecard |
| Stat/cards | big_number, three_stat, metric_cards, four_column, icon_grid, icon_stat_grid |
| Tables | data_table, table_insight, checklist_status |
| Narrative | executive_summary, timeline, action_items, quote |
| Frames | cover, closing, funnel + 12 framework layouts |

## Dependencies

- `Mck-ppt-design-skill` at parent directory (PPTX rendering engine)
- Python 3.8+, see `scripts/requirements.txt`
- Optional: Playwright (HTML→PPTX converter), OpenAI/GLM API key (Smart Planner)

## Testing
```bash
python -m pytest tests/ -v   # 47 tests
```
