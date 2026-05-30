# app/schemas.py
from pydantic import BaseModel, EmailStr # EmailStr برای اعتبارسنجی فرمت ایمیل
from typing import Optional # برای تعریف فیلدهایی که می‌توانند خالی باشند

# --- Schemas for User ---

# این Schema برای زمانی است که می‌خواهیم یک کاربر جدید بسازیم
# فیلدهایی که الزامی هستند اینجا تعریف می‌شوند
class UserCreate(BaseModel):
    username: str
    email: EmailStr # فرمت ایمیل را چک می‌کند
    password: str # رمز عبور در این مرحله خام است، در ادامه هش می‌شود

    # مثال:
    # class Config:
    #     orm_mode = True # این برای نسخه های قدیمی تر Pydantic بود، الان لازم نیست

# این Schema برای زمانی است که می‌خواهیم اطلاعات کاربر را برگردانیم (مثلاً بعد از ساخت یا بازیابی)
# فیلدهایی که نباید به کاربر نمایش داده شوند (مثل رمز عبور) اینجا نیستند
# فیلدهایی که اختیاری هستند (مثل username یا email که شاید بعداً آپدیت شوند) را Optional می‌کنیم
class User(BaseModel):
    id: int
    username: Optional[str] = None # اگر username تنظیم نشد، مقدارش None است
    email: EmailStr
    # hashed_password را اینجا برنمی‌گردانیم چون نباید دیده شود

    # برای نگاشت به مدل SQLAlchemy (مخصوصا در نسخه های قدیمی تر Pydantic)
    # در نسخه های جدیدتر Pydantic v2+ ، این نگاشت به صورت خودکار انجام می شود
    # اگر خطایی در نگاشت دیدی، این بخش را اضافه کن
    # class Config:
    #     from_attributes = True # معادل orm_mode در نسخه های قدیمی تر
