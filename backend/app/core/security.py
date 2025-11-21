"""Security helpers for JWT token handling and password hashing."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: str | int, expires_delta: int | None = None) -> str:
    expire_seconds = expires_delta or settings.JWT_ACCESS_TOKEN_EXPIRES
    expire = datetime.now(timezone.utc) + timedelta(seconds=expire_seconds)
    to_encode: Dict[str, Any] = {"sub": str(subject), "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return _pwd_context.hash(password)
