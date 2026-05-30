# tSimpleUserAPI

A simple FastAPI project for user registration, authentication (JWT), and user management — with SQLAlchemy + Alembic migrations and a full pytest suite.

---

## Features

- Create user with email + password
- Password validation (min length, must contain letter & number)
- JWT login and protected endpoints
- Get current user profile (`/users/me/profile`)
- List users and get a single user (protected)
- SQLAlchemy ORM + SQLite
- Alembic migrations
- 9/9 tests passing with `-W error` (warnings treated as errors)

---

## Tech Stack

- FastAPI
- SQLAlchemy
- Alembic
- Pydantic + pydantic-settings
- bcrypt (password hashing)
- python-jose (JWT)
- Pytest

---

## Project Structure
```text
tSimpleUserAPI/
├── alembic/
├── app/
│   ├── core/
│   │   └── config.py
│   ├── dependencies/
│   │   └── auth.py
│   ├── models/
│   │   └── user.py
│   ├── routers/
│   │   ├── auth.py
│   │   └── users.py
│   ├── schemas/
│   │   └── user.py
│   ├── services/
│   │   └── auth.py
│   ├── tests/
│   │   └── test_users.py
│   ├── database.py
│   └── main.py
├── user_data.db
├── alembic.ini
└── README.md
