from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(12), unique=True, nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(12), unique=True, nullable=False, index=True)
    content = Column(Text, default="")

class ReviewChanges(Base):
    __tablename__ = "review_changes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    change_hash = Column(String(12), unique=True, nullable=False, index=True)
    document_id = Column(String(12), unique=False, nullable=False, index=False)
    changes = Column(Text, default="")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String(16), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
