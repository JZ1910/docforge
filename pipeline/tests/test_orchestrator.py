from pathlib import Path

from pipeline.orchestrator import IngestionOrchestrator
from pipeline.tests.fixtures import make_native_pdf


def test_orchestrator_end_to_end(tmp_path: Path):
    p = tmp_path / "native.pdf"
    text = "End-to-end DocForge test"
    make_native_pdf(p, text=text)
    orch = IngestionOrchestrator()
    result = orch.ingest(p)
    assert result.profile.recommended_strategy == "native"
    assert result.pages
    assert text in result.pages[0].text
    assert result.quality_scores[0].overall > 0.7
