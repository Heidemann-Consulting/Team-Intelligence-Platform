# File: ulacm_backend/tests/core/test_security.py
# Purpose: Unit tests for security utility functions in app/core/security.py
# Corrected: Removed unnecessary relative import for conftest fixture

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
from freezegun import freeze_time

from jose import jwt, JWTError
from pydantic import UUID4

# Assuming TokenPayload is importable and correctly defined
from app.schemas.token import TokenPayload
# Import functions to test (adjust path if necessary)
from app.core import security
# Import mock settings fixture if needed, or patch directly
# from ..conftest import mock_settings # <-- REMOVE THIS LINE (pytest injects fixtures automatically)

# Fixture for team_id
@pytest.fixture
def sample_team_id() -> UUID4:
    return UUID4("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")

# Fixture for admin subject
@pytest.fixture
def admin_subject() -> str:
    return "admin"

# Test password hashing and verification
def test_password_hashing_and_verification():
    """
    Test that password hashing produces a hash and verification works.
    """
    password = "testpassword123"
    hashed_password = security.get_password_hash(password)

    assert isinstance(hashed_password, str)
    assert hashed_password != password
    assert len(hashed_password) > len(password) # Basic check for hashing

    # Verify correct password
    assert security.verify_password(password, hashed_password) is True

    # Verify incorrect password
    assert security.verify_password("wrongpassword", hashed_password) is False

# Test creating and decoding team tokens
@freeze_time("2023-01-01 12:00:00+00:00")
def test_create_and_decode_team_token(sample_team_id, mock_settings): # Fixture 'mock_settings' is injected
    """
    Test JWT creation and decoding for a team user.
    """
    with patch("app.core.security.settings", mock_settings):
        # Test creation with default expiry
        token = security.create_access_token(
            subject=str(sample_team_id),
            is_admin=False,
            team_id_for_token=sample_team_id
        )
        assert isinstance(token, str)

        # Test decoding valid token
        payload = security.decode_token(token)
        assert payload is not None
        assert isinstance(payload, TokenPayload)
        assert payload.sub == str(sample_team_id)
        assert payload.team_id == sample_team_id
        assert payload.is_admin is False

        # Check expiry (approximate based on freeze_time and settings)
        expected_expiry = datetime.now(timezone.utc) + timedelta(minutes=mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        decoded_jwt_payload = jwt.decode(token, mock_settings.SESSION_SECRET_KEY, algorithms=[security.ALGORITHM])
        assert abs(datetime.fromtimestamp(decoded_jwt_payload['exp'], timezone.utc) - expected_expiry) < timedelta(seconds=5)

# Test creating and decoding admin tokens
@freeze_time("2023-01-01 12:00:00+00:00")
def test_create_and_decode_admin_token(admin_subject, mock_settings): # Fixture 'mock_settings' is injected
    """
    Test JWT creation and decoding for an admin user.
    """
    with patch("app.core.security.settings", mock_settings):
        # Test creation with default expiry
        token = security.create_access_token(
            subject=admin_subject,
            is_admin=True
        )
        assert isinstance(token, str)

        # Test decoding valid token
        payload = security.decode_token(token)
        assert payload is not None
        assert isinstance(payload, TokenPayload)
        assert payload.sub == admin_subject
        assert payload.team_id is None # Admin token shouldn't have team_id unless specifically added
        assert payload.is_admin is True

        # Check expiry (approximate based on freeze_time and settings)
        expected_expiry = datetime.now(timezone.utc) + timedelta(minutes=mock_settings.ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES)
        decoded_jwt_payload = jwt.decode(token, mock_settings.SESSION_SECRET_KEY, algorithms=[security.ALGORITHM])
        assert abs(datetime.fromtimestamp(decoded_jwt_payload['exp'], timezone.utc) - expected_expiry) < timedelta(seconds=5)

# Test decoding invalid or expired tokens
def test_decode_invalid_token(mock_settings): # Fixture 'mock_settings' is injected
    """
    Test decoding various invalid tokens.
    """
    with patch("app.core.security.settings", mock_settings):
        # Test completely invalid token string
        assert security.decode_token("this.is.not.a.jwt") is None

        # Test token signed with wrong key
        wrong_key = "another-secret-key-minimum-32-bytes-long"
        valid_payload = {"sub": "test_user", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)}
        token_wrong_key = jwt.encode(valid_payload, wrong_key, algorithm=security.ALGORITHM)
        assert security.decode_token(token_wrong_key) is None

        # Test token with invalid algorithm (if applicable)
        # token_wrong_alg = jwt.encode(valid_payload, mock_settings.SESSION_SECRET_KEY, algorithm="HS512")
        # assert security.decode_token(token_wrong_alg) is None # Depends on how decode is called

        # Test missing required fields (sub, exp) - relies on JWT library behavior
        invalid_payload_no_sub = {"exp": datetime.now(timezone.utc) + timedelta(minutes=5)}
        token_no_sub = jwt.encode(invalid_payload_no_sub, mock_settings.SESSION_SECRET_KEY, algorithm=security.ALGORITHM)
        # Assuming decode_token checks for 'sub' implicitly or explicitly
        decoded = security.decode_token(token_no_sub)
        assert decoded is None or decoded.sub is None

# Test decoding expired tokens
@freeze_time("2023-01-01 12:00:00+00:00")
def test_decode_expired_token(sample_team_id, mock_settings): # Fixture 'mock_settings' is injected
    """
    Test decoding an expired JWT token.
    """
    with patch("app.core.security.settings", mock_settings):
        # Create token that expires *before* the validation time
        expires_delta = timedelta(seconds=-5) # Expired 5 seconds ago
        token = security.create_access_token(
            subject=str(sample_team_id),
            is_admin=False,
            team_id_for_token=sample_team_id,
            expires_delta=expires_delta
        )

    # No need to freeze time again, decode immediately
    with patch("app.core.security.settings", mock_settings):
         payload = security.decode_token(token)
         assert payload is None # Now it should definitely be expired

# Test admin password verification
def test_verify_admin_password(mock_settings): # Fixture 'mock_settings' is injected
    """
    Test verification against the configured ADMIN_PASSWORD.
    """
    with patch("app.core.security.settings", mock_settings):
        # Test correct password
        assert security.verify_admin_password(mock_settings.ADMIN_PASSWORD) is True

        # Test incorrect password
        assert security.verify_admin_password("wrongadminpass") is False

        # Test empty password
        assert security.verify_admin_password("") is False
