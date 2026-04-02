import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.postgres import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum('user', 'admin', name='user_role'), default='user', nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
