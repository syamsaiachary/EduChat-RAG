from fastapi import Depends, Request
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.models.user import User
from app.core.security import verify_jwt
from app.core.exceptions import AuthenticationError, ForbiddenError
from app.core.config import settings

async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(settings.COOKIE_NAME)
    if not token:
        raise AuthenticationError()
    
    payload = verify_jwt(token)
    if not payload or "sub" not in payload:
        raise AuthenticationError()
    
    user_id = payload["sub"]
    user = db.query(User).filter(User.id == str(user_id)).first()
    
    if not user or user.is_deleted:
        raise AuthenticationError()
        
    return user

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise ForbiddenError()
    return current_user
