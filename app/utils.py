# مسیر فایل: app/utils.py

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    # پسورد را به بایت تبدیل می‌کنیم
    password_bytes = password.encode("utf-8")

    # اگر طول بایت‌ها بیشتر از 72 بود، فقط 72 تای اول را برمی‌داریم
    # این همان کاری است که bcrypt به صورت استاندارد انجام می‌دهد
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    return pwd_context.hash(password_bytes)
