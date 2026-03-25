"""Security utilities for authentication and password handling."""

import os
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production-insecure-key")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))
ALGORITHM = "HS256"

# Password hashing
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated="auto",
    pbkdf2_sha256__default_rounds=260000,
)


def hash_password(password: str) -> str:
    """
    Hash a plaintext password.

    Args:
        password: Plaintext password to hash

    Returns:
        Hashed password safe for storage
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password.

    Args:
        plain_password: Plaintext password to verify
        hashed_password: Previously hashed password

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: UUID, email: str, expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token for a user.

    Args:
        user_id: Unique identifier of the user
        email: User's email address
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token as string
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=JWT_EXPIRE_HOURS)

    now = datetime.utcnow()
    expire = now + expires_delta

    payload = {
        "sub": str(user_id),
        "email": email,
        "iat": now,
        "exp": expire,
    }

    encoded_jwt = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Args:
        token: Encoded JWT token

    Returns:
        Decoded token payload with user claims

    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise JWTError(f"Invalid token: {str(e)}")


def extract_user_id_from_token(token: str) -> UUID:
    """
    Extract user ID from a JWT token.

    Args:
        token: Encoded JWT token

    Returns:
        User UUID from token payload

    Raises:
        JWTError: If token is invalid
        ValueError: If user_id is not in token
    """
    payload = decode_access_token(token)
    user_id_str = payload.get("sub")

    if not user_id_str:
        raise ValueError("Token missing user ID (sub claim)")

    try:
        return UUID(user_id_str)
    except (ValueError, ValidationError) as e:
        raise ValueError(f"Invalid user ID in token: {str(e)}")
