# File: ulacm_backend/app/schemas/team.py
# Purpose: Pydantic schemas for Team data.

from pydantic import BaseModel, UUID4, constr, Field, EmailStr # Using EmailStr for username if it were email
from typing import Optional, List
import datetime

# Shared properties
class TeamBase(BaseModel):
    """
    Base schema for team properties.
    """
    team_name: constr(min_length=1, max_length=100) # FR-ADM-003
    username: constr(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$") # FR-ADM-003, Alphanumeric and underscores

# Properties to receive via API on creation
class TeamCreate(TeamBase):
    """
    Schema for creating a new team. Includes password.
    """
    password: constr(min_length=8) # FR-ADM-003

# Properties to receive via API on update
class TeamUpdate(BaseModel):
    """
    Schema for updating an existing team. All fields are optional.
    Username is not updatable as per SRS 8.3.4.
    """
    team_name: Optional[constr(min_length=1, max_length=100)] = None
    password: Optional[constr(min_length=8)] = None
    is_active: Optional[bool] = None


# Properties stored in DB
class TeamInDBBase(TeamBase):
    """
    Schema for properties of a team as stored in the database (excluding hashed_password).
    """
    team_id: UUID4
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {
        "from_attributes": True # Formerly orm_mode = True
    }

# Additional properties stored in DB but not returned by default
class TeamInDB(TeamInDBBase):
    """
    Schema for properties of a team including the hashed password (for internal use).
    """
    hashed_password: str

# Properties to return to client
class Team(TeamInDBBase):
    """
    Schema for representing a team in API responses (excluding sensitive data like password).
    """
    pass # Inherits all from TeamInDBBase

class TeamListResponse(BaseModel):
    """
    Schema for the response when listing multiple teams.
    """
    total_count: int
    offset: int
    limit: int
    teams: List[Team]
