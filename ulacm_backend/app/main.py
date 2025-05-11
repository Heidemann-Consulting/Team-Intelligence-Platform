# File: ulacm_backend/app/main.py
# Purpose: Main FastAPI application instance creation and setup.
# Updated: Refined model_rebuild calls in lifespan event with _types_namespace and explicit top-level imports.
# Modification: Added 'app' package to _types_namespace to resolve forward references.
# Modification: Aliased ulacm_fastapi_app back to 'app' for Uvicorn.

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# --- Critical: Ensure all schema modules are imported first ---
# This helps sys.modules get populated correctly before model_rebuild attempts to resolve strings.
from app.schemas import token
from app.schemas import team
from app.schemas import content_item # module
from app.schemas import content_version # module
from app.schemas import workflow_definition # module
from app.schemas import msg

# --- Now import specific classes needed in this file ---
from app.api.v1.api import api_router as api_router_v1
from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging_config import setup_logging

# Specific models for model_rebuild
from app.schemas.content_item import ContentItemWithCurrentVersion, ContentItemSearchResult, ContentItemListResponse, ContentItem as ContentItemClass # Renamed for clarity
# Import the actual WorkflowDefinition class to be used in the namespace
from app.schemas.workflow_definition import WorkflowDefinition as ActualWorkflowDefinitionClassTarget
from app.schemas.workflow_definition import WorkflowExecutionOutputDocument, RunWorkflowResponse

# Import the 'app' package itself to make it available in _types_namespace
import app as app_package

setup_logging()
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(fastapi_app_instance: FastAPI): # Parameter name changed for clarity
    log.info("Application startup: Rebuilding Pydantic models...")

    types_namespace_for_rebuild = {
        'app': app_package, # Make the 'app' package itself resolvable
        'app.schemas.workflow_definition.WorkflowDefinition': ActualWorkflowDefinitionClassTarget,
        'app.schemas.content_item.ContentItem': ContentItemClass
    }

    try:
        # It's crucial that the classes being rebuilt are fully known at this point.
        content_item.ContentItemWithCurrentVersion.model_rebuild(_types_namespace=types_namespace_for_rebuild)
        content_item.ContentItemSearchResult.model_rebuild(_types_namespace=types_namespace_for_rebuild)

        workflow_definition.WorkflowDefinition.model_rebuild(_types_namespace=types_namespace_for_rebuild)
        workflow_definition.WorkflowExecutionOutputDocument.model_rebuild(_types_namespace=types_namespace_for_rebuild)

        content_item.ContentItemListResponse.model_rebuild(_types_namespace=types_namespace_for_rebuild)
        workflow_definition.RunWorkflowResponse.model_rebuild(_types_namespace=types_namespace_for_rebuild)

        log.info("Pydantic models rebuilt successfully during startup.")
    except Exception as e:
        log.error(f"Error rebuilding Pydantic models during startup: {e}", exc_info=True)
        raise # Re-raise to halt startup if models are critical
    yield
    log.info("Application shutdown.")


# Rename variable to avoid conflict if 'app' is used for the package elsewhere
ulacm_fastapi_app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Universal Lean AI-Co-Management (ULACM) Service API",
    lifespan=lifespan
)

# --- Middleware setup ---
ulacm_fastapi_app.state.limiter = limiter
ulacm_fastapi_app.add_middleware(SlowAPIMiddleware)

@ulacm_fastapi_app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    log.warning(f"Rate limit exceeded for client {request.client.host}: {exc.detail}")
    response = JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}"}
    )
    response = await _rate_limit_exceeded_handler(request, exc)
    return response

@ulacm_fastapi_app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    log.exception(f"Unhandled exception during request to {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )

if settings.BACKEND_CORS_ORIGINS:
    ulacm_fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    log.info(f"CORS enabled for origins: {settings.BACKEND_CORS_ORIGINS}")

# --- Router inclusion ---
ulacm_fastapi_app.include_router(api_router_v1, prefix=settings.API_V1_STR)
log.info(f"API V1 router included at prefix: {settings.API_V1_STR}")

# --- Root endpoint ---
@ulacm_fastapi_app.get("/", summary="Root endpoint", description="Provides a welcome message and basic API information.")
@limiter.exempt
async def root():
    log.debug("Root endpoint '/' accessed")
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "api_v1_url": settings.API_V1_STR
    }

log.info(f"{settings.PROJECT_NAME} v{settings.PROJECT_VERSION} setup complete (pending startup events).")

# Alias ulacm_fastapi_app to 'app' so Uvicorn can find it using "app.main:app"
app = ulacm_fastapi_app
