# File: ulacm_backend/tests/api/test_main.py
# Purpose: Example integration tests for basic API endpoints (e.g., root, health).

import pytest
from httpx import AsyncClient
from fastapi import status

# Import your FastAPI app instance
# Ensure your app definition is accessible for testing
# You might need to adjust the import path based on your project structure
from app.main import app
from app.core.config import settings

@pytest.mark.asyncio
async def test_read_root():
    """
    Test the root endpoint '/'.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["message"] == f"Welcome to {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}"
    assert json_response["api_v1_url"] == settings.API_V1_STR

@pytest.mark.asyncio
async def test_read_health_check():
    """
    Test the health check endpoint '/api/v1/health'.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "API is healthy"}

# --- Example Structure for Authenticated Endpoint Test (Placeholder) ---
# This requires setting up fixtures for authentication (e.g., creating test users, logging in)
#
# @pytest.mark.asyncio
# async def test_read_items_unauthenticated(test_client: AsyncClient): # Assuming test_client fixture exists
#     """ Test accessing a protected route without authentication """
#     response = await test_client.get(f"{settings.API_V1_STR}/items")
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
#
# @pytest.mark.asyncio
# async def test_read_items_authenticated(authenticated_client: AsyncClient): # Assuming fixture provides authenticated client
#     """ Test accessing a protected route with authentication """
#     response = await authenticated_client.get(f"{settings.API_V1_STR}/items")
#     assert response.status_code == status.HTTP_200_OK
#     # Add more assertions based on expected response structure for /items
#     assert "items" in response.json()
