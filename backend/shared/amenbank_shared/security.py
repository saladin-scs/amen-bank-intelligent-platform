from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(
    data: dict[str, Any],
    secret_key: str,
    algorithm: str = "HS256",
    expires_minutes: int = 30,
) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(UTC) + timedelta(minutes=expires_minutes)
    payload["iat"] = datetime.now(UTC)
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_token(token: str, secret_key: str, algorithm: str = "HS256") -> dict[str, Any] | None:
    try:
        return jwt.decode(token, secret_key, algorithms=[algorithm])
    except JWTError:
        return None
