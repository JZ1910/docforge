"""NativeExtractor: extract text from digital PDFs using pdfplumber."""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import List

import pdfplumber

from .base import Extractor, ExtractionError
from ..models.document import PageContent

LOGGER = logging.getLogger(__name__)


class NativeExtractor:
    """Extractor that uses pdfplumber to extract text from PDFs.

    This extractor is intended for native/digital PDFs with text layers.
    """

    name = "native"

    def extract(self, pdf_path: Path) -> List[PageContent]:
        """Extract text per page and return `PageContent` list.

        Raises:
            ExtractionError: on known pdfplumber errors.
        """
        if not pdf_path.exists():
            raise ExtractionError(filename=str(pdf_path), strategy=self.name, original_exception=FileNotFoundError(str(pdf_path)))

        pages_out: List[PageContent] = []
        total_start = time.perf_counter()

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    start = time.perf_counter()
                    try:
                        text = page.extract_text() or ""
                        w, h = page.width, page.height
                        raw_metadata = {"strategy": "pdfplumber", "page_dimensions": [w, h]}
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
                    except Exception as e:
                        LOGGER.error("Error extracting page %s from %s: %s", i, pdf_path, e)
                        raise ExtractionError(filename=str(pdf_path), strategy=self.name, page=i, original_exception=e)
        except pdfplumber.pdf.PDFSyntaxError as e:
            LOGGER.error("PDFSyntaxError opening %s: %s", pdf_path, e)
            raise ExtractionError(filename=str(pdf_path), strategy=self.name, original_exception=e)

        total_ms = (time.perf_counter() - total_start) * 1000.0
        LOGGER.info("Native extraction complete for %s: %d pages, %.1fms total", pdf_path, len(pages_out), total_ms)
        return pages_out
