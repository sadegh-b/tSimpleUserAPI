# app/models.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session # برای type hinting

# Base کلاسی است که تمام مدل‌های SQLAlchemy از آن ارث می‌برند
Base = declarative_base()

# تعریف مدل User که با جدول users در دیتابیس مطابقت دارد
class User(Base):
    __tablename__ = "users"  # نام جدول در دیتابیس

    id = Column(Integer, primary_key=True, index=True)  # کلید اصلی، ایندکس شده
    username = Column(String, unique=True, index=True)  # نام کاربری، باید منحصر به فرد و ایندکس شده باشد
    email = Column(String, unique=True, index=True)  # ایمیل، باید منحصر به فرد و ایندکس شده باشد
    hashed_password = Column(String)  # رمز عبور هش شده

    # نمایش رشته‌ای از مدل برای دیباگینگ (اختیاری)
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

# تابع کمکی برای گرفتن سشن دیتابیس (این رو قبلا در main.py داشتیم، اینجا فقط برای کامل بودن کد مدل آوردم)
# در عمل، شما این تابع رو یک بار در main.py تعریف می‌کنید و از آن استفاده می‌کنید
# def get_db_session():
#     db_url = os.getenv("DATABASE_URL")
#     if not db_url:
#         raise ValueError("DATABASE_URL environment variable not set")
#     engine = create_engine(db_url)
#     Base.metadata.create_all(bind=engine)  # اطمینان از ایجاد جدول‌ها
#     SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
