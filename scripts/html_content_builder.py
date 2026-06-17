"""S3b: Build content.html.json from outline."""

import json
from pathlib import Path
from typing import Dict, Any, List
from pptx_content_builder import BUILDERS as PPTX_BUILDERS


def build_html_content(outline: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    slides: List[Dict[str, Any]] = []
    for slide in outline["slides"]:
        layout = slide["layout"]
        builder = PPTX_BUILDERS.get(layout)
        if not builder:
            raise ValueError(f"Unsupported HTML slide_type: {layout}")
        data = builder(slide)
        data["idx"] = slide["idx"]
        data["slide_type"] = data.pop("layout")
        data["key_point"] = slide.get("key_point", "")
        data["animation"] = "fade-up" if layout != "cover" else "none"
        slides.append(data)

    content = {
        "brief": outline["brief"],
        "framework": outline.get("framework", "pyramid"),
        "slides": slides,
    }

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "content.html.json"
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    return content
