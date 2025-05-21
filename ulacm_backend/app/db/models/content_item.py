# File: ulacm_backend/app/db/models/content_item.py
# Purpose: SQLAlchemy ORM model for the CONTENT_ITEMS table.
# Changes: team_id remains NOT NULL. For Admin T/W, it points to ADMIN_SYSTEM_TEAM_ID.

import uuid
from sqlalchemy import Column, String, Boolean, TIMESTAMP, text, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

from app.db.base_class import Base
import enum

class ContentItemTypeEnum(str, enum.Enum):
    DOCUMENT = "DOCUMENT"
    TEMPLATE = "TEMPLATE"
    WORKFLOW = "WORKFLOW"

class ContentItem(Base):
    """
    Represents a content item (Document, Template, or Workflow) in the database.
    Corresponds to the CONTENT_ITEMS table in SRS 7.3.2.
    """
    __tablename__ = "content_items"

    item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    # team_id is NOT NULL. For Admin-created Templates/Workflows, it points to the ADMIN_SYSTEM_TEAM_ID.
    # For Documents, it points to the creating team.
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.team_id", ondelete="CASCADE"), nullable=False, index=True)
    item_type = Column(SQLAlchemyEnum(ContentItemTypeEnum, name="content_item_type_enum", create_type=True), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    # is_globally_visible will be True for Admin-owned Templates/Workflows usable by teams.
    is_globally_visible = Column(Boolean, nullable=False, default=False, server_default=text("FALSE"))

    current_version_id = Column(UUID(as_uuid=True), ForeignKey("content_versions.version_id", ondelete="SET NULL", use_alter=True, name="fk_content_items_current_version_id"), nullable=True, index=True)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    # Relationships
    owner_team = relationship("Team", back_populates="owned_content_items") # type: ignore
    versions = relationship(
        "ContentVersion", # type: ignore
        back_populates="item",
        cascade="all, delete-orphan",
        order_by="desc(ContentVersion.version_number)", # type: ignore
        foreign_keys="ContentVersion.item_id" # type: ignore
    )
    current_version = relationship(
        "ContentVersion", # type: ignore
        foreign_keys=[current_version_id],
        post_update=True
    )

    __table_args__ = (
        UniqueConstraint('team_id', 'name', 'item_type', name='uq_team_item_name_type'),
    )

    def __repr__(self):
        return f"<ContentItem(item_id='{self.item_id}', name='{self.name}', type='{self.item_type}', team_id='{self.team_id}')>"
