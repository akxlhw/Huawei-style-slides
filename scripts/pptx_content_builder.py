"""S3a: Build content.pptx.json from outline, with sample data for each layout.

This builder emits the API format expected by MckEngine and gate_check_s3.py:
- executive_summary items are (num, title, description) tuples
- matrix_2x2 quadrants are (label, color_hex, description) tuples
- funnel stages are (label, count_label, pct_of_max) tuples
- timeline milestones are (label, description) tuples
- action_items actions are (title, timeline, description, owner) tuples
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple


def _make_cover(slide: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "layout": "cover",
        "title": slide["title"],
        "subtitle": "HR 招聘调配汇报",
        "author": "HR Team",
        "date": "2026",
    }


def _make_executive_summary(slide: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "layout": "executive_summary",
        "title": slide["title"],
        "headline": slide["key_point"],
        "items": [
            (1, "招聘完成率 60%", "低于目标 20 个百分点"),
            (2, "技术岗缺口最大", "缺口 30% 集中在后端/Java"),
            (3, "Q4 追赶计划已制定", "预计 12 月底前补齐"),
        ],
        "source": "HR 数据平台",
    }


def _make_table_insight(slide: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "layout": "table_insight",
        "title": slide["title"],
        "headers": ["环节", "数量", "转化率", "目标"],
        "rows": [
            ["渠道曝光", "10,000", "100%", "100%"],
            ["简历投递", "1,500", "15%", "≥10%"],
            ["初筛通过", "600", "40%", "30%-50%"],
            ["面试通过", "180", "30%", "25%-40%"],
            ["Offer 接受", "144", "80%", "≥75%"],
            ["入职到岗", "130", "90%", "≥90%"],
        ],
        "insights": ["简历投递转化率刚好达标", "面试通过环节低于目标，需优化面试官效率", "Offer 接受率健康"],
        "source": "招聘系统 2026Q3",
    }


def _make_funnel(slide: Dict[str, Any]) -> Dict[str, Any]:
    """Build funnel slide data.

    The PPTX track renders this as a process_chevron (the retired funnel layout
    overflows). The HTML track renders it as a funnel bar chart.
    """
    stages = [
        ("曝光", "10,000", 1.000),
        ("投递", "1,500", 0.150),
        ("初筛", "600", 0.060),
        ("面试", "180", 0.018),
        ("入职", "130", 0.013),
    ]
    return {
        "layout": "funnel",
        "title": slide["title"],
        "stages": stages,
        "source": "招聘系统",
    }


def _make_data_table(slide: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "layout": "data_table",
        "title": slide["title"],
        "headers": ["渠道", "费用", "简历", "面试", "入职", "单入职成本", "性价比"],
        "rows": [
            ["BOSS 直聘", "20,000", "200", "32", "10", "2,000", "1.6"],
            ["猎聘", "30,000", "80", "20", "6", "5,000", "0.8"],
            ["内推", "5,000", "30", "15", "9", "556", "3.6"],
            ["智联", "10,000", "120", "8", "0", "∞", "0"],
        ],
        "source": "Q3 渠道统计",
    }


def _make_matrix_2x2(slide: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "layout": "matrix_2x2",
        "title": slide["title"],
        "quadrants": [
            ("立即行动", "#C7000B", "核心架构师\n算法负责人"),
            ("提前布局", "#30B5C5", "校招 Pipeline\n高潜储备"),
            ("快速解决", "#FCC800", "实习生\n辅助岗"),
            ("暂缓/冻结", "#DCDDDD", "非关键替补"),
        ],
        "axis_labels": {"x": "紧急度", "y": "影响度"},
        "source": "HRBP 评估",
    }


def _make_timeline(slide: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "layout": "timeline",
        "title": slide["title"],
        "milestones": [
            ("10 月 W1", "优化 JD + 开通猎聘，预计简历 +40%"),
            ("10 月 W2", "薪酬特批，Offer 接受率 +20%"),
            ("10 月 W3", "面试流程精简，周期 -5 天"),
            ("11 月 内推", "内推激励翻倍，入职 +30%"),
            ("12 月", "复盘：目标达成率评估"),
        ],
        "source": "招聘计划",
    }


def _make_action_items(slide: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "layout": "action_items",
        "title": slide["title"],
        "actions": [
            ("优化 JD", "第 1 周", "覆盖 Spring Cloud 等热词", "HRBP-A"),
            ("薪酬特批", "第 1-2 周", "技术岗调薪至 75 分位", "HRD"),
            ("面试精简", "第 2 周", "4 轮 → 3 轮", "招聘组"),
        ],
        "source": "行动计划",
    }


def _make_closing(slide: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "layout": "closing",
        "title": slide["title"],
        "message": "期待进一步交流",
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
}


def build_pptx_content(outline: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    slides: List[Dict[str, Any]] = []
    for slide in outline["slides"]:
        layout = slide["layout"]
        builder = BUILDERS.get(layout)
        if not builder:
            raise ValueError(f"Unsupported PPTX layout: {layout}")
        data = builder(slide)
        data["idx"] = slide["idx"]
        data["key_point"] = slide.get("key_point", "")
        slides.append(data)

    content = {
        "brief": outline["brief"],
        "framework": outline.get("framework", "pyramid"),
        "slides": slides,
    }

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "content.pptx.json"
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    return content
