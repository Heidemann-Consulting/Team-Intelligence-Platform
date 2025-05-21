# File: ulacm_backend/app/api/v1/endpoints/admin_teams.py
# Purpose: API endpoints for managing Team User accounts by an Administrator.
# Updated with logging.

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select # Import select
from typing import Any, List, Optional
from pydantic import UUID4

from app.db.database import get_db
from app.db.models import Team as TeamModel # If needed for query
from app.api.v1.deps import get_current_admin_user
from app.crud.crud_team import team as crud_team
from app.schemas.team import Team as TeamSchema, TeamCreate, TeamUpdate, TeamListResponse
from app.schemas.token import TokenPayload
from app.schemas.msg import Msg

log = logging.getLogger(__name__)
router = APIRouter()

@router.post(
    "",
    response_model=TeamSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create New Team",
    dependencies=[Depends(get_current_admin_user)]
)
async def create_team(
    request: Request, # Added for logging admin performing action
    *,
    db: AsyncSession = Depends(get_db),
    team_in: TeamCreate,
    current_admin: TokenPayload = Depends(get_current_admin_user)
):
    """
    Create a new team. (Requires Admin privileges)
    Checks for existing username and team name conflicts.
    """
    # --- Add Debugging Here ---
    print(f"DEBUG (endpoint): Received db object of type: {type(db)}")
    try:
        # Try a minimal query directly
        minimal_query = select(1)
        minimal_result = await db.execute(minimal_query)
        print(f"DEBUG (endpoint): Minimal query result type: {type(minimal_result)}")
        # You could even try fetching the result:
        # await minimal_result.scalar_one_or_none()
        # print("DEBUG (endpoint): Minimal query fetch successful")
    except Exception as e:
        print(f"DEBUG (endpoint): Error during minimal query: {e}")
    # --- End Debugging ---

    log.info(f"Admin attempting to create team: Name='{team_in.team_name}', Username='{team_in.username}'")

    # Check for existing username (This is where the original error occurred)
    existing_username = await crud_team.get_by_username(db, username=team_in.username)
    if existing_username:
        log.warning(f"Team creation failed: Username '{team_in.username}' already exists.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered by another team.",
        )

    # Check for existing team name
    existing_team_name = await crud_team.get_by_team_name(db, team_name=team_in.team_name)
    if existing_team_name:
        log.warning(f"Team creation failed: Team name '{team_in.team_name}' already exists.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Team name already exists.",
        )

    # Create the team
    try:
        team = await crud_team.create(db, obj_in=team_in)
        log.info(f"Successfully created team '{team.team_name}' (ID: {team.team_id})")
        return team
    except Exception as e:
        # Catch potential DB errors during creation
        log.error(f"Database error during team creation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the team.",
        )


@router.get(
    "",
    response_model=TeamListResponse,
    summary="List All Teams",
    dependencies=[Depends(get_current_admin_user)]
)
async def list_teams(
    request: Request, # Added for logging
    db: AsyncSession = Depends(get_db),
    offset: int = 0,
    limit: int = 50,
    current_admin: TokenPayload = Depends(get_current_admin_user)
):
    """
    Retrieve a list of all team user accounts. (FR-ADM-004)
    Corresponds to SRS 8.3.2. Pagination supported.
    """
    log.info(f"Admin requesting team list: offset={offset}, limit={limit}")
    if limit > 100: limit = 100
    teams, total_count = await crud_team.get_all_teams(db, skip=offset, limit=limit)
    log.info(f"Returning {len(teams)} teams out of {total_count} total.")
    return TeamListResponse(total_count=total_count, offset=offset, limit=limit, teams=teams)


@router.get(
    "/{team_id}",
    response_model=TeamSchema,
    summary="Get Team Details",
    dependencies=[Depends(get_current_admin_user)]
)
async def get_team_details(
    request: Request, # Added for logging
    team_id: UUID4 = Path(..., description="The ID of the team to retrieve"),
    db: AsyncSession = Depends(get_db),
    current_admin: TokenPayload = Depends(get_current_admin_user)
):
    """
    Retrieve details for a specific team account. Corresponds to SRS 8.3.3.
    """
    log.info(f"Admin requesting details for team ID: {team_id}")
    team = await crud_team.get_by_id(db, team_id=team_id)
    if not team:
        log.warning(f"Admin request failed: Team not found for ID: {team_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found.")
    log.info(f"Returning details for team: {team.team_name} ({team_id})")
    return team


