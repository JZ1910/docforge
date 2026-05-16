"""Test fixtures for generating simple PDFs programmatically."""
from __future__ import annotations

from pathlib import Path
from typing import Tuple

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, Paragraph, Spacer, PageTemplate, BaseDocTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PIL import Image, ImageDraw, ImageFont


TESTS_DIR = Path(__file__).resolve().parent

# Lorem ipsum text for realistic test PDFs (300+ characters)
LOREM_TEXT = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor "
    "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
    "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure "
    "dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
)


def make_native_pdf(path: Path, text: str = None) -> Path:
    if text is None:
        text = LOREM_TEXT
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 11)
    # Split text into multiple lines to ensure it fits and is readable
    lines = text.split('\n') if '\n' in text else [text]
    y_pos = height - 72
    for line in lines:
        if y_pos < 72:
            c.showPage()
            y_pos = height - 72
        c.drawString(72, y_pos, line)
        y_pos -= 15
    c.showPage()
    c.save()
    return path


def make_scanned_pdf(path: Path, text: str = None) -> Path:
    if text is None:
        text = "Scanned text example with some additional content to reach the character threshold"
    # Create an image with text and embed as PDF page
    img = Image.new("RGB", (600, 800), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    d.text((50, 50), text, fill=(0, 0, 0), font=font)
    img_path = path.with_suffix('.png')
    img.save(img_path)

    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    c.drawImage(str(img_path), 0, 0, width=width, height=height)
    c.showPage()
    c.save()
    img_path.unlink(missing_ok=True)
    return path


def make_table_pdf(path: Path) -> Path:
    data = [
        ["Header1", "Header2"],
        ["This is the first data cell", "This is the second data cell"],
        ["Another row first cell", "Another row second cell with more text"],
        ["Lorem ipsum dolor", "Sit amet consectetur"]
    ]
    t = Table(data)
    # render table onto canvas
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    t.wrapOn(c, width, height)
    t.drawOn(c, 72, height - 200)
    c.showPage()
    c.save()
    return path
