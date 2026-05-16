# DocForge

DocForge is a foundation for a multi-strategy PDF ingestion pipeline with a citation-aware chat layer for RAG-based AI products. It is designed to route documents through the right extraction path, score extraction confidence, and preserve citation context for reliable answers.

## Problem Statement

Many enterprise and product use cases need PDF content to be searchable, answerable, and cite-aware. DocForge solves the PDF ingestion problem by building a modular ingestion pipeline, a vector-backed store, and a chat service that can return cited answers for documents at scale.

## Architecture Overview

```mermaid
flowchart TD
  A[PDF Upload / Source] --> B[Pipeline FastAPI]
  B --> C{Extraction Strategy}
  C --> D[Native PDF Extraction]
  C --> E[OCR Extraction]
  C --> F[Fallback / Hybrid]
  D --> G[Chunk + Score]
  E --> G
  F --> G
  G --> H[Postgres + pgvector]
  H --> I[Chat Service Express]
  I --> J[LLM Providers]
  J --> K[Groq Llama / Gemini]
  I --> L[Client UI / Dashboard]
```

## Stack

- Python 3.12, FastAPI, Uvicorn
- Node 20, Express
- Postgres 16 with pgvector
- Tesseract OCR + layout extraction strategy
- Groq Llama + Google Gemini for model A/B
- sentence-transformers embeddings
- Streamlit for dashboarding

## Setup

1. Clone the repo.
2. Copy `.env.example` to `.env` and add your API keys.
3. Install the Python pipeline dependencies:
   - `cd pipeline`
   - `python3 -m venv venv`
   - `source venv/bin/activate`
   - `pip install -r requirements.txt`
4. Install the chat service dependencies:
   - `cd chat-service`
   - `npm install`
5. Start the services:
   - `cd pipeline && source venv/bin/activate && uvicorn main:app --reload --port 8000`
   - `cd chat-service && npm run dev`

## Current status

- Foundation repo structure created
- Python FastAPI pipeline service scaffolded
- Node Express chat service scaffolded
- Dashboard and test corpus folders initialized
- Database and LLM integration planned but not implemented yet
