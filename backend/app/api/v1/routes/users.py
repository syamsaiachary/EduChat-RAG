from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.models.user import User
from app.schemas.user import UserListResponse
from app.core.dependencies import require_admin
from app.core.exceptions import NotFoundError, ForbiddenError

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    total = db.query(User).count()
    items = db.query(User).order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    pages = (total + limit - 1) // limit
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }

@router.delete("/{user_id}")
async def soft_delete_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("User not found.")
        
    if user.role == "admin":
        raise ForbiddenError("Cannot delete an admin user.")
        
    user.is_deleted = True
    db.commit()
    
    return {"message": "User deleted successfully."}
