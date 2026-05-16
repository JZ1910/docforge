from pathlib import Path

from pipeline.orchestrator import IngestionOrchestrator
from pipeline.tests.fixtures import make_native_pdf, LOREM_TEXT


def test_orchestrator_end_to_end(tmp_path: Path):
    p = tmp_path / "native.pdf"
    # Use LOREM_TEXT to ensure enough characters for the router's is_scanned heuristic
    make_native_pdf(p)
    orch = IngestionOrchestrator()
    result = orch.ingest(p)
    assert result.profile.recommended_strategy == "native"
    assert result.pages
    # Verify the extracted text contains some of the lorem ipsum content
    assert "Lorem ipsum" in result.pages[0].text
    assert result.quality_scores[0].overall > 0.7
