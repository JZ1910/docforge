from pathlib import Path

from pipeline.extractors.native import NativeExtractor
from pipeline.tests.fixtures import make_native_pdf


def test_native_extractor(tmp_path: Path):
    p = tmp_path / "native.pdf"
    text = "DocForge extraction test page"
    make_native_pdf(p, text=text)
    extractor = NativeExtractor()
    pages = extractor.extract(p)
    assert pages
    assert pages[0].page_number == 1
    assert text in pages[0].text
