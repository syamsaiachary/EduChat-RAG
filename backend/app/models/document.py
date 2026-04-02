import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.postgres import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    chunk_count = Column(Integer, nullable=True)
    status = Column(Enum('processing', 'ready', 'failed', name='document_status'), nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
