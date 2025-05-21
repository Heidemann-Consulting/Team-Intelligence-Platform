# File: ulacm_backend/app/schemas/ai_tools.py
# Purpose: Pydantic schemas for direct AI interaction tools.

from pydantic import BaseModel, Field
from typing import Optional

class AskAIRequest(BaseModel):
    current_document_content: str = Field(..., description="The full content of the document being worked on.")
    user_query: str = Field(..., description="The user's question or instruction for the AI regarding the document.")
    document_name: Optional[str] = Field(None, description="Optional name of the document for context.")

class AskAIResponse(BaseModel):
    ai_response: str = Field(..., description="The raw text response from the AI model.")
    model_used: Optional[str] = Field(None, description="The AI model that processed the request.")
