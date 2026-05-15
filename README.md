# Document Reviewer

A full-stack application for uploading title/legal documents, generating AI-powered title review reports, and discussing them via chat.

## Architecture

```
┌──────────┐     ┌────────────┐     ┌──────────────────┐
│  Vue 3   │────▶│  FastAPI   │────▶│   LLM Agent      │
│  (Vite)  │     │  Backend   │     │  (LangChain +    │
│          │     │            │     │   HuggingFace)    │
│  NGINX   │◀────│  SQLite    │     │   ChromaDB       │
│  (prod)  │     │  (async)   │     │                  │
└──────────┘     └────────────┘     └──────────────────┘
```

### Frontend (`ui/`)

- **Vue 3** (Composition API) + **Vite** + **Tailwind CSS**
- `md-editor-v3` for markdown review editing
- Axios-based API layer in `src/api/`
- Three main panels: Upload → Review Editor → Chat
- Status bar for transient notifications
- **Dev**: Vite proxies `/api` to `localhost:8000`
- **Prod**: NGINX serves the SPA and reverse-proxies `/api` to the backend

### Backend (`backend/`)

- **FastAPI** with async SQLAlchemy + aiosqlite
- SQLite database with 4 tables: `documents`, `reviews`, `review_changes`, `chat_messages`
- Pydantic V2 models for request/response validation
- File storage on disk (configurable via `UPLOAD_DIR`)
- Change tracking on review edits (SHA-256 content hashing)

### LLM App (`backend/app/llm_app/`)

Separate module for AI-powered title review generation. See its [README](backend/app/llm_app/README.md) for details.

- **PDF Ingestion** — text extraction via PaddleOCR / OpenDataLoader, chunked by section
- **Hybrid Retrieval** — BM25 + MMR with RRF reranking
- **Report Generation** — LangChain + HuggingFace (Qwen3-4B-Instruct) via LangGraph
- **ChromaDB** vector store for embeddings (Ollama)
- Falls back to `TestAgent` for small synthetic documents (feeds chunks directly)

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/documents/upload` | Upload PDF/PNG (max 2MB) |
| `POST` | `/api/documents/{id}/generate` | Generate AI title review |
| `GET` | `/api/documents/{id}/review` | Get saved review |
| `PUT` | `/api/documents/{id}/review` | Save review (tracks diffs) |
| `GET` | `/api/documents/{id}/changes` | Get change history |
| `POST` | `/api/chat` | Send chat message |
| `GET` | `/api/chat/history` | Get chat history |
| `GET` | `/health` | Health check |

## Quick Start

### Docker Compose (production-like)

```bash
docker compose up --build
```

Backend at `http://localhost:8000`, UI at `http://localhost:8080`.

### Local Development

**Backend:**
```bash
cd backend
uv sync
fastapi run --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd ui
npm install
npm run dev
```

**Mock server** (for frontend-only work):
```bash
node mock-server.js
```

## Tech Stack

- **Backend**: Python 3.13+, FastAPI, SQLAlchemy (async), aiosqlite, LangChain, LangGraph, HuggingFace, ChromaDB, Ollama
- **Frontend**: Vue 3, Vite, Tailwind CSS, Axios, md-editor-v3
- **Infra**: Docker, Docker Compose, NGINX
