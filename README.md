# huawei-style-slides

Generate HR recruitment/allocation presentations in Huawei visual style using McKinsey frameworks.

## Outputs

- `deck.pptx` — editable Office PPTX (via MckEngine)
- `slides.html` — browser-presentable HTML deck (via frontend-slides)

## Usage

```bash
cd huawei-style-slides
python scripts/orchestrator.py --scenario recruitment-review --output ppt-project-demo
```

## Scenarios

- `recruitment-review` — quarterly recruitment retrospective
- `channel-roi` — recruitment channel ROI analysis
- `allocation-plan` — internal allocation plan

## Environment

```bash
export PPT_LLM_BACKEND=glm   # optional
export GLM_API_KEY=...       # required only for glm backend
```

## Dependencies

See `scripts/requirements.txt`.

## Known Limitations

- HTML deck uses a fixed 16:9 stage; mobile view letterboxes.
- PPTX rendering requires `Mck-ppt-design-skill` at the repository root.
- Generated content uses sample data; replace with real data in production.
