"""TesseractExtractor: rasterize PDF pages and OCR with Tesseract."""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import List, Dict, Any

from pdf2image import convert_from_path
import pytesseract

from .base import Extractor, ExtractionError
from ..models.document import PageContent

LOGGER = logging.getLogger(__name__)

# Default DPI for rasterization
DEFAULT_DPI = 200


class TesseractExtractor:
    """Extractor that converts PDF pages to images and runs Tesseract OCR.

    Configurable via environment variables if needed. Produces per-page
    text and average word confidence in `raw_metadata`.
    """

    name = "ocr"

    def __init__(self, dpi: int = DEFAULT_DPI, lang: str = "eng") -> None:
        self.dpi = dpi
        self.lang = lang

    def extract(self, pdf_path: Path) -> List[PageContent]:
        start_total = time.perf_counter()
        if not pdf_path.exists():
            raise ExtractionError(filename=str(pdf_path), strategy=self.name, original_exception=FileNotFoundError(str(pdf_path)))

        try:
            pil_pages = convert_from_path(str(pdf_path), dpi=self.dpi)
        except Exception as e:
            LOGGER.error("pdf2image failed to render %s: %s", pdf_path, e)
            raise ExtractionError(filename=str(pdf_path), strategy=self.name, original_exception=e)

        pages_out: List[PageContent] = []
        for i, img in enumerate(pil_pages, start=1):
            start = time.perf_counter()
            try:
                text = pytesseract.image_to_string(img, lang=self.lang)
                data = pytesseract.image_to_data(img, lang=self.lang, output_type=pytesseract.Output.DICT)
                confs = [int(c) for c in data.get("conf", []) if c and c != "-1"]
                avg_conf = float(sum(confs)) / len(confs) / 100.0 if confs else 0.0
                raw_metadata: Dict[str, Any] = {"strategy": "tesseract", "avg_word_confidence": avg_conf}
                elapsed_ms = (time.perf_counter() - start) * 1000.0
                pages_out.append(
                    PageContent(
                        page_number=i,
                        text=text,
                        extraction_strategy=self.name,
                        extraction_time_ms=elapsed_ms,
                        raw_metadata=raw_metadata,
                    )
                )
            except pytesseract.TesseractNotFoundError as e:
                LOGGER.error("Tesseract not found: %s", e)
                raise ExtractionError(filename=str(pdf_path), strategy=self.name, page=i, original_exception=e)
            except Exception as e:
                LOGGER.error("Tesseract OCR failed on page %s of %s: %s", i, pdf_path, e)
                raise ExtractionError(filename=str(pdf_path), strategy=self.name, page=i, original_exception=e)

        total_ms = (time.perf_counter() - start_total) * 1000.0
        LOGGER.info("Tesseract extraction complete for %s: %d pages, %.1fms total", pdf_path, len(pages_out), total_ms)
        return pages_out
