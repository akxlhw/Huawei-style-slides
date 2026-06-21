"""S3a: Build content.pptx.json from outline + scenario.

This builder emits the API format expected by MckEngine and gate_check_s3.py:
- executive_summary items are (num, title, description) tuples
- matrix_2x2 quadrants are (label, color_hex, description) tuples
- funnel stages are (label, count_label, pct_of_max) tuples
- timeline milestones are (label, description) tuples
- action_items actions are (title, timeline, description, owner) tuples

Data is chosen per scenario so that an allocation-plan deck does not get
polluted with recruitment-review sample numbers.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple


# ──────────────────────────────────────────────────────────────────────────────
# Scenario-specific data tables
# ──────────────────────────────────────────────────────────────────────────────


def _make_cover(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    # cover_image: None (no image), 'auto' (Tencent Hunyuan AI), or a file
    # path under assets/covers/. Override per-scenario if a cover asset exists.
    cover_image = slide.get("cover_image")
    # NOTE: auto-resolve of cover assets is available but OFF by default,
    # because MckEngine's cover() narrows the title box to 7.2" when an image
    # is present, which trips the QA text_overflow heuristic (a false positive
    # on the 44pt cover title). Enable by setting cover_image in the outline.
    # The HTML track renders bg_image cleanly without this issue.
    if scenario == "skill-report":
        return {
            "layout": "cover",
            "title": slide["title"],
            "subtitle": "研究与架构设计报告验收",
            "author": "Slide Skill Research",
            "date": "2026",
            "cover_image": cover_image,
        }
    return {
        "layout": "cover",
        "title": slide["title"],
        "subtitle": "HR 招聘调配汇报" if scenario == "allocation-plan" else "HR 数据汇报",
        "author": "HR Team",
        "date": "2026",
        "cover_image": cover_image,
    }


def _make_executive_summary(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "skill-report":
        items = [
            (1, "四层解耦架构", "内容→智能→布局→生成，每层可独立升级"),
            (2, "双通道独立生成", "PPT 可编辑性与 HTML 表现力各自最大化"),
            (3, "38 项检查清单", "前置为生成约束，实现一次生成即合规"),
        ]
        source = "Huawei Slide Skill 研究报告 · 执行摘要"
    elif scenario == "allocation-plan":
        items = [
            (1, "内部调配解决 5/8", "剩余 3 个关键岗走外部招聘"),
            (2, "平均匹配度 82%", "5 位候选人能力与发展意愿双高"),
            (3, "预计 2 周内到岗", "沟通→交接→上岗→跟踪四阶段推进"),
        ]
        source = "HRBP 评估"
    elif scenario == "channel-roi":
        items = [
            (1, "建议停投智联", "释放预算加投 BOSS 与内推"),
            (2, "内推性价比 3.6", "为当前最高效渠道"),
            (3, "BOSS 直聘性价比 1.6", "简历量大，适合中基层技术岗"),
        ]
        source = "Q3 渠道统计"
    else:  # recruitment-review
        items = [
            (1, "招聘完成率 60%", "低于目标 20 个百分点"),
            (2, "技术岗缺口最大", "缺口 30% 集中在后端/Java"),
            (3, "Q4 追赶计划已制定", "预计 12 月底前补齐"),
        ]
        source = "HR 数据平台"

    return {
        "layout": "executive_summary",
        "title": slide["title"],
        "headline": slide.get("key_point", ""),
        "items": items,
        "source": source,
    }


def _make_table_insight(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "allocation-plan":
        headers = ["阶段", "人数", "占比", "目标"]
        rows = [
            ["新增岗位需求", "8", "100%", "8"],
            ["内部可调配", "5", "62.5%", "≥50%"],
            ["外部招聘", "3", "37.5%", "≤50%"],
            ["预计 2 周内到岗", "5", "100%", "100%"],
            ["需跨部门协调", "2", "40%", "-"],
            ["需岗前培训", "3", "60%", "-"],
        ]
        insights = ["5 人可内部消化，降低外部招聘压力", "3 个外部岗位集中在稀缺技术栈", "2 人需跨部门协调，提前与负责人对齐"]
        source = "人员盘点系统 2026Q4"
    else:
        headers = ["环节", "数量", "转化率", "目标"]
        rows = [
            ["渠道曝光", "10,000", "100%", "100%"],
            ["简历投递", "1,500", "15%", "≥10%"],
            ["初筛通过", "600", "40%", "30%-50%"],
            ["面试通过", "180", "30%", "25%-40%"],
            ["Offer 接受", "144", "80%", "≥75%"],
            ["入职到岗", "130", "90%", "≥90%"],
        ]
        insights = ["简历投递转化率刚好达标", "面试通过环节低于目标，需优化面试官效率", "Offer 接受率健康"]
        source = "招聘系统 2026Q3"

    return {
        "layout": "table_insight",
        "title": slide["title"],
        "headers": headers,
        "rows": rows,
        "insights": insights,
        "source": source,
    }


def _make_funnel(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "allocation-plan":
        stages = [
            ("需求确认", "8", 1.000),
            ("内部盘点", "6", 0.750),
            ("意愿沟通", "5", 0.625),
            ("能力评估", "5", 0.625),
            ("确定调配", "5", 0.625),
        ]
        source = "调配流程"
    else:
        stages = [
            ("曝光", "10,000", 1.000),
            ("投递", "1,500", 0.150),
            ("初筛", "600", 0.060),
            ("面试", "180", 0.018),
            ("入职", "130", 0.013),
        ]
        source = "招聘系统"

    return {
        "layout": "funnel",
        "title": slide["title"],
        "stages": stages,
        "source": source,
    }


def _make_data_table(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "skill-report":
        # Two skill-report tables keyed by slide title keywords
        if "五层" in slide["title"] or "架构" in slide["title"]:
            headers = ["架构层", "映射维度", "核心职责", "关键技术"]
            rows = [
                ["应用接口层", "—", "REST API + WebSocket + CLI", "FastAPI"],
                ["内容层", "维度1", "场景识别→框架匹配→大纲", "金字塔/MECE/SCQA"],
                ["智能层", "维度4", "38项检查+评分+认知负荷", "Master Checklist"],
                ["布局层", "维度2", "12列网格+黄金比例混排", "华为 VIS"],
                ["生成层", "维度3", "python-pptx+中文排版", "MckEngine"],
            ]
            source = "V2 架构升级 · 四层→五层（新增表现层）"
        else:  # default skill-report table: Huawei color system
            headers = ["颜色名称", "Pantone", "HEX", "RGB", "使用场景"]
            rows = [
                ["华为红（主）", "185C", "#CF0A2C", "207,10,44", "标题强调·点睛"],
                ["标志黑", "426CU", "#000000", "0,0,0", "正文文字"],
                ["公司灰（深）", "432CU", "#595757", "89,87,87", "次级文字"],
                ["科技蓝", "—", "#007DFF", "0,125,255", "华为云主色·CTA"],
                ["暖橙", "—", "#FF9900", "255,153,0", "辅助强调"],
                ["暖绿", "—", "#669900", "102,153,0", "辅助强调"],
            ]
            source = "华为色彩体系标准值 · 交叉验证决议采用 #CF0A2C"
        return {
            "layout": "data_table",
            "title": slide["title"],
            "headers": headers,
            "rows": rows,
            "source": source,
        }
    if scenario == "allocation-plan":
        # Slide 3: background; Slide 5: allocation detail
        if "详表" in slide["title"] or "匹配" in slide["title"]:
            headers = ["姓名", "原岗位", "目标岗", "能力匹配", "意愿", "预计上岗"]
            rows = [
                ["张某", "后端开发 A 组", "架构师", "90%", "高", "12/25"],
                ["李某", "产品经理", "高级产品经理", "85%", "高", "12/28"],
                ["王某", "测试工程师", "测试负责人", "80%", "中", "12/30"],
                ["赵某", "运维工程师", "SRE", "78%", "高", "1/5"],
                ["孙某", "数据分析师", "数据负责人", "82%", "高", "1/8"],
            ]
            source = "人才盘点表"
        else:
            headers = ["类型", "数量", "占比", "说明"]
            rows = [
                ["业务扩张新增", "8", "100%", "Q4 新立项带来"],
                ["内部可覆盖", "5", "62.5%", "现有团队能力可迁移"],
                ["需外部招聘", "3", "37.5%", "稀缺技术栈/管理岗"],
                ["跨部门协调", "2", "25%", "需与原部门负责人对齐"],
            ]
            source = "部门需求梳理"
    elif scenario == "channel-roi":
        headers = ["渠道", "费用", "简历", "面试", "入职", "单入职成本", "性价比"]
        rows = [
            ["BOSS 直聘", "20,000", "200", "32", "10", "2,000", "1.6"],
            ["猎聘", "30,000", "80", "20", "6", "5,000", "0.8"],
            ["内推", "5,000", "30", "15", "9", "556", "3.6"],
            ["智联", "10,000", "120", "8", "0", "∞", "0"],
        ]
        source = "Q3 渠道统计"
    else:
        headers = ["渠道", "费用", "简历", "面试", "入职", "单入职成本", "性价比"]
        rows = [
            ["BOSS 直聘", "20,000", "200", "32", "10", "2,000", "1.6"],
            ["猎聘", "30,000", "80", "20", "6", "5,000", "0.8"],
            ["内推", "5,000", "30", "15", "9", "556", "3.6"],
            ["智联", "10,000", "120", "8", "0", "∞", "0"],
        ]
        source = "Q3 渠道统计"

    return {
        "layout": "data_table",
        "title": slide["title"],
        "headers": headers,
        "rows": rows,
        "source": source,
    }


def _make_matrix_2x2(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "allocation-plan":
        quadrants = [
            ("优先调配", "#CF0A2C", "张某 · 架构师\n李某 · 高级 PM"),
            ("培养储备", "#007DFF", "王某 · 测试负责人\n孙某 · 数据负责人"),
            ("快速补位", "#FCC800", "赵某 · SRE\n实习生转正"),
            ("外部招聘", "#DCDDDD", "稀缺技术栈\n高级管理岗"),
        ]
        axis_labels = {"x": "能力匹配度", "y": "发展意愿"}
    elif scenario == "channel-roi":
        quadrants = [
            ("加大投入", "#CF0A2C", "BOSS 直聘\n内推"),
            ("保持观察", "#007DFF", "猎聘"),
            ("优化后使用", "#FCC800", "校园招聘"),
            ("停投", "#DCDDDD", "智联"),
        ]
        axis_labels = {"x": "贡献度", "y": "单位成本（反向）"}
    else:
        quadrants = [
            ("立即行动", "#CF0A2C", "核心架构师\n算法负责人"),
            ("提前布局", "#007DFF", "校招 Pipeline\n高潜储备"),
            ("快速解决", "#FCC800", "实习生\n辅助岗"),
            ("暂缓/冻结", "#DCDDDD", "非关键替补"),
        ]
        axis_labels = {"x": "紧急度", "y": "影响度"}

    return {
        "layout": "matrix_2x2",
        "title": slide["title"],
        "quadrants": quadrants,
        "axis_labels": axis_labels,
        "source": "HRBP 评估",
    }


def _make_timeline(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "skill-report":
        milestones = [
            ("P0 阶段", "六周完成四层架构与中文排版引擎核心"),
            ("P1 阶段", "九周完成模板渲染与认知负荷计算器"),
            ("P2 阶段", "十周完成实时预览与缓存任务队列"),
            ("交付", "全量场景验收与文档交付"),
        ]
        source = "实施路线图 · 三阶段 P0/P1/P2"
    elif scenario == "allocation-plan":
        milestones = [
            ("W1 沟通", "与 5 名候选人一对一确认发展意愿"),
            ("W2 交接", "原岗位交接 + 新岗位 JD 对齐"),
            ("W3 上岗", "目标岗报到，导师制跟进"),
            ("W4 复盘", "30/60/90 天适应度评估"),
        ]
        source = "调配实施计划"
    elif scenario == "channel-roi":
        milestones = [
            ("10 月 W1", "停投智联，释放预算"),
            ("10 月 W2", "BOSS 加投 30%，内推激励翻倍"),
            ("11 月", "校园招聘启动，补充长期 Pipeline"),
            ("12 月", "渠道 ROI 复盘与预算再分配"),
        ]
        source = "Q4 渠道预算调整"
    else:
        milestones = [
            ("10 月 W1", "优化 JD + 开通猎聘，预计简历 +40%"),
            ("10 月 W2", "薪酬特批，Offer 接受率 +20%"),
            ("10 月 W3", "面试流程精简，周期 -5 天"),
            ("11 月 内推", "内推激励翻倍，入职 +30%"),
            ("12 月", "复盘：目标达成率评估"),
        ]
        source = "招聘计划"

    return {
        "layout": "timeline",
        "title": slide["title"],
        "milestones": milestones,
        "source": source,
    }


def _make_action_items(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "skill-report":
        actions = [
            ("中文排版引擎攻关", "P0 阶段", "CJK 字宽与标点挤压是核心差异化护城河", "架构组"),
            ("门禁自动化", "P0 阶段", "38 项检查前置为生成约束避免后期返工", "QA 组"),
            ("双通道协调器", "P1 阶段", "统一内容模型独立编译 PPT 与 HTML", "平台组"),
        ]
        source = "关键里程碑与风险 · P0 优先管控"
    elif scenario == "allocation-plan":
        actions = [
            ("不适应风险预案", "到岗后 30 天", "导师辅导 + 双向评估，必要时回退原岗", "HRBP-A"),
            ("岗位空缺预案", "交接期", "原岗位工作暂由组长承接，启动替补招聘", "部门负责人"),
            ("跨部门协调", "本周", "与 2 位原部门负责人确认放人条件", "HRD"),
        ]
        source = "风险应对"
    elif scenario == "channel-roi":
        actions = [
            ("停投智联", "第 1 周", "下架所有在招职位，释放 1 万元预算", "招聘组"),
            ("BOSS 加投", "第 1-2 周", "增加 30% 曝光，重点技术岗", "招聘组"),
            ("内推激励翻倍", "11 月", "推荐奖金提升，入职 +30%", "HRBP-A"),
        ]
        source = "行动计划"
    else:
        actions = [
            ("优化 JD", "第 1 周", "覆盖 Spring Cloud 等热词", "HRBP-A"),
            ("薪酬特批", "第 1-2 周", "技术岗调薪至 75 分位", "HRD"),
            ("面试精简", "第 2 周", "4 轮 → 3 轮", "招聘组"),
        ]
        source = "行动计划"

    return {
        "layout": "action_items",
        "title": slide["title"],
        "actions": actions,
        "source": source,
    }


def _make_closing(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    return {
        "layout": "closing",
        "title": slide["title"],
        "message": "期待进一步交流",
    }


# ──────────────────────────────────────────────────────────────────────────────
# Rich-chart builders (V2 — backed by MckEngine chart methods)
# These emit the API format expected by pptx_renderer + gate_check_s3.
# Each builder pulls scenario-specific data; unknown scenarios get a neutral
# fallback so every slide type stays usable across all HR scenarios.
# ──────────────────────────────────────────────────────────────────────────────

# Color tokens reused across charts (must stay in sync with huawei_theme.py)
C_RED = "#CF0A2C"
C_BLUE = "#007DFF"
C_GREEN = "#669900"
C_ORANGE = "#FF9900"
C_YELLOW = "#FCC800"
C_ICTBLUE = "#30B5C5"
C_GRAY = "#DCDDDD"
C_DARKGRAY = "#595757"


def _make_big_number(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "skill-report":
        return {
            "layout": "big_number",
            "title": slide["title"],
            "number": "200+",
            "unit": "信息源 · 5 Agent 并行交叉验证",
            "description": "调研覆盖汇报框架理论、华为视觉规范、PPT 布局算法与开源工具、内容优化与评估理论四大维度，产出 9 份研究文件后整合为综合报告。",
            "detail_items": [
                "5 个 Agent 并行深度研究，覆盖 200+ 信息源",
                "四大维度交叉验证，9 份研究文件整合",
                "提炼 38 项可自动化检查清单与 4 维度评分体系",
            ],
            "source": "Huawei Slide Skill 研究报告 · 维度 1-4",
        }
    return {
        "layout": "big_number",
        "title": slide["title"],
        "number": slide.get("key_point", "核心指标") or "—",
        "unit": "",
        "description": "关键业务指标及其业务含义说明，支撑本页核心结论。",
        "source": "HR 数据平台",
    }


def _make_three_stat(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "skill-report":
        stats = [
            ("44pt", "H0 封面标题字号", True),
            ("32pt", "H1 页面标题字号", False),
            ("18pt", "Body 正文字号下限", False),
        ]
        detail = "标题字号 ≥ 正文的 1.5 倍；同级标题字号差异 ≥ 4pt 才能形成有效视觉区分。"
        source = "华为 VIS 字号层级体系"
    else:
        stats = [
            ("85%", "完成率", True),
            ("60天", "平均周期", False),
            ("1.6", "渠道性价比", False),
        ]
        detail = "三组关键指标对比，红色为首要关注项。"
        source = "HR 数据平台"
    return {
        "layout": "three_stat",
        "title": slide["title"],
        "stats": stats,
        "detail_items": [detail],
        "source": source,
    }


def _make_metric_cards(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "skill-report":
        cards = [
            ("双", "双通道生成", "PPT 可编辑，HTML 强表现", C_RED, "#FCE8EA"),
            ("图", "图标匹配", "框架→图形级联规则化", C_BLUE, "#E6F0FF"),
            ("中", "中文排版", "CJK 字宽与标点挤压", C_GREEN, "#EEF6E0"),
            ("层", "新增表现层", "四层升级为五层架构", C_ORANGE, "#FFF3E0"),
        ]
        source = "V2 架构升级 · 新增能力总览"
    else:
        cards = [
            ("人", "到岗", "本周期实际到岗人数", C_RED, "#FCE8EA"),
            ("岗", "缺口", "尚未补齐的岗位数", C_ORANGE, "#FFF3E0"),
            ("率", "完成率", "到岗/需求的比率", C_BLUE, "#E6F0FF"),
            ("天", "周期", "平均招聘周期", C_GREEN, "#EEF6E0"),
        ]
        source = "HR 招聘指标"
    return {
        "layout": "metric_cards",
        "title": slide["title"],
        "cards": cards,
        "source": source,
    }


def _make_grouped_bar(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "skill-report":
        # 10 场景 × 时长（分钟）—— 2 系列对比（grouped_bar legend overflows
        # with 3 series, so cap at 2): 典型时长 vs 推荐页数(归一到分钟).
        return {
            "layout": "grouped_bar",
            "title": slide["title"],
            "categories": ["电梯", "概要", "进度", "风险", "述职"],
            "series": [("典型时长min", C_RED), ("推荐页数", C_BLUE)],
            "data": [
                [1, 3],
                [8, 8],
                [12, 10],
                [8, 8],
                [18, 12],
            ],
            "y_ticks": [0, 5, 10, 15, 20],
            "summary": ("规律", "时长越长页数越多，框架从 PREP 演进到 BSBRP"),
            "source": "场景-框架-页面路由表 · 10 场景映射",
        }
    return {
        "layout": "grouped_bar",
        "title": slide["title"],
        "categories": ["BOSS", "猎聘", "内推", "智联"],
        "series": [("简历", C_BLUE), ("面试", C_RED), ("入职", C_GREEN)],
        "data": [[200, 32, 10], [80, 20, 6], [30, 15, 9], [120, 8, 0]],
        "y_ticks": [0, 50, 100, 150, 200],
        "summary": ("结论", "内推入职转化率最高，智联零产出"),
        "source": "Q3 渠道统计",
    }


def _make_horizontal_bar(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "skill-report":
        # 双通道能力胜出分布（PPT vs HTML vs 平手），用占比表达
        return {
            "layout": "horizontal_bar",
            "title": slide["title"],
            "items": [
                ("PPT 通道胜出维度", 40, C_RED),
                ("HTML 通道胜出维度", 45, C_BLUE),
                ("双方势均力敌维度", 15, C_GRAY),
            ],
            "summary": ("洞察", "PPT 强在编辑/离线/打印，HTML 强在交互/响应式/分享"),
            "source": "V2 双通道能力对比矩阵 · 25+ 维度",
        }
    return {
        "layout": "horizontal_bar",
        "title": slide["title"],
        "items": [
            ("BOSS 直聘", 80, C_RED),
            ("内推", 60, C_BLUE),
            ("猎聘", 40, C_ORANGE),
            ("智联", 10, C_GRAY),
        ],
        "summary": ("性价比", "内推性价比 3.6 居首，智联为 0"),
        "source": "Q3 渠道 ROI",
    }


def _make_donut_chart(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "skill-report":
        # 38 项检查清单三类占比：CS 结论/ID 信息密度/LJ 逻辑
        return {
            "layout": "donut_chart",
            "title": slide["title"],
            "segments": [
                (0.34, C_RED, "CS 结论质量 13 项"),
                (0.32, C_BLUE, "ID 信息密度 12 项"),
                (0.34, C_ORANGE, "LJ 逻辑跳跃 13 项"),
            ],
            "center_label": "38",
            "center_sub": "检查项",
            "summary": "前置为生成约束即可实现一次生成即合规",
            "source": "Master Checklist · 38 项可自动化检查",
        }
    return {
        "layout": "donut_chart",
        "title": slide["title"],
        "segments": [
            (0.50, C_RED, "技术岗缺口"),
            (0.30, C_BLUE, "产品岗缺口"),
            (0.20, C_ORANGE, "其他岗位"),
        ],
        "center_label": "30%",
        "center_sub": "缺口率",
        "summary": "技术岗是主要招聘瓶颈",
        "source": "招聘缺口分析",
    }


def _make_kpi_tracker(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "skill-report":
        # 认知负荷预算达成度（各页型字数/图表上限的合规比例）
        return {
            "layout": "kpi_tracker",
            "title": slide["title"],
            "kpis": [
                ("封面页字数 ≤15", 1.0, "封面页负荷上限 30，字数 15", "on"),
                ("内容单论点 ≤50字", 0.85, "单页字数 50，上限 50", "on"),
                ("数据页图表 ≤2", 0.90, "数据页图表数 2，上限 2", "on"),
                ("内容多论点 ≤80字", 0.70, "卡片页字数偏多，接近上限", "risk"),
                ("总结页强调 ≤3", 0.60, "总结页信号数 3，已达上限", "risk"),
            ],
            "summary": "认知负荷预算为信息密度控制提供科学量化基础",
            "source": "认知负荷预算模型 · 页型参数表",
        }
    return {
        "layout": "kpi_tracker",
        "title": slide["title"],
        "kpis": [
            ("招聘完成率", 0.60, "目标 80%，实际 60%", "risk"),
            ("Offer 接受率", 0.80, "目标 75%，实际 80%", "on"),
            ("到岗率", 0.90, "目标 90%，实际 90%", "on"),
        ],
        "summary": "完成率是当前首要短板",
        "source": "招聘 KPI 看板",
    }


def _make_pyramid_steps(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "skill-report":
        # MckEngine pyramid (staircase) overflows the right edge at 4 levels;
        # the pyramid principle has exactly three sub-structures, so 3 levels
        # is both accurate and geometry-safe.
        return {
            "layout": "pyramid_steps",
            "title": slide["title"],
            "levels": [
                ("纵向结构", "疑问回答式对话，自上而下吸引注意", "纵"),
                ("横向结构", "演绎或归纳推理，遵循 MECE 原则", "横"),
                ("序言结构", "SCQA 框架引出读者最初的疑问", "序"),
            ],
            "source": "金字塔原理 · 三大子结构",
        }
    return {
        "layout": "pyramid_steps",
        "title": slide["title"],
        "levels": [
            ("需求确认", "明确岗位与编制", "1"),
            ("渠道投放", "多渠道并行寻访", "2"),
            ("面试评估", "结构化面试筛选", "3"),
            ("Offer 到岗", "薪酬谈判与入职", "4"),
        ],
        "source": "招聘全流程",
    }


def _make_four_column(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    """Four-Column Overview — used for the four-layer decoupled architecture.

    Note: pyramid/staircase overflows the right edge when there are 4 levels,
    so the report deck uses four_column (CW-based geometry, safe) for the
    four-layer architecture slide.
    """
    if scenario == "skill-report":
        return {
            "layout": "four_column",
            "title": slide["title"],
            "items": [
                (1, "内容层", ["场景识别", "框架匹配", "大纲生成", "文案撰写"]),
                (2, "智能层", ["38 项检查", "视觉评估", "合规校验", "认知负荷"]),
                (3, "布局层", ["12 列网格", "视觉层级", "黄金比例", "拥挤检测"]),
                (4, "生成层", ["python-pptx", "中文排版", "图表生成", "资源管理"]),
            ],
            "source": "四层解耦架构 · 内容→智能→布局→生成",
        }
    return {
        "layout": "four_column",
        "title": slide["title"],
        "items": [
            (1, "需求", "明确岗位与编制"),
            (2, "寻访", "多渠道并行触达"),
            (3, "评估", "结构化面试筛选"),
            (4, "到岗", "薪酬谈判与入职"),
        ],
        "source": "招聘全流程",
    }


def _make_scorecard(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "skill-report":
        return {
            "layout": "scorecard",
            "title": slide["title"],
            "items": [
                ("内容结构 35%", "★★★★★", 0.95),
                ("视觉设计 30%", "★★★★☆", 0.85),
                ("华为合规 25%", "★★★★★", 0.90),
                ("数据呈现 10%", "★★★★☆", 0.80),
            ],
            "source": "4 维度评分体系 · 内容35/视觉30/合规25/数据10",
        }
    return {
        "layout": "scorecard",
        "title": slide["title"],
        "items": [
            ("招聘速度", "★★★★", 0.75),
            ("渠道质量", "★★★", 0.55),
            ("候选人体验", "★★★★", 0.80),
        ],
        "source": "招聘质量评分",
    }


def _make_checklist_status(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "skill-report":
        return {
            "layout": "checklist_status",
            "title": slide["title"],
            "columns": ["页面类型", "推荐布局", "华为红占比", "留白要求", "状态"],
            "col_widths": [2.4, 3.2, 2.2, 2.2, 1.733],
            "rows": [
                ("封面页", "全幅背景+居中大标题", "≤5%", "≥40%", "done"),
                ("目录页", "左右/上下列表", "≤5%", "≥35%", "done"),
                ("过渡页", "大编号+标题+留白", "编号可用红", "60-70%", "done"),
                ("内容单论点", "标题+核心结论+支撑", "≤8%", "≥25%", "active"),
                ("数据页", "标题+核心数据+图表", "≤10%", "≥20%", "active"),
                ("总结页", "标题+3-5结论", "≤8%", "≥30%", "pending"),
            ],
            "source": "7 类页面标准结构 · 页面类型-布局映射矩阵",
        }
    return {
        "layout": "checklist_status",
        "title": slide["title"],
        "columns": ["岗位", "状态", "负责人", "预计到岗", "进展"],
        "col_widths": [3.0, 2.5, 2.5, 2.5, 1.233],
        "rows": [
            ("架构师", "面试中", "HRBP-A", "12/25", "active"),
            ("产品经理", "已 Offer", "HRBP-B", "12/28", "done"),
            ("测试工程师", "寻访中", "HRBP-A", "1/5", "pending"),
        ],
        "source": "招聘进展看板",
    }


def _make_value_chain(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "skill-report":
        return {
            "layout": "value_chain",
            "title": slide["title"],
            "stages": [
                ("生成", "LLM 按框架与约束产出大纲与文案", C_RED),
                ("评估", "38 项检查 + 4 维度评分 + 认知负荷", C_BLUE),
                ("优化", "诊断报告驱动 P0/P1/P2 修复", C_GREEN),
                ("交付", "通过门禁后输出 PPTX/HTML", C_ORANGE),
            ],
            "source": "跨维度洞察 1 · 生成-评估-优化闭环",
        }
    return {
        "layout": "value_chain",
        "title": slide["title"],
        "stages": [
            ("需求", "梳理岗位需求", C_RED),
            ("寻访", "多渠道触达", C_BLUE),
            ("评估", "面试筛选", C_GREEN),
            ("到岗", "Offer 与入职", C_ORANGE),
        ],
        "source": "招聘价值链",
    }


def _make_swot(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "skill-report":
        return {
            "layout": "swot",
            "title": slide["title"],
            "quadrants": [
                ("PPT 通道优势", C_RED, "#FCE8EA",
                 ["100% 兼容 Office，可二次编辑", "完全离线可用，企业内网友好", "原生打印讲义与审阅批注"]),
                ("PPT 通道劣势", C_ORANGE, "#FFF3E0",
                 ["固定尺寸，无响应式", "交互动效有限", "中文字体依赖系统安装"]),
                ("HTML 通道优势", C_BLUE, "#E6F0FF",
                 ["响应式自适应多终端", "ECharts/D3 全功能交互图表", "URL 在线分享，Git 原生版本控制"]),
                ("HTML 通道劣势", C_GRAY, "#F5F5F5",
                 ["客户无法逐行编辑文字", "Web 字体体积大", "离线需部署静态文件"]),
            ],
            "source": "双通道能力对比矩阵 · 25+ 维度",
        }
    return {
        "layout": "swot",
        "title": slide["title"],
        "quadrants": [
            ("内部优势", C_RED, "#FCE8EA", ["雇主品牌强", "薪酬有竞争力"]),
            ("内部劣势", C_ORANGE, "#FFF3E0", ["技术岗品牌弱", "流程偏长"]),
            ("外部机会", C_BLUE, "#E6F0FF", ["行业人才流动", "远程办公普及"]),
            ("外部威胁", C_GRAY, "#F5F5F5", ["竞品挖角", "薪酬通胀"]),
        ],
        "source": "招聘 SWOT 分析",
    }


def _make_icon_grid(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "skill-report":
        return {
            "layout": "icon_grid",
            "title": slide["title"],
            "items": [
                ("Phosphor", "Bold 风格为主，线条几何感强，推荐主力库", C_RED),
                ("Tabler", "补充稀缺图标，风格统一覆盖广", C_BLUE),
                ("Lucide", "Feather 衍生，轻量线性适合正文", C_GREEN),
                ("Heroicons", "Tailwind 官方，适合 Web 场景", C_ORANGE),
                ("Remix", "双色填充可选，表现力强", C_ICTBLUE),
                ("Material", "Google 标准，兼容性好", C_YELLOW),
            ],
            "source": "8 大图标库评估矩阵 · 推荐 Phosphor Bold + Tabler 补充",
        }
    return {
        "layout": "icon_grid",
        "title": slide["title"],
        "items": [
            ("到岗", "实际入职人数", C_RED),
            ("周期", "平均招聘天数", C_BLUE),
            ("成本", "单入职成本", C_GREEN),
            ("质量", "试用期留存率", C_ORANGE),
        ],
        "source": "招聘核心指标",
    }


def _make_quote(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    if scenario == "skill-report":
        text = "将 38 项检查清单中的大部分规则在生成阶段作为硬约束直接嵌入，实现一次生成即合规，而非生成-检查-修复的多轮循环。"
        attribution = "约束即生成范式 · 跨维度洞察 3"
    else:
        text = "结论先行，一页一个核心信息，标题应是结论性陈述而非话题标签。"
        attribution = "金字塔原理 · Action Title 规则"
    # quote() has no title/source params in MckEngine; we carry title/source in
    # content.json so the S3 gate (which requires a non-empty source on content
    # slides) passes, and the HTML track can render them.
    return {
        "layout": "quote",
        "title": slide["title"],
        "quote_text": text,
        "attribution": attribution,
        "source": "约束即生成范式 · 跨维度洞察 3",
    }


# ──────────────────────────────────────────────────────────────────────────────
# SmartArt-style logic-diagram builders (V2+) — express frameworks as diagrams
# rather than text. These map report frameworks onto MckEngine logic shapes:
#   cycle          → closed loop (生成-评估-优化-交付)
#   side_by_side   → left/right comparison (四层→五层演进)
#   case_study     → SAR narrative (双通道案例)
#   decision_tree  → scenario→framework routing tree
# ──────────────────────────────────────────────────────────────────────────────


def _make_cycle(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    """Closed-loop cycle diagram."""
    if scenario == "skill-report":
        # 4 nodes compressed to x=1-7" so they don't collide with the right
        # panel (which MckEngine places at x≈8.5-12.5").
        phases = [
            ("生成", 1.0, 3.2),
            ("评估", 3.0, 3.2),
            ("优化", 5.0, 3.2),
            ("交付", 7.0, 3.2),
        ]
        right_panel = ("闭环洞察", ["四个维度无缝组合", "无需额外粘合层", "理论体系自然支撑"])
        source = "跨维度洞察 1 · 生成-评估-优化闭环"
    else:
        phases = [("需求", 1.0, 3.2), ("寻访", 4.0, 3.2), ("评估", 7.0, 3.2), ("到岗", 10.0, 3.2)]
        right_panel = ("流程", ["招聘全流程闭环"])
        source = "招聘流程"
    return {"layout": "cycle", "title": slide["title"], "phases": phases,
            "right_panel": right_panel, "source": source}


def _make_side_by_side(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    """Left/right two-column comparison."""
    if scenario == "skill-report":
        # Two distinct comparisons keyed by slide title.
        title = slide.get("title", "")
        if "约束" in title or "生成" in title or "范式" in title:
            options = [
                ("传统做法", ["先生成 PPT 内容", "再走检查-修复循环", "多轮迭代返工", "合规靠人工把关"]),
                ("约束即生成", ["38 项检查前置为硬约束", "嵌入 System Prompt", "Pydantic 校验结构", "一次生成即合规"]),
            ]
            source = "跨维度洞察 3 · 约束即生成范式"
        else:  # default: architecture evolution 四层→五层
            options = [
                ("V1 四层架构", ["内容层 · 维度1", "智能层 · 维度4", "布局层 · 维度2", "生成层 · 维度3"]),
                ("V2 五层架构", ["新增表现层", "双通道独立生成", "图标 SmartArt 匹配", "中文排版引擎强化"]),
            ]
            source = "V2 架构升级 · 四层→五层（新增表现层）"
    else:
        options = [
            ("现状", ["完成率偏低", "渠道单一"]),
            ("目标", ["完成率达标", "渠道多元化"]),
        ]
        source = "现状与目标对比"
    return {"layout": "side_by_side", "title": slide["title"],
            "options": options, "source": source}


def _make_case_study(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    """SAR-style narrative sections (Situation-Action-Result)."""
    if scenario == "skill-report":
        sections = [
            ("S", "情境", "PPT 与 HTML 面向两个完全不同的使用场景与生态"),
            ("A", "行动", "统一内容抽象层，同一模型独立编译为两种格式"),
            ("R", "结果", "各自发挥最大优势，HTML 不再是 PPT 的劣化副本"),
        ]
        result_box = ("核心结论", "双通道独立生成优于转换生成")
        source = "V2 双通道设计哲学 · 为两个世界设计"
    else:
        sections = [
            ("S", "情境", "某关键岗位长期空缺"),
            ("A", "行动", "启动内推激励与猎头并行"),
            ("R", "结果", "两周内成功到岗"),
        ]
        result_box = ("成效", "招聘周期缩短")
        source = "招聘案例"
    return {"layout": "case_study", "title": slide["title"],
            "sections": sections, "result_box": result_box, "source": source}


def _make_decision_tree(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    """Scenario→framework routing decision tree."""
    if scenario == "skill-report":
        root = ("汇报场景",)
        branches = [
            ("进度类", "4P", C_RED, [("Plan", "计划"), ("Problem", "问题")]),
            ("风险类", "FIS", C_BLUE, [("Fact", "事实"), ("Solution", "方案")]),
            ("评审类", "BSBRP", C_GREEN, [("背景", "方案"), ("计划", "时间")]),
        ]
        right_panel = ("路由规则", ["10 场景→8 框架", "7 页型标准布局", "规则化可预测"])
        source = "知识图谱 · 场景-框架-页面路由表"
    else:
        root = ("招聘决策",)
        branches = [
            ("内部调配", "优先", C_RED, [("能力匹配", "高"), ("意愿", "强")]),
            ("外部招聘", "补充", C_BLUE, [("稀缺岗", "是"), ("紧急度", "高")]),
        ]
        right_panel = ("决策", ["能力×意愿矩阵"])
        source = "招聘决策树"
    return {"layout": "decision_tree", "title": slide["title"], "root": root,
            "branches": branches, "right_panel": right_panel, "source": source}


def _make_ecosystem_ring(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    """Concentric-ring ecosystem/architecture diagram (Huawei signature shape).

    PPTX track falls back to value_chain rendering (the ring is an HTML-native
    SVG shape); the HTML track renders the true concentric ring. Data model:
      rings: list of {label, color, items:[...]}  outer→inner
      center: {label, sub}
      side_cards: list of (title, color, desc) shown beside the ring
    """
    if scenario == "skill-report":
        return {
            "layout": "ecosystem_ring",
            "title": slide["title"],
            "rings": [
                {"label": "生成层", "color": C_GRAY, "items": ["python-pptx", "资源管理"]},
                {"label": "布局层", "color": C_YELLOW, "items": ["12 列网格", "黄金比例"]},
                {"label": "智能层", "color": C_BLUE, "items": ["38 项检查", "认知负荷"]},
                {"label": "内容层", "color": C_GREEN, "items": ["场景识别", "大纲生成"]},
            ],
            "center": {"label": "Skill", "sub": "内核"},
            "side_cards": [
                ("可独立升级", C_RED, "更换 LLM 不影响布局层"),
                ("约束即生成", C_BLUE, "38 项检查前置为硬约束"),
                ("双通道输出", C_GREEN, "PPT 与 HTML 各自最优"),
            ],
            "source": "四层解耦架构 · 同心圆表达层间关系",
        }
    return {
        "layout": "ecosystem_ring",
        "title": slide["title"],
        "rings": [
            {"label": "到岗", "color": C_GRAY, "items": ["Offer", "入职"]},
            {"label": "评估", "color": C_YELLOW, "items": ["面试", "筛选"]},
            {"label": "寻访", "color": C_BLUE, "items": ["多渠道", "触达"]},
            {"label": "需求", "color": C_GREEN, "items": ["岗位", "编制"]},
        ],
        "center": {"label": "招聘", "sub": "闭环"},
        "side_cards": [
            ("高效", C_RED, "缩短招聘周期"),
            ("精准", C_BLUE, "人岗匹配"),
            ("低成本", C_GREEN, "优化渠道 ROI"),
        ],
        "source": "招聘全流程闭环",
    }


# ──────────────────────────────────────────────────────────────────────────────
# Additional Huawei chart layouts (iteration round 2)
# harvey_ball_compare / swim_lane / pyramid_triangle / radar_chart /
# gantt_chart / icon_stat_grid
# ──────────────────────────────────────────────────────────────────────────────


def _make_harvey_ball_compare(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    """Harvey-ball comparison matrix (reuses MckEngine harvey_ball_table)."""
    if scenario == "skill-report":
        return {
            "layout": "harvey_ball_compare",
            "title": slide["title"],
            "criteria": ["可编辑性", "交互表现", "中文排版", "离线可用", "版本控制"],
            "options": ["PPT 通道", "HTML 通道"],
            "scores": [[4, 2], [1, 4], [4, 2], [4, 1], [1, 4]],
            "legend_text": ["● 满 = 完全支持", "◐ 半 = 部分支持", "○ 空 = 不支持"],
            "summary": "PPT 强编辑与离线，HTML 强交互与版本控制，按场景选择",
            "source": "双通道能力对比 · Harvey Ball 评估矩阵",
        }
    return {
        "layout": "harvey_ball_compare",
        "title": slide["title"],
        "criteria": ["成本", "速度", "质量", "覆盖"],
        "options": ["BOSS", "内推", "猎聘"],
        "scores": [[3, 4, 1], [3, 4, 2], [2, 3, 3], [4, 2, 3]],
        "legend_text": ["● 满", "◐ 半", "○ 空"],
        "summary": "内推综合最优",
        "source": "渠道评估矩阵",
    }


def _make_swim_lane(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    """Swim-lane flowchart: lanes (rows) × phases (columns)."""
    if scenario == "skill-report":
        return {
            "layout": "swim_lane",
            "title": slide["title"],
            "lanes": ["内容层", "智能层", "布局层", "生成层"],
            "phases": ["输入", "处理", "输出"],
            "steps": [
                # (lane_idx, phase_idx, label)
                (0, 0, "场景识别"), (0, 1, "框架匹配"), (0, 2, "大纲生成"),
                (1, 0, "约束解析"), (1, 1, "检查评估"), (1, 2, "诊断报告"),
                (2, 0, "网格计算"), (2, 1, "布局选择"), (2, 2, "黄金比例"),
                (3, 0, "PPTX 渲染"), (3, 1, "中文排版"), (3, 2, "HTML 渲染"),
            ],
            "source": "四层架构数据流 · 泳道流程图",
        }
    return {
        "layout": "swim_lane",
        "title": slide["title"],
        "lanes": ["HRBP", "用人部门", "候选人"],
        "phases": ["需求", "面试", "Offer"],
        "steps": [(0,0,"JD确认"),(0,1,"安排面试"),(0,2,"谈薪"),
                  (1,0,"编制审批"),(1,1,"技术面试"),(1,2,"审批"),
                  (2,0,"投递"),(2,1,"参加面试"),(2,2,"接受Offer")],
        "source": "招聘协作流程",
    }


def _make_pyramid_triangle(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    """True triangular pyramid (stacked centered decreasing-width trapezoids)."""
    if scenario == "skill-report":
        return {
            "layout": "pyramid_triangle",
            "title": slide["title"],
            "levels": [
                ("顶层结论", "一句话核心论点（封面/Action Title）", C_RED),
                ("一级论据", "3-5 个主要支撑（目录页）", C_ORANGE),
                ("二级论据", "数据/案例/引用（内容页）", C_YELLOW),
                ("基础事实", "详细数据与方法论（附录）", C_GREEN),
            ],
            "source": "金字塔原理 · 结论先行以上统下",
        }
    return {
        "layout": "pyramid_triangle",
        "title": slide["title"],
        "levels": [("战略", "人才战略规划", C_RED), ("战术", "年度招聘计划", C_ORANGE),
                   ("执行", "月度招聘动作", C_YELLOW), ("基础", "日常寻访", C_GREEN)],
        "source": "招聘目标金字塔",
    }


def _make_radar_chart(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    """Radar/spider chart for multi-dimension comparison."""
    if scenario == "skill-report":
        return {
            "layout": "radar_chart",
            "title": slide["title"],
            "axes": ["内容结构", "视觉设计", "华为合规", "数据呈现", "可读性", "交互性"],
            "series": [
                {"name": "PPT 通道", "color": C_RED, "values": [95, 80, 92, 85, 88, 40]},
                {"name": "HTML 通道", "color": C_BLUE, "values": [80, 92, 85, 78, 82, 95]},
            ],
            "source": "双通道六维度雷达对比 · 4 维度评分扩展",
        }
    return {
        "layout": "radar_chart",
        "title": slide["title"],
        "axes": ["速度", "成本", "质量", "覆盖", "留存"],
        "series": [{"name": "内推", "color": C_RED, "values": [85, 92, 88, 70, 90]},
                   {"name": "BOSS", "color": C_BLUE, "values": [70, 60, 75, 95, 80]}],
        "source": "渠道五维雷达",
    }


def _make_gantt_chart(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    """Gantt chart: tasks with start/end across a time axis."""
    if scenario == "skill-report":
        return {
            "layout": "gantt_chart",
            "title": slide["title"],
            "phases": ["W1-2", "W3-4", "W5-6", "W7-8", "W9-10"],
            "tasks": [
                ("四层架构核心", 0, 3, C_RED),
                ("中文排版引擎", 1, 4, C_BLUE),
                ("38 项检查自动化", 2, 4, C_GREEN),
                ("模板渲染引擎", 3, 5, C_ORANGE),
                ("认知负荷计算器", 4, 5, C_YELLOW),
            ],
            "source": "实施路线图 P0/P1 · 甘特图",
        }
    return {
        "layout": "gantt_chart",
        "title": slide["title"],
        "phases": ["W1", "W2", "W3", "W4"],
        "tasks": [("JD 优化", 0, 1, C_RED), ("渠道投放", 1, 3, C_BLUE),
                  ("面试评估", 2, 3, C_GREEN), ("Offer 发放", 3, 4, C_ORANGE)],
        "source": "招聘计划甘特图",
    }


def _make_icon_stat_grid(slide: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    """Icon + big-number grid (combines icon_grid visual with big stats)."""
    if scenario == "skill-report":
        return {
            "layout": "icon_stat_grid",
            "title": slide["title"],
            "items": [
                ("38", "项检查清单", "覆盖内容与逻辑质量", C_RED),
                ("4", "层解耦架构", "每层可独立升级", C_BLUE),
                ("2", "条生成通道", "PPT 与 HTML 各自最优", C_GREEN),
                ("25", "维双通道对比", "按场景选择最优通道", C_ORANGE),
                ("10", "种汇报场景", "差异化框架与页面预算", C_YELLOW),
                ("5", "Agent 并行", "200+ 信息源交叉验证", C_ICTBLUE),
            ],
            "source": "Skill 核心数据总览 · 图标数字网格",
        }
    return {
        "layout": "icon_stat_grid",
        "title": slide["title"],
        "items": [("85%", "完成率", "本季度达成", C_RED), ("60天", "周期", "平均到岗", C_BLUE),
                  ("1.6", "性价比", "渠道最高", C_GREEN), ("30%", "缺口", "技术岗为主", C_ORANGE)],
        "source": "招聘核心指标",
    }


BUILDERS = {
    "cover": _make_cover,
    "executive_summary": _make_executive_summary,
    "table_insight": _make_table_insight,
    "funnel": _make_funnel,
    "data_table": _make_data_table,
    "matrix_2x2": _make_matrix_2x2,
    "timeline": _make_timeline,
    "action_items": _make_action_items,
    "closing": _make_closing,
    # V2 rich-chart layouts
    "big_number": _make_big_number,
    "three_stat": _make_three_stat,
    "metric_cards": _make_metric_cards,
    "grouped_bar": _make_grouped_bar,
    "horizontal_bar": _make_horizontal_bar,
    "donut_chart": _make_donut_chart,
    "kpi_tracker": _make_kpi_tracker,
    "pyramid_steps": _make_pyramid_steps,
    "four_column": _make_four_column,
    "scorecard": _make_scorecard,
    "checklist_status": _make_checklist_status,
    "value_chain": _make_value_chain,
    "swot": _make_swot,
    "icon_grid": _make_icon_grid,
    "quote": _make_quote,
    # SmartArt-style logic diagrams (V2+)
    "cycle": _make_cycle,
    "side_by_side": _make_side_by_side,
    "case_study": _make_case_study,
    "decision_tree": _make_decision_tree,
    "ecosystem_ring": _make_ecosystem_ring,
    # Additional Huawei chart layouts (iteration round 2)
    "harvey_ball_compare": _make_harvey_ball_compare,
    "swim_lane": _make_swim_lane,
    "pyramid_triangle": _make_pyramid_triangle,
    "radar_chart": _make_radar_chart,
    "gantt_chart": _make_gantt_chart,
    "icon_stat_grid": _make_icon_stat_grid,
    # Framework-gallery layouts (12) — registered so outlines can reference
    # them. PPTX renders via icon_grid fallback; HTML uses gallery templates.
    "fishbone": _make_icon_grid,
    "five_w2h": _make_icon_grid,
    "pest_grid": _make_icon_grid,
    "porter_five": _make_icon_grid,
    "bmc_canvas": _make_icon_grid,
    "mckinsey_7s": _make_icon_grid,
    "bcg_matrix": _make_icon_grid,
    "grow_model": _make_icon_grid,
    "prep_model": _make_icon_grid,
    "fabe_model": _make_icon_grid,
    "raci_matrix": _make_icon_grid,
    "aida_funnel": _make_icon_grid,
}


def build_pptx_content(
    outline: Dict[str, Any],
    output_dir: Path,
    content_source: str = "sample",
) -> Dict[str, Any]:
    """Build content.pptx.json.

    content_source modes:
      - 'sample' (default): use the hardcoded per-scenario _make_* builders.
      - 'agent': write a content_prompt.md (outline + data contracts) for a
        Code Agent to fill; returns a minimal placeholder content so the rest
        of the pipeline can proceed with sample data.
      - 'file': read an already-filled content.pptx.json (produced by an agent
        from the prompt) and return it as-is.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    scenario = outline.get("scenario", "recruitment-review")

    # --- agent mode: emit the prompt for an external Code Agent to fill ---
    if content_source == "agent":
        prompt_path = _write_agent_prompt(outline, output_dir)
        # If an LLM API key is configured, auto-fill content immediately.
        filled = _try_llm_autofill(prompt_path, output_dir)
        if filled:
            return filled
        # No key / fill failed → fall through to sample so a deck still renders.

    # --- file mode: load an agent-filled content.json ---
    if content_source == "file":
        path = output_dir / "content.pptx.json"
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
        # No filled file yet → fall back to sample.

    # --- sample mode (and the fallback for the other two) ---
    total = len(outline["slides"])
    slides: List[Dict[str, Any]] = []
    for i, slide in enumerate(outline["slides"]):
        layout = slide["layout"]
        # If the slide YAML carries a full `data` block, use it directly — this
        # externalizes per-slide content so new scenarios need no code change.
        if isinstance(slide.get("data"), dict):
            data = dict(slide["data"])
            data.setdefault("layout", layout)
        else:
            builder = BUILDERS.get(layout)
            if not builder:
                raise ValueError(f"Unsupported PPTX layout: {layout}")
            data = builder(slide, scenario)
        data["idx"] = slide["idx"]
        data["key_point"] = slide.get("key_point", "")
        slides.append(data)

    # Chapter metadata for the Huawei left-nav rail (mirrors the HTML track).
    # Imported lazily to avoid a circular import at module load.
    try:
        from html_content_builder import _SCENARIO_CHAPTERS, _chapter_for
        chapters = _SCENARIO_CHAPTERS.get(scenario, [])
        for i, sl in enumerate(slides):
            sl["chapter"] = _chapter_for(scenario, i + 1, total)
    except Exception:
        chapters = []

    content = {
        "brief": outline["brief"],
        "framework": outline.get("framework", "pyramid"),
        "scenario": scenario,
        "chapters": chapters,
        "slides": slides,
    }

    path = output_dir / "content.pptx.json"
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    return content


