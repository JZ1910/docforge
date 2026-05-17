"""Semantic search retriever for RAG knowledge base."""
from __future__ import annotations

import logging
from typing import List

from pydantic import BaseModel
from sqlalchemy.orm import Session

from .embeddings.local import LocalSentenceTransformer
from .storage.repository import ChunkRepository
from .storage.database import SessionLocal

LOG = logging.getLogger(__name__)


class RetrievalResult(BaseModel):
    """Search result for a single chunk."""

    chunk_text: str
    source_filename: str
    page_number: int
    chunk_index: int
    quality_score: float
    similarity_score: float  # higher = more similar (= 1.0 - cosine_distance)


class Retriever:
    """Performs semantic search over the chunk store.

    Embeds the query, retrieves top-k similar chunks via pgvector cosine
    distance, filters by minimum quality, and returns results ordered by
    similarity descending.
    """

    def __init__(self) -> None:
        self.embedder = LocalSentenceTransformer()
        self.chunk_repo = ChunkRepository  # class, mirrors indexing_orchestrator pattern

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_quality: float = 0.6,
    ) -> List[RetrievalResult]:
        """Return up to top_k chunks most similar to the query.

        Args:
            query: natural language search query
            top_k: max number of results to return
            min_quality: chunks below this page_quality_score are excluded

        Returns:
            list[RetrievalResult] ordered by similarity_score descending.
            Empty list if no chunks meet the quality threshold (no raise).
        """
        # Handle empty query gracefully
        if not query or not query.strip():
            return []

        # Embed the query
        query_embedding = self.embedder.embed_one(query)

        # Search with proper session lifecycle
        session: Session = SessionLocal()
        try:
            repo = self.chunk_repo(session)
            raw_results = repo.search_similar(
                query_embedding, top_k=top_k, min_quality=min_quality
            )
        finally:
            session.close()

        # Map to RetrievalResult — adapt to whatever search_similar returns
        # search_similar returns List[Tuple[ChunkModel, float]] where float is cosine distance
        results: List[RetrievalResult] = []
        for chunk, distance in raw_results:
            results.append(
                RetrievalResult(
                    chunk_text=chunk.text,
                    source_filename=chunk.document.filename,  # via FK relationship
                    page_number=chunk.page_number,
                    chunk_index=chunk.chunk_index,
                    quality_score=chunk.page_quality_score,
                    similarity_score=1.0 - distance,
                )
            )

        # Enforce desc sort by similarity (DB usually returns this order, but be safe)
        results.sort(key=lambda r: r.similarity_score, reverse=True)
        return results
