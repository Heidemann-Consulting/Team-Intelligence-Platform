# File: ulacm_backend/app/crud/crud_content_item.py
# Purpose: CRUD operations for ContentItem model.
# Updated: Allow team users to create DOCUMENT type items without a template_id,
# resulting in an empty initial version.

from typing import Any, Dict, Optional, Union, List, Tuple
from uuid import UUID as PyUUID
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, and_, update as sqlalchemy_update, cast, String as SQLString, text
from sqlalchemy.orm import joinedload, selectinload, aliased
from sqlalchemy.dialects.postgresql import TSQUERY, TSVECTOR


from app.crud.base import CRUDBase
from app.db.models.content_item import ContentItem, ContentItemTypeEnum
from app.db.models.content_version import ContentVersion
from app.schemas.content_item import (
    ContentItemCreate,
    ContentItemUpdateMeta,
    ContentItemDuplicatePayload,
)
from app.schemas.content_version import ContentVersionCreate
from app.core.config import settings
from app.services.workflow_parser import WorkflowDefinitionParser, WorkflowParsingError, ValidatedWorkflowDefinition

import logging
import re

log = logging.getLogger(__name__)

FTS_CONFIG = 'english'

class CRUDContentItem(CRUDBase[ContentItem, ContentItemCreate, ContentItemUpdateMeta]):
    """
    CRUD operations for ContentItem model.
    """

    def _glob_to_sql_like(self, glob_pattern: str) -> str:
        """Converts a glob pattern to an SQL ILIKE pattern."""
        sql_pattern = glob_pattern.replace('%', '\\%').replace('_', '\\_')
        sql_pattern = sql_pattern.replace('*', '%').replace('?', '_')
        return sql_pattern

    def _parse_workflow_definition(self, item: ContentItem) -> Optional[ValidatedWorkflowDefinition]:
        """Helper to parse workflow definition from an item's content."""
        if item.item_type == ContentItemTypeEnum.WORKFLOW and \
           item.current_version and \
           item.current_version.markdown_content:
            try:
                return WorkflowDefinitionParser.parse_and_validate(item.current_version.markdown_content)
            except WorkflowParsingError as e:
                log.warning(f"CRUD: Failed to parse workflow definition for item {item.item_id}: {e}")
        return None

    async def get_by_id(self, db: AsyncSession, *, item_id: PyUUID) -> Optional[ContentItem]:
        statement = select(self.model).where(self.model.item_id == item_id).options(
            joinedload(self.model.current_version).joinedload(ContentVersion.saving_team),
            joinedload(self.model.owner_team)
        )
        result = await db.execute(statement)
        item = result.scalar_one_or_none()
        return item

    async def get_by_id_for_team_or_admin_usage(
        self, db: AsyncSession, *, item_id: PyUUID, requesting_team_id: Optional[PyUUID], is_admin_request: bool
    ) -> Optional[ContentItem]:
        item = await self.get_by_id(db, item_id=item_id)

        if not item:
            return None

        if is_admin_request:
            return item

        if requesting_team_id:
            if item.item_type == ContentItemTypeEnum.DOCUMENT:
                if item.team_id == requesting_team_id or item.is_globally_visible:
                    return item
            elif item.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW]:
                if item.team_id == settings.ADMIN_SYSTEM_TEAM_ID and item.is_globally_visible:
                    return item
                elif item.team_id == requesting_team_id and item.is_globally_visible:
                    log.warning(f"Team {requesting_team_id} accessing a Template/Workflow they own (item_id: {item.item_id}). This is legacy or for 'use if visible'.")
                    return item

        log.warning(f"Team {requesting_team_id} access denied for item {item_id} (type: {item.item_type}, owner: {item.team_id}) via get_by_id_for_team_or_admin_usage.")
        return None


    async def create_item_for_team_or_admin(
        self, db: AsyncSession, *, obj_in: ContentItemCreate,
        actor_team_id: Optional[PyUUID],
        is_admin_actor: bool
    ) -> ContentItem:
        db_obj_data = obj_in.model_dump(exclude_unset=True)
        item_owner_team_id: PyUUID

        if is_admin_actor and obj_in.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW]:
            item_owner_team_id = settings.ADMIN_SYSTEM_TEAM_ID
            db_obj_data["team_id"] = item_owner_team_id
            db_obj_data["is_globally_visible"] = True # Admin T/W are global by default for now
            if "template_id" in db_obj_data: # Ensure template_id is not passed for T/W
                del db_obj_data["template_id"]
        elif not is_admin_actor and actor_team_id and obj_in.item_type == ContentItemTypeEnum.DOCUMENT:
            item_owner_team_id = actor_team_id
            db_obj_data["team_id"] = item_owner_team_id
            db_obj_data.setdefault('is_globally_visible', False)
            # template_id handling for documents is now more flexible (see below)
        else:
            raise ValueError("Invalid parameters for item creation: role, type, or team_id mismatch.")

        if not await self.check_name_uniqueness(db, name=obj_in.name, item_type=obj_in.item_type, team_id=item_owner_team_id):
            raise ValueError(f"{obj_in.item_type.value} with name '{obj_in.name}' already exists for the owner.")

        template_id_for_doc_creation: Optional[PyUUID] = None
        initial_content_for_version = "" # Default to empty

        if obj_in.item_type == ContentItemTypeEnum.DOCUMENT:
            if obj_in.template_id: # If a template_id IS provided for a document
                if isinstance(obj_in.template_id, str):
                    try:
                        template_id_for_doc_creation = PyUUID(obj_in.template_id)
                    except ValueError:
                        raise ValueError("Invalid template_id format for Document creation.")
                elif isinstance(obj_in.template_id, PyUUID):
                    template_id_for_doc_creation = obj_in.template_id
                else: # Should not happen due to Pydantic validation, but as a safeguard
                    raise ValueError("Invalid template_id type.")

                # Fetch template content only if template_id_for_doc_creation is valid
                if template_id_for_doc_creation and actor_team_id: # actor_team_id implies a team user
                    template_item_stmt = select(ContentItem).where(
                        ContentItem.item_id == template_id_for_doc_creation,
                        ContentItem.item_type == ContentItemTypeEnum.TEMPLATE,
                        ContentItem.team_id == settings.ADMIN_SYSTEM_TEAM_ID, # Templates are admin owned
                        ContentItem.is_globally_visible == True
                    ).options(joinedload(ContentItem.current_version))

                    template_result = await db.execute(template_item_stmt)
                    template_item_db = template_result.scalar_one_or_none()

                    if template_item_db and template_item_db.current_version:
                        initial_content_for_version = template_item_db.current_version.markdown_content
                    elif not template_item_db: # template_id was provided but template not found/accessible
                        await db.rollback()
                        raise ValueError(f"Selected Template (ID: {template_id_for_doc_creation}) not found or not an accessible Admin System Template.")
            # If template_id is NOT provided for a DOCUMENT by a team user, initial_content_for_version remains ""
            # This is for cases like saving AI response as a new document.

            # Remove template_id from data to be passed to model constructor if it was just for lookup
            if "template_id" in db_obj_data:
                del db_obj_data["template_id"]

        # For TEMPLATE or WORKFLOW, initial_content_for_version remains ""
        # The frontend provides the actual default content when saving the first version.

        db_item = self.model(**db_obj_data)
        db.add(db_item)
        await db.flush() # item_id is generated here

        from app.crud.crud_content_version import content_version as crud_version_module
        version_payload = ContentVersionCreate(markdown_content=initial_content_for_version)

        if db_item.item_id is None: # Should not happen after flush
             await db.rollback()
             raise RuntimeError("Failed to get item_id for new item after flush.")

        version_saver_id = actor_team_id if obj_in.item_type == ContentItemTypeEnum.DOCUMENT and not is_admin_actor else settings.ADMIN_SYSTEM_TEAM_ID
        if is_admin_actor and obj_in.item_type == ContentItemTypeEnum.DOCUMENT: # Should not happen with current frontend logic
            version_saver_id = settings.ADMIN_SYSTEM_TEAM_ID # Or decide how admin saving doc is handled

        await crud_version_module.create_new_version(
            db,
            item_id=db_item.item_id,
            version_in=version_payload,
            saved_by_team_id=version_saver_id,
            is_initial_version=True
        )
        await db.commit() # Commit after item and its initial version are successfully prepared
        await db.refresh(db_item, attribute_names=['current_version', 'owner_team', 'current_version_id'])
        return db_item

    async def get_items_for_team_or_admin(
        self,
        db: AsyncSession,
        *,
        requesting_actor_team_id: Optional[PyUUID],
        is_admin_actor: bool,
        item_type_filter: Optional[ContentItemTypeEnum] = None,
        name_query: Optional[str] = None,
        content_query: Optional[str] = None,
        name_glob_patterns: Optional[List[str]] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        is_globally_visible_filter: Optional[bool] = None,
        list_for_team_usage: bool = False,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "updated_at",
        sort_order: str = "desc"
    ) -> Tuple[List[ContentItem], int]:
        CurrentVersionAliased = aliased(ContentVersion)

        query = select(self.model)
        count_query = select(func.count(self.model.item_id)).select_from(self.model)

        needs_version_join = bool(content_query) or (content_query and sort_by == "rank")
        if needs_version_join:
            query = query.join(CurrentVersionAliased, self.model.current_version_id == CurrentVersionAliased.version_id, isouter=True)
            count_query = count_query.join(CurrentVersionAliased, self.model.current_version_id == CurrentVersionAliased.version_id, isouter=True)

        conditions = []

        if is_admin_actor:
            if item_type_filter:
                conditions.append(self.model.item_type == item_type_filter)
                if item_type_filter in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW]:
                    conditions.append(self.model.team_id == settings.ADMIN_SYSTEM_TEAM_ID)
            # If no item_type_filter, admin sees all types. Further filtering by team_id (e.g. ADMIN_SYSTEM_TEAM_ID for T/W) happens here.
            elif not item_type_filter : # Admin listing all items, default to showing their T/W and all docs
                 # This logic might need refinement based on desired "all items" view for admin
                pass


        else: # Team user
            if not requesting_actor_team_id:
                return [], 0 # Should not happen if auth is checked

            if list_for_team_usage and item_type_filter in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW]:
                # Team listing T/W for usage: only admin-owned, globally visible
                conditions.append(self.model.item_type == item_type_filter)
                conditions.append(self.model.team_id == settings.ADMIN_SYSTEM_TEAM_ID)
                conditions.append(self.model.is_globally_visible == True)
            elif item_type_filter == ContentItemTypeEnum.DOCUMENT:
                # Team listing their documents or globally visible ones
                conditions.append(self.model.item_type == ContentItemTypeEnum.DOCUMENT)
                conditions.append(or_(
                    self.model.team_id == requesting_actor_team_id,
                    and_(
                        self.model.is_globally_visible == True,
                        self.model.team_id != settings.ADMIN_SYSTEM_TEAM_ID, # Ensure not accidentally listing admin system as global if it's a doc
                        self.model.team_id != requesting_actor_team_id # Already covered by OR, but explicit
                    )
                ))
            elif not item_type_filter: # Default for team user: list their own documents
                conditions.append(self.model.item_type == ContentItemTypeEnum.DOCUMENT)
                conditions.append(self.model.team_id == requesting_actor_team_id)
            else: # e.g. team user trying to list TEMPLATE/WORKFLOW not for_usage - show nothing
                return [], 0

        if name_glob_patterns:
            glob_filter_conditions = []
            for pattern in name_glob_patterns:
                sql_like_pattern = self._glob_to_sql_like(pattern)
                glob_filter_conditions.append(self.model.name.ilike(sql_like_pattern))
            if glob_filter_conditions:
                conditions.append(or_(*glob_filter_conditions))

        if name_query:
            conditions.append(self.model.name.ilike(f"%{name_query}%"))

        if content_query and needs_version_join:
            ts_query_obj = func.plainto_tsquery(FTS_CONFIG, content_query)
            content_match_condition = or_(
                func.to_tsvector(FTS_CONFIG, self.model.name).op('@@')(ts_query_obj),
                CurrentVersionAliased.content_tsv.op('@@')(ts_query_obj)
            )
            conditions.append(content_match_condition)

        if created_after:
            conditions.append(self.model.created_at >= created_after)
        if created_before: # Inclusive end day
            conditions.append(self.model.created_at < (created_before + datetime.timedelta(days=1)))


        if is_globally_visible_filter is not None:
            conditions.append(self.model.is_globally_visible == is_globally_visible_filter)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        total_count_result = await db.execute(count_query)
        total_count = total_count_result.scalar_one()

        allowed_sort_columns = ["name", "created_at", "updated_at", "item_type"]
        if content_query and needs_version_join and sort_by == "rank":
            ts_query_obj_for_rank = func.plainto_tsquery(FTS_CONFIG, content_query)
            rank_expression = (
                func.ts_rank_cd(CurrentVersionAliased.content_tsv, ts_query_obj_for_rank) * 0.8 +
                func.ts_rank_cd(func.to_tsvector(FTS_CONFIG, self.model.name), ts_query_obj_for_rank) * 0.2
            )
            query = query.order_by(rank_expression.desc() if sort_order.lower() == "desc" else rank_expression.asc())
        else:
            sort_column_name_to_use = sort_by if sort_by in allowed_sort_columns else "updated_at"
            sort_attr = getattr(self.model, sort_column_name_to_use)
            query = query.order_by(sort_attr.asc() if sort_order.lower() == "asc" else sort_attr.desc())

        query = query.offset(skip).limit(limit).options(
            selectinload(self.model.current_version).joinedload(ContentVersion.saving_team),
            selectinload(self.model.owner_team)
        )

        items_orm_result = await db.execute(query)
        items_orm = items_orm_result.scalars().unique().all()

        return items_orm, total_count

    async def check_name_uniqueness(
        self, db: AsyncSession, *, name: str, item_type: ContentItemTypeEnum,
        team_id: PyUUID, # This is the owner_team_id
        exclude_item_id: Optional[PyUUID] = None
    ) -> bool:
        query = select(func.count(self.model.item_id)).where(
            func.lower(self.model.name) == func.lower(name),
            self.model.item_type == item_type,
            self.model.team_id == team_id # Check against the owner
        )
        if exclude_item_id:
            query = query.where(self.model.item_id != exclude_item_id)

        count_result = await db.execute(query)
        count = count_result.scalar_one()
        return count == 0

    async def update_item_meta_for_owner_or_admin(
        self, db: AsyncSession, *, item_id: PyUUID, item_in: ContentItemUpdateMeta,
        requesting_actor_team_id: Optional[PyUUID],
        is_admin_actor: bool
    ) -> Optional[ContentItem]:
        db_obj = await self.get_by_id(db, item_id=item_id)
        if not db_obj:
            return None

        can_update = False
        effective_item_owner_id = db_obj.team_id # The actual owner of the item

        if is_admin_actor:
            # Admin can edit meta of their own T/W or ANY document
            if (db_obj.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW] and db_obj.team_id == settings.ADMIN_SYSTEM_TEAM_ID) \
               or db_obj.item_type == ContentItemTypeEnum.DOCUMENT:
                can_update = True
        elif requesting_actor_team_id and db_obj.team_id == requesting_actor_team_id:
            # Team user can edit meta of their own documents
            if db_obj.item_type == ContentItemTypeEnum.DOCUMENT:
                can_update = True

        if not can_update:
            log.warning(f"Update meta failed: User (Admin: {is_admin_actor}, TeamID: {requesting_actor_team_id}) cannot update item {item_id} of type {db_obj.item_type} owned by {db_obj.team_id}")
            return None # Or raise HTTPException(403)

        update_data = item_in.model_dump(exclude_unset=True)
        item_updated = False

        if "name" in update_data and update_data["name"].lower() != db_obj.name.lower():
            if not await self.check_name_uniqueness(
                db, name=update_data["name"], item_type=db_obj.item_type,
                team_id=effective_item_owner_id, # Check uniqueness against the item's actual owner
                exclude_item_id=db_obj.item_id
            ):
                raise ValueError(f"{db_obj.item_type.value} with name '{update_data['name']}' already exists for the owner.")
            setattr(db_obj, "name", update_data["name"])
            item_updated = True

        if "is_globally_visible" in update_data and update_data["is_globally_visible"] != db_obj.is_globally_visible:
            can_change_visibility = False
            if is_admin_actor: # Admin can change visibility for items they manage (their T/W or any Doc)
                 if (db_obj.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW] and db_obj.team_id == settings.ADMIN_SYSTEM_TEAM_ID) \
                    or db_obj.item_type == ContentItemTypeEnum.DOCUMENT:
                    can_change_visibility = True
            elif requesting_actor_team_id and db_obj.team_id == requesting_actor_team_id and db_obj.item_type == ContentItemTypeEnum.DOCUMENT:
                 # Team users can change visibility of their own documents
                can_change_visibility = True

            if can_change_visibility:
                setattr(db_obj, "is_globally_visible", update_data["is_globally_visible"])
                item_updated = True
            elif "is_globally_visible" in update_data : # Attempted but not allowed
                 log.warning(f"User (Admin: {is_admin_actor}, TeamID: {requesting_actor_team_id}) not allowed to change visibility for item {item_id}")
                 # Optionally raise 403 here if this should be a hard stop

        if item_updated:
            db_obj.updated_at = datetime.now(timezone.utc) # Ensure updated_at is modified
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj, attribute_names=['current_version', 'owner_team'])
        return db_obj

    async def remove_item_for_owner_or_admin(
        self, db: AsyncSession, *, item_id: PyUUID, requesting_actor_team_id: Optional[PyUUID], is_admin_actor: bool
    ) -> Optional[ContentItem]:
        item_to_delete = await self.get_by_id(db, item_id=item_id)
        if not item_to_delete:
            return None

        can_delete = False
        if is_admin_actor:
            # Admin can delete their own T/W or ANY document
            if (item_to_delete.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW] and item_to_delete.team_id == settings.ADMIN_SYSTEM_TEAM_ID) \
                or item_to_delete.item_type == ContentItemTypeEnum.DOCUMENT:
                can_delete = True
        elif requesting_actor_team_id and item_to_delete.team_id == requesting_actor_team_id:
             # Team user can delete their own documents
             if item_to_delete.item_type == ContentItemTypeEnum.DOCUMENT:
                can_delete = True

        if not can_delete:
            log.warning(f"Delete item failed: User (Admin: {is_admin_actor}, TeamID: {requesting_actor_team_id}) cannot delete item {item_id} of type {item_to_delete.item_type} owned by {item_to_delete.team_id}")
            return None # Or raise 403

        await db.delete(item_to_delete) # Versions will cascade delete due to DB schema
        await db.commit()
        return item_to_delete


    async def duplicate_item_logic(
        self, db: AsyncSession, *,
        source_item_id: PyUUID,
        payload: ContentItemDuplicatePayload,
        requesting_actor_team_id: Optional[PyUUID], # This is the ID of the team performing the duplication
        is_admin_actor: bool
    ) -> ContentItem:
        source_item = await self.get_by_id(db=db, item_id=source_item_id)
        if not source_item:
            raise ValueError("Source item not found.")

        new_owner_id: PyUUID
        new_item_type = source_item.item_type # Default to same type
        new_is_globally_visible = False # Default to private for new duplicate

        if is_admin_actor:
            # Admin duplicating:
            if source_item.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW]:
                # Admin duplicates T/W -> new T/W owned by ADMIN_SYSTEM_TEAM_ID
                new_owner_id = settings.ADMIN_SYSTEM_TEAM_ID
                new_is_globally_visible = source_item.is_globally_visible # Retain global status for Admin T/W duplicates
            elif source_item.item_type == ContentItemTypeEnum.DOCUMENT:
                # Admin duplicates a Document.
                # Target owner can be specified, or defaults to original owner. Result is a Document.
                new_owner_id = payload.target_owner_team_id if payload.target_owner_team_id else source_item.team_id
                if new_owner_id == settings.ADMIN_SYSTEM_TEAM_ID: # If admin makes themselves owner of duplicated doc
                     new_is_globally_visible = source_item.is_globally_visible # Maintain if admin owns it
                else: # If owned by a regular team, default to private
                     new_is_globally_visible = False
            else:
                raise ValueError("Invalid item type for admin duplication.")
        else: # Team user duplicating
            if not requesting_actor_team_id:
                raise ValueError("Requesting team ID is required for team duplication.")

            if source_item.item_type == ContentItemTypeEnum.DOCUMENT and \
               (source_item.team_id == requesting_actor_team_id or source_item.is_globally_visible):
                # Team duplicates their own doc or a global doc -> new doc owned by them
                new_owner_id = requesting_actor_team_id
                new_item_type = ContentItemTypeEnum.DOCUMENT
                new_is_globally_visible = False
            elif source_item.item_type == ContentItemTypeEnum.TEMPLATE and \
                 source_item.team_id == settings.ADMIN_SYSTEM_TEAM_ID and source_item.is_globally_visible:
                # Team duplicates a global template -> new doc owned by them
                new_owner_id = requesting_actor_team_id
                new_item_type = ContentItemTypeEnum.DOCUMENT # Templates become documents for teams
                new_is_globally_visible = False
            elif source_item.item_type == ContentItemTypeEnum.WORKFLOW and \
                 source_item.team_id == settings.ADMIN_SYSTEM_TEAM_ID and source_item.is_globally_visible:
                raise ValueError("Teams execute Workflows, not duplicate them directly. This action is not permitted.")
            else:
                raise ValueError("Not authorized to duplicate this item or invalid duplication scenario.")

        if not await self.check_name_uniqueness(db, name=payload.new_name, item_type=new_item_type, team_id=new_owner_id):
            raise ValueError(f"{new_item_type.value} with name '{payload.new_name}' already exists for the target owner.")

        duplicated_item_data = {
            "name": payload.new_name,
            "item_type": new_item_type,
            "team_id": new_owner_id,
            "is_globally_visible": new_is_globally_visible,
        }

        new_db_item = ContentItem(**duplicated_item_data)
        db.add(new_db_item)
        await db.flush()

        content_to_copy = ""
        version_to_copy_from: Optional[ContentVersion] = None

        if payload.source_version_id:
            from app.crud.crud_content_version import content_version as crud_cv # Local import
            version_to_copy_from = await crud_cv.get_by_id(db, version_id=payload.source_version_id)
            if not version_to_copy_from or version_to_copy_from.item_id != source_item_id:
                raise ValueError("Specified source version not found or does not belong to the source item.")
        elif source_item.current_version:
            version_to_copy_from = source_item.current_version

        if version_to_copy_from:
            content_to_copy = version_to_copy_from.markdown_content
        elif new_item_type == ContentItemTypeEnum.DOCUMENT: # Only raise if it's a doc and no content could be found
             # This might happen if source_item had no current_version and no source_version_id was given
             log.warning(f"Source item {source_item_id} (type: {source_item.item_type}) had no content to copy for duplication to new type {new_item_type}.")
             # content_to_copy remains "" which is acceptable for a new document.

        if new_db_item.item_id is None:
            await db.rollback()
            raise RuntimeError("Failed to get item_id for duplicated item after flush.")

        version_payload = ContentVersionCreate(markdown_content=content_to_copy)
        # The saver of the first version of a duplicated item is the duplicator
        version_saver_id = requesting_actor_team_id if not is_admin_actor else settings.ADMIN_SYSTEM_TEAM_ID
        if new_item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW] and is_admin_actor:
            version_saver_id = settings.ADMIN_SYSTEM_TEAM_ID


        if version_saver_id is None: # Should not happen given logic above
             await db.rollback()
             raise ValueError("Could not determine saver ID for duplicated item's first version.")

        from app.crud.crud_content_version import content_version as crud_version_module # Local import
        await crud_version_module.create_new_version(
            db, item_id=new_db_item.item_id, version_in=version_payload,
            saved_by_team_id=version_saver_id,
            is_initial_version=True
        )

        await db.commit()
        await db.refresh(new_db_item, attribute_names=['current_version', 'owner_team', 'current_version_id'])
        if new_db_item.current_version: # Ensure current_version and its related saving_team are loaded
            await db.refresh(new_db_item.current_version, attribute_names=['saving_team'])

        return new_db_item

content_item = CRUDContentItem(ContentItem)
