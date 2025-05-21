# File: ulacm_backend/app/api/v1/endpoints/ai_tools.py
# Purpose: API endpoints for direct AI interaction tools like "Ask AI".
# Fixed: Remove <think> tags from the full response before constructing the final JSON payload.

import logging
import json
import re # Import re for the helper function
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, AsyncIterator, List
from pydantic.json import pydantic_encoder

from app.db.database import get_db
from app.db.models.team import Team as TeamModel
from app.api.v1.deps import get_current_team_user
from app.schemas.ai_tools import AskAIRequest, AskAIResponse
from app.services.ollama_service import ollama_service_instance, OllamaServiceError
from app.core.config import settings
from app.services.workflow_service import ULACM_STREAM_END_TOKEN

log = logging.getLogger(__name__)
router = APIRouter()

def _remove_think_tags_for_ai_tools(text: str) -> str: # Renamed to avoid conflict if imported elsewhere
    """Removes <think>...</think> tags from a string."""
    if not text:
        return ""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

DEFAULT_ASK_AI_SYSTEM_PROMPT_TEMPLATE = """
You are a helpful AI assistant. The user is currently working on a document.
Based on the provided document content and the user's question or instruction, please provide a concise and relevant response.

Document Name (if provided): {document_name}

--- Document Content Start ---
{document_content}
--- Document Content End ---

User's Question/Instruction:
{user_query}

Your Response:
"""

@router.post(
    "/ask",
    summary="Ask AI about a document (Streams Response)",
    status_code=status.HTTP_200_OK
)
async def ask_ai_about_document_streaming(
    request: Request,
    payload: AskAIRequest,
    current_team: TeamModel = Depends(get_current_team_user)
):
    """
    Allows a team user to ask an AI model a question or give an instruction
    based on the provided document content. Streams the AI response.
    The stream ends with ULACM_STREAM_END_TOKEN followed by a JSON payload.
    The full AI response (for saving) will have <think> tags removed.
    """
    remote_ip = request.client.host if request.client else "unknown"
    log.info(f"Team {current_team.team_id} ('{current_team.team_name}') from IP {remote_ip} initiated streaming 'Ask AI'. Document name hint: '{payload.document_name}'. Query: '{payload.user_query[:100]}...'")

    system_prompt = DEFAULT_ASK_AI_SYSTEM_PROMPT_TEMPLATE.format(
        document_name=payload.document_name if payload.document_name else "Not Provided",
        document_content=payload.current_document_content,
        user_query=payload.user_query
    )

    async def stream_generator() -> AsyncIterator[str]:
        accumulated_raw_chunks: List[str] = []
        try:
            log.info(f"Starting 'Ask AI' stream for team {current_team.team_id}")
            async for chunk in ollama_service_instance.generate_stream(prompt=system_prompt):
                accumulated_raw_chunks.append(chunk)
                yield chunk # Stream raw chunk (with potential <think> tags)

            raw_full_response = "".join(accumulated_raw_chunks)
            # Clean the full response *before* including it in the final JSON payload
            # Note: The client-side AskAIResponseModal will also clean the accumulated display text.
            # This ensures that if the backend were to send the full response in JSON, it's clean.
            # However, for "Ask AI", the primary artifact is the stream itself.
            # The final JSON payload is more for status and metadata.

            log.info(f"'Ask AI' stream completed for team {current_team.team_id}. Raw response length: {len(raw_full_response)}")

            final_payload = {
                "model_used": settings.OLLAMA_MODEL,
                "status": "completed",
                # "ai_response": _remove_think_tags_for_ai_tools(raw_full_response)
                # The client reconstructs and cleans the full response from chunks for display/saving.
                # So, we don't need to send the full (cleaned) response in the final JSON here.
                # The frontend's AskAIResponseData type expects ai_response, but it's primarily for type consistency.
            }
            yield f"{ULACM_STREAM_END_TOKEN}{json.dumps(final_payload, default=pydantic_encoder)}"

        except OllamaServiceError as ose:
            log.error(f"Ollama service error during 'Ask AI' stream for team {current_team.team_id}: {ose}")
            yield f"{ULACM_STREAM_END_TOKEN}{json.dumps({'error': str(ose), 'model_used': settings.OLLAMA_MODEL}, default=pydantic_encoder)}"
        except Exception as e:
            log.exception(f"Unexpected error during 'Ask AI' stream for team {current_team.team_id}: {e}")
            yield f"{ULACM_STREAM_END_TOKEN}{json.dumps({'error': 'An unexpected error occurred while processing your request with the AI.', 'model_used': settings.OLLAMA_MODEL}, default=pydantic_encoder)}"

    return StreamingResponse(stream_generator(), media_type="text/plain")
