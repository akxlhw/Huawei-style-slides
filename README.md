# huawei-style-slides

Generate presentations in Huawei official visual style. Outputs both an
editable Office PPTX (via MckEngine) and a browser-presentable Huawei-styled
HTML deck.

## Quick Start

```bash
# 1. Clone + install
git clone https://github.com/akxlhw/Huawei-style-slides.git
cd Huawei-style-slides
pip install -r scripts/requirements.txt

# 2. MckEngine needed at parent dir for PPTX rendering
cd .. && git clone https://github.com/likaku/Mck-ppt-design-skill.git
cd Huawei-style-slides

# 3a. Generate from a built-in scenario
python scripts/orchestrator.py --scenario recruitment-review --output ppt-demo

# 3b. Generate from raw material via Smart Planner (needs API key)
export GLM_API_KEY=...
python scripts/orchestrator.py --input material.txt --title "Q3汇报" --output ppt-demo
```

Output: `ppt-demo/deck.pptx` (PowerPoint) + `ppt-demo/slides.html` (browser).

## Three Generation Modes

| Mode | Command | When to use |
|------|---------|-------------|
| **YAML Scenario** | `--scenario <name>` | Structured outline, 7 built-in + custom |
| **Smart Planner** | `--input material.txt` | Raw material → LLM plans + fills + grounding-checks |
| **Agent Fill** | `--content-source agent` | Generate prompt for a Code Agent to fill |

## Scenarios (7 built-in + unlimited custom)

| Scenario | Framework | Description |
|----------|-----------|-------------|
| `skill-report` | pyramid | Skill research deck (acceptance) |
| `recruitment-review` | seven-step | Quarterly recruitment retrospective |
| `channel-roi` | mece | Channel ROI analysis |
| `allocation-plan` | scqa | Internal allocation plan |
| `annual-review` | star | Annual performance review |
| `risk-report` | fis | Risk early-warning report |
| `proposal-review` | bsbrp | Proposal evaluation |

Custom scenario:
```bash
cp scenarios/allocation-plan.yaml scenarios/my-report.yaml
# Edit titles/layouts, then:
python scripts/orchestrator.py --scenario my-report --output ppt-x
```
See `docs/scenario-guide.md` for YAML schema and rules.

## Layouts (47 types, PPTX + HTML dual-track)

| Category | Layouts |
|----------|---------|
| **Logic diagrams** | ecosystem_ring, cycle, decision_tree, value_chain, swot, matrix_2x2, side_by_side, case_study, pyramid_triangle, pyramid_steps, swim_lane |
| **Data charts** | grouped_bar, horizontal_bar, donut_chart, kpi_tracker, radar_chart, gantt_chart, harvey_ball_compare, scorecard |
| **Stat/cards** | big_number, three_stat, metric_cards, four_column, icon_grid, icon_stat_grid |
| **Tables** | data_table, table_insight, checklist_status |
| **Narrative** | executive_summary, timeline, action_items, quote |
| **Frames** | cover, closing, funnel + 12 framework layouts |

## Framework Gallery (25 frameworks)

`references/framework-gallery/` contains 25 Huawei-style framework example
images: Ishikawa, 5W2H, PESTEL, Porter's Five Forces, BMC, 7S, BCG Matrix,
Pyramid, SCQA, STAR, PREP, FABE, RACI, AIDA, etc.

Regenerate: `python scripts/generate_framework_gallery.py`

## Configuration (no code changes needed)

| File | Controls |
|------|----------|
| `theme.yaml` | Colors, fonts, brand name (light theme) |
| `theme-dark.yaml` | Dark theme — activate via `HUAWEI_THEME=dark` |
| `scenarios/*.yaml` | Deck outlines (titles, layouts, pages) |
| `slide.data` | Per-slide content data override in YAML |

## Quality Assurance

- **S3 Gate**: content format / quantity / title length validation
- **S4 Gate**: overflow / whitespace / overlap / font consistency (must be 0 errors)
- **Grounding Checker**: verifies LLM-generated content traces back to source material
- **47 tests**: `python -m pytest tests/ -v`

## Advanced

### Corpus Learning (learn from real PPTs)
```bash
python scripts/orchestrator.py learn --ppt-dir /path/to/decks --model gpt-4o
```

### HTML → PPTX converter
```bash
python scripts/html_to_pptx.py slides.html -o deck_from_html.pptx
```

## Environment Variables

| Variable | Purpose | Required? |
|----------|---------|-----------|
| `GLM_API_KEY` | Smart Planner / Agent fill (GLM backend) | LLM modes only |
| `OPENAI_API_KEY` | Smart Planner / Agent fill (OpenAI backend) | LLM modes only |
| `HUAWEI_THEME` | `dark` to use dark theme | Optional |

## Dependencies

- `Mck-ppt-design-skill` at parent directory (PPTX engine)
- Python 3.8+: `python-pptx`, `lxml`, `Jinja2`, `PyYAML`, `pydantic`
- Optional: Playwright (HTML→PPTX), `openai` package (Smart Planner)

See `scripts/requirements.txt` for full list.
