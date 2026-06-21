"""
生成PPT生成要求文档

从corpus learning的结果中生成人可读的要求文档。
如果没有corpus数据，使用内置默认规则。
"""
import os
import json


DEFAULT_REQUIREMENTS = """# PPT Generation Requirements (华为内部汇报材料)

## 1. 总体定位
用于华为内部洞察、HR战略、AI技术分析、组织机制分析等汇报材料。
面向高层领导、研发主管、HR管理层。

## 2. Input-grounded 内容边界
- 所有事实、数字、案例、benchmark必须来自input
- 不得复用历史PPT中的事实内容
- 不得无中生有扩展input
- input不足时输出missing_information.md

## 3. 标题规则
- 必须是直接结论型标题
- 不使用"趋势判断：""机制分析：""数据发现："等固定前缀
- 标题应表达判断、发现、风险、建议或机制结论
- 标题要有分量感，像高管说话的语气
- 示例："AI人才供给不足已成为研发组织扩张的核心瓶颈"

## 4. 页面类型
- cover: 封面
- trend_insight: 趋势/洞察页 - 展示行业趋势、数据对比
- challenge_cards: 问题/挑战分析 - 多列卡片展开
- solution_split: 解决方案 - 左右分栏
- data_insight: 数据洞察 - 大数字高亮
- mechanism_analysis: 机制分析 - 中心概念+要素
- case_study: 案例 - 三栏结构
- roadmap: 路线图/时间线
- executive_summary: 执行摘要
- option_comparison: 方案对比表格
- talent_profile: 人才/角色画像
- risk_matrix: 风险矩阵
- recommendation: 建议决策
- closing: 结尾

## 5. 信息密度规则
- 每页500-800字中文（含标题）
- 每页2-4个section
- 每个section 2-5个bullet
- 趋势洞察页可高密度，案例页可中等密度
- 封面、结尾页低密度

## 6. 数据与证据规则
- 数字必须有来源（来自input）
- 无来源数字不得写成事实
- 如果input没有证据，标注evidence_gap

## 7. 视觉规则
- 主色：华为红 #C00000
- 文字：黑#000000、深灰#333333、灰#595659
- 背景：白#FFFFFF、浅灰#F2F2F2
- 强调：红色用于标题、关键数字、左侧竖条
- 右上角标签：红底白字
- 字体：微软雅黑（中文）、Arial（英文/数字）
- 标题22pt粗体红色、正文11-12pt、数字强调32-36pt

## 8. 禁止事项
- 不要客户销售味道
- 不要无来源数字
- 不要空bullet
- 不要整页截图式PPT
- 不要花哨咨询风格
- 不要互联网发布会风格
- 不要"趋势判断："等前缀式标题
- 不要把结构字段名直接作为标题

## 9. 可编辑PPTX要求
- 标题、正文必须是可编辑textbox
- 图形用shape/line/connector
- 不得把整页作为图片
"""


def build_requirements(corpus_dir, output_path):
    """生成PPT生成要求文档"""
    agg_dir = os.path.join(corpus_dir, "aggregate")

    # 检查是否有corpus数据
    has_corpus = os.path.exists(os.path.join(agg_dir, "page_type_distribution.json"))

    if not has_corpus:
        # 使用默认规则
        print("No corpus data found, using default requirements")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(DEFAULT_REQUIREMENTS)
        print(f"Requirements saved: {output_path}")
        return

    # 从corpus数据构建增强版requirements
    doc = DEFAULT_REQUIREMENTS

    # 补充corpus发现
    doc += "\n\n## 10. Corpus Learning发现\n\n"

    # Page type distribution
    try:
        with open(os.path.join(agg_dir, "page_type_distribution.json"), 'r') as f:
            dist = json.load(f)
        doc += "### 页面类型分布\n"
        for pt, count in dist.items():
            doc += f"- {pt}: {count}页\n"
        doc += "\n"
    except:
        pass

    # Top reusable rules
    try:
        with open(os.path.join(agg_dir, "reusable_rules_raw.json"), 'r') as f:
            rules = json.load(f)
        doc += "### 高频可复用规则\n"
        for rule, count in list(rules.items())[:15]:
            doc += f"- {rule} ({count}次)\n"
        doc += "\n"
    except:
        pass

    # Avoid patterns
    try:
        with open(os.path.join(agg_dir, "avoid_patterns_raw.json"), 'r') as f:
            avoids = json.load(f)
        doc += "### 应避免的模式\n"
        for pattern, count in list(avoids.items())[:10]:
            doc += f"- {pattern} ({count}次)\n"
        doc += "\n"
    except:
        pass

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(doc)

    print(f"Requirements saved: {output_path}")
