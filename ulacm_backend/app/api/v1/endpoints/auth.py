# File: ulacm_backend/app/api/v1/endpoints/auth.py
# Purpose: API endpoints for team user and administrator authentication.
# Updated with logging.
# Updated cookie 'secure' flag to True for HTTPS.

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, constr
from typing import Optional

from app.db.database import get_db
from app.core import security
from app.core.config import settings
from app.core.limiter import limiter
from app.crud.crud_team import team as crud_team
from app.schemas.team import Team as TeamSchema
from app.schemas.token import Token
from app.schemas.msg import Msg

from app.api.v1.deps import get_current_team_user, get_current_admin_user
from app.db.models.team import Team as TeamModel
# from app.schemas.team import Team as TeamSchema # Already imported
# from app.schemas.msg import Msg # For the admin response # Already imported

log = logging.getLogger(__name__)
router = APIRouter()

class AdminLoginRequest(BaseModel):
    password: str

class TeamLoginRequest(BaseModel):
    username: str
    password: str


@router.post("/auth/login", response_model=TeamSchema, summary="Team User Login")
async def login_team_user(
    request: Request,
    response: Response,
    form_data: TeamLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Logs in a team user. Sets an HTTP-only session cookie.
    Corresponds to SRS 8.2.2. FR-AUTH-001.
    """
    remote_ip = request.client.host if request.client else "unknown"
    log.info(f"Team login attempt for username '{form_data.username}' from IP {remote_ip}")
    team = await crud_team.get_by_username(db, username=form_data.username)

    if not team or not security.verify_password(form_data.password, team.hashed_password):
        log.warning(f"Failed team login attempt for username '{form_data.username}' from IP {remote_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not team.is_active:
        log.warning(f"Inactive team login attempt for username '{form_data.username}' (Team ID: {team.team_id}) from IP {remote_ip}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team account is deactivated."
        )

    log.info(f"Successful team login for username '{form_data.username}' (Team ID: {team.team_id}) from IP {remote_ip}")
    access_token = security.create_access_token(
        subject=str(team.team_id),
        is_admin=False,
        team_id_for_token=team.team_id
    )

    response.set_cookie(
        key="team_session_id",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=True, # Set to True for HTTPS
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )
    return TeamSchema.model_validate(team)


@router.post("/auth/logout", response_model=Msg, summary="Team User Logout")
async def logout_team_user(request: Request, response: Response):
    """
    Logs out a team user by clearing the session cookie.
    Corresponds to SRS 8.2.3. FR-AUTH-005.
    """
    remote_ip = request.client.host if request.client else "unknown"
    log.info(f"Team user logout request from IP {remote_ip}")
    response.delete_cookie(
        key="team_session_id",
        path="/",
        samesite="lax",
        secure=True # Set to True for HTTPS
    )
    return {"message": "Team user logout successful."}


@router.post("/admin/auth/login", response_model=Msg, summary="Administrator Login")
@limiter.limit("5/minute")
async def login_admin(
    request: Request,
    response: Response,
    form_data: AdminLoginRequest,
):
    """
    Logs in the Administrator. Sets an HTTP-only admin session cookie.
    Protected against brute-force attacks by rate limiting.
    Corresponds to SRS 8.2.1. FR-ADM-002.
    """
    remote_ip = request.client.host if request.client else "unknown"
    log.info(f"Admin login attempt from IP {remote_ip}")

    if not security.verify_admin_password(form_data.password):
        log.warning(f"Failed admin login attempt from IP {remote_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid administrator password",
        )

    log.info(f"Successful admin login from IP {remote_ip}")
    admin_access_token = security.create_access_token(
        subject=settings.ADMIN_USERNAME,
        is_admin=True
    )

    response.set_cookie(
        key="admin_session_id",
        value=admin_access_token,
        httponly=True,
        samesite="lax",
        secure=True, # Set to True for HTTPS
        max_age=settings.ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )
    return {"message": "Admin login successful."}


@router.post("/admin/auth/logout", response_model=Msg, summary="Administrator Logout")
async def logout_admin(request: Request, response: Response):
    """
    Logs out the Administrator by clearing the admin session cookie.
    Corresponds to SRS 8.2.3.
    """
    remote_ip = request.client.host if request.client else "unknown"
    log.info(f"Admin logout request from IP {remote_ip}")
    response.delete_cookie(
        key="admin_session_id",
        path="/",
        samesite="lax",
        secure=True # Set to True for HTTPS
    )
    return {"message": "Admin logout successful."}

@router.get(
    "/auth/me",
    response_model=TeamSchema,
    summary="Get Current Authenticated Team User",
    tags=["Authentication"]
)
async def read_current_team(
    current_team: TeamModel = Depends(get_current_team_user)
):
    """
    Fetch details for the currently authenticated team user based on session cookie.
    """
    return current_team

@router.get(
    "/admin/auth/me",
    response_model=Msg,
    summary="Check Current Admin Session",
    tags=["Admin - Authentication"]
)
async def read_current_admin(
    current_admin_payload: dict = Depends(get_current_admin_user)
):
    """
    Check if the current session belongs to a valid administrator.
    Returns a simple success message if authenticated via admin cookie.
    """
    return {"message": "Admin session is valid"}