@router.put(
    "/{team_id}",
    response_model=TeamSchema,
    summary="Update Team Details",
    dependencies=[Depends(get_current_admin_user)]
)
async def update_team(
    request: Request, # Added for logging
    team_id: UUID4 = Path(..., description="The ID of the team to update"),
    team_in: TeamUpdate = ...,
    db: AsyncSession = Depends(get_db),
    current_admin: TokenPayload = Depends(get_current_admin_user)
):
    """
    Update an existing team account's details (team name, password, active status). (FR-ADM-005)
    Username is not updatable. Corresponds to SRS 8.3.4.
    """
    log.info(f"Admin attempting to update team ID: {team_id} with data: {team_in.model_dump(exclude_unset=True)}")
    team = await crud_team.get_by_id(db, team_id=team_id)
    if not team:
        log.warning(f"Admin update failed: Team not found for ID: {team_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found.")

    if team_in.team_name and team_in.team_name.lower() != team.team_name.lower():
        existing_team_name = await crud_team.get_by_team_name(db, team_name=team_in.team_name)
        if existing_team_name and existing_team_name.team_id != team_id:
            log.warning(f"Admin update conflict: New team name '{team_in.team_name}' already exists (Team ID: {existing_team_name.team_id}).")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Team name '{team_in.team_name}' already exists.",
            )

    updated_team = await crud_team.update(db=db, db_obj=team, obj_in=team_in)
    log.info(f"Admin successfully updated team: {updated_team.team_name} ({team_id})")
    return updated_team


@router.post(
    "/{team_id}/deactivate",
    response_model=TeamSchema,
    summary="Deactivate Team",
    dependencies=[Depends(get_current_admin_user)]
)
async def deactivate_team(
    request: Request, # Added for logging
    team_id: UUID4 = Path(..., description="The ID of the team to deactivate"),
    db: AsyncSession = Depends(get_db),
    current_admin: TokenPayload = Depends(get_current_admin_user)
):
    """
    Deactivate a team user account. (FR-ADM-006) Corresponds to SRS 8.3.5.
    """
    log.info(f"Admin attempting to deactivate team ID: {team_id}")
    team = await crud_team.get_by_id(db, team_id=team_id)
    if not team:
        log.warning(f"Admin deactivate failed: Team not found for ID: {team_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found.")
    if not team.is_active:
        log.warning(f"Admin deactivate conflict: Team '{team.team_name}' ({team_id}) is already deactivated.")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Team is already deactivated.")

    updated_team = await crud_team.activate_deactivate_team(db=db, team=team, is_active=False)
    log.info(f"Admin successfully deactivated team: {updated_team.team_name} ({team_id})")
    return TeamSchema.model_validate(updated_team)


@router.post(
    "/{team_id}/reactivate",
    response_model=TeamSchema,
    summary="Reactivate Team",
    dependencies=[Depends(get_current_admin_user)]
)
async def reactivate_team(
    request: Request, # Added for logging
    team_id: UUID4 = Path(..., description="The ID of the team to reactivate"),
    db: AsyncSession = Depends(get_db),
    current_admin: TokenPayload = Depends(get_current_admin_user)
):
    """
    Reactivate a previously deactivated team user account. (FR-ADM-007) Corresponds to SRS 8.3.6.
    """
    log.info(f"Admin attempting to reactivate team ID: {team_id}")
    team = await crud_team.get_by_id(db, team_id=team_id)
    if not team:
        log.warning(f"Admin reactivate failed: Team not found for ID: {team_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found.")
    if team.is_active:
        log.warning(f"Admin reactivate conflict: Team '{team.team_name}' ({team_id}) is already active.")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Team is already active.")

    updated_team = await crud_team.activate_deactivate_team(db=db, team=team, is_active=True)
    log.info(f"Admin successfully reactivated team: {updated_team.team_name} ({team_id})")
    return TeamSchema.model_validate(updated_team)


@router.delete(
    "/{team_id}",
    response_model=Msg,
    status_code=status.HTTP_200_OK,
    summary="Delete Team",
    dependencies=[Depends(get_current_admin_user)]
)
async def delete_team(
    request: Request, # Added for logging
    team_id: UUID4 = Path(..., description="The ID of the team to delete"),
    db: AsyncSession = Depends(get_db),
    current_admin: TokenPayload = Depends(get_current_admin_user)
):
    """
    Permanently delete a team user account and all its associated content. (FR-ADM-008)
    Database cascade rules should handle deletion of associated content. Corresponds to SRS 8.3.7.
    """
    log.info(f"Admin attempting to delete team ID: {team_id}")
    team = await crud_team.get_by_id(db, team_id=team_id)
    if not team:
        log.warning(f"Admin delete failed: Team not found for ID: {team_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found.")

    team_name_for_log = team.team_name # Get name before deletion
    deleted_team = await crud_team.remove_team(db=db, team_id=team_id) # remove_team handles the actual deletion
    if not deleted_team:
        # This case should ideally not be reached if the first check passed, but log just in case
        log.error(f"Admin delete inconsistency: Team found initially but failed on removal for ID: {team_id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Team deletion failed unexpectedly.")

    log.info(f"Admin successfully deleted team: Name='{team_name_for_log}', ID='{team_id}'")
    return Msg(message=f"Team '{team_name_for_log}' (ID: {team_id}) and all associated content deleted successfully.")
