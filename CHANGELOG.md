# Changelog — huawei-style-slides

## v0.4.0 — 架构优化 11 项 (2026-06-21)

### 1. content 数据外置
- slide.data 机制：YAML 场景的 slide 可带 data 字段直接提供内容，不必改代码
- build_pptx_content 主循环优先读 slide.data，无则回退到 builder sample

### 2. llm_client 改造为可用
- agent 模式新增 _try_llm_autofill：有 GLM/Anthropic key 时自动填充 content
- 无 key 时优雅跳过，保留 content_prompt.md 供外部 agent 填充

### 3. PPTX 内容图布局接真实图
- monkey-patch add_image_placeholder：label 是文件路径时插入真实图
- 覆盖 MckEngine 全部 7 个图布局（content_right_image/three_images 等）

### 4. pptx_renderer.py 拆分
- 875 行拆为 597（主分发+主题+ring/nav）+ 327（native_renderers.py）
- 9 个 native 渲染函数移入独立模块

### 5. native 渲染函数几何测试
- 新增 test_native_geometry.py：8 个版式无溢出断言
- 防止 overlap/overflow 回归

### 6. HTML→PPTX 转换器
- 新增 html_to_pptx.py：Playwright 截图每页 HTML → 嵌入 PPTX
- 华为风 HTML deck 可转成可分享的 PPTX（图片版）

### 7. 双轨渲染逻辑统一
- 新增 layout_spec.py：35+12 版式的字段/约束/轨类型统一登记
- 两轨共享同一版式规范真相源，减少不一致

### 8. 12 种框架图接入正式版式
- fishbone/5w2h/pest/porter/bmc/7s/bcg/grow/prep/fabe/raci/aida 注册进 BUILDERS
- 可在 YAML 场景 outline 中直接引用

### 9. 主题配置外置 theme.yaml
- 色板/字体/品牌名从代码移到 theme.yaml
- 换品牌/配色只需改 YAML，不改代码

### 10. 性能优化
- render_pptx 加 content hash 缓存：content 没变则跳过重渲染

### 11. 文档同步
- CHANGELOG/README/layout-mapping/scenario-guide 全面更新

## v0.3.0 — 彻底迭代优化 (2026-06-20)

### 优化一：PPTX 轨华为风（消除双轨风格割裂）
- **弧形红色标题线**：monkey-patch `add_action_title`，每页标题下自动加华为红短线
- **同心圆架构图原生渲染**：新增 `_render_huawei_ring`，PPTX 用 OVAL 堆叠多层环（不再 fallback value_chain）
- **左侧导航条**：新增 `_render_huawei_nav`，内容页左侧绘制章节导航，当前章节红色高亮
- 配色彻底对齐华为色板（#CF0A2C / #007DFF / #669900 / #FF9900）

### 优化二：新增 6 种华为图形版式（PPTX + HTML 双轨）
- `harvey_ball_compare` — Harvey 球评估矩阵（复用引擎 `harvey_ball_table`）
- `swim_lane` — 泳道流程图（lane × phase）
- `pyramid_triangle` — 真三角形金字塔（堆叠居中递减宽度矩形）
- `radar_chart` — 雷达图（同心圆 + 辐射线 + freeform 数据多边形）
- `gantt_chart` — 甘特图（时间轴 + 圆角条形）
- `icon_stat_grid` — 图标数字网格（大数字 + 卡片）

### 优化三：内容 LLM 自动化（Agent 填充模式）
- 新增 `--content-source sample|agent|file` 三种内容来源
- `agent` 模式：生成 `content_prompt.md`（outline + 35 种 layout 数据契约 + 华为约束），供 Code Agent 填充
- 新增 `scripts/prompts/content_filler.md` 数据契约库
- 新增 `docs/agent-content-guide.md` 填充指引

### 优化四：全页图片支持
- PPTX 封面：`cover_image` 字段（路径 / `'auto'` 腾讯混元 AI）
- PPTX 内容页：新增 `_render_image_bg` 全幅背景图 + 白色蒙版
- HTML：slide 支持 `bg_image` / `image_url` 字段，cover 模板支持背景图
- 新增 `assets/covers/`、`assets/cases/`、`assets/icons/` 目录
- 自动生成华为风格封面背景图 `skill-report-cover.png`

### 其他
- `huawei_theme.py` 补齐完整色板（科技蓝/暖橙/暖绿/中灰）
- `html_validator.py` 正则修复（匹配 `class="slide no-nav"`）
- 修复 HTML 数据契约 bug（action_items/timeline 的 desc→description）
- 修复 outline_builder trim 逻辑丢失 executive_summary 的问题
- 测试从 20 项增至 34 项，覆盖新版式/agent模式/图片字段

## v0.2.0 — 华为风接入 + SmartArt (2026-06-20)

### 华为全局视觉框架
- 弧形红色标题线（`hw_title` 宏，SVG 拱形）
- 左侧章节导航条（`huawei-frame.css.j2`，当前章节高亮）
- 同心圆架构图 `ecosystem_ring`（SVG 多层环）
- 大数字 KPI 卡片矩阵（华风样式）

### SmartArt 逻辑图形（4 种）
- `cycle`（闭环）、`side_by_side`（对比）、`case_study`（SAR 叙事）、`decision_tree`（路由树）

### V2 富图表（14 种）
- big_number, three_stat, metric_cards, grouped_bar, horizontal_bar, donut_chart,
  kpi_tracker, pyramid_steps, four_column, scorecard, checklist_status, value_chain,
  swot, icon_grid, quote

## v0.1.0 — 初始版本 (2026-06-17)

- 双轨架构：PPTX (MckEngine) + HTML (frontend-slides)
- S1-S5 流程：brief → outline → content → render → QA gate
- 4 场景：recruitment-review, channel-roi, allocation-plan, skill-report
- 9 基础版式 + gate_check 门禁
