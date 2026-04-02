from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.schemas.auth import RegisterRequest, LoginRequest
from app.schemas.user import UserResponse
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions import AuthenticationError, ValidationError
from app.core.config import settings
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise ValidationError("Email is already registered.")
    if db.query(User).filter(User.username == body.username).first():
        raise ValidationError("Username is already taken.")
        
    hashed_password = get_password_hash(body.password)
    user = User(
        username=body.username,
        email=body.email,
        hashed_password=hashed_password,
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login")
async def login(body: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or user.is_deleted:
        raise AuthenticationError()
        
    if not verify_password(body.password, user.hashed_password):
        raise AuthenticationError()
        
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=access_token,
        httponly=True,
        max_age=settings.JWT_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax",
        secure=False  # True in prod ideally
    )
    return {"message": "Logged in successfully"}

@router.post("/logout")
async def logout(response: Response, current_user: User = Depends(get_current_user)):
    response.delete_cookie(key=settings.COOKIE_NAME)
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
