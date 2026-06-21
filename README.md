# huawei-style-slides

Generate presentations in Huawei official visual style using McKinsey frameworks.
Outputs both an editable Office PPTX (via MckEngine) and a browser-presentable
Huawei-styled HTML deck.

## Outputs

- `deck.pptx` — editable Office PPTX (via MckEngine, Huawei theme)
- `slides.html` — browser-presentable HTML deck (Huawei visual language)

## Usage

```bash
cd huawei-style-slides
# Default: sample data
python scripts/orchestrator.py --scenario skill-report --output ppt-project-foo
# Agent-filled content (emit prompt for a Code Agent to fill)
python scripts/orchestrator.py --scenario skill-report --output ppt-project-foo \
    --content-source agent --skip-qa
# Render the agent-filled content
python scripts/orchestrator.py --scenario skill-report --output ppt-project-foo \
    --content-source file
```

## Scenarios

- `skill-report` — Skill research & architecture deck (acceptance scenario)
- `recruitment-review` — quarterly recruitment retrospective
- `channel-roi` — recruitment channel ROI analysis
- `allocation-plan` — internal allocation plan

## Content Sources (`--content-source`)

| Mode | Description |
|------|-------------|
| `sample` (default) | hardcoded per-scenario sample data |
| `agent` | write `content_prompt.md` (outline + data contracts) for a Code Agent to fill |
| `file` | load an agent-filled `content.pptx.json` and render |

See `docs/agent-content-guide.md` for the agent fill workflow.

## Layouts (35 types, PPTX + HTML dual-track)

| Category | Layouts |
|----------|---------|
| **Huawei logic diagrams** | ecosystem_ring(同心圆), cycle, decision_tree, value_chain, swot, matrix_2x2, side_by_side, case_study, pyramid_steps, pyramid_triangle, swim_lane |
| **Data charts** | grouped_bar, horizontal_bar, donut_chart, kpi_tracker, scorecard, radar_chart, gantt_chart, harvey_ball_compare |
| **Stat/cards** | big_number, three_stat, metric_cards, four_column, icon_grid, icon_stat_grid |
| **Tables** | data_table, table_insight, checklist_status |
| **Narrative** | executive_summary, timeline, action_items, quote |
| **Frames** | cover, closing, funnel |

## Huawei Visual Language

- **Arc-red title line** (Huawei signature) on every content slide
- **Left nav rail** with chapter highlighting (HTML + PPTX)
- **Concentric ring diagrams** for ecosystem/architecture
- Color: Huawei red `#CF0A2C` (Pantone 185C), accent blue/green/orange/yellow
- Fonts: Microsoft YaHei (CJK) / Arial (Latin)

## Image Support

- Cover: `cover_image` field (file path or `'auto'` for Tencent Hunyuan AI)
- Content slides: `image` field → full-bleed background (PPTX `add_picture` + HTML `bg_image`)
- HTML cover auto-resolves `assets/covers/<scenario>-cover.png`

## Environment

```bash
export PPT_LLM_BACKEND=glm   # optional
export GLM_API_KEY=...       # required only for glm backend
# Tencent Hunyuan AI cover (optional):
export TENCENT_SECRET_ID=...
export TENCENT_SECRET_KEY=...
```

## Dependencies

See `scripts/requirements.txt`.

## Testing

```bash
python -m pytest tests/ -v          # 34 tests
python scripts/orchestrator.py --scenario skill-report --output ppt-project-foo
```

## Known Limitations

- HTML deck uses a fixed 16:9 stage; mobile view letterboxes.
- PPTX rendering requires `Mck-ppt-design-skill` at the repository root.
- `radar_chart` PPTX uses freeform; degrades to dots if freeform fails.
- PPTX cover image is opt-in (QA text_overflow heuristic); HTML cover image is on by default.
