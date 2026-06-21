# Content Filler Prompt — 华为 Style Slides 内容生成总纲

> 本文件供 Code Agent（Claude Code / Kimi Code / ZCode 等）读取。
> Agent 读取下方 outline 与数据契约，调用其宿主 LLM 为每页生成内容，
> 输出 `content.pptx.json`，再交由 skill 渲染。

---

## 任务

给定 `outline.json`（含每页 `layout` + `title` + `key_point`），为每一页填充
该 layout 所需的数据字段，生成完整的 `content.pptx.json`。

## 输入：outline.json 结构

```json
{
  "scenario": "skill-report",
  "framework": "pyramid",
  "brief": {"audience": "...", "goal": "...", "duration_minutes": 28},
  "slides": [
    {"idx": 1, "layout": "cover", "title": "...", "key_point": ""}
  ]
}
```

## 输出：content.pptx.json 结构

每页 = outline 页 + 该 layout 的数据字段。**必须**额外包含顶层：
```json
{"scenario": "...", "framework": "...", "chapters": [...], "slides": [...]}
```
每个 content 页（非 cover/closing）**必须**有非空 `source` 且 `title` > 10 字符。

## 华为视觉约束（生成内容时遵守）

- 华为红 `#CF0A2C`（Pantone 185C），仅点睛用，单页面积 ≤ 10%
- 辅助色：科技蓝 `#007DFF`、暖绿 `#669900`、暖橙 `#FF9900`、黄 `#FCC800`、灰 `#DCDDDD`
- 标题必须是**结论性陈述句**（不是话题标签），> 10 字符
- 配色：用 `#CF0A2C`/`#007DFF`/`#669900`/`#FF9900`/`#FCC800`/`#DCDDDD` 这些 hex 字符串

## 数据契约（按 layout）

### cover
```json
{"layout":"cover","title":"...","subtitle":"...","author":"...","date":"2026"}
```

### executive_summary
```json
{"layout":"executive_summary","title":"结论句(>10字)","source":"...","items":[[1,"小标题","描述"],[2,"...","..."],[3,"...","..."]]}
```

### big_number
```json
{"layout":"big_number","title":"...","number":"200+","unit":"...","description":"...","detail_items":["...","..."],"source":"..."}
```

### three_stat
```json
{"layout":"three_stat","title":"...","stats":[["值1","标签1",true],["值2","标签2",false],["值3","标签3",false]],"detail_items":["..."],"source":"..."}
```
（第 3 元素 true=红色高亮首个）

### metric_cards
```json
{"layout":"metric_cards","title":"...","cards":[["字","标题","描述","#CF0A2C","#FCE8EA"],...],"source":"..."}
```
（3-4 张卡，每张 5 元组：letter,title,desc,accent_hex,light_hex）

### four_column
```json
{"layout":"four_column","title":"...","items":[[1,"标题",["点1","点2"]],[2,...]],"source":"..."}
```

### grouped_bar
```json
{"layout":"grouped_bar","title":"...","categories":["A","B","C","D","E"],"series":[["系列1","#CF0A2C"],["系列2","#007DFF"]],"data":[[1,3],[5,8],...],"y_ticks":[0,5,10],"summary":["标签","结论"],"source":"..."}
```
**约束：categories ≤ 6，series ≤ 2（3 会溢出）**

### horizontal_bar
```json
{"layout":"horizontal_bar","title":"...","items":[["标签",80,"#CF0A2C"],...],"summary":["标签","结论"],"source":"..."}
```

### donut_chart
```json
{"layout":"donut_chart","title":"...","segments":[[0.34,"#CF0A2C","标签"],...],"center_label":"38","center_sub":"项","summary":"...","source":"..."}
```
**约束：segments ≤ 6，pct 为 0-1 小数，3 元组 (pct,color_hex,label)**

### kpi_tracker
```json
{"layout":"kpi_tracker","title":"...","kpis":[["名称",0.85,"详情","on"],["名称",0.7,"详情","risk"]],"summary":"...","source":"..."}
```
（status: "on"/"risk"/"off"）

### scorecard
```json
{"layout":"scorecard","title":"...","items":[["维度","★★★★★",0.95],...],"source":"..."}
```

