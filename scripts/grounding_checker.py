"""Grounding Checker — verify that all content text is grounded in the source
input material, preventing LLM fabrication.

Adapted from huawei-ppt-generator/generator/grounding_checker.py to work with
our content.pptx.json structure (slides with layout-specific fields).

Usage:
    from grounding_checker import check_grounding
    report = check_grounding(content_json, input_text)
    # report = {total_slides, checked_claims, supported_claims,
    #           unsupported_claims, missing_information, warnings}
"""
import re
from typing import Any, Dict, List


def check_grounding(content: Dict[str, Any], input_text: str) -> Dict[str, Any]:
    """Check that all text in content.pptx.json is grounded in input_text.

    Returns a report dict with supported/unsupported claim counts and details.
    """
    result: Dict[str, Any] = {
        "total_slides": len(content.get("slides", [])),
        "checked_claims": 0,
        "supported_claims": 0,
        "unsupported_claims": [],
        "missing_information": [],
        "warnings": [],
        "support_rate": 0.0,
    }

    # Build input token index (2-gram and 3-gram for CJK, words for Latin).
    input_tokens: set = set()
    for i in range(len(input_text) - 1):
        input_tokens.add(input_text[i:i + 2])
    for i in range(len(input_text) - 2):
        input_tokens.add(input_text[i:i + 3])
    input_tokens.update(re.findall(r'[a-zA-Z]{3,}', input_text.lower()))

    for slide in content.get("slides", []):
        layout = slide.get("layout", "")
        if layout in ("cover", "closing"):
            continue

        texts = _extract_texts(slide)
        for text in texts:
            if len(text.strip()) < 4:
                continue
            result["checked_claims"] += 1
            if _is_grounded(text, input_text, input_tokens):
                result["supported_claims"] += 1
            elif _is_generic_statement(text):
                result["supported_claims"] += 1
            else:
                result["unsupported_claims"].append({
                    "slide_idx": slide.get("idx"),
                    "text": text[:120],
                })

    checked = result["checked_claims"]
    result["support_rate"] = (
        round(result["supported_claims"] / checked, 2) if checked > 0 else 1.0
    )
    if result["unsupported_claims"]:
        result["warnings"].append(
            f"{len(result['unsupported_claims'])} claims not found in input "
            f"(support rate: {result['support_rate']:.0%})"
        )
    return result


def _extract_texts(obj: Any, depth: int = 0) -> List[str]:
    """Recursively extract all meaningful text strings from a slide dict."""
    if depth > 5:
        return []
    texts: List[str] = []
    if isinstance(obj, str):
        if len(obj) > 3:
            texts.append(obj)
    elif isinstance(obj, list):
        for item in obj:
            texts.extend(_extract_texts(item, depth + 1))
    elif isinstance(obj, dict):
        skip_keys = {"idx", "layout", "slide_type", "source", "key_point",
                     "chapter", "number", "total", "animation", "section_title",
                     "color", "colors", "cover_image", "show_arc", "bg_image"}
        for k, v in obj.items():
            if k in skip_keys:
                continue
            texts.extend(_extract_texts(v, depth + 1))
    return texts


def _is_grounded(text: str, input_text: str, input_tokens: set) -> bool:
    """Check if text has sufficient overlap with input."""
    if text in input_text:
        return True
    # 2-gram coverage
    text_chars = set()
    for i in range(len(text) - 1):
        text_chars.add(text[i:i + 2])
    if not text_chars:
        return True
    overlap = text_chars & input_tokens
    return len(overlap) / len(text_chars) > 0.3


def _is_generic_statement(text: str) -> bool:
    """Generic structural text that doesn't need input support."""
    generic_patterns = [
        r'^(建议|对策|措施|方案|策略|路径|挑战|风险|问题|目标|原则|阶段|步骤)',
        r'(需要|应该|建议|可以|必须|优先|重点|核心|关键)',
        r'^(总结|摘要|概述|展望|小结|来源|数据)',
        r'^(背景|现状|趋势|影响|说明|备注|注释)',
        r'^[A-Z]{2,}$',  # acronyms like HCIA
    ]
    for pattern in generic_patterns:
        if re.search(pattern, text):
            return True
    return len(text) < 12
