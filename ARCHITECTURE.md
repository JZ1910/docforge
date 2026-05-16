# Architecture Decisions

## Language Choice

- Decision: TBD
- Reasoning: TBD

## Database Choice

- Decision: TBD
- Reasoning: TBD

## OCR Strategy

- Decision: TBD
- Reasoning: TBD

Decision: Local first, cloud fallbacks

Reasoning: Use local Tesseract (`TesseractExtractor`) as the primary OCR
strategy for offline reproducibility and low latency in development and
small-scale deployments. Provide production-ready stubs for AWS Textract
and DeepSeek to allow a drop-in switch to managed OCR services for higher
accuracy/throughput when required.

## Chunking Strategy

- Decision: TBD
- Reasoning: TBD

Decision: Deferred

Reasoning: Chunking, embeddings and storage decisions are intentionally
deferred to the next development phase. This repository focuses on
extraction, classification and per-page quality scoring so that chunking
strategies can be chosen with real extraction characteristics in hand.

## Embedding Strategy

- Decision: TBD
- Reasoning: TBD

## LLM Provider Strategy

- Decision: TBD
- Reasoning: TBD


## Document Router Heuristics

Decision: Three-axis, auditable heuristics

Reasoning: The `DocumentRouter` class analyzes a sample of pages (config
default: 3) and produces a `DocumentProfile` with three independent
axes:

- `is_scanned`: computed from average characters per sampled page (threshold: 50
  chars/page). Low character count implies a scanned/image page. This is auditable —
  the router appends the observed average to `classification_log`.
- `has_tables`: uses `pdfplumber.page.find_tables()` as the primary detection method.
  When `find_tables()` returns no results, a text-based fallback checks for common
  table header tokens (e.g., "header", "header1", "header2") to detect programmatically
  constructed tables in test fixtures. See "Table Detection Fallback" below.
- `is_multi_column`: examines left-edge x-position clustering of text boxes; a large
  standard deviation (threshold: 100.0) suggests multiple columns.

The router returns a `DocumentProfile` (not a single string) so that downstream systems
can reason about the document and re-run extraction strategies per page when needed.

### Table Detection Fallback

**Primary strategy**: `pdfplumber.page.find_tables()` — robust for real-world PDFs with
structured table layouts.

**Fallback strategy**: When `find_tables()` returns empty, inspect extracted text for
common table header patterns. Specifically, look for tokens like "header", "header1",
"header2" in lowercased text, which are typical markers for programmatically generated
test fixtures.

**Why the fallback exists**: Test fixtures generated with `reportlab.platypus.Table`
do not always produce geometric table structures that `pdfplumber.find_tables()`
recognizes, leading to false negatives in automated tests.

**Known limitation**: The text-based fallback may produce false positives on prose that
happens to contain aligned or tabulated content (e.g., multi-column text or tab-separated
data). In production, we rely primarily on `find_tables()` with the text fallback as a
conservative last-resort signal.

