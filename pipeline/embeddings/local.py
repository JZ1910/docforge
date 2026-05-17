from __future__ import annotations

from typing import List, Optional
import threading
import logging

from sentence_transformers import SentenceTransformer
from numpy import ndarray

from .base import EmbeddingProvider

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"


class LocalSentenceTransformer(EmbeddingProvider):
    """Local sentence-transformers based embedding provider.

    Lazy-loads the model on first use. Thread-safe.
    """

    _model: Optional[SentenceTransformer] = None
    _lock = threading.Lock()

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        self.model_name = model_name

    def _ensure_model(self) -> SentenceTransformer:
        if self._model is None:
            with self._lock:
                if self._model is None:
                    logger.info("Loading sentence-transformers model: %s", self.model_name)
                    self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        model = self._ensure_model()
        embs = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        # convert ndarray to nested lists
        return [list(map(float, vec)) for vec in embs]

    def embed_one(self, text: str) -> List[float]:
        model = self._ensure_model()
        vec = model.encode([text], show_progress_bar=False, convert_to_numpy=True)[0]
        return list(map(float, vec))
