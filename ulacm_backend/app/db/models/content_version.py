# File: ulacm_backend/app/db/models/content_version.py
# Purpose: SQLAlchemy ORM model for the CONTENT_VERSIONS table.

import uuid
from sqlalchemy import Column, String, Boolean, TIMESTAMP, text, ForeignKey, Integer, TEXT
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
# from .content_item import ContentItem # <-- REMOVE this import
from .team import Team # Keep Team import if needed elsewhere

from app.db.base_class import Base

class ContentVersion(Base):
    """
    Represents a specific version of a content item in the database.
    Corresponds to the CONTENT_VERSIONS table in SRS 7.3.3.
    """
    __tablename__ = "content_versions"

    version_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    item_id = Column(UUID(as_uuid=True), ForeignKey("content_items.item_id", ondelete="CASCADE"), nullable=False, index=True)
    markdown_content = Column(TEXT, nullable=False)
    version_number = Column(Integer, nullable=False, index=True)

    # FR-VER-003: Team ID that saved this version.
    # ON DELETE SET NULL: If the saving team is deleted, the version history remains, attributed to a "null" team.
    # This might be preferable to deleting version history if a team that only contributed a version is deleted.
    # The owning team of the item is distinct.
    saved_by_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.team_id", ondelete="SET NULL"), nullable=False, index=True)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    # Relationships
    # A version belongs to one content item
    item = relationship(
        "ContentItem", # Use string "ContentItem"
        back_populates="versions",
        foreign_keys=[item_id]
    )
    # A version was saved by one team
    saving_team = relationship(
        "Team", # Use string "Team"
        back_populates="saved_versions",
        foreign_keys=[saved_by_team_id]
    )
    # Constraints
    # Ensures version_number is unique per item_id
    __table_args__ = (
        UniqueConstraint('item_id', 'version_number', name='uq_item_version_number'),
    )

    def __repr__(self):
        return f"<ContentVersion(version_id='{self.version_id}', item_id='{self.item_id}', version_number={self.version_number})>"
