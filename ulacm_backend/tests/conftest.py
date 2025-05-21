# File: ulacm_backend/tests/conftest.py
# Purpose: Pytest configuration and shared fixtures for backend tests.

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from pydantic import UUID4

# --- Event Loop Policy ---
# Required by pytest-asyncio for some environments
@pytest.fixture(scope="session")
def event_loop_policy():
    """Set the asyncio event loop policy."""
    return asyncio.DefaultEventLoopPolicy()

# --- Mock Database Session ---
@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Provides a mock SQLAlchemy AsyncSession."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    session.scalars = AsyncMock()
    session.scalar_one_or_none = AsyncMock()
    session.scalar_one = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()
    session.delete = AsyncMock()
    session.flush = AsyncMock()
    session.close = AsyncMock()
    # Mock the context manager methods
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock()

    # Mock nested methods if needed (e.g., result object from execute)
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = AsyncMock()
    mock_result.scalar_one = AsyncMock()
    mock_result.scalars.return_value.all = MagicMock(return_value=[])
    mock_result.scalars.return_value.first = MagicMock(return_value=None)
    mock_result.unique.return_value.all = MagicMock(return_value=[]) # For unique() results
    session.execute.return_value = mock_result

    return session

# --- Mock FastAPI Request ---
@pytest.fixture
def mock_request() -> MagicMock:
    """Provides a mock FastAPI Request object."""
    request = MagicMock(spec=Request)
    request.client = MagicMock()
    request.client.host = "127.0.0.1"
    request.state = MagicMock() # Add state if used by dependencies
    return request

# --- Mock Settings ---
# It's often better to mock specific setting values where needed using patch
# rather than mocking the whole object, but a fixture can be useful.
@pytest.fixture
def mock_settings():
    """Provides a mock settings object."""
    settings = MagicMock()
    settings.SESSION_SECRET_KEY = "test-secret-key-minimum-32-bytes-long"
    settings.ACCESS_TOKEN_EXPIRE_MINUTES = 15
    settings.ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES = 10
    settings.ADMIN_PASSWORD = "testadminpassword"
    settings.OLLAMA_API_URL = "http://mock-ollama:11434"
    settings.BACKEND_CORS_ORIGINS = ["http://localhost:4000", "https://localhost:4000"]
    return settings

# --- Test Data Fixtures (Examples) ---
@pytest.fixture
def test_team_id() -> UUID4:
    """Provides a consistent test team UUID."""
    return UUID4("11111111-1111-1111-1111-111111111111")

@pytest.fixture
def test_admin_id() -> str:
    """Provides a consistent test admin identifier."""
    return "admin"
