"""MarkItDownExtractor converts PDFs to markdown and splits into pages."""
from __future__ import annotations

import logging
import subprocess
import time
from pathlib import Path
from typing import List

try:
    import markitdown  # type: ignore
    HAS_MARKITDOWN = True
except Exception:
    HAS_MARKITDOWN = False

from .base import Extractor, ExtractionError
from ..models.document import PageContent

LOGGER = logging.getLogger(__name__)


class MarkItDownExtractor:
    """Extractor that uses MarkItDown to convert a PDF to markdown.

    If MarkItDown is not available, falls back to extracting text via pdfplumber
    and returns a single page with a warning in raw_metadata.
    """

    name = "markitdown"

    def extract(self, pdf_path: Path) -> List[PageContent]:
        start_total = time.perf_counter()
        if not pdf_path.exists():
            raise ExtractionError(filename=str(pdf_path), strategy=self.name, original_exception=FileNotFoundError(str(pdf_path)))

        if HAS_MARKITDOWN:
            try:
                # markitdown has CLI-style usage; attempt to call its to_markdown function if available
                try:
                    md = markitdown.to_markdown(str(pdf_path))  # type: ignore
                except Exception:
                    # fallback to CLI
                    proc = subprocess.run(["markitdown", str(pdf_path)], capture_output=True, text=True, check=True)
                    md = proc.stdout

                # Split on form-feed or common page-break markers
                parts = [p for p in md.split("\f") if p.strip()]
                pages: List[PageContent] = []
                if parts:
                    for i, part in enumerate(parts, start=1):
                        elapsed_ms = (time.perf_counter() - start_total) * 1000.0
                        pages.append(
                            PageContent(
                                page_number=i,
                                text=part,
                                extraction_strategy=self.name,
                                extraction_time_ms=elapsed_ms,
                                raw_metadata={"strategy": "markitdown", "format": "markdown"},
                            )
                        )
                else:
                    # No page breaks found — return as single page
                    elapsed_ms = (time.perf_counter() - start_total) * 1000.0
                    pages.append(
                        PageContent(
                            page_number=1,
                            text=md,
                            extraction_strategy=self.name,
                            extraction_time_ms=elapsed_ms,
                            raw_metadata={"strategy": "markitdown", "format": "markdown", "warning": "no page breaks detected"},
                        )
                    )
                return pages
            except subprocess.CalledProcessError as e:
                LOGGER.error("MarkItDown CLI failed: %s", e)
                raise ExtractionError(filename=str(pdf_path), strategy=self.name, original_exception=e)
            except Exception as e:
                LOGGER.error("MarkItDown extraction failed: %s", e)
                raise ExtractionError(filename=str(pdf_path), strategy=self.name, original_exception=e)
        else:
            # Fallback using pdfplumber
            try:
                import pdfplumber

                with pdfplumber.open(pdf_path) as pdf:
                    text = "\n\n".join([(p.extract_text() or "") for p in pdf.pages])
                    elapsed_ms = (time.perf_counter() - start_total) * 1000.0
                    return [
                        PageContent(
                            page_number=1,
                            text=text,
                            extraction_strategy=self.name,
                            extraction_time_ms=elapsed_ms,
                            raw_metadata={"strategy": "markitdown_fallback", "format": "text", "warning": "markitdown not installed; returned single page"},
                        )
                    ]
            except Exception as e:
                raise ExtractionError(filename=str(pdf_path), strategy=self.name, original_exception=e)
