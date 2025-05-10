# File: ulacm_backend/app/crud/crud_content_item.py
# Purpose: CRUD operations for ContentItem model.
# Changes for Option 3 (Admin System Team):
# - Templates/Workflows created by Admins are owned by ADMIN_SYSTEM_TEAM_ID.
# - These Admin-owned T/W are set to is_globally_visible = True.
# - Listing and access logic updated to reflect ADMIN_SYSTEM_TEAM_ID ownership for T/W.
# - Name uniqueness checks for Admin T/W are scoped to ADMIN_SYSTEM_TEAM_ID.

from typing import Any, Dict, Optional, Union, List, Tuple
from uuid import UUID as PyUUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, and_, update as sqlalchemy_update
from sqlalchemy.orm import joinedload

from app.crud.base import CRUDBase
from app.db.models.content_item import ContentItem, ContentItemTypeEnum
from app.db.models.content_version import ContentVersion
from app.schemas.content_item import ContentItemCreate, ContentItemUpdateMeta
from app.schemas.content_version import ContentVersionCreate
from app.core.config import settings # For ADMIN_SYSTEM_TEAM_ID
import logging

log = logging.getLogger(__name__)

class CRUDContentItem(CRUDBase[ContentItem, ContentItemCreate, ContentItemUpdateMeta]):
    """
    CRUD operations for ContentItem model.
    """

    async def get_by_id(self, db: AsyncSession, *, item_id: PyUUID) -> Optional[ContentItem]:
        """
        Get a content item by its ID, joining with current version, its saving team, and owner team.
        Access control should be handled by the calling service/endpoint.
        """
        statement = select(self.model).where(self.model.item_id == item_id).options(
            joinedload(self.model.current_version).joinedload(ContentVersion.saving_team), # type: ignore
            joinedload(self.model.owner_team) # type: ignore
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none() # type: ignore

    async def get_by_id_for_team_or_admin_usage(
        self, db: AsyncSession, *, item_id: PyUUID, requesting_team_id: Optional[PyUUID], is_admin_request: bool
    ) -> Optional[ContentItem]:
        """
        Get a content item by its ID for usage or admin view.
        - If admin, gets any item.
        - If team:
            - For DOCUMENT: gets if owned by team or globally visible.
            - For TEMPLATE/WORKFLOW (for usage): gets if owned by ADMIN_SYSTEM_TEAM_ID AND is_globally_visible.
        """
        item = await self.get_by_id(db, item_id=item_id)

        if not item:
            return None

        if is_admin_request:
            return item

        # Team user logic
        if item.item_type == ContentItemTypeEnum.DOCUMENT:
            if item.team_id == requesting_team_id or item.is_globally_visible:
                return item
        elif item.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW]:
            if item.team_id == settings.ADMIN_SYSTEM_TEAM_ID and item.is_globally_visible:
                return item
            # A team should not "own" a Template/Workflow directly anymore for editing.
            # If they did previously, this logic might allow usage but not editing.
            elif item.team_id == requesting_team_id and item.is_globally_visible:
                 log.warning(f"Team {requesting_team_id} accessing a Template/Workflow they own (item_id: {item_id}). This is legacy or for 'use if visible'.")
                 return item

        log.warning(f"Team {requesting_team_id} access denied or item {item_id} not found under allowed conditions for usage.")
        return None

    async def create_item_for_team_or_admin(
        self, db: AsyncSession, *, obj_in: ContentItemCreate,
        actor_team_id: Optional[PyUUID], # ID of the team performing action, or None if Admin acts as system
        is_admin_actor: bool
    ) -> ContentItem:
        db_obj_data = obj_in.model_dump(exclude_unset=True)
        item_owner_team_id: PyUUID

        if is_admin_actor and obj_in.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW]:
            item_owner_team_id = settings.ADMIN_SYSTEM_TEAM_ID
            db_obj_data["team_id"] = item_owner_team_id
            db_obj_data["is_globally_visible"] = True # Admin T/W are usable by all teams
        elif not is_admin_actor and actor_team_id and obj_in.item_type == ContentItemTypeEnum.DOCUMENT:
            item_owner_team_id = actor_team_id
            db_obj_data["team_id"] = item_owner_team_id
            db_obj_data.setdefault('is_globally_visible', False) # Docs are private by default
        else:
            raise ValueError("Invalid parameters for item creation: role, type, or team_id mismatch.")

        # Check uniqueness against the determined owner
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

            if "template_id" in db_obj_data: # Not a direct column
                del db_obj_data["template_id"]

        db_item = self.model(**db_obj_data)
        db.add(db_item)
        await db.flush()

        if obj_in.item_type == ContentItemTypeEnum.DOCUMENT and template_id_for_doc_creation and actor_team_id:
            template_item_stmt = select(ContentItem).where(
                ContentItem.item_id == template_id_for_doc_creation,
                ContentItem.item_type == ContentItemTypeEnum.TEMPLATE,
                ContentItem.team_id == settings.ADMIN_SYSTEM_TEAM_ID, # Must use Admin System Template
                ContentItem.is_globally_visible == True
            ).options(joinedload(ContentItem.current_version))
            template_result = await db.execute(template_item_stmt)
            template_item_db = template_result.scalar_one_or_none()

            initial_content = ""
            if template_item_db and template_item_db.current_version:
                initial_content = template_item_db.current_version.markdown_content
            elif not template_item_db:
                await db.rollback()
                raise ValueError(f"Selected Template (ID: {template_id_for_doc_creation}) not found or not an accessible Admin System Template.")

            from app.crud.crud_content_version import content_version as crud_version_module
            version_payload = ContentVersionCreate(markdown_content=initial_content)
            if db_item.item_id is None: await db.refresh(db_item, attribute_names=['item_id'])
            if db_item.item_id is None:
                 await db.rollback()
                 raise RuntimeError("Failed to get item_id for new Document after flush.")
            # The document's first version is saved by the team creating the document
            await crud_version_module.create_new_version(db, item_id=db_item.item_id, version_in=version_payload, saved_by_team_id=actor_team_id, is_initial_version=True)
        # For Admin-created T/W, initial version on first save by Admin (see versions endpoint)

        await db.commit()
        await db.refresh(db_item, attribute_names=['current_version', 'owner_team'])
        return db_item

    async def get_items_for_team_or_admin(
        self,
        db: AsyncSession,
        *,
        requesting_actor_team_id: Optional[PyUUID], # ID of the team making the request, can be ADMIN_SYSTEM_TEAM_ID if admin acts as system
        is_admin_actor: bool,
        item_type_filter: Optional[ContentItemTypeEnum] = None,
        list_for_team_usage: bool = False,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "updated_at",
        sort_order: str = "desc"
    ) -> Tuple[List[ContentItem], int]:
        allowed_sort_columns = ["name", "created_at", "updated_at", "item_type"]
        sort_column_name = sort_by if sort_by in allowed_sort_columns else "updated_at"
        sort_attr = getattr(self.model, sort_column_name)

        query = select(self.model)
        count_query = select(func.count(self.model.item_id)).select_from(self.model) # type: ignore
        conditions = []

        if is_admin_actor:
            if item_type_filter in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW]:
                conditions.append(self.model.item_type == item_type_filter)
                conditions.append(self.model.team_id == settings.ADMIN_SYSTEM_TEAM_ID) # Admin manages Admin System Team's T/W
            elif item_type_filter == ContentItemTypeEnum.DOCUMENT:
                 conditions.append(self.model.item_type == ContentItemTypeEnum.DOCUMENT) # Admin lists all team documents
            # If no item_type_filter, admin sees all items of all types (usually filtered by type)
        else: # Team user request
            if not requesting_actor_team_id: return [], 0 # Should not happen

            if list_for_team_usage and item_type_filter in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW]:
                # Teams listing Templates/Workflows to USE
                conditions.append(self.model.item_type == item_type_filter)
                conditions.append(self.model.team_id == settings.ADMIN_SYSTEM_TEAM_ID)
                conditions.append(self.model.is_globally_visible == True)
            elif item_type_filter == ContentItemTypeEnum.DOCUMENT:
                # Teams listing their own Documents or globally visible documents from other teams (excluding Admin System Team docs unless also global)
                conditions.append(self.model.item_type == ContentItemTypeEnum.DOCUMENT)
                conditions.append(or_(
                    self.model.team_id == requesting_actor_team_id,
                    and_(self.model.is_globally_visible == True, self.model.team_id != settings.ADMIN_SYSTEM_TEAM_ID)
                ))
            elif not item_type_filter: # Team's general list (their Documents)
                conditions.append(self.model.item_type == ContentItemTypeEnum.DOCUMENT)
                conditions.append(self.model.team_id == requesting_actor_team_id)
            else: # Team trying to list non-document types for management (should yield nothing)
                return [], 0

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        total_count = (await db.execute(count_query)).scalar_one() # type: ignore

        query = query.order_by(sort_attr.asc() if sort_order.lower() == "asc" else sort_attr.desc())
        query = query.offset(skip).limit(limit).options(
            joinedload(self.model.current_version).joinedload(ContentVersion.saving_team), # type: ignore
            joinedload(self.model.owner_team) # type: ignore
        )
        items = (await db.execute(query)).scalars().unique().all()
        return items, total_count # type: ignore

    async def check_name_uniqueness(
        self, db: AsyncSession, *, name: str, item_type: ContentItemTypeEnum,
        team_id: PyUUID, # For Admin T/W, this will be ADMIN_SYSTEM_TEAM_ID
        exclude_item_id: Optional[PyUUID] = None
    ) -> bool:
        # team_id is now mandatory and points to the owner (actual team or Admin System Team)
        query = select(func.count(self.model.item_id)).where( # type: ignore
            func.lower(self.model.name) == func.lower(name), # type: ignore
            self.model.item_type == item_type,
            self.model.team_id == team_id
        )
        if exclude_item_id:
            query = query.where(self.model.item_id != exclude_item_id) # type: ignore

        count_result = await db.execute(query)
        count = count_result.scalar_one() # type: ignore
        return count == 0

    async def update_item_meta_for_owner_or_admin(
        self, db: AsyncSession, *, item_id: PyUUID, item_in: ContentItemUpdateMeta,
        requesting_actor_team_id: Optional[PyUUID], # Actual team ID if team actor, None if Admin actor acting as system
        is_admin_actor: bool
    ) -> Optional[ContentItem]:
        db_obj = await self.get_by_id(db, item_id=item_id)
        if not db_obj:
            return None

        can_update = False
        # Determine effective owner_id of the item for uniqueness checks if name changes
        effective_item_owner_id = db_obj.team_id

        if is_admin_actor:
            # Admins can update metadata of Admin System Team's T/W
            if db_obj.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW] and db_obj.team_id == settings.ADMIN_SYSTEM_TEAM_ID:
                can_update = True
            # Admins can update metadata of any Document (owned by any team)
            elif db_obj.item_type == ContentItemTypeEnum.DOCUMENT:
                can_update = True
        elif requesting_actor_team_id and db_obj.team_id == requesting_actor_team_id:
            # Teams can only update metadata of their own Documents
            if db_obj.item_type == ContentItemTypeEnum.DOCUMENT:
                can_update = True

        if not can_update:
            log.warning(f"Update meta failed: User (Admin: {is_admin_actor}, TeamID: {requesting_actor_team_id}) cannot update item {item_id} of type {db_obj.item_type} owned by {db_obj.team_id}")
            return None

        update_data = item_in.model_dump(exclude_unset=True)

        if "name" in update_data and update_data["name"].lower() != db_obj.name.lower(): # type: ignore
            if not await self.check_name_uniqueness(
                db, name=update_data["name"], item_type=db_obj.item_type, # type: ignore
                team_id=effective_item_owner_id, # type: ignore
                exclude_item_id=db_obj.item_id
            ):
                raise ValueError(f"{db_obj.item_type.value} with name '{update_data['name']}' already exists for the owner.")

        # Admins can toggle is_globally_visible for their T/W
        if is_admin_actor and db_obj.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW] and db_obj.team_id == settings.ADMIN_SYSTEM_TEAM_ID:
            if "is_globally_visible" in update_data:
                 setattr(db_obj, "is_globally_visible", update_data["is_globally_visible"])
        # Teams can toggle for their own Documents
        elif not is_admin_actor and requesting_actor_team_id and db_obj.team_id == requesting_actor_team_id and db_obj.item_type == ContentItemTypeEnum.DOCUMENT:
            if "is_globally_visible" in update_data:
                 setattr(db_obj, "is_globally_visible", update_data["is_globally_visible"])
        elif "is_globally_visible" in update_data: # Prevent non-owners/non-admins from changing this for other cases
            del update_data["is_globally_visible"]


        if "name" in update_data:
            setattr(db_obj, "name", update_data["name"])
        db_obj.updated_at = datetime.now(timezone.utc) # type: ignore

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
            # Admins can delete their T/W (owned by ADMIN_SYSTEM_TEAM_ID) or any Document
            if (item_to_delete.item_type in [ContentItemTypeEnum.TEMPLATE, ContentItemTypeEnum.WORKFLOW] and item_to_delete.team_id == settings.ADMIN_SYSTEM_TEAM_ID) \
               or item_to_delete.item_type == ContentItemTypeEnum.DOCUMENT:
                can_delete = True
        elif requesting_actor_team_id and item_to_delete.team_id == requesting_actor_team_id:
            # Teams can only delete their own Documents
             if item_to_delete.item_type == ContentItemTypeEnum.DOCUMENT:
                can_delete = True

        if not can_delete:
            log.warning(f"Delete item failed: User (Admin: {is_admin_actor}, TeamID: {requesting_actor_team_id}) cannot delete item {item_id} of type {item_to_delete.item_type} owned by {item_to_delete.team_id}")
            return None

        await db.delete(item_to_delete)
        await db.commit()
        return item_to_delete

content_item = CRUDContentItem(ContentItem)
