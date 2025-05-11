# File: ulacm_backend/app/crud/crud_content_item.py
# Purpose: CRUD operations for ContentItem model.
# Updated: Parse workflow definition for WORKFLOW type items to populate schema fields.
# Updated: Enhanced get_items_for_team_or_admin with more filtering capabilities.

from typing import Any, Dict, Optional, Union, List, Tuple
from uuid import UUID as PyUUID
from datetime import datetime, timezone # Added timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, and_, update as sqlalchemy_update, cast, String as SQLString
from sqlalchemy.orm import joinedload, selectinload # Added selectinload

from app.crud.base import CRUDBase
from app.db.models.content_item import ContentItem, ContentItemTypeEnum
from app.db.models.content_version import ContentVersion
from app.schemas.content_item import (
    ContentItemCreate,
    ContentItemUpdateMeta,
    ContentItemDuplicatePayload,
    # ContentItemListItem, # Not directly used for return type here, but for context
)
from app.schemas.content_version import ContentVersionCreate
from app.core.config import settings
from app.services.workflow_parser import WorkflowDefinitionParser, WorkflowParsingError, ValidatedWorkflowDefinition

import logging

log = logging.getLogger(__name__)

class CRUDContentItem(CRUDBase[ContentItem, ContentItemCreate, ContentItemUpdateMeta]):
    """
    CRUD operations for ContentItem model.
    """

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
        """
        Get a content item by its ID, joining with current version, its saving team, and owner team.
        Access control should be handled by the calling service/endpoint.
        """
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
        # This method was specific to a previous access pattern.
        # For general fetching with authorization, rely on get_by_id and endpoint-level checks,
        # or refine this method if a specific "usage" access pattern is still needed distinctly.
        # For now, we assume get_by_id is the primary fetch, and endpoints handle access logic.
        item = await self.get_by_id(db, item_id=item_id)

        if not item:
            return None

        if is_admin_request:
            return item # Admins can access any item by ID directly via this CRUD

        # Team user access logic
        if requesting_team_id:
            if item.item_type == ContentItemTypeEnum.DOCUMENT:
                if item.team_id == requesting_team_id or item.is_globally_visible:
                    return item
            elif item.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW]:
                # Teams can access globally visible Admin System Templates/Workflows
                if item.team_id == settings.ADMIN_SYSTEM_TEAM_ID and item.is_globally_visible:
                    return item
                # Legacy case: Team accessing a T/W they somehow "own" (should not happen with ADMIN_SYSTEM_TEAM_ID model)
                # or a globally visible T/W not owned by ADMIN_SYSTEM_TEAM_ID (also unlikely)
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
            db_obj_data["is_globally_visible"] = True # Admin T/W are global by default
        elif not is_admin_actor and actor_team_id and obj_in.item_type == ContentItemTypeEnum.DOCUMENT:
            item_owner_team_id = actor_team_id
            db_obj_data["team_id"] = item_owner_team_id
            # Documents are private by default unless explicitly set, which ContentItemCreate doesn't support.
            # Default is_globally_visible is False in the model.
            db_obj_data.setdefault('is_globally_visible', False)
        else:
            raise ValueError("Invalid parameters for item creation: role, type, or team_id mismatch.")

        if not await self.check_name_uniqueness(db, name=obj_in.name, item_type=obj_in.item_type, team_id=item_owner_team_id):
            raise ValueError(f"{obj_in.item_type.value} with name '{obj_in.name}' already exists for the owner.")

        template_id_for_doc_creation = None
        if obj_in.item_type == ContentItemTypeEnum.DOCUMENT and obj_in.template_id:
            if isinstance(obj_in.template_id, str):
                try:
                    template_id_for_doc_creation = PyUUID(obj_in.template_id)
                except ValueError:
                    raise ValueError("Invalid template_id format for Document creation.")
            else: # Is already UUID4
                template_id_for_doc_creation = obj_in.template_id # type: ignore

            if "template_id" in db_obj_data: # template_id is not a DB column on ContentItem
                del db_obj_data["template_id"]

        db_item = self.model(**db_obj_data)
        db.add(db_item)
        await db.flush() # Get item_id

        initial_content_for_version = ""
        if obj_in.item_type == ContentItemTypeEnum.DOCUMENT and template_id_for_doc_creation and actor_team_id:
            # Fetch the template to get its content
            template_item_stmt = select(ContentItem).where(
                ContentItem.item_id == template_id_for_doc_creation,
                ContentItem.item_type == ContentItemTypeEnum.TEMPLATE,
                ContentItem.team_id == settings.ADMIN_SYSTEM_TEAM_ID, # Templates are admin-owned
                ContentItem.is_globally_visible == True # Must be usable by team
            ).options(joinedload(ContentItem.current_version)) # Eager load its current version

            template_result = await db.execute(template_item_stmt)
            template_item_db = template_result.scalar_one_or_none()

            if template_item_db and template_item_db.current_version:
                initial_content_for_version = template_item_db.current_version.markdown_content
            elif not template_item_db:
                await db.rollback() # Rollback the item creation if template is invalid
                raise ValueError(f"Selected Template (ID: {template_id_for_doc_creation}) not found or not an accessible Admin System Template.")

        # For new Templates/Workflows by Admins, or Documents by teams.
        # An initial version is created. For T/W, content is often default, for Docs, from template.
        # The `contentService.createItem` in frontend for Admin T/W creation navigates to EditorViewPage
        # where the first save will create the first version with actual content.
        # So, for Admin T/W, initial_content_for_version might be empty here, and that's okay.
        # For Documents, it must come from a template.

        from app.crud.crud_content_version import content_version as crud_version_module # Local import
        version_payload = ContentVersionCreate(markdown_content=initial_content_for_version)

        if db_item.item_id is None: # Should not happen after flush
             await db.rollback()
             raise RuntimeError("Failed to get item_id for new item after flush.")

        version_saver_id = actor_team_id if obj_in.item_type == ContentItemTypeEnum.DOCUMENT else settings.ADMIN_SYSTEM_TEAM_ID

        await crud_version_module.create_new_version(
            db,
            item_id=db_item.item_id,
            version_in=version_payload,
            saved_by_team_id=version_saver_id,
            is_initial_version=True
        )

        await db.commit() # Commit after item and its initial version are created
        await db.refresh(db_item, attribute_names=['current_version', 'owner_team'])
        return db_item

    async def get_items_for_team_or_admin(
        self,
        db: AsyncSession,
        *,
        requesting_actor_team_id: Optional[PyUUID],
        is_admin_actor: bool,
        item_type_filter: Optional[ContentItemTypeEnum] = None,
        name_query: Optional[str] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        is_globally_visible_filter: Optional[bool] = None,
        list_for_team_usage: bool = False, # True if team is listing T/W to use (not manage)
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "updated_at",
        sort_order: str = "desc"
    ) -> Tuple[List[ContentItem], int]:
        allowed_sort_columns = ["name", "created_at", "updated_at", "item_type"]
        sort_column_name = sort_by if sort_by in allowed_sort_columns else "updated_at"
        sort_attr = getattr(self.model, sort_column_name)

        query = select(self.model)
        count_query = select(func.count(self.model.item_id)).select_from(self.model)

        conditions = []

        # Primary access control based on role
        if is_admin_actor:
            # Admin can see all items, but filters apply
            if item_type_filter:
                conditions.append(self.model.item_type == item_type_filter)
                # If admin is listing T/W, they are usually interested in Admin System owned ones
                if item_type_filter in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW]:
                    conditions.append(self.model.team_id == settings.ADMIN_SYSTEM_TEAM_ID)
            # If no item_type_filter, admin sees all types. UI usually filters this.
        else: # Team user request
            if not requesting_actor_team_id:
                return [], 0 # Should not happen if endpoint requires auth

            if list_for_team_usage and item_type_filter in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW]:
                # Team listing T/W to use: must be Admin System owned and globally visible
                conditions.append(self.model.item_type == item_type_filter)
                conditions.append(self.model.team_id == settings.ADMIN_SYSTEM_TEAM_ID)
                conditions.append(self.model.is_globally_visible == True)
            elif item_type_filter == ContentItemTypeEnum.DOCUMENT:
                # Team listing their own documents or globally visible documents from other teams
                conditions.append(self.model.item_type == ContentItemTypeEnum.DOCUMENT)
                conditions.append(or_(
                    self.model.team_id == requesting_actor_team_id,
                    and_(
                        self.model.is_globally_visible == True,
                        self.model.team_id != settings.ADMIN_SYSTEM_TEAM_ID # Exclude admin system items unless explicitly asked for usage
                    )
                ))
            elif not item_type_filter: # Team's general list (their Documents)
                conditions.append(self.model.item_type == ContentItemTypeEnum.DOCUMENT)
                conditions.append(self.model.team_id == requesting_actor_team_id)
            else: # Team trying to list non-document types for management (should yield nothing for T/W)
                return [], 0

        # Apply additional filters
        if name_query:
            conditions.append(self.model.name.ilike(f"%{name_query}%"))
        if created_after:
            conditions.append(self.model.created_at >= created_after)
        if created_before:
            # Add 1 day to created_before to make the range inclusive of the end date
            # or adjust comparison to be strictly less than the day after created_before
            conditions.append(self.model.created_at < (created_before + timezone.timedelta(days=1)))
        if is_globally_visible_filter is not None:
            conditions.append(self.model.is_globally_visible == is_globally_visible_filter)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        total_count_result = await db.execute(count_query)
        total_count = total_count_result.scalar_one()

        query = query.order_by(sort_attr.asc() if sort_order.lower() == "asc" else sort_attr.desc())
        query = query.offset(skip).limit(limit).options(
            joinedload(self.model.current_version).joinedload(ContentVersion.saving_team),
            joinedload(self.model.owner_team)
        )

        items_orm_result = await db.execute(query)
        items_orm = items_orm_result.scalars().unique().all()

        return items_orm, total_count


    async def check_name_uniqueness(
        self, db: AsyncSession, *, name: str, item_type: ContentItemTypeEnum,
        team_id: PyUUID, # This is the prospective owner's ID
        exclude_item_id: Optional[PyUUID] = None
    ) -> bool:
        query = select(func.count(self.model.item_id)).where(
            func.lower(self.model.name) == func.lower(name), # Case-insensitive check
            self.model.item_type == item_type,
            self.model.team_id == team_id # Check against the specific owner
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
        db_obj = await self.get_by_id(db, item_id=item_id) # Fetches with relationships
        if not db_obj:
            return None

        can_update = False
        effective_item_owner_id = db_obj.team_id # The actual owner of the item

        if is_admin_actor:
            # Admin can update metadata of their own T/W or any Document
            if (db_obj.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW] and db_obj.team_id == settings.ADMIN_SYSTEM_TEAM_ID) \
               or db_obj.item_type == ContentItemTypeEnum.DOCUMENT:
                can_update = True
        elif requesting_actor_team_id and db_obj.team_id == requesting_actor_team_id:
            # Team user can update metadata of their own Documents
            if db_obj.item_type == ContentItemTypeEnum.DOCUMENT:
                can_update = True

        if not can_update:
            log.warning(f"Update meta failed: User (Admin: {is_admin_actor}, TeamID: {requesting_actor_team_id}) cannot update item {item_id} of type {db_obj.item_type} owned by {db_obj.team_id}")
            return None

        update_data = item_in.model_dump(exclude_unset=True)
        item_updated = False

        if "name" in update_data and update_data["name"].lower() != db_obj.name.lower():
            if not await self.check_name_uniqueness(
                db, name=update_data["name"], item_type=db_obj.item_type,
                team_id=effective_item_owner_id, # Check uniqueness against actual owner
                exclude_item_id=db_obj.item_id
            ):
                raise ValueError(f"{db_obj.item_type.value} with name '{update_data['name']}' already exists for the owner.")
            setattr(db_obj, "name", update_data["name"])
            item_updated = True

        if "is_globally_visible" in update_data and update_data["is_globally_visible"] != db_obj.is_globally_visible:
            # Permission to change visibility depends on who is acting and what item type
            can_change_visibility = False
            if is_admin_actor: # Admin can change visibility for their T/W or any Document
                can_change_visibility = True
            elif requesting_actor_team_id and db_obj.team_id == requesting_actor_team_id and db_obj.item_type == ContentItemTypeEnum.DOCUMENT:
                # Team user can change visibility for their own documents
                can_change_visibility = True

            if can_change_visibility:
                setattr(db_obj, "is_globally_visible", update_data["is_globally_visible"])
                item_updated = True
            elif "is_globally_visible" in update_data: # Tried to update but not allowed
                log.warning(f"User (Admin: {is_admin_actor}, TeamID: {requesting_actor_team_id}) not allowed to change visibility for item {item_id}")
                # Optionally raise an error or just ignore the change for this field
                # For now, we ignore if not permitted, only applying allowed changes.

        if item_updated:
            db_obj.updated_at = datetime.now(timezone.utc) # Manually set updated_at
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj, attribute_names=['current_version', 'owner_team'])
        return db_obj

    async def remove_item_for_owner_or_admin(
        self, db: AsyncSession, *, item_id: PyUUID, requesting_actor_team_id: Optional[PyUUID], is_admin_actor: bool
    ) -> Optional[ContentItem]:
        item_to_delete = await self.get_by_id(db, item_id=item_id) # Fetches with relationships
        if not item_to_delete:
            return None

        can_delete = False
        if is_admin_actor:
            # Admin can delete their own T/W or any Document
            if (item_to_delete.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW] and item_to_delete.team_id == settings.ADMIN_SYSTEM_TEAM_ID) \
               or item_to_delete.item_type == ContentItemTypeEnum.DOCUMENT:
                can_delete = True
        elif requesting_actor_team_id and item_to_delete.team_id == requesting_actor_team_id:
             # Team user can delete their own Documents
             if item_to_delete.item_type == ContentItemTypeEnum.DOCUMENT:
                can_delete = True

        if not can_delete:
            log.warning(f"Delete item failed: User (Admin: {is_admin_actor}, TeamID: {requesting_actor_team_id}) cannot delete item {item_id} of type {item_to_delete.item_type} owned by {item_to_delete.team_id}")
            return None

        await db.delete(item_to_delete) # SQLAlchemy handles cascade deletes based on model relationships
        await db.commit()
        return item_to_delete


    async def duplicate_item_logic(
        self, db: AsyncSession, *,
        source_item_id: PyUUID,
        payload: ContentItemDuplicatePayload,
        requesting_actor_team_id: Optional[PyUUID], # ID of the team/admin performing action
        is_admin_actor: bool
    ) -> ContentItem:
        source_item = await self.get_by_id(db=db, item_id=source_item_id)
        if not source_item:
            raise ValueError("Source item not found.")

        new_owner_id: PyUUID
        new_item_type = source_item.item_type # Default to same type

        if is_admin_actor:
            if source_item.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW]:
                new_owner_id = settings.ADMIN_SYSTEM_TEAM_ID # Admin duplicates their own T/W
            elif source_item.item_type == ContentItemTypeEnum.DOCUMENT:
                # Admin duplicating a doc. If target_owner_team_id is provided, use it. Else, duplicate for source item's team.
                new_owner_id = payload.target_owner_team_id or source_item.team_id
            else:
                raise ValueError("Invalid item type for admin duplication.")
        else: # Team actor
            if not requesting_actor_team_id:
                raise ValueError("Requesting team ID is required for team duplication.")

            if source_item.item_type == ContentItemTypeEnum.DOCUMENT and source_item.team_id == requesting_actor_team_id:
                new_owner_id = requesting_actor_team_id # Team duplicates their own document
            elif source_item.item_type == ContentItemTypeEnum.TEMPLATE and \
                 source_item.team_id == settings.ADMIN_SYSTEM_TEAM_ID and source_item.is_globally_visible:
                # Team duplicating an Admin System Template into a new Document for themselves
                new_owner_id = requesting_actor_team_id
                new_item_type = ContentItemTypeEnum.DOCUMENT # Result is a Document
            elif source_item.item_type == ContentItemTypeEnum.WORKFLOW and \
                 source_item.team_id == settings.ADMIN_SYSTEM_TEAM_ID and source_item.is_globally_visible:
                # Teams cannot duplicate Workflows directly. They execute them.
                raise ValueError("Teams execute Workflows, not duplicate them directly. This action is not permitted.")
            else: # Other cases, e.g. trying to duplicate a global doc not owned by them, or a non-global T/W
                raise ValueError("Not authorized to duplicate this item or invalid duplication scenario.")

        if not await self.check_name_uniqueness(db, name=payload.new_name, item_type=new_item_type, team_id=new_owner_id):
            raise ValueError(f"{new_item_type.value} with name '{payload.new_name}' already exists for the target owner.")

        duplicated_item_data = {
            "name": payload.new_name,
            "item_type": new_item_type,
            "team_id": new_owner_id,
            # New items are private by default, unless admin duplicates their own global T/W
            "is_globally_visible": (is_admin_actor and \
                                    source_item.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW] and \
                                    source_item.is_globally_visible and \
                                    new_owner_id == settings.ADMIN_SYSTEM_TEAM_ID)
        }

        new_db_item = ContentItem(**duplicated_item_data)
        db.add(new_db_item)
        await db.flush() # Get new_db_item.item_id

        content_to_copy = ""
        version_to_copy_from: Optional[ContentVersion] = None

        if payload.source_version_id:
            version_to_copy_from = await crud_content_version.content_version.get_by_id(db, version_id=payload.source_version_id)
            if not version_to_copy_from or version_to_copy_from.item_id != source_item_id:
                raise ValueError("Specified source version not found or does not belong to the source item.")
        elif source_item.current_version:
            version_to_copy_from = source_item.current_version

        if version_to_copy_from:
            content_to_copy = version_to_copy_from.markdown_content
        elif new_item_type == ContentItemTypeEnum.DOCUMENT: # Document must have content
             raise ValueError("Source item for duplication has no content.")

        if new_db_item.item_id is None:
            await db.rollback()
            raise RuntimeError("Failed to get item_id for duplicated item after flush.")

        version_payload = ContentVersionCreate(markdown_content=content_to_copy)
        # The saver of the first version of the duplicate is the actor performing the duplication
        # If admin duplicates, saved_by_team_id is ADMIN_SYSTEM_TEAM_ID
        # If team duplicates (a template into a doc, or their own doc), saved_by_team_id is their team_id
        version_saver_id = settings.ADMIN_SYSTEM_TEAM_ID if is_admin_actor else requesting_actor_team_id

        if version_saver_id is None: # Should not happen due to logic above
            await db.rollback()
            raise ValueError("Could not determine saver ID for duplicated item's first version.")

        await crud_content_version.content_version.create_new_version(
            db, item_id=new_db_item.item_id, version_in=version_payload,
            saved_by_team_id=version_saver_id,
            is_initial_version=True
        )

        await db.commit()
        await db.refresh(new_db_item, attribute_names=['current_version', 'owner_team'])
        if new_db_item.current_version: # Ensure saving_team is loaded for the new version
            await db.refresh(new_db_item.current_version, attribute_names=['saving_team'])

        return new_db_item

content_item = CRUDContentItem(ContentItem)
