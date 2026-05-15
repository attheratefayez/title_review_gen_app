from pydantic import BaseModel, Field
from datetime import datetime


class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    uploaded_at: datetime


class GenerateResponse(BaseModel):
    review: str


class ReviewContent(BaseModel):
    content: str = Field(..., description="Markdown content of the review")

class ReviewChangesContent(BaseModel):
    content: list = Field(..., description="Markdown content of the review changes")

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)


class ChatResponse(BaseModel):
    response: str


class ChatHistoryResponse(BaseModel):
    messages: list[ChatMessage]


class StatusResponse(BaseModel):
    status: str
