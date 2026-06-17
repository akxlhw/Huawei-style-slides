"""HR scenario templates: framework + default slide sequence."""

from typing import Dict, Any

SCENARIOS: Dict[str, Dict[str, Any]] = {
    "recruitment-review": {
        "name": "Q3 招聘复盘汇报",
        "framework": "seven-step",
        "secondary": ["issue-tree", "mece"],
        "audience": "CTO / 技术总监 / HRD",
        "goal": "review",
        "duration_minutes": 15,
        "slides": [
            {"idx": 1, "layout": "cover", "title": "Q3 招聘复盘汇报", "key_point": ""},
            {"idx": 2, "layout": "executive_summary", "title": "Q3 招聘完成率未达目标，技术岗缺口最大", "key_point": "Q3 招聘完成率低于目标，技术岗是主要缺口"},
            {"idx": 3, "layout": "table_insight", "title": "Q3 招聘漏斗全图与各环节转化率", "key_point": "简历获取环节转化率最低，是首要瓶颈"},
            {"idx": 4, "layout": "funnel", "title": "招聘漏斗各环节转化率分析", "key_point": "从曝光到入职的各环节转化率"},
            {"idx": 5, "layout": "data_table", "title": "各招聘渠道 ROI 对比与投放建议", "key_point": "内推性价比最高，智联零产出"},
            {"idx": 6, "layout": "matrix_2x2", "title": "岗位优先级矩阵：影响度 × 紧急度", "key_point": "高影响高紧急岗位优先补齐"},
            {"idx": 7, "layout": "timeline", "title": "Q4 追赶计划与关键里程碑", "key_point": "10-12 月关键里程碑"},
            {"idx": 8, "layout": "action_items", "title": "Q4 招聘追赶行动计划与责任人", "key_point": "责任人、时间、预期效果"},
            {"idx": 9, "layout": "closing", "title": "谢谢", "key_point": ""},
        ],
    },
    "channel-roi": {
        "name": "招聘渠道 ROI 分析",
        "framework": "mece",
        "secondary": ["3c", "pyramid"],
        "audience": "HRD / 招聘负责人",
        "goal": "decision",
        "duration_minutes": 10,
        "slides": [
            {"idx": 1, "layout": "cover", "title": "Q3 招聘渠道 ROI 分析", "key_point": ""},
            {"idx": 2, "layout": "executive_summary", "title": "建议停投智联，将预算转向 BOSS 与内推", "key_point": "建议停投智联，释放预算加投 BOSS 与内推"},
            {"idx": 3, "layout": "data_table", "title": "按 MECE 原则对招聘渠道进行分类", "key_point": "自有 / 付费 / 社交 / 猎头 / 校园"},
            {"idx": 4, "layout": "table_insight", "title": "各渠道 ROI 对比与投放效果分析", "key_point": "内推性价比 3.6 分，智联 0 分"},
            {"idx": 5, "layout": "matrix_2x2", "title": "渠道贡献度与单位成本二维矩阵", "key_point": "高贡献低成本渠道加大投入"},
            {"idx": 6, "layout": "timeline", "title": "Q4 渠道预算调整与执行时间表", "key_point": "预算重新分配时间表"},
            {"idx": 7, "layout": "closing", "title": "谢谢", "key_point": ""},
        ],
    },
    "allocation-plan": {
        "name": "人员调配方案",
        "framework": "scqa",
        "secondary": ["mece", "9-box"],
        "audience": "业务部门负责人 / HRD",
        "goal": "proposal",
        "duration_minutes": 12,
        "slides": [
            {"idx": 1, "layout": "cover", "title": "XX 部门人员调配方案", "key_point": ""},
            {"idx": 2, "layout": "executive_summary", "title": "8 个新增需求中 5 个通过内部调配解决", "key_point": "8 个新增需求中 5 个通过内部调配解决，3 个外部招聘"},
            {"idx": 3, "layout": "data_table", "title": "业务扩张带来的人员调配背景说明", "key_point": "业务扩张带来 8 个新增岗位需求"},
            {"idx": 4, "layout": "matrix_2x2", "title": "内部调配决策矩阵：能力 × 意愿", "key_point": "能力匹配度 × 发展意愿"},
            {"idx": 5, "layout": "data_table", "title": "内部调配人员详表与匹配度评估", "key_point": "姓名、原岗位、目标岗、匹配度、上岗时间"},
            {"idx": 6, "layout": "timeline", "title": "人员调配实施时间表与关键节点", "key_point": "沟通、交接、上岗、跟踪四阶段"},
            {"idx": 7, "layout": "action_items", "title": "人员调配风险识别与应对措施", "key_point": "不适应与岗位空缺预案"},
            {"idx": 8, "layout": "closing", "title": "谢谢", "key_point": ""},
        ],
    },
}


def get_scenario(name: str) -> Dict[str, Any]:
    if name not in SCENARIOS:
        raise ValueError(f"Unknown scenario '{name}'. Available: {list(SCENARIOS.keys())}")
    return SCENARIOS[name]


def build_default_outline(name: str) -> Dict[str, Any]:
    s = get_scenario(name)
    return {
        "brief": {
            "audience": s["audience"],
            "goal": s["goal"],
            "duration_minutes": s["duration_minutes"],
        },
        "framework": s["framework"],
        "secondary_frameworks": s["secondary"],
        "slides": s["slides"],
    }
