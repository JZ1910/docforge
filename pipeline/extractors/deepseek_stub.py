"""Stub extractor for DeepSeek OCR API integration."""
from __future__ import annotations

from pathlib import Path
from typing import List

from .base import Extractor, ExtractionError
from ..models.document import PageContent


class DeepSeekExtractor:
    """Stub for DeepSeek OCR integration.

    Raises NotImplementedError to show a production-swappable interface.
    """

    name = "deepseek"

    def extract(self, pdf_path: Path) -> List[PageContent]:
        raise NotImplementedError(
            "DeepSeekExtractor not implemented. Implement API client and return List[PageContent]."
        )
