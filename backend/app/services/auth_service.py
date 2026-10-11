import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.user import User, UserRole
from app.schemas.auth import UserRegister, UserLogin

password_hash = PasswordHash.recommended()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

async def register_user(db: AsyncSession, user_in: UserRegister) -> User:
    # Check existing
    stmt = select(User).where(User.email == user_in.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise ValueError("User with this email already exists")

    new_user = User(
        id=str(uuid.uuid4()),
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        company_name=user_in.company_name,
        phone=user_in.phone,
        role=user_in.role
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def authenticate_user(db: AsyncSession, login_in: UserLogin) -> Optional[User]:
    stmt = select(User).where(User.email == login_in.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(login_in.password, user.password_hash):
        return None
    return user
