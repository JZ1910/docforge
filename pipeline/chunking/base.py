from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, List


@dataclass
class Chunk:
    """Pydantic-like dataclass representing a chunk of text.

    Fields:
        text: the chunk text
        chunk_index: index within the page (0-based)
        char_start: start char offset within the original page text
        char_end: end char offset (exclusive)
        page_number: which page this chunk came from (1-based)
        source_filename: original filename
        page_quality_score: the quality score inherited from the page
        token_count: estimated token count for the chunk
    """
    text: str
    chunk_index: int
    char_start: int
    char_end: int
    page_number: int
    source_filename: str
    page_quality_score: float
    token_count: int


class Chunker(Protocol):
    """Protocol for chunking page-level text into Chunk objects."""

    def chunk(self, text: str, page_number: int, source_filename: str, page_quality_score: float) -> List[Chunk]:
        ...
