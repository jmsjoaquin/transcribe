from __future__ import annotations

import base64
import hashlib
import hmac
import os
from typing import Any
from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import settings

PASSWORD_HASH_ITERATIONS = 600_000
PASSWORD_HASH_NAME = "pbkdf2_sha256"


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
    )
    salt_b64 = base64.b64encode(salt).decode("utf-8")
    hash_b64 = base64.b64encode(password_hash).decode("utf-8")
    return f"{PASSWORD_HASH_NAME}${PASSWORD_HASH_ITERATIONS}${salt_b64}${hash_b64}"


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        algorithm, iterations_str, salt_b64, expected_hash_b64 = hashed_password.split("$", maxsplit=3)
    except ValueError:
        return False

    if algorithm != PASSWORD_HASH_NAME:
        return False

    derived_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        base64.b64decode(salt_b64),
        int(iterations_str),
    )
    expected_hash = base64.b64decode(expected_hash_b64)
    return hmac.compare_digest(derived_hash, expected_hash)


def create_access_token(subject: str) -> tuple[str, datetime]:
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": subject,
        "type": "access",
        "exp": expires_at,
    }
    token = jwt.encode(payload, settings.secret_key, algorithm="HS256")
    return token, expires_at


def decode_access_token(token: str) -> dict[str, Any]:
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Invalid token type.")
    return payload
