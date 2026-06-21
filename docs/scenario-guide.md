# 场景编写指南（Scenario Authoring Guide）

huawei-style-slides 的场景大纲现在是 **YAML 文件**，放在 `scenarios/` 目录下。
新增或修改汇报场景**只需编辑 YAML，无需改任何 Python 代码**。

## 快速开始：新增一个场景

1. 复制模板：
```bash
cp scenarios/allocation-plan.yaml scenarios/my-report.yaml
```

2. 编辑 `scenarios/my-report.yaml`，修改 name/slides 等字段（见下方 schema）。

3. 生成 PPT：
```bash
python scripts/orchestrator.py --scenario my-report --output ppt-project-my-report
```

## YAML Schema

```yaml
# 必填顶层字段
name: 场景显示名称              # 出现在 brief.md 标题
framework: pyramid              # 主框架：pyramid|scqa|mece|seven-step|...
secondary: [mece, 9-box]        # 辅助框架（可选，默认空）
audience: HRD / 业务负责人       # 目标听众
goal: review                    # 目的：review|decision|proposal
duration_minutes: 15            # 时长（分钟），决定页数预算

slides:                         # 幻灯片序列
  - idx: 1                      # 页码（从1开始）
    layout: cover               # 版式名（见下方可选列表）
    title: 封面标题              # 标题文字
    key_point: ""               # 关键点（内容生成的种子，可选）
    # 可选字段：
    # cover_image: assets/covers/x.png   # 仅 cover：封面背景图路径或 'auto'
    # show_arc: true                     # 可选：该页标题下加弧形红线装饰
```

## 必须遵守的规则（否则过不了门禁）

1. **每个内容页（非 cover/closing）的 title 必须 > 10 字符**，且是结论性陈述句
   - ✅ "Q3 招聘完成率未达目标，技术岗缺口最大"
   - ❌ "招聘复盘"（太短，是话题标签不是结论）
2. **每个内容页必须有非空的 key_point**（或内容会回退到占位文本）
3. **第一页必须是 cover，最后一页必须是 closing**
4. **版式数量约束**（违反会被 S3 门禁拦截）：
   - `donut_chart`: segments ≤ 6
   - `grouped_bar`: categories ≤ 6, series ≤ 2
   - `matrix_2x2`: quadrants = 4
   - `radar_chart`: axes 3-6
   - `timeline`: 最后一个 milestone 标签 ≤ 6 字符

## 可用的 35 种版式

| 类别 | 版式 |
|------|------|
| 框架页 | cover, closing |
| 叙事 | executive_summary, big_number, three_stat, timeline, action_items, quote |
| 卡片 | metric_cards, four_column, icon_grid, icon_stat_grid, pyramid_steps |
| 表格 | data_table, table_insight, checklist_status, scorecard |
| 图表 | grouped_bar, horizontal_bar, donut_chart, kpi_tracker, radar_chart, gantt_chart, harvey_ball_compare |
| 逻辑图 | ecosystem_ring, cycle, value_chain, decision_tree, matrix_2x2, swot, side_by_side, case_study, swim_lane, pyramid_triangle, funnel |

完整字段规范见 `scripts/prompts/content_filler.md`（每种 layout 的数据契约）。

## 查看现有场景

```bash
ls scenarios/
# allocation-plan.yaml  channel-roi.yaml  recruitment-review.yaml  skill-report.yaml
```

## 使用自定义路径（场景不在 scenarios/ 目录）

```bash
python scripts/orchestrator.py --scenario-yaml /path/to/my-scenario.yaml --output ppt-project-x
```

## 与内容来源（content-source）的关系

场景 YAML 定义的是**大纲结构**（哪些页、什么版式、什么标题）。每页的**具体内容数据**
（图表数值、表格行、卡片文字）由 `--content-source` 决定：

| content-source | 内容来源 |
|----------------|---------|
| `sample`（默认） | 各版式内置的样本数据（scenario 相关） |
| `agent` | 生成 content_prompt.md，由 Code Agent 填充真实内容 |
| `file` | 读取已填充的 content.pptx.json |

典型工作流：用 sample 快速看结构 → 用 agent 生成真实内容 → 用 file 渲染最终版。

## 25 种思维框架参考

设计场景大纲时，可参考 `references/framework-gallery/` 里的 25 种框架示例图，
选择最匹配汇报目的的框架来组织页面顺序。
