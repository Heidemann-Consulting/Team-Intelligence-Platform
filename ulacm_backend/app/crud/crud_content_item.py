# File: ulacm_backend/app/crud/crud_content_item.py
# Purpose: CRUD operations for ContentItem model.
# Updated: Parse workflow definition for WORKFLOW type items to populate schema fields.

from typing import Any, Dict, Optional, Union, List, Tuple
from uuid import UUID as PyUUID
from datetime import datetime, timezone # Added timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, and_, update as sqlalchemy_update
from sqlalchemy.orm import joinedload, selectinload # Added selectinload

from app.crud.base import CRUDBase
from app.db.models.content_item import ContentItem, ContentItemTypeEnum
from app.db.models.content_version import ContentVersion
from app.schemas.content_item import ContentItemCreate, ContentItemUpdateMeta, ContentItemWithCurrentVersion, ContentItemDuplicatePayload
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
        If the item is a workflow, its definition will be parsed.
        """
        statement = select(self.model).where(self.model.item_id == item_id).options(
            joinedload(self.model.current_version).joinedload(ContentVersion.saving_team),
            joinedload(self.model.owner_team)
        )
        result = await db.execute(statement)
        item = result.scalar_one_or_none()

        if item:
            # For ContentItemWithCurrentVersion schema, we need to ensure _parsed_workflow_definition_internal is set
            # This is typically done when the schema is instantiated from the ORM object.
            # The schema's model_validator will attempt to use this if present.
            # To ensure it's available for the schema, we can add it as a temporary attribute to the ORM model instance
            # *before* it's passed to Pydantic for validation, or ensure the schema validator has access.
            # The Pydantic schema now handles this via its model_validator if the CRUD passes the raw ORM model.
            # Let's ensure the schema has what it needs or handle it during schema creation in the endpoint.
            # For directness here, if we return the ORM model, the schema will handle it.
            # If we were converting to a dict first, we'd add it to the dict.
            # The new schema ContentItemWithCurrentVersion has a model_validator that will call the parser.
            # To make it available more explicitly for the schema's computed_fields,
            # we can pre-populate it on the schema object if needed, or rely on the schema validator.
            # The schema expects _parsed_workflow_definition_internal for its computed fields.
            # Let's ensure this is available if the schema is directly instantiated from the model.
            # Pydantic's from_orm/model_validate will try to access attributes.
            # We need to ensure the parsing happens transparently for the schema.
            # The schema validator will handle this now by looking at current_version.markdown_content.
            pass # Parsing is handled by the schema's validator now.

        return item

    async def get_by_id_for_team_or_admin_usage(
        self, db: AsyncSession, *, item_id: PyUUID, requesting_team_id: Optional[PyUUID], is_admin_request: bool
    ) -> Optional[ContentItem]:
        item = await self.get_by_id(db, item_id=item_id) # This already calls the modified get_by_id

        if not item:
            return None

        if is_admin_request:
            return item

        if item.item_type == ContentItemTypeEnum.DOCUMENT:
            if item.team_id == requesting_team_id or item.is_globally_visible:
                return item
        elif item.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW]:
            if item.team_id == settings.ADMIN_SYSTEM_TEAM_ID and item.is_globally_visible:
                return item
            elif item.team_id == requesting_team_id and item.is_globally_visible:
                log.warning(f"Team {requesting_team_id} accessing a Template/Workflow they own (item_id: {item.item_id}). This is legacy or for 'use if visible'.")
                return item

        log.warning(f"Team {requesting_team_id} access denied or item {item_id} not found under allowed conditions for usage.")
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
            db_obj_data["is_globally_visible"] = True
        elif not is_admin_actor and actor_team_id and obj_in.item_type == ContentItemTypeEnum.DOCUMENT:
            item_owner_team_id = actor_team_id
            db_obj_data["team_id"] = item_owner_team_id
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
            else:
                template_id_for_doc_creation = obj_in.template_id # type: ignore

            if "template_id" in db_obj_data:
                del db_obj_data["template_id"]

        # For new Templates/Workflows by Admins, markdown content might be part of obj_in if frontend allows direct content input on create.
        # If so, it needs to be passed to create_new_version.
        # Currently, obj_in (ContentItemCreate) doesn't have markdown_content.
        # It's assumed content for T/W is added via a subsequent version save.

        db_item = self.model(**db_obj_data)
        db.add(db_item)
        await db.flush() # Get item_id

        initial_content_for_version = ""
        if obj_in.item_type == ContentItemTypeEnum.DOCUMENT and template_id_for_doc_creation and actor_team_id:
            template_item_stmt = select(ContentItem).where(
                ContentItem.item_id == template_id_for_doc_creation,
                ContentItem.item_type == ContentItemTypeEnum.TEMPLATE,
                ContentItem.team_id == settings.ADMIN_SYSTEM_TEAM_ID,
                ContentItem.is_globally_visible == True
            ).options(joinedload(ContentItem.current_version))
            template_result = await db.execute(template_item_stmt)
            template_item_db = template_result.scalar_one_or_none()

            if template_item_db and template_item_db.current_version:
                initial_content_for_version = template_item_db.current_version.markdown_content
            elif not template_item_db:
                await db.rollback()
                raise ValueError(f"Selected Template (ID: {template_id_for_doc_creation}) not found or not an accessible Admin System Template.")

        # Create initial version for Documents, or if content is provided for new T/W (future enhancement)
        if obj_in.item_type == ContentItemTypeEnum.DOCUMENT or \
           (obj_in.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW] and initial_content_for_version):
            # The second part of OR is for future if T/W can be created with initial content directly

            from app.crud.crud_content_version import content_version as crud_version_module
            version_payload = ContentVersionCreate(markdown_content=initial_content_for_version)

            if db_item.item_id is None: # Should not happen after flush
                 await db.rollback()
                 raise RuntimeError("Failed to get item_id for new item after flush.")

            # Determine who saves the first version
            version_saver_id = actor_team_id if obj_in.item_type == ContentItemTypeEnum.DOCUMENT else settings.ADMIN_SYSTEM_TEAM_ID

            await crud_version_module.create_new_version(
                db,
                item_id=db_item.item_id,
                version_in=version_payload,
                saved_by_team_id=version_saver_id,
                is_initial_version=True
            )

        await db.commit()
        await db.refresh(db_item, attribute_names=['current_version', 'owner_team'])
        return db_item

    async def get_items_for_team_or_admin(
        self,
        db: AsyncSession,
        *,
        requesting_actor_team_id: Optional[PyUUID],
        is_admin_actor: bool,
        item_type_filter: Optional[ContentItemTypeEnum] = None,
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

        if is_admin_actor:
            if item_type_filter: # Admin listing specific type
                conditions.append(self.model.item_type == item_type_filter)
                if item_type_filter in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW]:
                    conditions.append(self.model.team_id == settings.ADMIN_SYSTEM_TEAM_ID)
                # For Documents, admin sees all teams' documents if item_type_filter is DOCUMENT
            # If no item_type_filter, admin sees all items (typically UI filters this)
        else: # Team user request
            if not requesting_actor_team_id: return [], 0

            if list_for_team_usage and item_type_filter in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW]:
                conditions.append(self.model.item_type == item_type_filter)
                conditions.append(self.model.team_id == settings.ADMIN_SYSTEM_TEAM_ID)
                conditions.append(self.model.is_globally_visible == True)
            elif item_type_filter == ContentItemTypeEnum.DOCUMENT:
                conditions.append(self.model.item_type == ContentItemTypeEnum.DOCUMENT)
                conditions.append(or_(
                    self.model.team_id == requesting_actor_team_id,
                    and_(self.model.is_globally_visible == True, self.model.team_id != settings.ADMIN_SYSTEM_TEAM_ID)
                ))
            elif not item_type_filter: # Team's general list (their Documents)
                conditions.append(self.model.item_type == ContentItemTypeEnum.DOCUMENT)
                conditions.append(self.model.team_id == requesting_actor_team_id)
            else: # Team trying to list non-document types for management (should yield nothing for T/W)
                return [], 0

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        total_count = (await db.execute(count_query)).scalar_one()

        query = query.order_by(sort_attr.asc() if sort_order.lower() == "asc" else sort_attr.desc())
        query = query.offset(skip).limit(limit).options(
            joinedload(self.model.current_version).joinedload(ContentVersion.saving_team),
            joinedload(self.model.owner_team)
        )
        items_orm = (await db.execute(query)).scalars().unique().all()

        # The Pydantic schema ContentItemWithCurrentVersion will handle parsing
        # when instantiated with from_attributes=True or model_validate.
        # So, we return the ORM items directly.
        return items_orm, total_count


    async def check_name_uniqueness(
        self, db: AsyncSession, *, name: str, item_type: ContentItemTypeEnum,
        team_id: PyUUID,
        exclude_item_id: Optional[PyUUID] = None
    ) -> bool:
        query = select(func.count(self.model.item_id)).where(
            func.lower(self.model.name) == func.lower(name),
            self.model.item_type == item_type,
            self.model.team_id == team_id
        )
        if exclude_item_id:
            query = query.where(self.model.item_id != exclude_item_id)

        count = (await db.execute(query)).scalar_one()
        return count == 0

    async def update_item_meta_for_owner_or_admin(
        self, db: AsyncSession, *, item_id: PyUUID, item_in: ContentItemUpdateMeta,
        requesting_actor_team_id: Optional[PyUUID],
        is_admin_actor: bool
    ) -> Optional[ContentItem]:
        # Fetch with relationships needed for schema validation if it re-parses workflow
        db_obj = await self.get_by_id(db, item_id=item_id)
        if not db_obj:
            return None

        can_update = False
        effective_item_owner_id = db_obj.team_id

        if is_admin_actor:
            if db_obj.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW] and db_obj.team_id == settings.ADMIN_SYSTEM_TEAM_ID:
                can_update = True
            elif db_obj.item_type == ContentItemTypeEnum.DOCUMENT:
                can_update = True
        elif requesting_actor_team_id and db_obj.team_id == requesting_actor_team_id:
            if db_obj.item_type == ContentItemTypeEnum.DOCUMENT:
                can_update = True

        if not can_update:
            log.warning(f"Update meta failed: User (Admin: {is_admin_actor}, TeamID: {requesting_actor_team_id}) cannot update item {item_id} of type {db_obj.item_type} owned by {db_obj.team_id}")
            return None

        update_data = item_in.model_dump(exclude_unset=True)

        if "name" in update_data and update_data["name"].lower() != db_obj.name.lower():
            if not await self.check_name_uniqueness(
                db, name=update_data["name"], item_type=db_obj.item_type,
                team_id=effective_item_owner_id,
                exclude_item_id=db_obj.item_id
            ):
                raise ValueError(f"{db_obj.item_type.value} with name '{update_data['name']}' already exists for the owner.")
            setattr(db_obj, "name", update_data["name"])

        if "is_globally_visible" in update_data:
            can_change_visibility = False
            if is_admin_actor and db_obj.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW] and db_obj.team_id == settings.ADMIN_SYSTEM_TEAM_ID:
                can_change_visibility = True
            elif not is_admin_actor and requesting_actor_team_id and db_obj.team_id == requesting_actor_team_id and db_obj.item_type == ContentItemTypeEnum.DOCUMENT:
                can_change_visibility = True

            if can_change_visibility:
                setattr(db_obj, "is_globally_visible", update_data["is_globally_visible"])
            elif "is_globally_visible" in update_data: # Tried to update but not allowed
                log.warning(f"User (Admin: {is_admin_actor}, TeamID: {requesting_actor_team_id}) not allowed to change visibility for item {item_id}")

        db_obj.updated_at = datetime.now(timezone.utc)
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
            if (item_to_delete.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW] and item_to_delete.team_id == settings.ADMIN_SYSTEM_TEAM_ID) \
               or item_to_delete.item_type == ContentItemTypeEnum.DOCUMENT:
                can_delete = True
        elif requesting_actor_team_id and item_to_delete.team_id == requesting_actor_team_id:
             if item_to_delete.item_type == ContentItemTypeEnum.DOCUMENT:
                can_delete = True

        if not can_delete:
            log.warning(f"Delete item failed: User (Admin: {is_admin_actor}, TeamID: {requesting_actor_team_id}) cannot delete item {item_id} of type {item_to_delete.item_type} owned by {item_to_delete.team_id}")
            return None

        await db.delete(item_to_delete)
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

        # Determine owner of the new duplicated item
        new_owner_id: PyUUID
        if is_admin_actor:
            if source_item.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW]:
                new_owner_id = settings.ADMIN_SYSTEM_TEAM_ID # Admin duplicates their own T/W
            elif source_item.item_type == ContentItemTypeEnum.DOCUMENT:
                # Admin duplicating a doc. If target_owner_team_id is provided, use it. Else, duplicate for source item's team.
                new_owner_id = payload.target_owner_team_id or source_item.team_id
            else: # Should not happen
                raise ValueError("Invalid item type for admin duplication.")
        else: # Team actor
            if source_item.item_type == ContentItemTypeEnum.DOCUMENT and source_item.team_id == requesting_actor_team_id:
                new_owner_id = requesting_actor_team_id # Team duplicates their own document
            elif source_item.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW] and \
                 source_item.team_id == settings.ADMIN_SYSTEM_TEAM_ID and source_item.is_globally_visible:
                # Team duplicating an Admin System T/W into a new Document for themselves
                if source_item.item_type == ContentItemTypeEnum.WORKFLOW:
                     raise ValueError("Teams cannot directly duplicate Workflows into new Workflows. They can execute them to produce Documents.")
                # For TEMPLATE, it becomes a new DOCUMENT for the team
                new_owner_id = requesting_actor_team_id # type: ignore
            else:
                raise ValueError("Not authorized to duplicate this item or invalid duplication scenario.")

        # Check name uniqueness for the new owner
        if not await self.check_name_uniqueness(db, name=payload.new_name, item_type=source_item.item_type, team_id=new_owner_id):
            raise ValueError(f"{source_item.item_type.value} with name '{payload.new_name}' already exists for the target owner.")

        # Create new ContentItem (metadata)
        duplicated_item_data = {
            "name": payload.new_name,
            "item_type": source_item.item_type,
            "team_id": new_owner_id,
            "is_globally_visible": source_item.is_globally_visible if new_owner_id == source_item.team_id else False, # New docs are private by default
        }
        # If team duplicates an Admin Template, the new item is a DOCUMENT
        if not is_admin_actor and source_item.item_type == ContentItemTypeEnum.TEMPLATE:
            duplicated_item_data["item_type"] = ContentItemTypeEnum.DOCUMENT
            duplicated_item_data["is_globally_visible"] = False # New doc is private


        new_db_item = ContentItem(**duplicated_item_data)
        db.add(new_db_item)
        await db.flush() # Get new_db_item.item_id

        # Determine which version's content to copy
        content_to_copy = ""
        version_to_copy_from: Optional[ContentVersion] = None

        if payload.source_version_id: # User specified a version
            version_to_copy_from = await crud_content_version.content_version.get_by_id(db, version_id=payload.source_version_id)
            if not version_to_copy_from or version_to_copy_from.item_id != source_item_id:
                raise ValueError("Specified source version not found or does not belong to the source item.")
        elif source_item.current_version: # Default to current version
            version_to_copy_from = source_item.current_version

        if version_to_copy_from:
            content_to_copy = version_to_copy_from.markdown_content
        elif source_item.item_type == ContentItemTypeEnum.DOCUMENT: # Document must have content
             raise ValueError("Source document has no content to duplicate.")


        # Create the first version for the duplicated item
        if new_db_item.item_id is None: # Should not happen after flush
            await db.rollback()
            raise RuntimeError("Failed to get item_id for duplicated item after flush.")

        version_payload = ContentVersionCreate(markdown_content=content_to_copy)
        # The saver of the first version of the duplicate is the actor performing the duplication
        version_saver_id = requesting_actor_team_id if not is_admin_actor else settings.ADMIN_SYSTEM_TEAM_ID
        if not is_admin_actor and source_item.item_type == ContentItemTypeEnum.TEMPLATE: # Team duplicating template
            version_saver_id = requesting_actor_team_id # type: ignore


        await crud_content_version.content_version.create_new_version(
            db, item_id=new_db_item.item_id, version_in=version_payload,
            saved_by_team_id=version_saver_id, # type: ignore
            is_initial_version=True
        )

        await db.commit()
        # Refresh to get all relationships, including current_version for schema
        await db.refresh(new_db_item, attribute_names=['current_version', 'owner_team'])
        if new_db_item.current_version:
            await db.refresh(new_db_item.current_version, attribute_names=['saving_team'])

        return new_db_item


content_item = CRUDContentItem(ContentItem)
