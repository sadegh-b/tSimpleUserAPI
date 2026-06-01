# مسیر فایل: app/utils.py
import bcrypt


def get_password_hash(password: str) -> str:
    # 1. تبدیل پسورد به بایت و محدود کردن به 72 بایت
    password_bytes = password.encode("utf-8")[:72]

    # 2. تولید سالت (Salt) و هش کردن
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # 3. بازگشت به صورت رشته (استرینگ)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 1. تبدیل پسورد ورودی به بایت و محدود کردن به 72 بایت
    password_bytes = plain_password.encode("utf-8")[:72]

    # 2. تبدیل هش دیتابیس به بایت
    hashed_password_bytes = hashed_password.encode("utf-8")

    # 3. چک کردن پسورد
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)
