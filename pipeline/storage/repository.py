from __future__ import annotations

from typing import List, Tuple
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select, func, text
from sqlalchemy.exc import SQLAlchemyError

from .models import Document as DocumentModel, Chunk as ChunkModel

logger = logging.getLogger(__name__)


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, extraction_result: dict) -> DocumentModel:
        try:
            doc = DocumentModel(
                filename=extraction_result["profile"]["filename"],
                page_count=extraction_result["profile"]["page_count"],
                strategy_used=extraction_result.get("strategy_used", ""),
                total_chunks=extraction_result.get("total_chunks", 0),
                avg_quality_score=extraction_result.get("avg_quality_score", 0.0),
                raw_extraction_result=extraction_result,
            )
            self.db.add(doc)
            self.db.flush()  # get id
            return doc
        except SQLAlchemyError as e:
            logger.exception("Failed to create document: %s", e)
            self.db.rollback()
            raise

    def get_by_filename(self, filename: str) -> DocumentModel | None:
        stmt = select(DocumentModel).where(DocumentModel.filename == filename)
        res = self.db.execute(stmt).scalars().first()
        return res

    def delete(self, document_id: str) -> None:
        try:
            stmt = select(DocumentModel).where(DocumentModel.id == document_id)
            doc = self.db.execute(stmt).scalars().first()
            if not doc:
                return
            self.db.delete(doc)
            self.db.flush()
        except SQLAlchemyError as e:
            logger.exception("Failed to delete document: %s", e)
            self.db.rollback()
            raise


class ChunkRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def bulk_insert(self, chunks: List[dict], document_id, embeddings: List[List[float]]) -> List[ChunkModel]:
        models: List[ChunkModel] = []
        try:
            for i, c in enumerate(chunks):
                m = ChunkModel(
                    document_id=document_id,
                    text=c["text"],
                    chunk_index=c["chunk_index"],
                    char_start=c["char_start"],
                    char_end=c["char_end"],
                    page_number=c["page_number"],
                    page_quality_score=c["page_quality_score"],
                    token_count=c["token_count"],
                    embedding=embeddings[i],
                )
                self.db.add(m)
                models.append(m)
            self.db.flush()
            return models
        except SQLAlchemyError as e:
            logger.exception("Failed to bulk insert chunks: %s", e)
            self.db.rollback()
            raise

    def search_similar(self, query_embedding: List[float], top_k: int = 5, min_quality: float = 0.0) -> List[Tuple[ChunkModel, float]]:
        # Use pgvector cosine distance (1 - cosine_similarity) ordering
        try:
            stmt = text(
                "SELECT id, document_id, text, chunk_index, char_start, char_end, page_number, page_quality_score, token_count, embedding <-> :vec as distance "
                "FROM chunks WHERE page_quality_score >= :min_quality ORDER BY embedding <-> :vec LIMIT :limit"
            )
            params = {"vec": query_embedding, "min_quality": min_quality, "limit": top_k}
            res = self.db.execute(stmt, params)
            rows = res.fetchall()
            results: List[Tuple[ChunkModel, float]] = []
            for r in rows:
                # map row to a lightweight object
                cid = r[0]
                chunk = self.db.get(ChunkModel, cid)
                distance = r[-1]
                results.append((chunk, float(distance)))
            return results
        except SQLAlchemyError as e:
            logger.exception("Failed to search similar chunks: %s", e)
            raise
