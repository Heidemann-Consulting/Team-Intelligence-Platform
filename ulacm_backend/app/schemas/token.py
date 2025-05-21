# File: ulacm_backend/app/schemas/token.py
# Purpose: Pydantic schemas for JWT tokens.

from pydantic import BaseModel, UUID4
from typing import Optional, Union

class Token(BaseModel):
    """
    Schema for the access token response.
    """
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    """
    Schema for the data encoded within the JWT.
    'sub' typically holds the user identifier (team_id or admin identifier).
    """
    sub: Optional[Union[UUID4, str]] = None  # Allow sub to be UUID or string
    team_id: Optional[UUID4] = None # Explicitly for team users
    is_admin: Optional[bool] = False # Flag for admin users
