from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response

from .database import engine
from .db_models import Base
from .routers import documents, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    print("FastAPI application closing.")


app = FastAPI(
    title="Document Reviewer API",
    description="Backend for the LangChain Document Reviewer UI. "
    "Handles file uploads, LLM-powered title review generation, and chat.",
    version="0.0.1",
    lifespan=lifespan,
)

# NOTE: can avoid CORS here, cause NGINX is reversing-proxies

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)