### data_table
```json
{"layout":"data_table","title":"...","headers":["列1","列2"],"rows":[["a","b"],["c","d"]],"source":"..."}
```

### swot
```json
{"layout":"swot","title":"...","quadrants":[["标签","#CF0A2C","#FCE8EA",["点1","点2"]],...4个],"source":"..."}
```

### value_chain
```json
{"layout":"value_chain","title":"...","stages":[["阶段","描述","#CF0A2C"],...],"source":"..."}
```

### cycle
```json
{"layout":"cycle","title":"...","phases":[["生成",1.0,3.2],["评估",4.0,3.2],["优化",7.0,3.2],["交付",10.0,3.2]],"right_panel":["标题",["点1","点2"]],"source":"..."}
```

### side_by_side
```json
{"layout":"side_by_side","title":"...","options":[["左标题",["点1","点2"]],["右标题",["点1","点2"]]],"source":"..."}
```

### case_study
```json
{"layout":"case_study","title":"...","sections":[["S","情境","描述"],["A","行动","描述"],["R","结果","描述"]],"result_box":["结论","内容"],"source":"..."}
```

### decision_tree
```json
{"layout":"decision_tree","title":"...","root":["根节点"],"branches":[["分支1","指标","#CF0A2C",[["子1","值"],["子2","值"]]],...],"right_panel":["标题",["点1"]],"source":"..."}
```

### ecosystem_ring
```json
{"layout":"ecosystem_ring","title":"...","rings":[{"label":"外环","color":"#DCDDDD","items":["a","b"]},...],"center":{"label":"核心","sub":"副"},"side_cards":[["标题","#CF0A2C","描述"],...],"source":"..."}
```

### harvey_ball_compare
```json
{"layout":"harvey_ball_compare","title":"...","criteria":["维度1","维度2"],"options":["选项A","选项B"],"scores":[[4,2],[3,3]],"legend_text":["● 满","◐ 半"],"summary":"...","source":"..."}
```
（scores 0-4 整数）

### swim_lane
```json
{"layout":"swim_lane","title":"...","lanes":["泳道1","泳道2"],"phases":["阶段1","阶段2"],"steps":[[0,0,"步骤"],[1,1,"步骤"]],"source":"..."}
```
（steps 三元组 lane_idx, phase_idx, label）

### pyramid_triangle
```json
{"layout":"pyramid_triangle","title":"...","levels":[["顶层","描述","#CF0A2C"],["中层","描述","#FF9900"],...],"source":"..."}
```
**约束：≤5 层**

### radar_chart
```json
{"layout":"radar_chart","title":"...","axes":["维度1","维度2","维度3","维度4","维度5","维度6"],"series":[{"name":"系列1","color":"#CF0A2C","values":[95,80,92,85,88,40]}],"source":"..."}
```
**约束：axes 3-6 个，values 0-100**

### gantt_chart
```json
{"layout":"gantt_chart","title":"...","phases":["W1","W2","W3"],"tasks":[["任务名",0,2,"#CF0A2C"]],"source":"..."}
```
（tasks 四元组 name,start,end,color；start/end 是 phase 索引）

### icon_stat_grid
```json
{"layout":"icon_stat_grid","title":"...","items":[["38","项检查","描述","#CF0A2C"],...],"source":"..."}
```
（items 四元组 num,label,desc,color_hex，≤6 项）

### timeline
```json
{"layout":"timeline","title":"...","milestones":[["阶段1","描述1"],["阶段2","描述2"]],"source":"..."}
```
**约束：最后 milestone 标签 ≤ 6 字符**

### action_items
```json
{"layout":"action_items","title":"...","actions":[["标题","时间","描述","负责人"],...],"source":"..."}
```

### closing
```json
{"layout":"closing","title":"谢谢","message":"期待交流"}
```

---

## 生成规则

1. 每页内容必须**真实、具体、与标题强相关**，不要泛泛而谈
2. 标题保持 outline 给定的（已是结论句），只填充数据字段
3. 数值要合理可信，符合该场景的业务逻辑
4. 配色在华为色板内选择，同页主色不超过 4 种
5. 输出纯 JSON，可直接写入 `content.pptx.json`
6. 完成后可运行 `python references/scripts/gate_check_s3.py content.pptx.json ./` 验证
