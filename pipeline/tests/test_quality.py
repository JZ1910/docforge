from pipeline.quality.scorer import QualityScorer


def test_quality_clean_text():
    scorer = QualityScorer()
    text = "The quick brown fox jumps over the lazy dog. This is well-formed English text."
    score = scorer.score(text)
    assert score.overall > 0.7
    assert score.flagged_for_review is False


def test_quality_ocr_garbage():
    scorer = QualityScorer()
    text = "Th3 d0g ran fast with numb3r5"
    score = scorer.score(text)
    assert score.overall < 0.7


def test_quality_noise():
    scorer = QualityScorer()
    text = "�������� ������"
    score = scorer.score(text)
    # Short text triggers the language guard, so confidence is 0.5 (not 0.3)
    assert score.language_confidence == 0.5
    assert score.flagged_for_review is True

def test_quality_short_text():
    """Test that langdetect is guarded against short text instability."""
    scorer = QualityScorer()
    # Short text that langdetect may misclassify
    text = "Sample PDF for /extract endpoint test — DocForge"
    score = scorer.score(text)
    # Language confidence should be 0.5 (guard value) for short text
    assert score.language_confidence == 0.5
    # Reasoning should mention the short-text warning
    assert "too short for reliable language detection" in score.reasoning.lower()