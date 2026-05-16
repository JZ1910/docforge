"""Pydantic model for quality scoring per page."""
from __future__ import annotations

from pydantic import BaseModel, Field, confloat


class QualityScore(BaseModel):
    """Structured quality score with sub-scores for debugging.

    Attributes:
        overall: Weighted overall score in [0.0, 1.0].
        char_distribution_score: Ratio of alphabetic characters to total.
        word_length_score: Score based on average word length.
        language_confidence: Highest language detection confidence.
        flagged_for_review: True if overall < QUALITY_THRESHOLD.
        reasoning: Human readable explanation for the score.
    """

    overall: confloat(ge=0.0, le=1.0) = Field(..., description="Overall quality score 0.0-1.0")
    char_distribution_score: confloat(ge=0.0, le=1.0) = Field(..., description="Alpha/total character ratio score")
    word_length_score: confloat(ge=0.0, le=1.0) = Field(..., description="Score for mean word length")
    language_confidence: confloat(ge=0.0, le=1.0) = Field(..., description="Language detection confidence")
    flagged_for_review: bool = Field(..., description="True if page should be flagged for human review")
    reasoning: str = Field(..., description="Human-readable explanation of the scoring decision")
