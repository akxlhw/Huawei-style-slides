"""Validate generated HTML deck."""

import re
from pathlib import Path
from typing import Any, Dict


def validate_html(html_path: Path, expected_slides: int) -> Dict[str, Any]:
    """Check that the generated HTML has the expected structure and slide count."""
    text = Path(html_path).read_text(encoding="utf-8")
    slides = re.findall(r'<section[^>]*class=["\']slide["\']', text)
    errors = []
    if len(slides) != expected_slides:
        errors.append(
            f"Slide count mismatch: expected {expected_slides}, got {len(slides)}"
        )
    if "<html" not in text:
        errors.append("Missing <html> tag")
    if "deck-stage" not in text and "SlidePresentation" not in text:
        errors.append("Missing slide controller")
    return {"ok": len(errors) == 0, "errors": errors, "slide_count": len(slides)}
