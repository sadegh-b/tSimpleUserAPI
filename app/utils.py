# app/utils.py
from passlib.context import CryptContext

# تنظیمات رمزنگاری: Bcrypt بهترین گزینه برای هش کردن رمز عبور است
# اتو-اسکیما یعنی passlib خودش الگوریتم هش را تشخیص می‌دهد
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    رمز عبور را با استفاده از Bcrypt هش می‌کند.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    رمز عبور ورودی را با رمز عبور هش شده مقایسه می‌کند.
    """
    return pwd_context.verify(plain_password, hashed_password)
