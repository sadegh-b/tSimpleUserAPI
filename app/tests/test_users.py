# app/tests/test_users.py
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


def _debug_response(resp):
    # برای دیباگ در CI/لوکال
    print("\n--- RESPONSE DEBUG ---")
    print("URL:", resp.request.url)
    print("METHOD:", resp.request.method)
    try:
        print("REQUEST BODY:", resp.request.content.decode())
    except Exception:
        print("REQUEST BODY: <non-decodable>")
    print("STATUS:", resp.status_code)
    print("HEADERS:", dict(resp.headers))
    print("TEXT:", resp.text)
    try:
        print("JSON:", resp.json())
    except Exception as e:
        print("JSON decode error:", repr(e))
    print("--- END DEBUG ---\n")


async def create_user(client: AsyncClient, email: str, password: str):
    return await client.post("/users/", json={"email": email, "password": password})


async def login_user(client: AsyncClient, email: str, password: str):
    """
    بعضی پیاده‌سازی‌ها login را با JSON می‌گیرند،
    بعضی با فرم (OAuth2PasswordRequestForm).
    این تابع اول JSON را امتحان می‌کند، اگر 422 گرفت، با form دوباره می‌زند.
    """
    resp = await client.post("/login", json={"email": email, "password": password})
    if resp.status_code == 422:
        # fallback to form-encoded
        resp = await client.post(
            "/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    return resp


async def get_auth_headers(client: AsyncClient, email: str, password: str):
    # create
    create_resp = await create_user(client, email=email, password=password)
    if create_resp.status_code != 201:
        _debug_response(create_resp)
    assert create_resp.status_code == 201

    # login
    login_resp = await login_user(client, email=email, password=password)
    if login_resp.status_code != 200:
        _debug_response(login_resp)
    assert login_resp.status_code == 200

    data = login_resp.json()
    assert "access_token" in data, f"login response missing token. body={login_resp.text}"
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_create_user_success(client: AsyncClient):
    resp = await create_user(client, email="unique_user@example.com", password="Password123")
    if resp.status_code != 201:
        _debug_response(resp)
    assert resp.status_code == 201

    data = resp.json()
    assert data["email"] == "unique_user@example.com"
    assert "id" in data


async def test_create_user_invalid_email(client: AsyncClient):
    resp = await client.post("/users/", json={"email": "not-an-email", "password": "Password123"})
    if resp.status_code != 422:
        _debug_response(resp)
    assert resp.status_code == 422


async def test_create_user_weak_password(client: AsyncClient):
    resp = await client.post("/users/", json={"email": "weak@example.com", "password": "123"})
    if resp.status_code != 422:
        _debug_response(resp)
    assert resp.status_code == 422


async def test_get_users(client: AsyncClient):
    headers = await get_auth_headers(client, email="list@example.com", password="Password123")

    resp = await client.get("/users/", headers=headers)
    if resp.status_code != 200:
        _debug_response(resp)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_get_single_user(client: AsyncClient):
    create_resp = await create_user(client, email="single@example.com", password="Password123")
    if create_resp.status_code != 201:
        _debug_response(create_resp)
    assert create_resp.status_code == 201

    user_id = create_resp.json()["id"]
    headers = await get_auth_headers(client, email="auth_user@example.com", password="Password123")

    resp = await client.get(f"/users/{user_id}", headers=headers)
    if resp.status_code != 200:
        _debug_response(resp)
    assert resp.status_code == 200
    assert resp.json()["email"] == "single@example.com"


async def test_login_success(client: AsyncClient):
    create_resp = await create_user(client, email="login_test@example.com", password="Password123")
    if create_resp.status_code != 201:
        _debug_response(create_resp)
    assert create_resp.status_code == 201

    resp = await login_user(client, email="login_test@example.com", password="Password123")
    if resp.status_code != 200:
        _debug_response(resp)
    assert resp.status_code == 200

    data = resp.json()
    assert "access_token" in data
    assert data.get("token_type") in ("bearer", "Bearer")


async def test_login_invalid_password(client: AsyncClient):
    create_resp = await create_user(client, email="wrong_p@example.com", password="Password123")
    if create_resp.status_code != 201:
        _debug_response(create_resp)
    assert create_resp.status_code == 201

    resp = await login_user(client, email="wrong_p@example.com", password="WrongPassword")
    # برای invalid password معمولاً 401 می‌دهند
    if resp.status_code != 401:
        _debug_response(resp)
    assert resp.status_code == 401


async def test_get_users_without_token(client: AsyncClient):
    resp = await client.get("/users/")
    assert resp.status_code == 401


async def test_get_me_profile(client: AsyncClient):
    headers = await get_auth_headers(client, email="me_profile@example.com", password="Password123")

    resp = await client.get("/users/me/profile", headers=headers)
    if resp.status_code != 200:
        _debug_response(resp)
    assert resp.status_code == 200
    assert resp.json()["email"] == "me_profile@example.com"
