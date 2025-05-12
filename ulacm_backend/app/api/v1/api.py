# File: ulacm_backend/app/api/v1/api.py
# Purpose: Main API router that includes all sub-routers for version 1 of the API.
# Updated: Added ai_tools_router.
from fastapi import APIRouter

from app.api.v1.endpoints import auth as auth_router
from app.api.v1.endpoints import admin_teams as admin_teams_router
from app.api.v1.endpoints import content_items as content_items_router
from app.api.v1.endpoints import versions as versions_router
from app.api.v1.endpoints import workflows_exec as workflows_exec_router
from app.api.v1.endpoints import search as search_router
from app.api.v1.endpoints import ai_tools as ai_tools_router # New import

api_router = APIRouter()

# Include authentication router
api_router.include_router(auth_router.router, tags=["Authentication"])

# Include admin teams router
api_router.include_router(
    admin_teams_router.router,
    prefix="/admin/teams",
    tags=["Admin - Team Management"]
)

api_router.include_router(content_items_router.router, prefix="/items", tags=["Content Items"])
api_router.include_router(versions_router.router, prefix="/items", tags=["Content Versions"])
api_router.include_router(workflows_exec_router.router, prefix="/workflows", tags=["Workflow Execution"])
api_router.include_router(search_router.router, prefix="/search", tags=["Search"])

# Include AI tools router
api_router.include_router(ai_tools_router.router, prefix="/ai", tags=["AI Tools"]) # New router included

# A simple health check endpoint for the API itself
@api_router.get("/health", summary="API Health Check", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint to confirm the API is running.
    """
    return {"status": "API is healthy"}
