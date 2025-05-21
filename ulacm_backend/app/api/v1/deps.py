# File: ulacm_backend/app/api/v1/deps.py
# Purpose: API dependencies, e.g., for getting current user.
# Updated: Ensure get_current_admin_user uses ADMIN_USERNAME from settings.

import logging
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import APIKeyCookie
from pydantic import UUID4
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Union
from jose import JWTError
from pydantic import ValidationError

from app.core.config import settings
from app.core import security
from app.db.database import get_db
from app.db.models.team import Team as TeamModel
from app.crud.crud_team import team as crud_team
from app.schemas.token import TokenPayload

log = logging.getLogger(__name__)

team_cookie_scheme = APIKeyCookie(name="team_session_id", auto_error=False)
admin_cookie_scheme = APIKeyCookie(name="admin_session_id", auto_error=False)


async def get_current_team_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    session_cookie: Optional[str] = Depends(team_cookie_scheme)
) -> TeamModel:
    remote_ip = request.client.host if request.client else "unknown"
    if not session_cookie:
        log.debug(f"Team authentication failed: No session cookie provided. IP: {remote_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated (no session cookie)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    team_uuid_from_token: Optional[uuid.UUID] = None

    try:
        token_data: Optional[TokenPayload] = security.decode_token(session_cookie)

        if not token_data or not token_data.sub:
            log.warning(f"Team authentication failed: No token data or subject is missing/None. IP: {remote_ip}. Token Data: {token_data}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials (token data or subject missing)",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if token_data.is_admin:
            log.warning(f"Team authentication failed: Admin token provided for team user endpoint. IP: {remote_ip}. Token Data: {token_data}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials (admin token for team route)",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if isinstance(token_data.sub, uuid.UUID):
            team_uuid_from_token = token_data.sub
        elif isinstance(token_data.sub, str):
            try:
                team_uuid_from_token = uuid.UUID(token_data.sub, version=4)
            except ValueError:
                log.warning(f"Team authentication failed: Subject ('{token_data.sub}') for team token is a string but not a valid UUID. IP: {remote_ip}.")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials (malformed subject ID for team)",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            log.warning(f"Team authentication failed: Subject for team token has an unexpected type: {type(token_data.sub)}. IP: {remote_ip}. Token Data: {token_data}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials (invalid subject type for team)",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not team_uuid_from_token:
             log.error(f"Team authentication failed: Could not determine team UUID from token after processing subject. IP: {remote_ip}. Token Data: {token_data}")
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error processing token subject.")

    except (JWTError, ValidationError) as e:
        log.warning(f"Team authentication failed: Could not validate credentials, token expired/malformed, or validation error. Error: {e}. IP: {remote_ip}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials or token expired/malformed.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        # Ensure that the team_uuid_from_token is not the ADMIN_SYSTEM_TEAM_ID for regular team operations
        if team_uuid_from_token == settings.ADMIN_SYSTEM_TEAM_ID:
            log.warning(f"Team authentication failed: ADMIN_SYSTEM_TEAM_ID ('{team_uuid_from_token}') used as a regular team ID. IP: {remote_ip}.")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid team identifier.")

        user = await crud_team.get_by_id(db, team_id=team_uuid_from_token)
    except ValueError as e: # Should not happen if team_uuid_from_token is always uuid.UUID
         log.error(f"Database query error with team_id type: {e}. team_id was: {team_uuid_from_token} of type {type(team_uuid_from_token)}. IP: {remote_ip}")
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error processing user ID.")

    if not user:
        log.error(f"Team authentication failed: Team user not found for ID '{team_uuid_from_token}' in token. IP: {remote_ip}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team user not found")
    if not user.is_active:
        log.warning(f"Team authentication failed: Team user '{user.username}' (ID: {team_uuid_from_token}) is inactive. IP: {remote_ip}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Team account is inactive")
    if user.team_id == settings.ADMIN_SYSTEM_TEAM_ID: # Double check after fetching
        log.error(f"Critical: ADMIN_SYSTEM_TEAM_ID ('{user.team_id}') resolved to an actual user object intended for team operations. This should not happen. IP: {remote_ip}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied for system-level identity.")


    log.debug(f"Team authentication successful for team ID {user.team_id} ('{user.team_name}'). IP: {remote_ip}")
    return user

async def get_current_admin_user(
    request: Request,
    # db: AsyncSession = Depends(get_db), # Admin user isn't fetched from DB like teams
    session_cookie: Optional[str] = Depends(admin_cookie_scheme)
) -> TokenPayload: # Returns TokenPayload for admin
    """
    Dependency to verify an admin user based on session cookie.
    Raises HTTPException 401 if not an admin. FR-ADM-002, FR-SEC-005.
    """
    remote_ip = request.client.host if request.client else "unknown"
    if not session_cookie:
        log.debug(f"Admin authentication failed: No session cookie provided. IP: {remote_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not authenticated (no session cookie)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        token_data: Optional[TokenPayload] = security.decode_token(session_cookie)
        if (
            not token_data
            or not token_data.is_admin
            or not token_data.sub
            or not isinstance(token_data.sub, str)
            # Validate that the 'sub' field matches the configured ADMIN_USERNAME
            or token_data.sub != settings.ADMIN_USERNAME
        ):
            log.warning(f"Admin authentication failed: Invalid token (Not admin, wrong subject '{token_data.sub if token_data else 'N/A'}' vs expected '{settings.ADMIN_USERNAME}', or missing fields). IP: {remote_ip}. Token Data: {token_data}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not an authorized administrator",
            )
        log.debug(f"Admin authentication successful for '{token_data.sub}'. IP: {remote_ip}")
        return token_data
    except (JWTError, ValidationError) as e:
        log.warning(f"Admin authentication failed: Could not validate admin credentials, token expired/malformed, or validation error. Error: {e}. IP: {remote_ip}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate admin credentials or token expired/malformed.",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_or_admin_marker(
    request: Request,
    db: AsyncSession = Depends(get_db), # db needed for get_current_team_user
    team_session_cookie: Optional[str] = Depends(team_cookie_scheme),
    admin_session_cookie: Optional[str] = Depends(admin_cookie_scheme),
) -> Union[TeamModel, TokenPayload, None]:
    """
    Attempts to authenticate as Admin first using admin_cookie.
    If admin_cookie is present and valid, returns Admin TokenPayload.
    If admin_cookie is present but invalid, raises HTTPException.
    If no admin_cookie, attempts to authenticate as Team user using team_cookie.
    If team_cookie is present and valid, returns TeamModel.
    If team_cookie is present but invalid, raises HTTPException.
    If neither cookie is present, returns None.
    """
    if admin_session_cookie:
        # If an admin cookie is present, we prioritize admin authentication.
        # get_current_admin_user will raise HTTPException if it's invalid.
        return await get_current_admin_user(request, admin_session_cookie) # db not needed by get_current_admin_user

    if team_session_cookie:
        # If no admin cookie, try team authentication.
        # get_current_team_user will raise HTTPException if it's invalid.
        return await get_current_team_user(request, db, team_session_cookie)

    # No relevant cookies were present
    return None


async def get_requesting_user_is_admin(
    current_user_session_info: Union[TeamModel, TokenPayload, None] = Depends(get_current_user_or_admin_marker)
) -> bool:
    """
    Dependency that returns True if the current user is an Admin based on the marker from get_current_user_or_admin_marker.
    """
    if current_user_session_info and isinstance(current_user_session_info, TokenPayload) and current_user_session_info.is_admin:
        return True
    return False

# Dependency to ensure the user is an admin, otherwise raises 403
# This is stricter than get_requesting_user_is_admin as it enforces admin presence.
async def ensure_admin_user(
    admin_payload: TokenPayload = Depends(get_current_admin_user)
) -> TokenPayload:
    """Ensures the current user is an admin, otherwise raises 403. Returns admin payload."""
    # get_current_admin_user already raises if not a valid admin
    return admin_payload
