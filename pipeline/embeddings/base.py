from __future__ import annotations

from typing import Protocol, List


class EmbeddingProvider(Protocol):
    """Protocol for embedding providers."""

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        ...

    def embed_one(self, text: str) -> List[float]:
        ...
