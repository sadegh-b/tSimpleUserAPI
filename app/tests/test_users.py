# مسیر فایل: app/tests/test_users.py
import pytest
from httpx import AsyncClient

# import های زیر دیگه لازم نیست چون fixture client از conftest.py میاد
# from httpx import ASGITransport
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import StaticPool
# from app.main import app
# from app.database import Base, get_db

pytestmark = pytest.mark.asyncio

# fixture client از اینجا حذف شد.
# @pytest.fixture
# async def client():
#     transport = ASGITransport(app=app)
#     async with AsyncClient(transport=transport, base_url="http://test") as ac:
#         yield ac

async def create_user(
    client: AsyncClient,
    email: str = "test@example.com",
    password: str = "Password123",
):
    return await client.post(
        "/users/",
        json={"email": email, "password": password},
    )


async def login_user(
    client: AsyncClient,
    email: str = "test@example.com",
    password: str = "Password123",
):
    return await client.post(
        "/login",
        json={"email": email, "password": password},
    )


async def get_auth_headers(
    client: AsyncClient,
    email: str = "test@example.com",
    password: str = "Password123",
):
    await create_user(client, email=email, password=password)
    login_response = await login_user(client, email=email, password=password)

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_create_user_success(client: AsyncClient):
    response = await create_user(client, email="unique_user@example.com", password="Password123")

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "unique_user@example.com"
    assert "id" in data


async def test_create_user_invalid_email(client: AsyncClient):
    response = await client.post(
        "/users/",
        json={"email": "not-an-email", "password": "Password123"},
    )
    assert response.status_code == 422


async def test_create_user_weak_password(client: AsyncClient):
    response = await client.post(
        "/users/",
        json={"email": "weak@example.com", "password": "123"},
    )
    assert response.status_code == 422


async def test_get_users(client: AsyncClient):
    headers = await get_auth_headers(client, email="list@example.com", password="Password123")

    response = await client.get("/users/", headers=headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_get_single_user(client: AsyncClient):
    create_response = await create_user(client, email="single@example.com", password="Password123")
    assert create_response.status_code == 201

    user_id = create_response.json()["id"]
    headers = await get_auth_headers(client, email="auth_user@example.com", password="Password123")

    response = await client.get(f"/users/{user_id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == "single@example.com"


async def test_login_success(client: AsyncClient):
    create_response = await create_user(client, email="login_test@example.com", password="Password123")
    assert create_response.status_code == 201

    response = await login_user(client, email="login_test@example.com", password="Password123")

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_invalid_password(client: AsyncClient):
    create_response = await create_user(client, email="wrong_p@example.com", password="Password123")
    assert create_response.status_code == 201

    response = await login_user(client, email="wrong_p@example.com", password="WrongPassword")
    assert response.status_code == 401


async def test_get_users_without_token(client: AsyncClient):
    response = await client.get("/users/")
    assert response.status_code == 401


async def test_get_me_profile(client: AsyncClient):
    headers = await get_auth_headers(client, email="me_profile@example.com", password="Password123")

    response = await client.get("/users/me/profile", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == "me_profile@example.com"
