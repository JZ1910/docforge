"""QualityScorer computes per-page quality scores with sub-scores."""
from __future__ import annotations

import logging
import statistics
from typing import Tuple

from langdetect import detect_langs, LangDetectException

from ..models.quality import QualityScore

LOGGER = logging.getLogger(__name__)

# Constants
QUALITY_THRESHOLD = 0.6


class QualityScorer:
    """Compute a QualityScore for a block of text.

    Methods
    -------
    score(text: str) -> QualityScore
        Returns a QualityScore dataclass with sub-scores and reasoning.
    """

    def score(self, text: str) -> QualityScore:
        text = text or ""
        total_chars = max(1, len(text))
        alpha_chars = sum(1 for c in text if c.isalpha())
        char_distribution_score = alpha_chars / total_chars

        # Word length score
        words = [w for w in text.split() if w]
        if words:
            mean_len = statistics.mean(len(w) for w in words)
            word_length_score = max(0.0, 1.0 - abs(mean_len - 6.0) / 6.0)
        else:
            mean_len = 0.0
            word_length_score = 0.0

        # Language confidence
        language_confidence = 0.0
        lang_reason = ""
        try:
            # Guard against short text: langdetect is unreliable with < 20 words
            if len(words) < 20:
                language_confidence = 0.5
                lang_reason = f"Text too short for reliable language detection ({len(words)} words, minimum 20)"
            # If the text is heavily non-alphabetic, skip trusting language detector
            elif char_distribution_score < 0.2:
                language_confidence = 0.3
                lang_reason = "Language detection skipped (low alphabetic char ratio)"
            else:
                langs = detect_langs(text)
                if langs:
                    best = langs[0]
                    language_confidence = float(best.prob)
                    lang_reason = f"Language {best.lang} confidence {best.prob:.2f}"
                else:
                    language_confidence = 0.3
                    lang_reason = "Language detection returned no candidates"
        except LangDetectException:
            language_confidence = 0.3
            lang_reason = "Language detection failed (text too short or garbled)"

        # Penalize language confidence when many words contain digits (OCR artifacts)
        digit_words = sum(1 for w in words if any(c.isdigit() for c in w))
        digit_word_ratio = (digit_words / len(words)) if words else 0.0
        if digit_word_ratio > 0.2:
            language_confidence = language_confidence * max(0.0, 1.0 - digit_word_ratio)
            lang_reason += f"; reduced for digit_word_ratio={digit_word_ratio:.2f}"

        overall = 0.4 * char_distribution_score + 0.3 * word_length_score + 0.3 * language_confidence
        flagged = overall < QUALITY_THRESHOLD

        reasoning_parts = []
        reasoning_parts.append(f"Char distribution {char_distribution_score:.2f}")
        reasoning_parts.append(f"Mean word length {mean_len:.2f} -> score {word_length_score:.2f}")
        reasoning_parts.append(lang_reason)
        reasoning = "; ".join(reasoning_parts)

        score = QualityScore(
            overall=overall,
            char_distribution_score=char_distribution_score,
            word_length_score=word_length_score,
            language_confidence=language_confidence,
            flagged_for_review=flagged,
            reasoning=reasoning,
        )
        LOGGER.debug("Quality score: %s", score)
        return score
