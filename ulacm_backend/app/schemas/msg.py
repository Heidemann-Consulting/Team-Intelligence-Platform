# File: ulacm_backend/app/schemas/msg.py
# Purpose: Pydantic schema for simple message responses.

from pydantic import BaseModel

class Msg(BaseModel):
    """
    Schema for returning simple messages in API responses.
    """
    message: str
