# File: ulacm_backend/app/db/models/content_version.py
# Purpose: SQLAlchemy ORM model for the CONTENT_VERSIONS table.

import uuid
from sqlalchemy import Column, String, Boolean, TIMESTAMP, text, ForeignKey, Integer, TEXT
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR # Import TSVECTOR
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

from .team import Team

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

    # This column is populated by a database trigger with the tsvector of markdown_content.
    content_tsv = Column(TSVECTOR, nullable=True) # Added content_tsv column

    saved_by_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.team_id", ondelete="SET NULL"), nullable=False, index=True)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    # Relationships
    item = relationship(
        "ContentItem",
        back_populates="versions",
        foreign_keys=[item_id]
    )

    saving_team = relationship(
        "Team",
        back_populates="saved_versions",
        foreign_keys=[saved_by_team_id]
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint('item_id', 'version_number', name='uq_item_version_number'),
    )

    def __repr__(self):
        return f"<ContentVersion(version_id='{self.version_id}', item_id='{self.item_id}', version_number={self.version_number})>"
