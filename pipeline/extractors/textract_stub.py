"""Stub extractor for AWS Textract to demonstrate interface readiness."""
from __future__ import annotations

from pathlib import Path
from typing import List

from .base import Extractor, ExtractionError
from ..models.document import PageContent


class TextractExtractor:
    """Stub for Textract-based extraction.

    Raises NotImplementedError to indicate this is a placeholder. To
    implement: configure AWS credentials and use boto3 Textract client.
    """

    name = "textract"

    def extract(self, pdf_path: Path) -> List[PageContent]:
        raise NotImplementedError(
            "TextractExtractor not implemented. Set AWS_ACCESS_KEY_ID and AWS_REGION in .env, then implement using boto3 textract client. Interface: extract(Path) -> List[PageContent]."
        )
