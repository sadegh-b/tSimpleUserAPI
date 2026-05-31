# app/services/auth.py

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database import get_db
from app.models.user import User

settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# اگر مسیر لاگین در پروژه‌ات فرق دارد، همین را تغییر بده
# (بعد از دیدن app/routers/auth.py می‌توانیم دقیقش کنیم)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password_bytes = plain_password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """
    انتظار می‌رود data شامل یکی از کلیدهای زیر باشد:
    - sub (ترجیحاً email)
    یا
    - email
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # پیام دقیق اهمیتی ندارد؛ تست‌ها معمولاً status_code را چک می‌کنند
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """
    Dependency برای routeهای protected.
    - اگر توکن نباشد: OAuth2PasswordBearer خودش 401 می‌دهد.
    - اگر توکن نامعتبر/کاربر ناموجود باشد: اینجا 401 می‌دهیم.
    """
    payload = decode_access_token(token)

    # سازگاری با دو حالت رایج
    email = payload.get("sub") or payload.get("email")
    if not email or not isinstance(email, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    return user
