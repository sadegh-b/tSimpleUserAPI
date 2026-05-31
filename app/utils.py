import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    if isinstance(password, str):
        password_bytes = password.encode("utf-8")
    else:
        password_bytes = bytes(password)

    if len(password_bytes) > 72:
        password_bytes = hashlib.sha256(password_bytes).digest()  # 32 bytes

    return pwd_context.hash(password_bytes)