def _write_agent_prompt(outline: Dict[str, Any], output_dir: Path) -> Path:
    """Write content_prompt.md: the data contracts + this deck's outline, so a
    Code Agent can read it, call its host LLM, and fill content.pptx.json."""
    prompt_path = Path(__file__).resolve().parent / "prompts" / "content_filler.md"
    contract = prompt_path.read_text(encoding="utf-8") if prompt_path.is_file() else ""
    scenario = outline.get("scenario", "")
    outline_json = json.dumps(outline, ensure_ascii=False, indent=2)
    doc = (
        f"# 内容填充任务 — 场景: {scenario}\n\n"
        f"请阅读下方【数据契约】，然后根据【本 deck 的 outline.json】为每页生成内容，\n"
        f"输出完整的 content.pptx.json（写入同目录），再运行 gate_check_s3 验证。\n\n"
        f"---\n\n## 本 deck 的 outline.json\n\n```json\n{outline_json}\n```\n\n"
        f"---\n\n## 数据契约（所有 layout 的字段规范与华为约束）\n\n{contract}\n"
    )
    out = output_dir / "content_prompt.md"
    out.write_text(doc, encoding="utf-8")
    return out


def _try_llm_autofill(prompt_path, output_dir: Path):
    """Attempt to auto-fill content via llm_client if an API key is set.

    Returns the filled content dict on success, or None if no key / fill
    failed (so the caller falls back to sample data gracefully).
    """
    import os
    backend = os.getenv("PPT_LLM_BACKEND", "").lower()
    has_key = bool(os.getenv("GLM_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))
    if not has_key:
        return None  # no key → agent prompt left for external Code Agent
    try:
        from llm_client import LLMClient
        client = LLMClient(backend=backend or "glm")
        prompt = prompt_path.read_text(encoding="utf-8")
        raw = client.complete(prompt, temperature=0.4)
        # Try to extract a JSON object from the response.
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("```json\n")[-1].split("```\n")[-1].split("```")[0]
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            return None
        content = json.loads(text[start:end + 1])
        if "slides" not in content:
            return None
        # Write and return.
        out = output_dir / "content.pptx.json"
        out.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[S3] LLM auto-fill succeeded ({len(content['slides'])} slides)")
        return content
    except Exception as e:
        print(f"[S3] LLM auto-fill skipped: {e}")
        return None
