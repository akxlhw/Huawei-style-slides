# 思维逻辑框架图库（Framework Gallery）

> 25 种 PPT 常用思维逻辑框架的标准示例图，全部华为视觉风格（白底红点睛）。
> 生成方式：`python scripts/generate_framework_gallery.py`
> 用途：做 PPT 时查阅"某个框架长什么样"，或作为内容生成的视觉参考。

## 一、分析诊断类（讲清现状/问题/原因）

| 框架 | 示例图 | 一句话 | 适用场景 |
|------|--------|--------|---------|
| 鱼骨图 Ishikawa | [fishbone.png](fishbone.png) | 问题→6M 根因 | 质量分析、复盘根因 |
| 5W2H | [5w2h.png](5w2h.png) | What/Why/Who/When/Where/How/HowMuch | 项目计划、问题梳理 |
| PESTEL | [pest.png](pest.png) | 政治/经济/社会/技术/环境/法律 | 宏观环境分析 |
| 波特五力 | [porter.png](porter.png) | 供应商/买方/替代品/新进入者/竞争 | 行业竞争分析 |
| MECE | [mece.png](mece.png) | 相互独立、完全穷尽 | 分类分析、离职归因 |
| 七步成诗 | [7step.png](7step.png) | 定义-拆解-优先-分析-综合-建议-行动 | 复杂项目复盘 |

## 二、战略规划类（讲清往哪走/怎么赢）

| 框架 | 示例图 | 一句话 | 适用场景 |
|------|--------|--------|---------|
| 业务画布 BMC | [bmc.png](bmc.png) | 9 宫格商业模式 | 新业务规划 |
| 7S 模型 | [7s.png](7s.png) | 战略/结构/制度/风格/员工/技能/价值观 | 组织诊断 |
| BCG 矩阵 | [bcg.png](bcg.png) | 明星/现金牛/问题/瘦狗 | 业务组合分析 |
| 9-Box 人才盘点 | [9box.png](9box.png) | 绩效×潜力九宫格 | 人才盘点、调配 |
| 3C 分析 | [3c.png](3c.png) | 公司/竞争者/客户 | 战略定位 |
| 黄金圈 | [goldencircle.png](goldencircle.png) | Why-How-What | 愿景传达、动员 |

## 三、说服沟通类（讲清为什么这么做）

| 框架 | 示例图 | 一句话 | 适用场景 |
|------|--------|--------|---------|
| 金字塔原理 | [pyramid.png](pyramid.png) | 结论先行，以上统下 | 所有结构化汇报 |
| SCQA | [scqa.png](scqa.png) | 情境-冲突-疑问-答案 | 申请类汇报、变革 |
| STAR | [star.png](star.png) | 情境-任务-行动-结果 | 成果复盘、绩效 |
| PREP | [prep.png](prep.png) | 观点-理由-例证-重申 | 观点表达、电梯汇报 |
| FABE | [fabe.png](fabe.png) | 特征-优势-利益-证据 | 方案推介、产品说服 |
| FIS | [fis.png](fis.png) | 事实-影响-方案 | 风险预警 |
| KISS | [kiss.png](kiss.png) | Keep It Simple | 极简表达 |

## 四、执行管理类（讲清怎么落地）

| 框架 | 示例图 | 一句话 | 适用场景 |
|------|--------|--------|---------|
| 4P 框架 | [4p.png](4p.png) | 计划-进展-问题-提案 | 进度汇报 |
| RACI | [raci.png](raci.png) | 负责/批准/咨询/知会 | 跨部门责任划分 |
| SMART | [smart.png](smart.png) | 具体/可衡量/可达成/相关/有时限 | 目标设定 |
| GROW | [grow.png](grow.png) | 目标-现状-选项-意愿 | 辅导、人才发展 |
| SWOT | [swot.png](swot.png) | 优势-劣势-机会-威胁 | 综合分析 |

## 五、营销增长类

| 框架 | 示例图 | 一句话 | 适用场景 |
|------|--------|--------|---------|
| AIDA | [aida.png](aida.png) | 注意-兴趣-欲望-行动 | 营销漏斗、活动招募 |

---

## 如何使用

1. **查阅参考**：打开对应 PNG 看框架的标准结构
2. **在 PPT 中复用**：部分框架已有对应版式（如金字塔→`pyramid_triangle`、SWOT→`swot`、鱼骨图→新增 `fishbone`），可在 outline 中指定该 layout
3. **重新生成**：修改 `scripts/generate_framework_gallery.py` 中的示例数据后重跑

## 框架→版式映射

| 框架 | 对应 layout | 状态 |
|------|------------|------|
| 金字塔原理 | pyramid_triangle | ✅ 已有 |
| SWOT | swot | ✅ 已有 |
| STAR | case_study | ✅ 已有 |
| MECE/9-Box | matrix_2x2 | ✅ 已有 |
| 黄金圈 | ecosystem_ring | ✅ 已有（同心圆） |
| 鱼骨图 | fishbone | 🆕 gallery 专用 |
| 5W2H/PEST/波特/BMC/7S/BCG/GROW/PREP/FABE/RACI/AIDA | — | 🆕 gallery 专用 HTML |

> 🆕 标记的为 gallery 专属 HTML 渲染（复杂几何在 HTML/SVG 中表现最佳）。
> 如需进入正式 PPTX deck，可为其补充 python-pptx builder。
