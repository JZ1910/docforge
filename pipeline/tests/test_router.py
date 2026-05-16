from pathlib import Path
import tempfile

from pipeline.router.document_router import DocumentRouter
from pipeline.tests.fixtures import make_native_pdf, make_scanned_pdf, make_table_pdf


def test_router_native(tmp_path: Path):
    p = tmp_path / "native.pdf"
    make_native_pdf(p, text="This is a native PDF with searchable text.")
    router = DocumentRouter()
    profile = router.classify(p)
    assert profile.recommended_strategy == "native"
    assert profile.is_scanned is False


def test_router_scanned(tmp_path: Path):
    p = tmp_path / "scanned.pdf"
    make_scanned_pdf(p, text="This looks like a scanned image.")
    router = DocumentRouter()
    profile = router.classify(p)
    assert profile.recommended_strategy == "ocr"
    assert profile.is_scanned is True


def test_router_table(tmp_path: Path):
    p = tmp_path / "table.pdf"
    make_table_pdf(p)
    router = DocumentRouter()
    profile = router.classify(p)
    assert profile.has_tables is True
    assert profile.recommended_strategy == "markitdown"
