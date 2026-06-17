# AGENTS.md — huawei-style-slides

## Project Structure

- `scripts/` — Python modules for the S1-S5 pipeline.
- `templates/` — Jinja2 HTML templates based on frontend-slides.
- `references/` — Huawei visual spec and McKinsey-HR mapping.
- `examples/` — Sample inputs and generated outputs.
- `tests/` — pytest unit tests.

## Conventions

- All Chinese text uses Microsoft YaHei; English uses Arial.
- Colors follow `huawei_theme.py` constants.
- PPTX path uses MckEngine tuple API; HTML path uses dict format.
- HTML deck uses the frontend-slides fixed 16:9 stage architecture.
- Every PR must pass `pytest tests/` and MckEngine `gate_check.py`.

## Local Development

```bash
cd huawei-style-slides
python -m venv .venv
.venv/Scripts/pip install -r scripts/requirements.txt
python -m pytest tests/ -v
```

## Generating Sample Decks

```bash
python scripts/orchestrator.py --scenario recruitment-review --output examples/output/recruitment-review
python scripts/orchestrator.py --scenario channel-roi --output examples/output/channel-roi
python scripts/orchestrator.py --scenario allocation-plan --output examples/output/allocation-plan
```
