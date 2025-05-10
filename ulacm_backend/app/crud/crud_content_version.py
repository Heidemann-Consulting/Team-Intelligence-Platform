# File: ulacm_backend/app/crud/crud_content_version.py
# Purpose: CRUD operations for ContentVersion model.
# Changes for Option 3 (Admin System Team):
# - saved_by_team_id remains NOT NULL.
# - If Admin saves a version of an Admin-owned Template/Workflow,
#   saved_by_team_id is set to ADMIN_SYSTEM_TEAM_ID.

from typing import Any, Dict, Optional, Union, List, Tuple
from uuid import UUID as PyUUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, update as sqlalchemy_update, and_
from sqlalchemy.orm import joinedload

from app.crud.base import CRUDBase
from app.db.models.content_version import ContentVersion
from app.db.models.content_item import ContentItem
from app.schemas.content_version import ContentVersionCreate
from app.core.config import settings # For ADMIN_SYSTEM_TEAM_ID
import logging

log = logging.getLogger(__name__)

class CRUDContentVersion(CRUDBase[ContentVersion, ContentVersionCreate, ContentVersionCreate]):
    """
    CRUD operations for ContentVersion model.
    """

    async def get_by_id(self, db: AsyncSession, *, version_id: PyUUID) -> Optional[ContentVersion]:
        statement = select(self.model).where(self.model.version_id == version_id).options(
            joinedload(self.model.saving_team), # type: ignore
            joinedload(self.model.item) # type: ignore
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none() # type: ignore

    async def create_new_version(
        self,
        db: AsyncSession,
        *,
        item_id: PyUUID,
        version_in: ContentVersionCreate,
        # saved_by_team_id is now the ID of the team performing the save,
        # or ADMIN_SYSTEM_TEAM_ID if an Admin is saving their Template/Workflow.
        saved_by_team_id: PyUUID, # Not optional, must be a valid team ID (user or system)
        is_initial_version: bool = False
    ) -> ContentVersion:
        if is_initial_version:
            next_version_number = 1
        else:
            subquery = (
                select(func.max(self.model.version_number)) # type: ignore
                .where(self.model.item_id == item_id) # type: ignore
                .scalar_subquery()
            )
            current_max_version_result = await db.execute(select(func.coalesce(subquery, 0)))
            current_max_version = current_max_version_result.scalar_one() # type: ignore
            next_version_number = current_max_version + 1

        db_obj_data = {
            "item_id": item_id,
            "markdown_content": version_in.markdown_content,
            "version_number": next_version_number,
            "saved_by_team_id": saved_by_team_id,
        }
        new_version = self.model(**db_obj_data) # type: ignore
        db.add(new_version)
        await db.flush()

        if new_version.version_id is None:
             await db.refresh(new_version, attribute_names=['version_id'])
        if new_version.version_id is None:
             raise RuntimeError("Failed to obtain version_id for the new ContentVersion.")

        update_item_stmt = (
            sqlalchemy_update(ContentItem)
            .where(ContentItem.item_id == item_id)
            .values(current_version_id=new_version.version_id, updated_at=func.now()) # type: ignore
            .execution_options(synchronize_session=False)
        )
        update_result = await db.execute(update_item_stmt)

        if update_result.rowcount == 0: # type: ignore
             await db.rollback()
             raise ValueError(f"ContentItem with id {item_id} not found, cannot set current_version_id.")

        # Commit should be handled by the calling service/endpoint
        # await db.commit()

        await db.refresh(new_version, attribute_names=['item', 'saving_team'])
        return new_version

    async def get_versions_for_item(
        self,
        db: AsyncSession,
        *,
        item_id: PyUUID,
        skip: int = 0,
        limit: int = 20,
        sort_order: str = "desc"
    ) -> Tuple[List[ContentVersion], int]:
        query = select(self.model).where(self.model.item_id == item_id) # type: ignore
        count_query = select(func.count(self.model.version_id)).select_from(self.model).where(self.model.item_id == item_id) # type: ignore

        total_count_result = await db.execute(count_query)
        total_count = total_count_result.scalar_one() # type: ignore

        sort_attr = self.model.version_number # type: ignore
        if sort_order.lower() == "asc":
            query = query.order_by(sort_attr.asc()) # type: ignore
        else:
            query = query.order_by(sort_attr.desc()) # type: ignore

        query = query.offset(skip).limit(limit).options(
             joinedload(self.model.saving_team) # type: ignore
        )
        versions_result = await db.execute(query)
        versions = versions_result.scalars().unique().all() # type: ignore
        return versions, total_count # type: ignore

    async def get_specific_version_by_number(
        self, db: AsyncSession, *, item_id: PyUUID, version_number: int
    ) -> Optional[ContentVersion]:
        statement = select(self.model).where( # type: ignore
            and_(
                self.model.item_id == item_id, # type: ignore
                self.model.version_number == version_number # type: ignore
            )
        ).options(
             joinedload(self.model.saving_team), # type: ignore
             joinedload(self.model.item) # type: ignore
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none() # type: ignore

content_version = CRUDContentVersion(ContentVersion)
