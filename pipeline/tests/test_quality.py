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
    assert score.language_confidence <= 0.3
    assert score.flagged_for_review is True
