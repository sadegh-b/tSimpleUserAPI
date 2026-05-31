# app/tests/conftest.py
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.database as database
import app.routers.users as users_router
import app.routers.auth as auth_router

from app.main import app

# خیلی مهم: مدل‌ها قبل از create_all لود شوند تا جدول‌ها ساخته شوند
from app.models.user import User  # noqa: F401


SQLALCHEMY_DATABASE_URL = "sqlite+pysqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _patch_db(monkeypatch):
    """
    هدف: مطمئن شویم تمام کد اپ (database + routerها) از DB تست استفاده می‌کند.
    """

    # 1) پچ کردن خودِ ماژول database (engine و SessionLocal واقعی اپ)
    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", TestingSessionLocal)

    # 2) ریست کامل اسکیمای DB قبل از هر تست
    database.Base.metadata.drop_all(bind=test_engine)
    database.Base.metadata.create_all(bind=test_engine)

    # 3) override dependency برای هر reference ممکن
    app.dependency_overrides[database.get_db] = override_get_db
    app.dependency_overrides[users_router.get_db] = override_get_db
    app.dependency_overrides[auth_router.get_db] = override_get_db

    # 4) دیباگ خیلی کوتاه (موقتاً نگه دار تا سبز شود)
    # اگر اینجا URL چیزی غیر از memory بود یعنی هنوز patch مشکل دارد
    # print("DB(engine.url) =", str(database.engine.url))

    yield

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
