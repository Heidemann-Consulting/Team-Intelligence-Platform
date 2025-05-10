# File: ulacm_backend/app/main.py
# Purpose: Main FastAPI application instance creation and setup.
# Updated to apply logging configuration and add basic startup/error logging.

import logging
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.api import api_router as api_router_v1
from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging_config import setup_logging # Import logging setup

# --- Configure Logging ---
# Apply logging configuration before creating the app instance
# to capture logs during startup as well.
setup_logging()
log = logging.getLogger(__name__)
# -------------------------

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Universal Lean AI-Co-Management (ULACM) Service API"
)

# Add Rate Limiter state and middleware FIRST
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Add Rate Limit Exceeded Exception Handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler for RateLimitExceeded exception from slowapi.
    Returns a 429 Too Many Requests response.
    """
    log.warning(f"Rate limit exceeded for client {request.client.host}: {exc.detail}")
    response = JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}"}
    )
    # Allow slowapi to add standard headers (like Retry-After)
    response = await _rate_limit_exceeded_handler(request, exc)
    return response

# Add a generic error handler to log unhandled exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    log.exception(f"Unhandled exception during request to {request.url.path}") # Use logger.exception to include stack trace
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )

# Set all CORS enabled origins (AFTER rate limiting middleware)
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    log.info(f"CORS enabled for origins: {settings.BACKEND_CORS_ORIGINS}")


# Include the API router (AFTER middleware)
app.include_router(api_router_v1, prefix=settings.API_V1_STR)
log.info(f"API V1 router included at prefix: {settings.API_V1_STR}")

@app.get("/", summary="Root endpoint", description="Provides a welcome message and basic API information.")
@limiter.exempt # Exempt the root endpoint from default rate limiting
async def root():
    """
    Root endpoint providing a welcome message.
    """
    log.debug("Root endpoint '/' accessed")
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "api_v1_url": settings.API_V1_STR
    }

# --- Optional Lifespan Events ---
# Use lifespan for setup/teardown tasks like DB connection pools or closing clients
# from contextlib import asynccontextmanager
# from app.services.ollama_service import ollama_service_instance # Assuming it's an instance
#
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Code to run on startup
#     log.info("Application startup...")
#     # Example: Initialize database, connection pools if needed
#     # await database.connect()
#     yield
#     # Code to run on shutdown
#     log.info("Application shutdown...")
#     # Example: Close external connections
#     await ollama_service_instance.close()
#     # await database.disconnect()
#
# app.router.lifespan = lifespan
# -----------------------------

log.info(f"{settings.PROJECT_NAME} v{settings.PROJECT_VERSION} setup complete.")
