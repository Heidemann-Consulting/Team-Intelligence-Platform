# File: ulacm_backend/app/crud/crud_content_version.py
# Purpose: CRUD operations for ContentVersion model.
# Ensuring the asterisk for keyword-only arguments is present.

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
from app.core.config import settings
from app.services.embedding_service import generate_embedding
import logging

log = logging.getLogger(__name__)


class CRUDContentVersion(
    CRUDBase[ContentVersion, ContentVersionCreate, ContentVersionCreate]
):
    """
    CRUD operations for ContentVersion model.
    """

    async def get_by_id(
        self, db: AsyncSession, *, version_id: PyUUID
    ) -> Optional[ContentVersion]:
        statement = (
            select(self.model)
            .where(self.model.version_id == version_id)
            .options(joinedload(self.model.saving_team), joinedload(self.model.item))
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def create_new_version(
        self,
        db: AsyncSession,  # Positional argument
        *,  # Keyword-only arguments follow
        item_id: PyUUID,
        version_in: ContentVersionCreate,
        saved_by_team_id: PyUUID,
        is_initial_version: bool = False,
    ) -> ContentVersion:

        if is_initial_version:
            next_version_number = 1
        else:
            subquery = (
                select(func.max(self.model.version_number))
                .where(self.model.item_id == item_id)
                .scalar_subquery()
            )
            current_max_version_result = await db.execute(
                select(func.coalesce(subquery, 0))
            )
            current_max_version = current_max_version_result.scalar_one()
            next_version_number = current_max_version + 1

        db_obj_data = {
            "item_id": item_id,
            "markdown_content": version_in.markdown_content,
            "version_number": next_version_number,
            "saved_by_team_id": saved_by_team_id,
            "content_vector": generate_embedding(version_in.markdown_content),
            "vector": generate_embedding(version_in.markdown_content),
        }
        new_version = self.model(**db_obj_data)
        db.add(new_version)
        await db.flush()

        if new_version.version_id is None:
            await db.refresh(new_version, attribute_names=["version_id"])
        if new_version.version_id is None:
            await db.rollback()
            log.error(
                f"Failed to obtain version_id for new ContentVersion for item_id {item_id} after flush and refresh."
            )
            raise RuntimeError(
                "Failed to obtain version_id for the new ContentVersion."
            )

        update_item_stmt = (
            sqlalchemy_update(ContentItem)
            .where(ContentItem.item_id == item_id)
            .values(current_version_id=new_version.version_id, updated_at=func.now())
            .execution_options(synchronize_session=False)
        )
        update_result = await db.execute(update_item_stmt)

        if update_result.rowcount == 0:
            await db.rollback()
            log.error(
                f"ContentItem with id {item_id} not found during version creation, cannot set current_version_id."
            )
            raise ValueError(
                f"ContentItem with id {item_id} not found, cannot set current_version_id."
            )

        await db.refresh(new_version, attribute_names=["item", "saving_team"])
        return new_version

    async def get_versions_for_item(
        self,
        db: AsyncSession,
        *,
        item_id: PyUUID,
        skip: int = 0,
        limit: int = 20,
        sort_order: str = "desc",
    ) -> Tuple[List[ContentVersion], int]:

        query = select(self.model).where(self.model.item_id == item_id)
        count_query = (
            select(func.count(self.model.version_id))
            .select_from(self.model)
            .where(self.model.item_id == item_id)
        )

        total_count_result = await db.execute(count_query)
        total_count = total_count_result.scalar_one()

        sort_attr = self.model.version_number
        if sort_order.lower() == "asc":
            query = query.order_by(sort_attr.asc())
        else:
            query = query.order_by(sort_attr.desc())

        query = (
            query.offset(skip).limit(limit).options(joinedload(self.model.saving_team))
        )
        versions_result = await db.execute(query)
        versions = versions_result.scalars().unique().all()
        return versions, total_count

    async def get_specific_version_by_number(
        self, db: AsyncSession, *, item_id: PyUUID, version_number: int
    ) -> Optional[ContentVersion]:
        statement = (
            select(self.model)
            .where(
                and_(
                    self.model.item_id == item_id,
                    self.model.version_number == version_number,
                )
            )
            .options(joinedload(self.model.saving_team), joinedload(self.model.item))
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()


content_version = CRUDContentVersion(ContentVersion)
