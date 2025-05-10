# File: ulacm_backend/app/crud/crud_team.py
# Purpose: CRUD operations for Team model.
# Changes:
# - Removed await from result.scalar_one_or_none() and similar calls.
#   This is based on logs indicating result might be a synchronous CursorResult/ChunkedIteratorResult,
#   which would make its methods synchronous. This directly addresses the TypeError.
#   The root cause of why AsyncSession might yield such results with a correct DSN needs further investigation.

from typing import Any, Dict, Optional, Union, List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from uuid import UUID as PyUUID
from .base import CRUDBase

from app.db.models.team import Team
from app.schemas.team import TeamCreate, TeamUpdate
from app.core.security import get_password_hash
import logging

log = logging.getLogger(__name__)

class CRUDTeam(CRUDBase[Team, TeamCreate, TeamUpdate]):
    """
    CRUD operations for Team model.
    """
    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[Team]:
        query = select(self.model).where(func.lower(self.model.username) == func.lower(username))
        log.debug(f"Executing query for username: {username}") # Ensure this prints
        result = await db.execute(query)
        log.debug(f"DEBUG: db.execute result type in get_by_username: {type(result)}") # CRUCIAL LOG
        # Assuming result is CursorResult/ChunkedIteratorResult based on logs,
        # making scalar_one_or_none() a synchronous call.
        return result.scalar_one_or_none() # type: ignore


    async def get_by_team_name(self, db: AsyncSession, *, team_name: str) -> Optional[Team]:
        statement = select(self.model).where(func.lower(self.model.team_name) == func.lower(team_name))
        result = await db.execute(statement)
        log.debug(f"DEBUG: db.execute result type in get_by_team_name: {type(result)}")
        return result.scalar_one_or_none() # type: ignore


    async def get_by_id(self, db: AsyncSession, *, team_id: PyUUID) -> Optional[Team]:
        statement = select(self.model).where(self.model.team_id == team_id)
        result = await db.execute(statement)
        log.debug(f"DEBUG: db.execute result type in get_by_id: {type(result)}")
        return result.scalar_one_or_none() # type: ignore


    async def create(self, db: AsyncSession, *, obj_in: TeamCreate) -> Team:
        hashed_password = get_password_hash(obj_in.password)
        db_obj_data = obj_in.model_dump(exclude={"password"})
        db_obj_data["hashed_password"] = hashed_password
        if 'is_active' not in db_obj_data:
            db_obj_data['is_active'] = True

        db_obj = self.model(**db_obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Team,
        obj_in: Union[TeamUpdate, Dict[str, Any]]
    ) -> Team:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            update_data["hashed_password"] = hashed_password
            del update_data["password"]

        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def get_all_teams(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Team], int]:
        return await super().get_multi_with_total_count(db, skip=skip, limit=limit)

    async def activate_deactivate_team(
        self, db: AsyncSession, *, team: Team, is_active: bool
    ) -> Team:
        team.is_active = is_active
        db.add(team)
        await db.commit()
        await db.refresh(team)
        return team

    async def remove_team(self, db: AsyncSession, *, team_id: PyUUID) -> Optional[Team]:
        statement = select(self.model).where(self.model.team_id == team_id)
        result = await db.execute(statement)
        log.debug(f"DEBUG: db.execute result type in remove_team: {type(result)}")
        obj = result.scalar_one_or_none() # type: ignore
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

team = CRUDTeam(Team)
