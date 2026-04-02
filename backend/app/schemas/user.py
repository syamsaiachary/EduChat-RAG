from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from typing import Literal

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: Literal['user', 'admin']
    is_deleted: bool

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    limit: int
    pages: int
