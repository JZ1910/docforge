"""Extractor protocol and ExtractionError used by all extractors."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Protocol, Optional

from ..models.document import PageContent

LOGGER = logging.getLogger(__name__)


class ExtractionError(Exception):
    """Typed exception for extraction failures.

    Attributes:
        filename: The PDF filename being processed.
        page: Optional page number where the error occurred.
        strategy: Name of the extractor strategy.
        original_exception: The caught exception instance.
    """

    def __init__(self, filename: str, strategy: str, page: Optional[int] = None, original_exception: Optional[Exception] = None) -> None:
        self.filename = filename
        self.page = page
        self.strategy = strategy
        self.original_exception = original_exception
        super().__init__(str(self))

    def __str__(self) -> str:  # pragma: no cover - formatting
        base = f"ExtractionError(strategy={self.strategy}, filename={self.filename}"
        if self.page is not None:
            base += f", page={self.page}"
        if self.original_exception:
            base += f", cause={type(self.original_exception).__name__}: {self.original_exception}"
        base += ")"
        return base


class Extractor(Protocol):
    """Interface every extractor must implement.

    Implementations must be stateless: calling `extract` multiple times with
    the same PDF should be idempotent.
    """

    name: str

    def extract(self, pdf_path: Path) -> List[PageContent]:
        """Extract text and metadata from `pdf_path` into per-page `PageContent`.

        Args:
            pdf_path: Path to the PDF file to extract.

        Returns:
            List[PageContent]: extracted content per page.
        """
        ...
