from __future__ import annotations

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base
from pgvector.sqlalchemy import Vector


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, unique=True, index=True, nullable=False)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    page_count = Column(Integer, nullable=False)
    strategy_used = Column(String, nullable=False)
    total_chunks = Column(Integer, nullable=False)
    avg_quality_score = Column(Float, nullable=False)
    raw_extraction_result = Column(JSONB, nullable=False)

    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    text = Column(String, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    char_start = Column(Integer, nullable=False)
    char_end = Column(Integer, nullable=False)
    page_number = Column(Integer, index=True, nullable=False)
    page_quality_score = Column(Float, nullable=False)
    token_count = Column(Integer, nullable=False)
    embedding = Column(Vector(384))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    document = relationship("Document", back_populates="chunks")
