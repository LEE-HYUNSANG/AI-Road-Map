# File: utils/renderer.py
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def render_html(data: dict, cfg: dict) -> str:
    """Render the report HTML using Jinja2 templates."""
    project_root = Path(__file__).resolve().parents[1]
    env = Environment(loader=FileSystemLoader(project_root / "templates"))
    template = env.get_template("report.html")
    # Resolve the CSS path relative to the output HTML so both the browser and
    # WeasyPrint can correctly load the stylesheet.  Without this, the
    # generated HTML contained a broken path (e.g. ``templates/assets/style.css``)
    # which caused the PDF to render without colours or layout.
    style_src = project_root / cfg["styles"]["css"]
    rel_style = os.path.relpath(
        style_src, start=os.path.dirname(cfg["output"]["html"])
    ).replace(os.sep, "/")
    styles = dict(cfg["styles"])
    styles["css"] = rel_style

    # Convert chart image paths to be relative to the HTML output.  WeasyPrint
    # resolves relative URLs based on the HTML file location, so using relative
    # paths keeps the generated report portable.  The original configuration may
    # contain absolute paths, so we normalise them here.
    charts_cfg = dict(cfg["charts"])
    if "images" in charts_cfg:
        rel_images = {
            key: os.path.relpath(
                path, start=os.path.dirname(cfg["output"]["html"])
            ).replace(os.sep, "/")
            for key, path in charts_cfg["images"].items()
        }
        charts_cfg["images"] = rel_images

    scripts_cfg = dict(cfg.get("scripts", {}))
    if "chartjs" in scripts_cfg:
        rel_script = os.path.relpath(
            scripts_cfg["chartjs"], start=os.path.dirname(cfg["output"]["html"])
        ).replace(os.sep, "/")
        scripts_cfg["chartjs"] = rel_script

    html = template.render(
        **data, styles=styles, charts=charts_cfg, scripts=scripts_cfg
    )
    output_path = cfg["output"]["html"]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path
