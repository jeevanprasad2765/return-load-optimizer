from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse
from app.services.auth_service import register_user, authenticate_user, create_access_token
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    try:
        user = await register_user(db, user_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    token = create_access_token(data={"sub": user.id, "role": user.role.value})
    return Token(access_token=token, user=UserResponse.model_validate(user))

@router.post("/login", response_model=Token)
async def login(login_in: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, login_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": user.id, "role": user.role.value})
    return Token(access_token=token, user=UserResponse.model_validate(user))

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
