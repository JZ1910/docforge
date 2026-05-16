"""Test fixtures for generating simple PDFs programmatically."""
from __future__ import annotations

from pathlib import Path
from typing import Tuple

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table
from PIL import Image, ImageDraw, ImageFont


TESTS_DIR = Path(__file__).resolve().parent


def make_native_pdf(path: Path, text: str = "Hello from DocForge") -> Path:
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 12)
    c.drawString(72, height - 72, text)
    c.showPage()
    c.save()
    return path


def make_scanned_pdf(path: Path, text: str = "Scanned text example") -> Path:
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
    data = [["Header1", "Header2"], ["a", "b"], ["c", "d"]]
    t = Table(data)
    # render table onto canvas
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    t.wrapOn(c, width, height)
    t.drawOn(c, 72, height - 200)
    c.showPage()
    c.save()
    return path
