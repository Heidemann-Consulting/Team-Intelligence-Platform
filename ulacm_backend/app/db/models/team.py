# File: ulacm_backend/app/db/models/team.py
# Purpose: SQLAlchemy ORM model for the TEAMS table.

import uuid
from sqlalchemy import Column, String, Boolean, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Team(Base):
    """
    Represents a team account in the database.
    Corresponds to the TEAMS table in SRS 7.3.1.
    """
    __tablename__ = "teams" # Explicitly defining, though Base would derive it

    team_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    team_name = Column(String(100), nullable=False, unique=True, index=True) # FR-ADM-003
    username = Column(String(50), nullable=False, unique=True, index=True) # FR-ADM-003
    hashed_password = Column(String(255), nullable=False) # FR-AUTH-002
    is_active = Column(Boolean, nullable=False, default=True, server_default=text("TRUE")) # FR-ADM-006
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))

    # Relationships
    # A team owns many content items
    owned_content_items = relationship("ContentItem", back_populates="owner_team", cascade="all, delete-orphan")
    # A team saves many content versions
    saved_versions = relationship("ContentVersion", back_populates="saving_team")

    def __repr__(self):
        return f"<Team(team_id='{self.team_id}', team_name='{self.team_name}', username='{self.username}')>"
