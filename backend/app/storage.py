import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .db_models import Document, Review, ChatMessage, ReviewChanges


async def create_document(
    db: AsyncSession, document_id: str, filename: str, file_path: Path
) -> None:
    doc = Document(
        document_id=document_id,
        filename=filename,
        file_path=str(file_path),
        uploaded_at=datetime.now(timezone.utc),
    )
    db.add(doc)
    await db.commit()


async def get_document(db: AsyncSession, document_id: str) -> Optional[dict]:
    result = await db.execute(
        select(Document).where(Document.document_id == document_id)
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        return None
    return {
        "document_id": doc.document_id,
        "filename": doc.filename,
        "file_path": doc.file_path,
        "uploaded_at": doc.uploaded_at,
    }


async def save_review(db: AsyncSession, document_id: str, content: str) -> None:
    result = await db.execute(select(Review).where(Review.document_id == document_id))
    review = result.scalar_one_or_none()
    if review:
        review.content = content
    else:
        review = Review(document_id=document_id, content=content)
        db.add(review)
    await db.commit()


async def get_review(db: AsyncSession, document_id: str) -> Optional[str]:
    result = await db.execute(select(Review).where(Review.document_id == document_id))
    review = result.scalar_one_or_none()
    return review.content if review else None


async def save_changes(db: AsyncSession, document_id: str, changes: str):

    change_hash = hashlib.sha256(changes.encode("utf-8")).hexdigest()[:12]
    result = await db.execute(
        select(ReviewChanges).where(ReviewChanges.change_hash == change_hash)
    )

    old_review_change = result.scalar_one_or_none()

    if old_review_change: return 

    new_review_change = ReviewChanges(
        change_hash=change_hash, document_id=document_id, changes=changes
    )
    db.add(new_review_change)
    await db.commit()

async def get_changes(db: AsyncSession, document_id: str):

    result = await db.execute(
        select(ReviewChanges).where(ReviewChanges.document_id == document_id)
    )

    changes = result.scalars()

    return changes


async def add_chat_message(db: AsyncSession, role: str, content: str) -> None:
    msg = ChatMessage(role=role, content=content, created_at=datetime.now(timezone.utc))
    db.add(msg)
    await db.commit()


async def get_chat_history(db: AsyncSession) -> list[dict]:
    result = await db.execute(select(ChatMessage).order_by(ChatMessage.id))
    rows = result.scalars().all()
    return [
        {"role": row.role, "content": row.content, "created_at": row.created_at}
        for row in rows
    ]
