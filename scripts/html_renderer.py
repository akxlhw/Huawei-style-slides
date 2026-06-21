"""S4b: Render content.html.json to slides.html via Jinja2."""

from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape


def render_html(content: Dict[str, Any], output_dir: Path) -> Path:
    """Render a content.html.json dict to a self-contained slides.html file."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    template_dir = Path(__file__).resolve().parent.parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("slides.html.j2")

    slides = content.get("slides", [])
    title = slides[0].get("title", "Huawei HR PPT") if slides else "Huawei HR PPT"

    try:
        html = template.render(title=title, slides=slides, content=content)
    except TemplateNotFound as e:
        missing = getattr(e, "name", str(e))
        raise TemplateNotFound(
            f"Missing HTML template for slide_type: {missing}. "
            f"Expected a template file at templates/slide-types/<slide_type>.html.j2"
        ) from e

    html_path = output_dir / "slides.html"
    html_path.write_text(html, encoding="utf-8")
    return html_path
