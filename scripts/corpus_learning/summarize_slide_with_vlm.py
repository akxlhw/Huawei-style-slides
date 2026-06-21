"""
逐页VLM归纳模块

对每页PPT调用多模态模型，分析风格和结构。
"""
import os
import json
from llm_client import call_vlm


VLM_PROMPT = """你是华为内部汇报PPT风格分析专家。请分析这一页PPT，归纳它的生成规律。

重要约束：
1. 这页PPT的具体事实、数字、客户名、人名、项目名只能用于理解样本，不得作为未来生成内容复用。
2. 你的任务是归纳页面类型、内容结构、标题风格、布局策略、视觉层级和可复用生成规则。
3. 请关注"为什么这页这样写、这样排、这样表达"。
4. 不要输出markdown，只输出合法JSON。

请输出JSON，包含以下字段:
{
  "quality_for_learning": "high|medium|low|exclude",
  "page_type": "cover|executive_summary|trend_insight|mechanism_analysis|data_insight|talent_profile|policy_proposal|risk_control|decision_recommendation|roadmap|option_comparison|organization_analysis|technology_route|case_study|other",
  "core_message": "这页核心想表达的判断",
  "title_analysis": {
    "title_text": "标题原文",
    "is_direct_conclusion": true,
    "title_pattern": "结论句式描述",
    "strength": "strong|medium|weak"
  },
  "content_structure": {
    "structure_type": "结构类型描述",
    "logic_flow": "逻辑流",
    "contains_judgment": true,
    "contains_evidence": true
  },
  "visual_layout": {
    "layout_type": "布局类型描述",
    "density": "low|medium|medium_high|high",
    "color_usage": "颜色使用描述"
  },
  "reusable_generation_rules": ["规则1", "规则2", "..."],
  "avoid_patterns": ["禁区1", "禁区2"],
  "do_not_reuse_content": ["具体事实内容不得复用"]
}

补充信息 - 该页的文字内容:
{text_content}

该页的对象统计:
{features}"""


def summarize_all_slides(corpus_dir, model=None):
    """对所有slide调用VLM分析"""
    index_path = os.path.join(corpus_dir, "corpus_index.json")
    if not os.path.exists(index_path):
        print("Error: corpus_index.json not found. Run corpus-ingest first.")
        return

    with open(index_path, 'r', encoding='utf-8') as f:
        index = json.load(f)

    slides = index.get("slides", [])
    print(f"Total slides to analyze: {len(slides)}")

    summary_dir = os.path.join(corpus_dir, "slide_summaries")
    os.makedirs(summary_dir, exist_ok=True)

    success = 0
    errors = 0

    for i, slide_info in enumerate(slides):
        slide_id = slide_info["slide_id"]

        # 跳过已有summary（断点续传）
        summary_path = os.path.join(summary_dir, f"{slide_id}.json")
        if os.path.exists(summary_path):
            print(f"  [{i+1}/{len(slides)}] {slide_id} - already done, skipping")
            success += 1
            continue

        image_path = os.path.join(corpus_dir, "slide_images", f"{slide_id}.png")
        text_path = os.path.join(corpus_dir, "slide_text", f"{slide_id}.txt")
        obj_path = os.path.join(corpus_dir, "slide_objects", f"{slide_id}.json")

        if not os.path.exists(image_path):
            print(f"  [{i+1}/{len(slides)}] {slide_id} - no image, skipping")
            errors += 1
            continue

        # 读取文字和特征
        text_content = ""
        if os.path.exists(text_path):
            with open(text_path, 'r', encoding='utf-8') as f:
                text_content = f.read()[:2000]

        features = "{}"
        if os.path.exists(obj_path):
            with open(obj_path, 'r', encoding='utf-8') as f:
                obj_data = json.load(f)
                features = json.dumps(obj_data.get("features", {}), ensure_ascii=False)

        prompt = VLM_PROMPT.replace("{text_content}", text_content).replace("{features}", features)

        try:
            print(f"  [{i+1}/{len(slides)}] {slide_id} - analyzing...")
            raw_response = call_vlm(prompt, image_path, model=model)

            # 保存raw
            raw_path = os.path.join(summary_dir, f"{slide_id}_raw.txt")
            with open(raw_path, 'w', encoding='utf-8') as f:
                f.write(raw_response)

            # 解析JSON
            summary = _parse_json(raw_response)
            summary["slide_id"] = slide_id
            summary["deck_name"] = slide_info.get("deck_name", "")
            summary["slide_no"] = slide_info.get("slide_no", 0)

            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)

            success += 1

        except Exception as e:
            print(f"    ✗ Error: {e}")
            # 写error记录
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "slide_id": slide_id,
                    "error": str(e),
                    "quality_for_learning": "exclude",
                    "exclude_reason": f"VLM analysis failed: {e}",
                }, f, ensure_ascii=False, indent=2)
            errors += 1

    print(f"\n=== VLM Summary Complete ===")
    print(f"Success: {success}, Errors: {errors}")


def _parse_json(text):
    """从VLM返回中解析JSON"""
    import re

    # 直接尝试
    try:
        return json.loads(text)
    except:
        pass

    # 从code block提取
    match = re.search(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except:
            pass

    # 找{...}
    start = text.find('{')
    end = text.rfind('}')
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except:
            pass

    raise ValueError("Cannot parse JSON from VLM response")
