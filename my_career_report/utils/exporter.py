# File: utils/exporter.py
from weasyprint import HTML
import os


def html_to_pdf(html_path: str, output_pdf: str) -> str:
    """Convert an HTML file to PDF and return the PDF path."""
    base_url = os.path.dirname(html_path)
    HTML(filename=html_path, base_url=base_url).write_pdf(output_pdf)
    return output_pdf
