"""Orchestrates the full extract → chunk → embed → store pipeline for PDFs."""
from __future__ import annotations

import time
import logging
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from .orchestrator import IngestionOrchestrator
from .chunking.base import Chunk
from .chunking.recursive import RecursiveCharacterChunker
from .embeddings.local import LocalSentenceTransformer
from .storage.database import SessionLocal
from .storage.repository import DocumentRepository, ChunkRepository
from .storage.models import Document
from .models.document import ExtractionResult

LOG = logging.getLogger(__name__)


class IndexingError(Exception):
    """Wraps pipeline stage failures with context (filename, stage, root cause)."""

    def __init__(self, filename: str, stage: str, root_cause: Exception) -> None:
        self.filename = filename
        self.stage = stage
        self.root_cause = root_cause
        super().__init__(self.__str__())

    def __str__(self) -> str:
        return (
            f"IndexingError at stage '{self.stage}' for '{self.filename}': "
            f"{type(self.root_cause).__name__}: {self.root_cause}"
        )


class IndexingOrchestrator:
    """Orchestrates the full extract → chunk → embed → store pipeline for a single PDF.

    The pipeline is transactional: if any database write fails, NO partial document
    is persisted. Logs per-stage timings at INFO level.

    Attributes:
        ingester: IngestionOrchestrator instance for extraction.
        chunker: RecursiveCharacterChunker instance for chunking.
        embedder: LocalSentenceTransformer instance for embedding.
    """

    def __init__(self) -> None:
        self.ingester = IngestionOrchestrator()
        self.chunker = RecursiveCharacterChunker()
        self.embedder = LocalSentenceTransformer()
        self.doc_repo = DocumentRepository
        self.chunk_repo = ChunkRepository

    def index(self, pdf_path: Path) -> tuple[Document, dict[str, float]]:
        """Run the full ingestion pipeline on one PDF.

        Args:
            pdf_path: filesystem path to a .pdf file

        Returns:
            Tuple of (persisted SQLAlchemy Document, timings_dict) where
            timings_dict contains per-stage timings in milliseconds:
            {
                "extraction_ms": float,
                "chunking_ms": float,
                "embedding_ms": float,
                "storage_ms": float,
                "total_ms": float,
                "chunk_count": int,
            }

        Raises:
            IndexingError: wraps any failure in extraction, chunking,
            embedding, or storage with context (filename, stage, root).
        """
        filename = pdf_path.name
        total_start = time.time()

        # === Stage 1: extraction ===
        try:
            stage_start = time.time()
            extraction_result: ExtractionResult = self.ingester.ingest(pdf_path)
            extraction_ms = (time.time() - stage_start) * 1000
        except Exception as e:
            raise IndexingError(filename, "extraction", e) from e

        # === Stage 2: chunking ===
        # Build a page_number -> page_quality_score map for robust lookup.
        # extraction_result.pages and .quality_scores are parallel lists in order
        # per the orchestrator's contract. We match by index alignment.
        try:
            stage_start = time.time()
            page_quality_lookup = {
                page.page_number: q_score.overall
                for page, q_score in zip(
                    extraction_result.pages,
                    extraction_result.quality_scores,
                )
            }

            all_chunks: list = []
            for page in extraction_result.pages:
                page_q = page_quality_lookup.get(page.page_number, 0.0)
                page_chunks = self.chunker.chunk(
                    text=page.text,
                    page_number=page.page_number,
                    source_filename=extraction_result.profile.filename,
                    page_quality_score=page_q,
                )
                all_chunks.extend(page_chunks)
            chunking_ms = (time.time() - stage_start) * 1000
        except Exception as e:
            raise IndexingError(filename, "chunking", e) from e

        # === Stage 3: embedding ===
        try:
            stage_start = time.time()
            if all_chunks:
                embeddings = self.embedder.embed_batch([c.text for c in all_chunks])
            else:
                embeddings = []
            embedding_ms = (time.time() - stage_start) * 1000
        except Exception as e:
            raise IndexingError(filename, "embedding", e) from e

        # === Stage 4: storage (transactional) ===
        session: Session = SessionLocal()
        storage_ms: Optional[float] = None
        try:
            stage_start = time.time()
            with session.begin():
                # Build extraction_result dict for repository
                extraction_dict = extraction_result.model_dump()
                extraction_dict["total_chunks"] = len(all_chunks)
                extraction_dict["avg_quality_score"] = (
                    sum(q.overall for q in extraction_result.quality_scores)
                    / len(extraction_result.quality_scores)
                    if extraction_result.quality_scores
                    else 0.0
                )

                doc_repo = self.doc_repo(session)
                document = doc_repo.create(extraction_dict)

                if all_chunks:
                    chunk_dicts = [
                        {
                            "text": c.text,
                            "chunk_index": c.chunk_index,
                            "char_start": c.char_start,
                            "char_end": c.char_end,
                            "page_number": c.page_number,
                            "page_quality_score": c.page_quality_score,
                            "token_count": c.token_count,
                        }
                        for c in all_chunks
                    ]
                    chunk_repo = self.chunk_repo(session)
                    chunk_repo.bulk_insert(chunk_dicts, document.id, embeddings)
            # After commit, refresh the document so caller can access chunks
            session.refresh(document)
            storage_ms = (time.time() - stage_start) * 1000
        except Exception as e:
            session.rollback()
            raise IndexingError(filename, "storage", e) from e
        finally:
            total_ms = (time.time() - total_start) * 1000
            LOG.info(
                "indexed %s — extraction=%.1fms chunking=%.1fms "
                "embedding=%.1fms storage=%.1fms total=%.1fms (chunks=%d)",
                filename,
                extraction_ms,
                chunking_ms,
                embedding_ms,
                storage_ms if storage_ms is not None else 0.0,
                total_ms,
                len(all_chunks),
            )
            session.close()

        # Build timings dict
        timings = {
            "extraction_ms": extraction_ms,
            "chunking_ms": chunking_ms,
            "embedding_ms": embedding_ms,
            "storage_ms": storage_ms if storage_ms is not None else 0.0,
            "total_ms": total_ms,
            "chunk_count": len(all_chunks),
        }
        
        return document, timings
