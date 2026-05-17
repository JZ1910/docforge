from __future__ import annotations

from typing import List
import logging

from .base import Chunk

logger = logging.getLogger(__name__)


# Constants
DEFAULT_TARGET_SIZE = 500
DEFAULT_OVERLAP = 50
_SPLIT_PRIORITIES = ["\n\n", "\n", ". ", " "]


class RecursiveCharacterChunker:
    """Chunker that recursively splits text to meet a target size while
    preserving accurate character offsets into the original page text.

    Splitting order: ['\n\n', '\n', '. ', ' ']
    """

    def __init__(self, target_size: int = DEFAULT_TARGET_SIZE, overlap: int = DEFAULT_OVERLAP) -> None:
        self.target_size = target_size
        self.overlap = overlap

    def chunk(self, text: str, page_number: int, source_filename: str, page_quality_score: float) -> List[Chunk]:
        if not text:
            return []

        spans = self._recursive_split(text)
        chunks: List[Chunk] = []
        for idx, (start, end) in enumerate(spans):
            chunk_text = text[start:end]
            token_count = max(1, len(chunk_text) // 4)
            chunks.append(
                Chunk(
                    text=chunk_text,
                    chunk_index=idx,
                    char_start=start,
                    char_end=end,
                    page_number=page_number,
                    source_filename=source_filename,
                    page_quality_score=page_quality_score,
                    token_count=token_count,
                )
            )
        return chunks

    def _recursive_split(self, text: str) -> List[tuple[int, int]]:
        """Return list of (start, end) spans that partition the text into
        chunks of roughly target_size with the configured overlap. Spans are
        computed as offsets into `text`.
        """
        n = len(text)
        spans: List[tuple[int, int]] = []

        def _split_range(start: int, end: int) -> None:
            length = end - start
            if length <= self.target_size:
                spans.append((start, end))
                return

            # try each splitter in priority order
            for splitter in _SPLIT_PRIORITIES:
                # search for splitter near the target split point
                split_pos = self._find_split_pos(text, start, end, splitter)
                if split_pos is not None and split_pos > start and split_pos < end:
                    _split_range(start, split_pos)
                    # for the right side, ensure overlap
                    right_start = max(split_pos - self.overlap, split_pos)
                    _split_range(right_start, end)
                    return

            # fallback: force split at target_size
            mid = start + self.target_size
            _split_range(start, mid)
            right_start = max(mid - self.overlap, mid)
            _split_range(right_start, end)

        _split_range(0, n)

        # merge adjacent spans to ensure contiguous, non-overlapping spans
        merged: List[tuple[int, int]] = []
        for s, e in spans:
            if not merged:
                merged.append((s, e))
            else:
                last_s, last_e = merged[-1]
                if s <= last_e:  # overlap or contiguous
                    merged[-1] = (last_s, max(last_e, e))
                else:
                    merged.append((s, e))

        # Now apply overlap by expanding spans except the first
        final_spans: List[tuple[int, int]] = []
        for i, (s, e) in enumerate(merged):
            if i == 0:
                final_spans.append((s, e))
            else:
                prev_s, prev_e = final_spans[-1]
                # overlap means start earlier
                new_s = max(s - self.overlap, prev_e)
                final_spans.append((new_s, e))

        return final_spans

    def _find_split_pos(self, text: str, start: int, end: int, splitter: str) -> int | None:
        """Find a splitter occurrence near the preferred split point.

        Prefer the last occurrence of splitter before target, but not before
        start; fall back to first occurrence after target within a small window.
        """
        target = start + self.target_size
        # clamp
        if target >= end:
            return None

        # search backwards for splitter
        try:
            before = text.rfind(splitter, start, min(target + 1, end))
        except Exception:
            before = -1

        if before != -1:
            return before + len(splitter)  # split after the splitter

        # search forward up to target + 200 chars
        after = text.find(splitter, target, min(end, target + 200))
        if after != -1:
            return after + len(splitter)

        return None
