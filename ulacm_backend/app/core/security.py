# File: ulacm_backend/app/core/security.py
# Purpose: Password hashing, JWT creation/decoding, and other security utilities.

from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import UUID4

from app.core.config import settings
from app.schemas.token import TokenPayload

# Password hashing context using bcrypt
# bcrypt is recommended for its strength.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256" # Algorithm for JWT signing

def create_access_token(
    subject: Union[str, Any], # Typically team_id or an admin identifier
    is_admin: bool = False,
    team_id_for_token: Optional[UUID4] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generates a new JWT access token.

    Args:
        subject: The subject of the token (e.g., team_id for team users, admin marker for admins).
        is_admin: Flag to indicate if the token is for an admin.
        team_id_for_token: Explicit team_id to include in the token payload if subject is not team_id itself.
        expires_delta: Optional timedelta for token expiry. Uses settings if None.

    Returns:
        The encoded JWT access token as a string.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        if is_admin:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES)
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "exp": expire,
        "sub": str(subject), # Ensure subject is a string
        "is_admin": is_admin
    }
    if team_id_for_token:
        to_encode["team_id"] = str(team_id_for_token)

    encoded_jwt = jwt.encode(to_encode, settings.SESSION_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.

    Args:
        plain_password: The password in plain text.
        hashed_password: The hashed password from storage.

    Returns:
        True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hashes a plain password.

    Args:
        password: The password in plain text.

    Returns:
        The hashed password as a string.
    """
    return pwd_context.hash(password)

def decode_token(token: str) -> Optional[TokenPayload]:
    """
    Decodes a JWT token and returns its payload.

    Args:
        token: The JWT token string.

    Returns:
        TokenPayload if the token is valid and successfully decoded, None otherwise.
    """
    try:
        payload = jwt.decode(token, settings.SESSION_SECRET_KEY, algorithms=[ALGORITHM])
        # Explicitly create TokenPayload to ensure all expected fields are present or defaulted
        token_data = TokenPayload(
            sub=payload.get("sub"),
            team_id=payload.get("team_id"),
            is_admin=payload.get("is_admin", False) # Default is_admin to False if not present
        )
        return token_data
    except JWTError:
        return None

def verify_admin_password(password: str) -> bool:
    """
    Verifies the provided password against the configured ADMIN_PASSWORD.
    Note: This is a direct comparison for a single admin password, not a hashed one from DB.
    For multiple admins with stored credentials, use verify_password with a hash.

    Args:
        password: The password provided for admin login.

    Returns:
        True if the password matches the configured ADMIN_PASSWORD, False otherwise.
    """
    return password == settings.ADMIN_PASSWORD
