# File: ulacm_backend/app/services/__init__.py
# Purpose: Makes service modules available for easier import.

from .ollama_service import OllamaService, OllamaServiceError
from .workflow_parser import (
    WorkflowDefinitionParser,
    validate_workflow_definition_string,
    WorkflowParsingError,
)
from .embedding_service import generate_embedding
from .retrieval_service import retrieve_top_k_chunks, get_relevant_snippets
from . import (
    workflow_service,
)  # Imports the module itself to access its functions/classes
