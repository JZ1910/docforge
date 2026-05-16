"""Pydantic models for document metadata and extraction results."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, Field, conint


class DocumentProfile(BaseModel):
    """DocumentProfile captures classification metadata for a PDF.

    Attributes:
        filename: The PDF filename.
        page_count: Number of pages in the document.
        is_scanned: True when most sampled pages lack extractable text.
        has_tables: True if any sampled page contains tables.
        is_multi_column: True if text blocks indicate multiple columns.
        recommended_strategy: The extraction strategy recommended by the router.
        classification_log: Human-readable audit log explaining decisions.
    """

    filename: str = Field(..., description="PDF filename")
    page_count: int = Field(..., description="Total number of pages in PDF")
    is_scanned: bool = Field(..., description="Whether the document appears scanned")
    has_tables: bool = Field(..., description="Whether any sampled page contains tables")
    is_multi_column: bool = Field(..., description="Whether pages appear multi-column")
    recommended_strategy: Literal["native", "markitdown", "ocr"] = Field(
        ..., description="Recommended extraction strategy"
    )
    classification_log: List[str] = Field(default_factory=list, description="Audit log for decisions")


class PageContent(BaseModel):
    """Text and metadata extracted from a single page.

    Attributes:
        page_number: 1-indexed page number.
        text: Extracted text for the page.
        extraction_strategy: Name of extractor used.
        extraction_time_ms: Time taken to extract this page in milliseconds.
        raw_metadata: Extractor-specific metadata (e.g., confidences).
    """

    page_number: conint(ge=1) = Field(..., description="1-indexed page number")
    text: str = Field(..., description="Extracted text content for the page")
    extraction_strategy: str = Field(..., description="Extractor strategy name used")
    extraction_time_ms: float = Field(..., description="Extraction time in milliseconds")
    raw_metadata: Dict[str, Any] = Field(default_factory=dict, description="Extractor-specific metadata")


class ExtractionResult(BaseModel):
    """Full result of an extraction pass for a document."""

    profile: DocumentProfile = Field(..., description="Document classification profile")
    pages: List[PageContent] = Field(..., description="Per-page extracted content")
    quality_scores: List["QualityScore"] = Field(..., description="Per-page quality scores")
    total_extraction_time_ms: float = Field(..., description="Total extraction time in milliseconds")
    strategy_used: str = Field(..., description="Strategy used for extraction")
    errors: List[str] = Field(default_factory=list, description="Non-fatal warnings encountered during extraction")

    class Config:
        arbitrary_types_allowed = True


# Forward references
from .quality import QualityScore

ExtractionResult.update_forward_refs()
