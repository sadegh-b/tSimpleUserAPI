from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.services.auth import get_current_user
from app.utils import get_password_hash

router = APIRouter()


def _make_username_from_email(email: str) -> str:
    base = (email.split("@", 1)[0] or "user").strip()
    return base if base else "user"


@router.post(
    "/users/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserOut,
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    username = getattr(user, "username", None) or _make_username_from_email(user.email)
    i = 0
    candidate = username
    while db.query(User).filter(User.username == candidate).first() is not None:
        i += 1
        candidate = f"{username}{i}"
    username = candidate

    new_user = User(
        username=username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # برگردوندن ORM object باعث می‌شود response_model خودش فیلدها را درست serialize کند
    return new_user


@router.get(
    "/users/",
    status_code=status.HTTP_200_OK,
    response_model=list[UserOut],
)
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(User).all()


@router.get(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserOut,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get(
    "/users/me/profile",
    status_code=status.HTTP_200_OK,
    response_model=UserOut,
)
def me_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user
