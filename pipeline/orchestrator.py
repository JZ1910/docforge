"""Ingestion orchestrator: route -> extract -> score and assemble results."""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Dict

from .models.document import ExtractionResult, PageContent
from .models.quality import QualityScore
from .router.document_router import DocumentRouter
from .quality.scorer import QualityScorer
from .extractors.base import ExtractionError
from .extractors.native import NativeExtractor
from .extractors.markitdown_extractor import MarkItDownExtractor
from .extractors.ocr import TesseractExtractor

LOGGER = logging.getLogger(__name__)


class IngestionOrchestrator:
    """Orchestrates document classification, extraction, and quality scoring."""

    def __init__(self) -> None:
        self.router = DocumentRouter()
        self.scorer = QualityScorer()
        # Registry of extractor instances
        self.registry: Dict[str, object] = {
            "native": NativeExtractor(),
            "markitdown": MarkItDownExtractor(),
            "ocr": TesseractExtractor(),
        }

    def ingest(self, pdf_path: Path) -> ExtractionResult:
        """Run the ingestion pipeline on `pdf_path` and return `ExtractionResult`.

        Raises:
            ExtractionError: when an extractor fails; re-raised with context.
        """
        start_total = time.perf_counter()
        profile = self.router.classify(pdf_path)

        strategy = profile.recommended_strategy
        LOGGER.info("Selected strategy %s for %s", strategy, pdf_path)

        extractor = self.registry.get(strategy)
        if extractor is None:
            raise RuntimeError(f"No extractor registered for strategy {strategy}")

        try:
            pages: list[PageContent] = extractor.extract(pdf_path)  # type: ignore[arg-type]
        except ExtractionError as e:
            LOGGER.error("ExtractionError during ingestion: %s", e)
            # Re-raise with context
            raise ExtractionError(filename=str(pdf_path), strategy=strategy, original_exception=e)

        quality_scores: list[QualityScore] = [self.scorer.score(p.text) for p in pages]
        total_ms = (time.perf_counter() - start_total) * 1000.0

        result = ExtractionResult(
            profile=profile,
            pages=pages,
            quality_scores=quality_scores,
            total_extraction_time_ms=total_ms,
            strategy_used=strategy,
            errors=[],
        )
        LOGGER.info("Ingestion complete for %s: strategy=%s, pages=%d", pdf_path, strategy, len(pages))
        return result
