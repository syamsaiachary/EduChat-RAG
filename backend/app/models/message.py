import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.postgres import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(Enum('user', 'assistant', name='message_role'), nullable=False)
    content = Column(String, nullable=False)
    sources = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
