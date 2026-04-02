from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Literal, Optional

class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    file_type: str
    file_size_bytes: Optional[int] = None
    chunk_count: Optional[int] = None
    status: Literal['processing', 'ready', 'failed']
    uploaded_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    page: int
    limit: int
    pages: int

class TextInputRequest(BaseModel):
    text: str
    filename: str
