from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Literal, Optional, Any

class ChatSessionBase(BaseModel):
    title: str

class ChatSessionResponse(ChatSessionBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SessionListResponse(BaseModel):
    items: list[ChatSessionResponse]
    total: int
    page: int
    limit: int
    pages: int

class SendMessageRequest(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: Literal['user', 'assistant']
    content: str
    sources: Optional[list[Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True
