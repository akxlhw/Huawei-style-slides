---
name: huawei-style-slides
description: >-
  Generate HR recruitment and allocation presentations in Huawei visual style using McKinsey frameworks.
  Outputs both an editable Office PPTX and a browser-based HTML slide deck.
  Trigger when the user asks for HR reports, recruitment reviews, channel ROI analysis,
  allocation plans, or any HR-related PowerPoint/HTML presentation.
license: MIT
metadata:
  version: "0.1.0"
  category: productivity
  sources:
    - https://github.com/likaku/Mck-ppt-design-skill
    - ./Mck-ppt-design-skill
    - ./frontend-slides
---

# Huawei HR PPT Skill

## Overview

Generate HR presentations for recruitment and allocation scenarios.
- **Visual style**: Huawei ICT Academy spec (Huawei Red #C7000B, title black #231815, body gray #595757, Microsoft YaHei/Arial, light backgrounds).
- **Logical frameworks**: McKinsey frameworks mapped to HR scenarios (pyramid, MECE, SCQA, issue tree, seven-step, 9-box, 7S, 3C, OHI, talent-to-value).
- **Outputs**:
  - `deck.pptx` — editable Office PPTX via MckEngine.
  - `slides.html` — browser-presentable HTML deck via frontend-slides.

## Workflow (S1-S5)

1. **S1 Requirements** → `ppt-project-{slug}/brief.md`
2. **S2 Structure** → `ppt-project-{slug}/outline.json`
3. **S3 Content** → `ppt-project-{slug}/content.pptx.json` + `content.html.json`
4. **S4 Render** → `deck.pptx` + `slides.html`
5. **S5 QA & Deliver** → run gate_check.py, read `gate_result.json`

## Quick Start

```bash
cd huawei-style-slides
python scripts/orchestrator.py --scenario recruitment-review --output ppt-project-demo
```

## Environment Variables

```bash
export PPT_LLM_BACKEND=glm   # optional; default uses Claude Code
export GLM_API_KEY=...       # required only if backend is glm
```

## Known Limitations

- HTML deck uses a fixed 16:9 stage; mobile view letterboxes.
- PPTX rendering requires `Mck-ppt-design-skill` at the repository root.
- Generated content uses sample data; replace with real data in production.
