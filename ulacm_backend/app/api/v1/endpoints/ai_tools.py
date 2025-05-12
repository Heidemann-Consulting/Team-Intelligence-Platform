# File: ulacm_backend/app/api/v1/endpoints/ai_tools.py
# Purpose: API endpoints for direct AI interaction tools like "Ask AI".

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

from app.db.database import get_db
from app.db.models.team import Team as TeamModel
from app.api.v1.deps import get_current_team_user # Assuming "Ask AI" is a team feature
from app.schemas.ai_tools import AskAIRequest, AskAIResponse
from app.services.ollama_service import ollama_service_instance, OllamaServiceError
from app.core.config import settings

log = logging.getLogger(__name__)
router = APIRouter()

# You can refine this system prompt
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
    response_model=AskAIResponse,
    summary="Ask AI about a document",
    status_code=status.HTTP_200_OK
)
async def ask_ai_about_document(
    request: Request,
    payload: AskAIRequest,
    db: AsyncSession = Depends(get_db), # Included if any DB interaction were needed, e.g., logging user
    current_team: TeamModel = Depends(get_current_team_user) # Ensure only authenticated team users can use
):
    """
    Allows a team user to ask an AI model a question or give an instruction
    based on the provided document content.
    """
    remote_ip = request.client.host if request.client else "unknown"
    log.info(f"Team {current_team.team_id} ('{current_team.team_name}') from IP {remote_ip} initiated 'Ask AI'. Document name hint: '{payload.document_name}'. Query: '{payload.user_query[:100]}...'")

    system_prompt = DEFAULT_ASK_AI_SYSTEM_PROMPT_TEMPLATE.format(
        document_name=payload.document_name if payload.document_name else "Not Provided",
        document_content=payload.current_document_content,
        user_query=payload.user_query
    )

    try:
        # Use the globally configured model and temperature from settings
        ai_raw_response = await ollama_service_instance.generate(prompt=system_prompt)

        log.info(f"'Ask AI' request for team {current_team.team_id} completed successfully. Response length: {len(ai_raw_response)}")

        return AskAIResponse(
            ai_response=ai_raw_response,
            model_used=settings.OLLAMA_MODEL # Add the model used to the response
        )

    except OllamaServiceError as ose:
        log.error(f"Ollama service error during 'Ask AI' for team {current_team.team_id}: {ose}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {str(ose)}"
        )
    except Exception as e:
        log.exception(f"Unexpected error during 'Ask AI' for team {current_team.team_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request with the AI."
        )
