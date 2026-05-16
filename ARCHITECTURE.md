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

- `is_scanned`: computed from average characters per sampled page (low
	character count implies a scanned/image page). This is auditable — the
	router appends the observed average to `classification_log`.
- `has_tables`: uses `pdfplumber.page.find_tables()` when available, with
	a text-based fallback to detect common table header tokens for
	programmatic fixtures.
- `is_multi_column`: examines left-edge x-position clustering of text
	boxes; a large standard deviation suggests multiple columns.

The router returns a `DocumentProfile` (not a single string) so that
downstream systems can reason about the document and re-run extraction
strategies per page when needed.
