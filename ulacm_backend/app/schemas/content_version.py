# File: ulacm_backend/app/schemas/content_version.py
# Purpose: Pydantic schemas for ContentVersion data.

from pydantic import BaseModel, UUID4, constr, Field
from typing import Optional, List
import datetime

# Base properties for a content version
class ContentVersionBase(BaseModel):
    """
    Base schema for content version properties.
    """
    markdown_content: str # FR-VER-003

# Properties to receive on creation (saving a new version)
class ContentVersionCreate(ContentVersionBase):
    """
    Schema for creating a new content version (i.e., saving content).
    """
    pass # markdown_content is the only direct input from user for content itself

# Properties shared by models stored in DB
class ContentVersionInDBBase(ContentVersionBase):
    """
    Schema for properties of a content version as stored in the database.
    """
    version_id: UUID4
    item_id: UUID4
    version_number: int # FR-VER-003
    saved_by_team_id: UUID4 # FR-VER-003
    created_at: datetime.datetime # FR-VER-003 (Save Time)

    model_config = {
        "from_attributes": True
    }

# Schema for returning a content version (full details)
class ContentVersion(ContentVersionInDBBase):
    """
    Schema for representing a content version in API responses.
    """
    pass

# Schema for version details when fetching a specific version (SRS 8.5.1)
class ContentVersionDetails(BaseModel):
    """
    Schema for detailed information of a specific version.
    """
    version_id: UUID4
    item_id: UUID4
    markdown_content: str
    version_number: int
    saved_by_team_id: UUID4
    created_at: datetime.datetime # Version save timestamp

    model_config = {
        "from_attributes": True
    }


# Schema for version metadata in a list (history) (SRS 8.5.2)
class VersionMeta(BaseModel):
    """
    Schema for metadata of a version in a list (version history).
    """
    version_id: UUID4
    version_number: int
    saved_by_team_id: UUID4
    created_at: datetime.datetime # Version save timestamp

    model_config = {
        "from_attributes": True
    }

class ContentVersionListResponse(BaseModel):
    """
    Schema for the response when listing multiple versions of an item.
    """
    total_count: int # Renamed from total_versions
    item_id: UUID4
    offset: int
    limit: int
    versions: List[VersionMeta]


class SaveVersionResponse(BaseModel):
    """
    Schema for the response after successfully saving a new version. SRS 8.5.3.
    """
    item_id: UUID4
    new_version: ContentVersionDetails # Details of the newly created version
    item_updated_at: datetime.datetime # Timestamp of when the parent ContentItem was updated
