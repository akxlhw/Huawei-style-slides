"""Generate the 25-framework gallery as standalone Huawei-style HTML/PNG.

Each framework renders to a single self-contained HTML slide (1920×1080,
Huawei visual language), then to a PNG screenshot via Playwright. The HTML
templates are inline here (framework-specific SVG/CSS) so the gallery is
self-contained and does not need the full deck Jinja2 pipeline.

Usage:
    python scripts/generate_framework_gallery.py
    python scripts/generate_framework_gallery.py --no-screenshot  # HTML only
"""
import argparse
import os
from pathlib import Path

GALLERY_DIR = Path(__file__).resolve().parent.parent / "references" / "framework-gallery"
RED = "#CF0A2C"
BLUE = "#007DFF"
GREEN = "#669900"
ORANGE = "#FF9900"
YELLOW = "#FCC800"
GRAY = "#DCDDDD"

# ── Shared HTML scaffold ─────────────────────────────────────────────────────
def _page(title_cn, title_en, body_html):
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<title>{title_cn}</title>
<style>
:root{{--red:{RED};--blue:{BLUE};--green:{GREEN};--orange:{ORANGE};--yellow:{YELLOW};
--gray:{GRAY};--title:#1a1a1a;--body:#595959;--muted:#999;--line:#E8E8E8;--bg:#F7F8FA;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:"Microsoft YaHei",sans-serif;}}
.slide{{width:1920px;height:1080px;background:#fff;position:relative;overflow:hidden;display:flex;flex-direction:column;padding:70px 90px 60px;}}
.brand{{position:absolute;left:0;top:0;width:10px;height:100%;background:{RED};}}
.twrap{{position:relative;margin-bottom:36px;}}
.tag{{display:inline-block;font-size:15px;color:{RED};font-weight:bold;background:rgba(207,10,44,.08);padding:4px 14px;border-radius:3px;margin-bottom:12px;}}
.h1{{font-size:40px;font-weight:bold;color:#1a1a1a;}}
.en{{font-size:16px;color:#999;margin-top:6px;}}
.arc{{position:absolute;left:0;bottom:-14px;width:280px;height:20px;}}
.src{{position:absolute;left:90px;bottom:28px;font-size:13px;color:#999;}}
.pn{{position:absolute;right:90px;bottom:28px;font-size:14px;color:#999;}}
.card{{background:#F7F8FA;border-radius:8px;padding:24px;border-top:4px solid var(--c,{RED});}}
</style></head>
<body><div class="slide"><div class="brand"></div>
<div class="twrap"><span class="tag">思维框架示例</span>
<div class="h1">{title_cn}</div><div class="en">{title_en}</div></div>
{body_html}
<div class="src">来源：华为 Style Slides 框架图库</div></div>
</body></html>"""


# ── 12 new framework body templates (Tier B) ────────────────────────────────

def _fishbone():
    # 鱼骨图：水平主骨 + 6 条斜支(人/机/料/法/环/测) + 鱼头(问题)
    branches = [("人 Man","技能不匹配/人手不足"),("机 Machine","工具落后/系统卡顿"),
                ("料 Material","预算不足/资源缺"),("法 Method","流程繁琐/标准缺失"),
                ("环 Environment","市场变化/政策"),("测 Measurement","指标偏差/KPI错")]
    top = branches[::2]; bot = branches[1::2]
    def _bones(items, y0, dy, dir_):
        out=""
        for i,(name,desc) in enumerate(items):
            bx=300+i*420; by=y0+dir_*i*dy; mx=bx+210; my=480
            out+=f'<line x1="{bx}" y1="{by}" x2="{mx}" y2="{my}" stroke="{GRAY}" stroke-width="2"/>'
            out+=f'<rect x="{bx-90}" y="{by-44 if dir_<0 else by+10}" width="180" height="60" rx="6" fill="{RED if dir_<0 else BLUE}" fill-opacity="0.1" stroke="{RED if dir_<0 else BLUE}"/>'
            out+=f'<text x="{bx}" y="{by-18 if dir_<0 else by+36}" text-anchor="middle" font-size="17" fill="#1a1a1a" font-weight="bold">{name}</text>'
            out+=f'<text x="{bx}" y="{by-2 if dir_<0 else by+52}" text-anchor="middle" font-size="14" fill="#595959">{desc}</text>'
        return out
    return f'''<div style="flex:1;display:flex;align-items:center;justify-content:center;">
    <svg viewBox="0 0 1740 720" style="width:100%;max-height:680px;">
    <line x1="120" y1="480" x2="1500" y2="480" stroke="#1a1a1a" stroke-width="4"/>
    {_bones(top,330,40,-1)}{_bones(bot,560,40,1)}
    <polygon points="1500,440 1500,520 1600,480" fill="{RED}"/>
    <rect x="1600" y="440" width="130" height="80" rx="8" fill="{RED}"/>
    <text x="1665" y="475" text-anchor="middle" font-size="18" fill="#fff" font-weight="bold">问题</text>
    <text x="1665" y="500" text-anchor="middle" font-size="14" fill="#fff">招聘周期长</text>
    <text x="80" y="490" text-anchor="middle" font-size="16" fill="#999">起点</text>
    </svg></div>'''

def _five_w2h():
    cells=[("What 什么","做什么：招聘后端工程师 5 名"),("Why 为什么","业务扩张，技术债积压"),
           ("Who 谁","HRBP-A 负责寻访"),("When 何时","Q4 内到岗"),
           ("Where 何地","北京/上海研发中心"),("How 怎么做","内推+猎头并行"),
           ("How much 多少","预算 30 万，周期 60 天")]
    cols={"#CF0A2C":0,"#007DFF":1,"#669900":2,"#FF9900":3,"#FCC800":4,"#CF0A2C":5,"#007DFF":6}
    items=""
    for i,(h,d) in enumerate(cells):
        colors=[RED,BLUE,GREEN,ORANGE,YELLOW,RED,BLUE]
        items+=f'''<div class="card" style="--c:{colors[i]};text-align:center;"><div style="font-size:22px;font-weight:bold;color:{colors[i]};margin-bottom:10px;">{h}</div><div style="font-size:17px;color:#595959;">{d}</div></div>'''
    return f'<div style="flex:1;display:grid;grid-template-columns:repeat(4,1fr);gap:20px;align-content:center;">{items}</div>'

def _pest():
    cells=[("P 政治Political","人才政策/签证/劳动法"),("E 经济Economic","薪酬通胀/融资环境"),
           ("S 社会Social","远程办公/择业观变化"),("T 技术Technological","AI替代/AI赋能"),
           ("E 环境Environmental","绿色低碳/ESG"),("L 法律Legal","数据合规/反歧视")]
    colors=[RED,BLUE,GREEN,ORANGE,GREEN,BLUE]
    items=""
    for i,(h,d) in enumerate(cells):
        items+=f'''<div class="card" style="--c:{colors[i]};"><div style="font-size:21px;font-weight:bold;color:{colors[i]};margin-bottom:8px;">{h}</div><div style="font-size:17px;color:#595959;line-height:1.5;">{d}</div></div>'''
    return f'<div style="flex:1;display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:1fr 1fr;gap:24px;">{items}</div>'

def _porter():
    # 波特五力：中心(竞争) + 上下左右四力
    forces=[("新进入者威胁","门槛低/同质化",RED,"top"),("替代品威胁","外包/灵活用工",BLUE,"right"),
            ("供应商议价","猎头/平台涨价",GREEN,"bottom"),("买方议价","候选人选择多",ORANGE,"left")]
    inner=f'<circle cx="870" cy="400" r="110" fill="{RED}"/><text x="870" y="392" text-anchor="middle" font-size="22" fill="#fff" font-weight="bold">行业内</text><text x="870" y="420" text-anchor="middle" font-size="22" fill="#fff" font-weight="bold">竞争</text>'
    pos={"top":(870,120),"right":(1500,400),"bottom":(870,680),"left":(240,400)}
    boxes=""
    for name,desc,color,d in forces:
        x,y=pos[d]
        boxes+=f'<rect x="{x-130}" y="{y-45}" width="260" height="90" rx="8" fill="{color}" fill-opacity="0.1" stroke="{color}" stroke-width="2"/>'
        boxes+=f'<text x="{x}" y="{y-8}" text-anchor="middle" font-size="19" fill="{color}" font-weight="bold">{name}</text>'
        boxes+=f'<text x="{x}" y="{y+18}" text-anchor="middle" font-size="15" fill="#595959">{desc}</text>'
    return f'<div style="flex:1;display:flex;align-items:center;justify-content:center;"><svg viewBox="0 0 1740 800" style="width:90%;max-height:720px;">{inner}{boxes}</svg></div>'

def _bmc():
    blocks=[("关键合作伙伴","供应商/渠道/高校"),("关键业务","寻访/评估/录用"),
            ("核心资源","人才库/雇主品牌"),("价值主张","高效精准匹配"),
            ("客户关系","长期服务/信任"),("渠道","内推/猎头/校招"),
            ("客户细分","业务部门/候选人"),("成本结构","渠道费/人力/工具"),
            ("收入来源","到岗产出/留存价值")]
    # BMC 布局: 左5列+右4列+底部2列，简化为 3 行
    layout=[(0,0,1,2),(1,0,1,1),(1,1,1,1),(2,0,1,2),(3,0,1,1),(3,1,1,1),(4,0,1,2),(0,2,4,1)]
    colors=[RED,BLUE,GREEN,RED,BLUE,GREEN,RED,"#999","#999"]
    items=""
    for i,(h,d) in enumerate(blocks):
        items+=f'''<div class="card" style="--c:{colors[i]};padding:18px;"><div style="font-size:18px;font-weight:bold;color:{colors[i]};margin-bottom:6px;">{h}</div><div style="font-size:15px;color:#595959;line-height:1.4;">{d}</div></div>'''
    return f'<div style="flex:1;display:grid;grid-template-columns:repeat(5,1fr);grid-template-rows:1fr 1fr 1fr;gap:14px;">{items}</div>'

def _seven_s():
    # 7S: 中心共同价值观 + 6 元素环绕
    elems=[("战略Strategy",RED),("结构Structure",BLUE),("制度Systems",GREEN),
          ("风格Style",ORANGE),("员工Staff",YELLOW),("技能Skills",RED)]
    import math
    cx,cy,R=870,400,220
    boxes=f'<circle cx="{cx}" cy="{cy}" r="95" fill="{RED}"/>'
    boxes+=f'<text x="{cx}" y="{cy-5}" text-anchor="middle" font-size="18" fill="#fff" font-weight="bold">共同</text><text x="{cx}" y="{cy+20}" text-anchor="middle" font-size="18" fill="#fff" font-weight="bold">价值观</text>'
    for i,(name,color) in enumerate(elems):
        ang=math.radians(-90+i*60)
        x=cx+int(R*math.cos(ang)); y=cy+int(R*math.sin(ang))
        boxes+=f'<circle cx="{x}" cy="{y}" r="70" fill="{color}" fill-opacity="0.15" stroke="{color}" stroke-width="2"/>'
        boxes+=f'<text x="{x}" y="{y+6}" text-anchor="middle" font-size="16" fill="{color}" font-weight="bold">{name}</text>'
    return f'<div style="flex:1;display:flex;align-items:center;justify-content:center;"><svg viewBox="0 0 1740 800" style="width:70%;max-height:720px;">{boxes}</svg></div>'

def _bcg():
    # BCG: 2×2 增长×份额
    quads=[("明星 Star","高增长高份额\n加大投入",RED,"top-right"),("现金牛 Cash Cow","低增长高份额\n维持收割",GREEN,"bottom-right"),
           ("问题 Question","高增长低份额\n选择性投入",ORANGE,"top-left"),("瘦狗 Dog","低增长低份额\n退出/剥离",GRAY,"bottom-left")]
    items=""
    for name,desc,color,pos in quads:
        items+=f'''<div class="card" style="--c:{color};border-top-width:5px;"><div style="font-size:22px;font-weight:bold;color:{color};margin-bottom:10px;">{name}</div><div style="font-size:16px;color:#595959;white-space:pre-line;">{desc}</div></div>'''
    return f'''<div style="flex:1;display:flex;flex-direction:column;">
    <div style="display:flex;font-size:15px;color:#999;font-weight:bold;padding:0 20px 8px;"><div style="flex:1;text-align:center;">← 市场份额</div></div>
    <div style="flex:1;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:16px;">{items}</div>
    <div style="text-align:center;font-size:15px;color:#999;font-weight:bold;padding:8px 0 0;">市场增长率 ↑</div></div>'''

def _grow():
    steps=[("G Goal 目标","明确想达成的结果"),("R Reality 现状","客观描述当前情况"),
           ("O Options 选项","探索所有可能方案"),("W Will 意愿","承诺行动与时间")]
    colors=[RED,BLUE,GREEN,ORANGE]
    items=""
    for i,(h,d) in enumerate(steps):
        items+=f'''<div style="display:flex;align-items:stretch;gap:24px;margin-bottom:20px;">
        <div style="width:80px;background:{colors[i]};color:#fff;display:flex;align-items:center;justify-content:center;font-size:36px;font-weight:bold;border-radius:8px 0 0 8px;">{i+1}</div>
        <div class="card" style="--c:{colors[i]};border-top:none;border-left:5px solid {colors[i]};border-radius:0 8px 8px 0;flex:1;">
        <div style="font-size:22px;font-weight:bold;color:{colors[i]};margin-bottom:6px;">{h}</div><div style="font-size:18px;color:#595959;">{d}</div></div></div>'''
    return f'<div style="flex:1;display:flex;flex-direction:column;justify-content:center;">{items}</div>'

def _prep():
    steps=[("P 观点 Point","开门见山亮结论：建议采用内推为主渠道"),
           ("R 理由 Reason","内推性价比 3.6，是付费渠道的 3 倍"),
           ("E 例证 Example","Q3 内推入职 9 人，留存率 90%"),
           ("P 重申 Point","综上，应将内推作为招聘主力渠道")]
    colors=[RED,BLUE,GREEN,RED]
    items=""
    for i,(h,d) in enumerate(steps):
        items+=f'''<div class="card" style="--c:{colors[i]};margin-bottom:18px;display:flex;gap:20px;align-items:center;">
        <div style="width:54px;height:54px;border-radius:50%;background:{colors[i]};color:#fff;display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:bold;flex-shrink:0;">{h[0]}</div>
        <div><div style="font-size:20px;font-weight:bold;color:{colors[i]};">{h}</div><div style="font-size:17px;color:#595959;margin-top:4px;">{d}</div></div></div>'''
    return f'<div style="flex:1;display:flex;flex-direction:column;justify-content:center;">{items}</div>'

def _fabe():
    cols=[("F 特征 Feature","内推激励翻倍方案",RED),("A 优势 Advantage","成本仅为猎头 1/5",BLUE),
          ("B 利益 Benefit","预计入职 +30%",GREEN),("E 证据 Evidence","友商案例已验证",ORANGE)]
    items=""
    for h,d,c in cols:
        items+=f'''<div class="card" style="--c:{c};text-align:center;"><div style="width:56px;height:56px;border-radius:14px;background:{c};color:#fff;display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:bold;margin:0 auto 18px;">{h[0]}</div><div style="font-size:20px;font-weight:bold;color:{c};margin-bottom:8px;">{h}</div><div style="font-size:16px;color:#595959;">{d}</div></div>'''
    return f'<div style="flex:1;display:grid;grid-template-columns:repeat(4,1fr);gap:24px;align-items:center;">{items}</div>'

def _raci():
    roles=["HRBP","用人经理","HRD","候选人"]
    tasks=[("需求确认","R","A","I","I"),("面试安排","R","C","I","R"),
           ("薪酬审批","C","C","A","I"),("Offer发放","R","A","I","C")]
    cmap={"R":(RED,"R 负责"),"A":(BLUE,"A 批准"),"C":(GREEN,"C 咨询"),"I":(GRAY,"I 知会")}
    head='<div style="display:flex;background:#1a1a1a;border-radius:8px 8px 0 0;"><div style="flex:0 0 280px;padding:16px 20px;font-size:16px;color:#fff;font-weight:bold;">任务\\角色</div>'+''.join(f'<div style="flex:1;padding:16px;text-align:center;font-size:16px;color:#fff;font-weight:bold;">{r}</div>' for r in roles)+'</div>'
    rows=""
    for t in tasks:
        cells='<div style="flex:0 0 280px;padding:14px 20px;font-size:17px;color:#1a1a1a;font-weight:bold;">'+t[0]+'</div>'
        for code in t[1:]:
            c,lab=cmap[code]
            cells+=f'<div style="flex:1;padding:14px;text-align:center;"><span style="display:inline-block;width:40px;height:40px;line-height:40px;border-radius:50%;background:{c};color:#fff;font-size:18px;font-weight:bold;">{code}</span></div>'
        rows+=f'<div style="display:flex;border-top:1px solid #E8E8E8;background:#fff;align-items:center;">{cells}</div>'
    legend='<div style="display:flex;gap:28px;margin-top:18px;font-size:15px;color:#999;">'+''.join(f'<span>● {lab}</span>' for c,lab in cmap.values())+'</div>'
    return f'<div style="flex:1;display:flex;flex-direction:column;justify-content:center;">{head}{rows}{legend}</div>'

def _aida():
    layers=[("A 注意 Attention","曝光量 10000",RED,100),("I 兴趣 Interest","简历 1500",ORANGE,75),
            ("D 欲望 Desire","面试 180",BLUE,50),("A 行动 Action","入职 130",GREEN,25)]
    items=""
    for h,d,c,w in layers:
        items+=f'''<div style="width:{w}%;background:{c};color:#fff;padding:24px;text-align:center;border-radius:6px;margin:0 auto 12px;">
        <div style="font-size:20px;font-weight:bold;">{h}</div><div style="font-size:16px;opacity:.9;margin-top:4px;">{d}</div></div>'''
    return f'<div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;">{items}</div>'


# ── Tier A framework bodies (reuse visual idioms with framework-specific data) ─

def _reuse_simple(bullets, kind="cards"):
    """Generic cards/quadrants body for Tier-A frameworks."""
    items=""
    colors=[RED,BLUE,GREEN,ORANGE,YELLOW,GRAY]
    for i,(h,d) in enumerate(bullets):
        c=colors[i%len(colors)]
        items+=f'''<div class="card" style="--c:{c};"><div style="font-size:20px;font-weight:bold;color:{c};margin-bottom:8px;">{h}</div><div style="font-size:16px;color:#595959;line-height:1.5;">{d}</div></div>'''
    cols = "repeat(2,1fr)" if len(bullets)==4 else "repeat(3,1fr)" if len(bullets)<=3 else "repeat(4,1fr)"
    return f'<div style="flex:1;display:grid;grid-template-columns:{cols};gap:22px;align-content:center;">{items}</div>'


# ── The 25 frameworks registry ───────────────────────────────────────────────
FRAMEWORKS = [
    # Tier A (reuse)
    ("pyramid", "金字塔原理", "Pyramid Principle", _reuse_simple([("结论先行","标题即核心结论"),("以上统下","上层概括下层"),("归类分组 MECE","同组同范畴互斥穷尽"),("逻辑递进","时间/结构/重要性顺序")])),
    ("mece", "MECE 分类法则", "MECE Principle", _reuse_simple([("相互独立 M","分类间无重叠"),("完全穷尽 E","覆盖所有情况"),("二分法","内/外、短期/长期"),("流程法","按时间步骤划分")])),
    ("scqa", "SCQA 叙事框架", "Situation-Complication-Question-Answer", _reuse_simple([("S 情境","建立共识背景(20%)"),("C 冲突","呈现关键矛盾(20%)"),("Q 疑问","聚焦核心痛点(10%)"),("A 答案","给出方案结论(50%)")])),
    ("star", "STAR 法则", "Situation-Task-Action-Result", _reuse_simple([("S 情境","事件背景环境"),("T 任务","角色与目标挑战"),("A 行动","具体步骤与决策"),("R 结果","量化成效影响")])),
    ("4p", "4P 进度框架", "Plan-Progress-Problem-Proposal", _reuse_simple([("Plan 计划","目标范围里程碑"),("Progress 进展","已完成与达成率"),("Problem 问题","风险与求助"),("Proposal 提案","下阶段任务资源")])),
    ("9box", "9-Box 人才盘点", "9-Box Talent Matrix", _reuse_simple([("低潜低绩","观察/淘汰"),("高潜低绩","培养提升"),("低潜高绩","保留激励"),("高潜高绩","重点发展")])),
    ("swot", "SWOT 分析", "Strengths-Weaknesses-Opportunities-Threats", _reuse_simple([("S 优势","内部长处"),("W 劣势","内部短板"),("O 机会","外部利好"),("T 威胁","外部风险")])),
    ("3c", "3C 战略分析", "Company-Competitor-Customer", _reuse_simple([("Company 公司","自身能力资源"),("Competitor 竞争者","对手优劣势"),("Customer 客户","需求与期望")])),
    ("fis", "FIS 事实影响方案", "Fact-Impact-Solution", _reuse_simple([("F 事实","客观陈述现状"),("I 影响","量化业务影响"),("S 方案","建议与行动")])),
    ("7step", "七步成诗", "Seven-Step Problem Solving", _reuse_simple([("1 定义问题","明确边界与目标"),("2 拆解问题","MECE 分解"),("3 优先排序","聚焦关键"),("4 分析论证","数据支撑")])),
    ("goldencircle", "黄金圈", "Why-How-What", None),  # special: reuse ecosystem_ring shape below
    ("smart", "SMART 目标", "Specific-Measurable-Achievable-Relevant-Time-bound", _reuse_simple([("Specific 具体","清晰可描述"),("Measurable 可衡量","有量化指标"),("Achievable 可达成","资源匹配"),("Relevant 相关","对齐战略"),("Time-bound 有时限","明确截止")])),
    ("kiss", "KISS 极简原则", "Keep It Simple", None),  # quote style
    # Tier B (dedicated)
    ("fishbone", "鱼骨图 Ishikawa", "Fishbone / Cause-and-Effect Diagram", None),
    ("5w2h", "5W2H 分析法", "What-Why-Who-When-Where-How-HowMuch", None),
    ("pest", "PESTEL 分析", "Political-Economic-Social-Tech-Env-Legal", None),
    ("porter", "波特五力模型", "Porter's Five Forces", None),
    ("bmc", "业务画布 BMC", "Business Model Canvas", None),
    ("7s", "麦肯锡 7S 模型", "McKinsey 7S Framework", None),
    ("bcg", "BCG 矩阵", "BCG Growth-Share Matrix", None),
    ("grow", "GROW 辅导模型", "Goal-Reality-Options-Will", None),
    ("prep", "PREP 表达法", "Point-Reason-Example-Point", None),
    ("fabe", "FABE 说服法", "Feature-Advantage-Benefit-Evidence", None),
    ("raci", "RACI 责任矩阵", "Responsible-Accountable-Consulted-Informed", None),
    ("aida", "AIDA 营销漏斗", "Attention-Interest-Desire-Action", None),
]

_BODY_FN = {
    "fishbone":_fishbone,"5w2h":_five_w2h,"pest":_pest,"porter":_porter,"bmc":_bmc,
    "7s":_seven_s,"bcg":_bcg,"grow":_grow,"prep":_prep,"fabe":_fabe,"raci":_raci,"aida":_aida,
}

def _goldencircle_body():
    import math
    cx,cy=870,400
    rings=[("What 做什么",RED,300),("How 怎么做",BLUE,200),("Why 为什么",GREEN,100)]
    s=f'<svg viewBox="0 0 1740 800" style="width:75%;max-height:720px;">'
    for name,color,r in rings:
        s+=f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" fill-opacity="0.12" stroke="{color}" stroke-width="2"/>'
        s+=f'<text x="{cx}" y="{cy-r+30}" text-anchor="middle" font-size="20" fill="{color}" font-weight="bold">{name}</text>'
    s+=f'<circle cx="{cx}" cy="{cy}" r="50" fill="{GREEN}"/><text x="{cx}" y="{cy+6}" text-anchor="middle" font-size="16" fill="#fff" font-weight="bold">核心</text></svg>'
    return f'<div style="flex:1;display:flex;align-items:center;justify-content:center;">{s}</div>'

def _kiss_body():
    return '''<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;">
    <div style="font-size:120px;font-weight:bold;color:#CF0A2C;letter-spacing:8px;">KISS</div>
    <div style="font-size:36px;color:#1a1a1a;margin-top:20px;">Keep It Simple, Stupid</div>
    <div style="font-size:22px;color:#595959;margin-top:40px;max-width:900px;text-align:center;line-height:1.6;">复杂是沟通的敌人。每页只传递一个核心信息，用最简单的结构表达。</div></div>'''


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--no-screenshot",action="store_true",help="skip PNG rendering")
    args=ap.parse_args()
    GALLERY_DIR.mkdir(parents=True,exist_ok=True)
    htmls=[]
    for key,cn,en,body in FRAMEWORKS:
        # body may be: a pre-rendered string (Tier A), None (Tier B / special),
        # then resolved via the lookup tables below.
        if key=="goldencircle": body=_goldencircle_body()
        elif key=="kiss": body=_kiss_body()
        elif key in _BODY_FN: body=_BODY_FN[key]()
        elif not isinstance(body, str):
            raise ValueError(f"no body for framework {key}")
        html=_page(cn,en,body)
        hp=GALLERY_DIR/f"{key}.html"
        hp.write_text(html,encoding="utf-8")
        htmls.append((key,hp))
        print(f"  {key}: {hp.name}")
    print(f"Wrote {len(htmls)} HTML files to {GALLERY_DIR}")
    if not args.no_screenshot:
        _screenshot(htmls)

def _screenshot(htmls):
    try:
        import asyncio
        from playwright.async_api import async_playwright
    except ImportError:
        print("playwright not installed; skipping PNG. HTML files are ready.")
        return
    async def shoot():
        async with async_playwright() as p:
            b=await p.chromium.launch()
            page=await b.new_page(viewport={"width":1920,"height":1080})
            for key,hp in htmls:
                await page.goto(f"file:///{hp.resolve().as_posix()}")
                await page.wait_for_timeout(400)
                await page.screenshot(path=str(GALLERY_DIR/f"{key}.png"))
                print(f"  {key}.png")
            await b.close()
    asyncio.run(shoot())

if __name__=="__main__":
    main()
