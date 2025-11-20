from __future__ import annotations

from datetime import datetime
from pathlib import Path

from weasyprint import HTML


def render_pdf(summary: str, raw_text: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    html = f"""
    <h1>Medical Report - {datetime.now().strftime('%Y-%m-%d')}</h1>
    <h2>AI Summary</h2>
    <pre>{summary}</pre>
    <h2>Raw OCR Text</h2>
    <pre style="font-size:10px">{raw_text}</pre>
    """
    HTML(string=html).write_pdf(str(destination))
    return destination
