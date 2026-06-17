"""S3a: Build content.pptx.json from outline, with sample data for each layout."""

import json
from pathlib import Path
from typing import Dict, Any, List


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
            {"title": "招聘完成率 60%", "description": "低于目标 20 个百分点"},
            {"title": "技术岗缺口最大", "description": "缺口 30% 集中在后端/Java"},
            {"title": "Q4 追赶计划已制定", "description": "预计 12 月底前补齐"},
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
    return {
        "layout": "funnel",
        "title": slide["title"],
        "stages": [
            {"label": "曝光", "value": 10000},
            {"label": "投递", "value": 1500},
            {"label": "初筛", "value": 600},
            {"label": "面试", "value": 180},
            {"label": "Offer", "value": 144},
            {"label": "入职", "value": 130},
        ],
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
            {"label": "立即行动", "items": ["核心架构师", "算法负责人"], "color": "#C7000B"},
            {"label": "提前布局", "items": ["校招 Pipeline", "高潜储备"], "color": "#30B5C5"},
            {"label": "快速解决", "items": ["实习生", "辅助岗"], "color": "#FCC800"},
            {"label": "暂缓/冻结", "items": ["非关键替补"], "color": "#DCDDDD"},
        ],
        "axis_labels": {"x": "紧急度", "y": "影响度"},
        "source": "HRBP 评估",
    }


def _make_timeline(slide: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "layout": "timeline",
        "title": slide["title"],
        "milestones": [
            {"date": "10 月 W1", "label": "优化 JD + 开通猎聘", "desc": "预计简历 +40%"},
            {"date": "10 月 W2", "label": "薪酬特批", "desc": "Offer 接受率 +20%"},
            {"date": "10 月 W3", "label": "面试流程精简", "desc": "周期 -5 天"},
            {"date": "11 月", "label": "内推激励翻倍", "desc": "入职 +30%"},
            {"date": "12 月", "label": "Q4 复盘", "desc": "目标达成率评估"},
        ],
        "source": "招聘计划",
    }


def _make_action_items(slide: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "layout": "action_items",
        "title": slide["title"],
        "actions": [
            {"title": "优化 JD", "owner": "HRBP-A", "timeline": "第 1 周", "desc": "覆盖 Spring Cloud 等热词"},
            {"title": "薪酬特批", "owner": "HRD", "timeline": "第 1-2 周", "desc": "技术岗调薪至 75 分位"},
            {"title": "面试精简", "owner": "招聘组", "timeline": "第 2 周", "desc": "4 轮 → 3 轮"},
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
