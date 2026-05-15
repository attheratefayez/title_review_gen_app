from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import ChatRequest, ChatResponse, ChatHistoryResponse
from ..storage import add_chat_message, get_chat_history

router = APIRouter(prefix="/api/chat", tags=["chat"])
DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def send_message(payload: ChatRequest, db: DbDep = None):
    await add_chat_message(db, "user", payload.message)

    response_text = (
        f"Thank you for your message. I've analyzed the document and here are my thoughts:\n\n"
        f"> {payload.message}\n\n"
        f"Based on the document review, I recommend focusing on the key areas mentioned "
        f"in the review draft. Would you like me to expand on any specific section?"
    )

    await add_chat_message(db, "assistant", response_text)

    return ChatResponse(response=response_text)


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history_endpoint(db: DbDep = None):
    messages = await get_chat_history(db)
    return ChatHistoryResponse(messages=messages)
