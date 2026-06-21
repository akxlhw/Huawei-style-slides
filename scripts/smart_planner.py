"""Smart Planner — input.txt → LLM → outline.json + content.pptx.json.

Adapted from huawei-ppt-generator/generator/planner.py. Instead of requiring a
pre-defined YAML scenario, this module reads raw source material (input.txt),
calls an LLM to plan the deck structure (which layouts, titles, key_points),
then optionally fills in per-slide content data.

Two modes:
  1. plan-only: generate outline.json (titles + layouts), then use sample
     builders for content. User reviews/edits the outline before rendering.
  2. full: LLM generates both outline AND content data in one pass.

Requires OPENAI_API_KEY (or compatible) / GLM_API_KEY env var.

Usage:
    from smart_planner import plan_from_input
    outline = plan_from_input("input.txt", title="XX汇报", page_count=8)

    # Or via orchestrator:
    python scripts/orchestrator.py --input input.txt --title "XX汇报" \\
        --page-count 8 --output ppt-project-foo
"""
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional


# Available layouts (from layout_spec.py, kept in sync manually here).
_LAYOUT_OPTIONS = [
    "cover", "executive_summary", "big_number", "three_stat", "icon_stat_grid",
    "pyramid_triangle", "ecosystem_ring", "cycle", "side_by_side", "swot",
    "case_study", "grouped_bar", "decision_tree", "donut_chart", "scorecard",
    "data_table", "kpi_tracker", "metric_cards", "radar_chart",
    "harvey_ball_compare", "gantt_chart", "checklist_status", "timeline",
    "action_items", "quote", "closing",
]

_SYSTEM_PROMPT = """你是华为风格PPT规划专家。根据用户提供的材料文本，规划PPT结构。

硬约束：
1. 所有事实、数字、案例必须来自input文本，不得编造
2. 标题必须是直接结论句（>10字符），不使用"趋势判断："等前缀
3. 每页必须选择一个layout
4. 第一页用cover，最后一页用closing
5. 不要凑页数，input信息不足就减少页数
6. 输出合法JSON"""


def plan_from_input(
    input_path: str,
    title: str = "",
    page_count: int = 6,
    output_dir: Optional[Path] = None,
    full_content: bool = False,
) -> Dict[str, Any]:
    """Read input.txt, call LLM, return an outline dict.

    If output_dir is given, writes outline.json (and content.pptx.json if
    full_content=True) to that directory.
    """
    input_text = Path(input_path).read_text(encoding="utf-8")

    # Build prompt
    layout_list = "\n".join(f'  - "{l}"' for l in _LAYOUT_OPTIONS)
    prompt = f"""请根据以下材料生成PPT大纲。

标题: {title or '根据内容自动生成'}
建议页数: {page_count}（不足可减）

可用版式:
{layout_list}

材料文本:
---
{input_text[:6000]}
---

输出JSON，schema:
{{
  "scenario": "auto",
  "framework": "pyramid|scqa|mece|star|...",
  "slides": [
    {{
      "idx": 1,
      "layout": "cover",
      "title": "直接结论句标题",
      "key_point": "核心观点（用于生成内容数据）"
    }}
  ]
}}

只输出JSON。"""

    # Call LLM
    deck_outline = _call_llm_json(prompt, system_prompt=_SYSTEM_PROMPT)

    # Normalize
    deck_outline.setdefault("scenario", "auto")
    deck_outline.setdefault("framework", "pyramid")
    deck_outline.setdefault("brief", {
        "audience": "管理层",
        "goal": "review",
        "duration_minutes": page_count * 2,
    })
    for i, slide in enumerate(deck_outline.get("slides", [])):
        slide.setdefault("idx", i + 1)
        slide.setdefault("key_point", "")

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "outline.json").write_text(
            json.dumps(deck_outline, ensure_ascii=False, indent=2), encoding="utf-8")

        if full_content:
            # Also generate content via LLM
            from pptx_content_builder import _write_agent_prompt, _try_llm_autofill
            prompt_path = _write_agent_prompt(deck_outline, output_dir)
            filled = _try_llm_autofill(prompt_path, output_dir)

    return deck_outline


def _call_llm_json(prompt: str, system_prompt: str = "") -> Dict[str, Any]:
    """Call LLM and parse JSON response. Supports GLM and OpenAI-compatible."""
    # Determine backend
    if os.getenv("GLM_API_KEY"):
        raw = _call_glm(prompt, system_prompt)
    elif os.getenv("OPENAI_API_KEY"):
        raw = _call_openai(prompt, system_prompt)
    else:
        raise RuntimeError(
            "No LLM API key found. Set GLM_API_KEY or OPENAI_API_KEY."
        )

    # Parse JSON from response
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    # Try markdown code block
    match = re.search(r'```(?:json)?\s*\n(.*?)\n```', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    # Try first { to last }
    start = raw.find('{')
    end = raw.rfind('}')
    if start >= 0 and end > start:
        return json.loads(raw[start:end + 1])
    raise ValueError(f"Cannot parse JSON from LLM response:\n{raw[:500]}")


def _call_glm(prompt: str, system_prompt: str = "") -> str:
    import urllib.request
    key = os.getenv("GLM_API_KEY")
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    payload = {"model": "glm-4", "messages": messages, "temperature": 0.3}
    req = urllib.request.Request(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"]


def _call_openai(prompt: str, system_prompt: str = "") -> str:
    from openai import OpenAI
    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    }
    client = OpenAI(**config)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    resp = client.chat.completions.create(
        model=model, messages=messages, temperature=0.3, max_tokens=4096)
    return resp.choices[0].message.content
