# DocForge Build Journal

## 2026-05-15

- Initialized project structure and foundation services
- Added pipeline FastAPI scaffold and Node chat service scaffold
- Created repository-level documentation and environment templates
- Verified health endpoints and initial git commit
## 2026-05-15 (continued)

- Implemented ingestion-core: Pydantic models, DocumentRouter,
	Extractor interface, Native/MarkItDown/Tesseract extractors, Textract
	& DeepSeek stubs, QualityScorer, IngestionOrchestrator, and tests.
- Resolved multiple installation issues: installed `python3.12-venv`,
	system build deps (`libfreetype-dev`, `libjpeg-dev`, `python3.12-dev`),
	and pinned package versions for compatibility.
- Notes: adjusted scanned-character threshold for synthetic test PDFs
	(configurable constant in router). MarkItDown and OCR are optional
	runtime dependencies; stubs demonstrate production swapability.
