# File: ulacm_backend/app/api/v1/api.py
# Purpose: Main API router that includes all sub-routers for version 1 of the API.

from fastapi import APIRouter

from app.api.v1.endpoints import auth as auth_router
from app.api.v1.endpoints import admin_teams as admin_teams_router
from app.api.v1.endpoints import content_items as content_items_router
from app.api.v1.endpoints import versions as versions_router
from app.api.v1.endpoints import workflows_exec as workflows_exec_router
from app.api.v1.endpoints import search as search_router


api_router = APIRouter()

# Include authentication router
api_router.include_router(auth_router.router, tags=["Authentication"])

# Include admin teams router
api_router.include_router(
    admin_teams_router.router,
    prefix="/admin/teams", # Prefix for all routes in admin_teams_router
    tags=["Admin - Team Management"]
)

api_router.include_router(content_items_router.router, prefix="/items", tags=["Content Items"])
api_router.include_router(versions_router.router, prefix="/items", tags=["Content Versions"]) # Often nested under items
api_router.include_router(workflows_exec_router.router, prefix="/workflows", tags=["Workflow Execution"])
api_router.include_router(search_router.router, prefix="/search", tags=["Search"])

# A simple health check endpoint for the API itself
@api_router.get("/health", summary="API Health Check", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint to confirm the API is running.
    """
    return {"status": "API is healthy"}
