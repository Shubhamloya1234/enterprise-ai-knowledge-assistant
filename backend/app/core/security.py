
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.core.config import (
    JWT_SECRET,
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(user_id: int, role: str) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "user_id": user_id,
        "role": role,
        "iat": now,
        "exp": now + timedelta(
            minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


def decode_access_token(token: str):
    payload = jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM],
        options={
            "require": ["user_id", "role", "iat", "exp"]
        }
    )

    if (
        isinstance(payload.get("user_id"), bool)
        or not isinstance(payload.get("user_id"), int)
        or payload["user_id"] <= 0
    ):
        raise jwt.InvalidTokenError("Invalid user_id claim.")

    if (
        not isinstance(payload.get("role"), str)
        or not payload["role"].strip()
    ):
        raise jwt.InvalidTokenError("Invalid role claim.")

    return payload


