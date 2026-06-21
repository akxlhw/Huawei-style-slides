# Agent 内容填充指引

华为 Style Slides 支持**三种内容来源**，让任意主题的 PPT 都能生成，而不必修改代码：

| 模式 | 命令 | 适用场景 |
|------|------|---------|
| `sample` | `--content-source sample`（默认） | 用内置样本数据快速出 deck |
| `agent` | `--content-source agent` | 生成 `content_prompt.md`，由 Code Agent 调用宿主 LLM 填充真实内容 |
| `file` | `--content-source file` | 加载 Agent 已填充的 `content.pptx.json` 渲染 |

## Agent 填充工作流

skill 由 Code Agent（Claude Code / Kimi Code / ZCode 等）调用，所以内容生成采用
**Agent 填充模式**：skill 提供 prompt，由 Agent 调用其宿主 LLM 生成内容，skill 本身不调 API。

### 步骤

```bash
# 1. 生成 prompt 文件（含 outline + 所有 layout 的数据契约 + 华为约束）
python scripts/orchestrator.py --scenario skill-report \
    --output ppt-project-foo --content-source agent --skip-qa

# → 产出 ppt-project-foo/content_prompt.md
```

```text
# 2. Code Agent 读取 content_prompt.md，调用宿主 LLM：
#    - 读取其中【本 deck 的 outline.json】（每页 layout + title + key_point）
#    - 按【数据契约】为每页填充字段（遵守华为配色/数量约束）
#    - 输出完整的 content.pptx.json 写入同目录
```

```bash
# 3. 渲染 Agent 填充的内容
python scripts/orchestrator.py --scenario skill-report \
    --output ppt-project-foo --content-source file

# → 用 Agent 填充的 content.pptx.json 渲染 deck.pptx + slides.html，跑 gate_check
```

### 验证

```bash
# 单独验证 content.json 是否符合 S3 门禁
python ../Mck-ppt-design-skill/references/scripts/gate_check_s3.py \
    ppt-project-foo/content.pptx.json ppt-project-foo/
```

## content_prompt.md 结构

该文件由 skill 自动生成，包含三部分：

1. **本 deck 的 outline.json** — 每页的 `layout` + `title` + `key_point`
2. **数据契约** — 每个 layout 的字段规范（从 `scripts/prompts/content_filler.md` 加载）
3. **华为视觉约束** — 配色（#CF0A2C 等）、数量限制（donut≤6段、grouped_bar≤2系列等）

## 数据契约要点

- 每个 content 页（非 cover/closing）**必须**有非空 `source` 且 `title` > 10 字符
- 配色用华为色板：`#CF0A2C`/`#007DFF`/`#669900`/`#FF9900`/`#FCC800`/`#DCDDDD`
- 各 layout 的数量约束（违反会过不了 S3 门禁）：
  - `donut_chart`: segments ≤ 6
  - `grouped_bar`: categories ≤ 6, series ≤ 2
  - `process_chevron`: steps ≤ 5
  - `matrix_2x2`: quadrants = 4
  - `radar_chart`: axes 3-6
  - `timeline`: 最后标签 ≤ 6 字符

完整的字段规范见 `scripts/prompts/content_filler.md`。
