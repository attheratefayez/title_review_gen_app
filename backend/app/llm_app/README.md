# LLM Title Review App

An AI-powered title review report generator. Ingests legal PDF documents, chunks them by section, generates embeddings via Ollama, stores them in ChromaDB, and uses LangChain with HuggingFace (Qwen3-4B-Instruct) to produce professional title review reports.

## Features

- **PDF Ingestion** — Extracts text via PaddleOCR / OpenDataLoader, chunks by section or element
- **Hybrid Retrieval** — BM25 + MMR retrieval with RRF-based reranking for relevant document lookup
- **Report Generation** — Produces structured title reviews: lien tables, risks, marketability verdict, closing instructions
- **Checkpointing** — LangGraph-based checkpoints persisted via SQLite (disabled by default)

## Structure

```
llm_app/
├── agent.py                # DraftGenAgent - LLM agent for report generation
├── retrival.py             # HybridRetriever - BM25 + MMR + RRF scoring
├── config.py               # Paths, model names, system prompt
├── test_agent.py           # Test agent for small synthetic docs (bypasses retrieval)
├── ingestion/
│   ├── pdf_chunking.py     # PDF → JSON → chunked Documents
│   └── ingestion_pipeline.py # Full pipeline: load → chunk → embed → index
├── assets/
│   ├── dataset/            # Input PDFs
│   └── vecdb/              # ChromaDB persistence
└── main.py                 # Entry point
```

## Setup

```bash
uv sync
```

Requires Python 3.13+. Ensure Ollama is running with the embedding model (`qwen3-embedding:0.6b`).

## Agent Usage

```python
from agent import DraftGenAgent

agent = DraftGenAgent()
result = agent.invoke("Analyze this title document for ARM mortgage")
```

**For small synthetic documents (where retrieval performs poorly), use `TestAgent` which feeds chunks directly into the LLM:**

```python
from test_agent import TestAgent

agent = TestAgent("assets/dataset/synthetic_data/ARM Mortgage with Rate Adjustments.pdf")
report = agent.generate_report()
print(report)
```

Or via CLI:
```bash
uv run main.py
```
