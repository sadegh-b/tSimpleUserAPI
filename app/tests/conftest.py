# مسیر فایل: app/tests/conftest.py

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
# مطمئن شو که مسیر import زیر درست باشه. اگر Base و get_db در فایل دیگری هستند، مسیر را اصلاح کن.
from app.database import Base, get_db

# تنظیمات دیتابیس برای تست
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    # Use a StaticPool to limit connections to one thread.
    poolclass=StaticPool,
)

# تنظیمات SessionLocal برای تست
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ایجاد جداول پایگاه داده بر اساس مدل‌های SQLAlchemy
# اگر Base را از جای دیگری import کرده‌ای، مطمئن شو که این خط درست کار می‌کند.
Base.metadata.create_all(bind=engine)


# اورراید کردن تابع get_db برای استفاده از دیتابیس تست
def override_get_db():
    """
    Dependency override for get_db to use the in-memory SQLite database for tests.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# اعمال اورراید در زمان تست
app.dependency_overrides[get_db] = override_get_db


# fixture اصلی برای کلاینت تست
@pytest_asyncio.fixture
async def client():
    """
    Provides an asynchronous HTTP client for making test requests to the application.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
