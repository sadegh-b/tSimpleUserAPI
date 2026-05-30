# app/crud.py
from sqlalchemy.orm import Session
from app import models, schemas  # مدل‌ها و اسکیمای ما
from app.utils import get_password_hash  # تابعی برای هش کردن رمز عبور


# --- CRUD operations for User ---

def get_user_by_email(db: Session, email: str):
    """
    کاربر را بر اساس ایمیل از دیتابیس پیدا می‌کند.
    """
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str):
    """
    کاربر را بر اساس نام کاربری از دیتابیس پیدا می‌کند.
    """
    return db.query(models.User).filter(models.User.username == username).first()


def get_user(db: Session, user_id: int):
    """
    کاربر را بر اساس ID از دیتابیس پیدا می‌کند.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate):
    """
    کاربر جدید را در دیتابیس ایجاد می‌کند.
    """
    # رمز عبور را هش می‌کنیم قبل از ذخیره
    hashed_password = get_password_hash(user.password)  # تابع get_password_hash را در ادامه می‌سازیم

    # یک نمونه از مدل User می‌سازیم
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )

    # کاربر را به سشن دیتابیس اضافه می‌کنیم
    db.add(db_user)
    # تغییرات را در دیتابیس ذخیره می‌کنیم
    db.commit()
    # اطلاعات کاربر ذخیره شده را به همراه ID جدید برمی‌گردانیم
    db.refresh(db_user)
    return db_user

# برای آپدیت کردن کاربر (فعلا لازم نیست ولی بعدا اضافه می‌کنیم)
# def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
#     pass

# برای حذف کاربر (فعلا لازم نیست)
# def delete_user(db: Session, user_id: int):
#     pass
