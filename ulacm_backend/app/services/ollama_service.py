# File: ulacm_backend/app/services/ollama_service.py
# Purpose: Service for interacting with the local Ollama server.
# Updated: Uses global OLLAMA_MODEL and OLLAMA_TEMPERATURE from settings.
# Updated: Strips <think>...</think> tags and leading/trailing newlines from the non-streaming response.
# Added generate_stream method for streaming responses.

import httpx
import logging
import json
import re
from typing import Optional, Dict, Any, AsyncIterator

from app.core.config import settings

log = logging.getLogger(__name__)

class OllamaServiceError(Exception):
    """Custom exception for errors encountered while interacting with the Ollama service."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code

class OllamaService:
    """Service class for making requests to the Ollama API."""
    def __init__(self, base_url: str = str(settings.OLLAMA_API_URL)):
        """Initializes the OllamaService."""
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=300.0) # Default timeout 300 seconds (5 minutes)

        log.info(f"OllamaService initialized with base URL: {self.base_url}")
        log.info(f"OllamaService default model: {settings.OLLAMA_MODEL}")
        log.info(f"OllamaService default temperature: {settings.OLLAMA_TEMPERATURE}")

    async def close(self):
        """Closes the HTTP client."""
        await self.client.aclose()
        log.info("OllamaService HTTP client closed.")

    async def generate(
        self,
        prompt: str,
        stream: bool = False, # Kept stream parameter for explicitness, though this method won't stream
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Sends a generation request to the Ollama /api/generate endpoint.
        Uses OLLAMA_MODEL and OLLAMA_TEMPERATURE from application settings.
        Strips <think>...</think> tags and surrounding newlines from the output.
        This method does NOT stream the response. Use generate_stream for streaming.
        """
        api_endpoint = "/api/generate"

        current_model = settings.OLLAMA_MODEL
        current_temperature = settings.OLLAMA_TEMPERATURE

        payload: Dict[str, Any] = {
            "model": current_model,
            "prompt": prompt,
            "stream": False, # Explicitly set to False for this non-streaming method

        }

        payload_options = options.copy() if options else {}
        if current_temperature is not None:
             payload_options["temperature"] = current_temperature

        if payload_options:
            payload["options"] = payload_options

        log.info(f"Sending request to Ollama {api_endpoint} with model '{current_model}'. Stream: False.")
        log.debug(f"Ollama request effective options: {payload.get('options', {})}")
        prompt_snippet = (prompt[:100] + '...') if len(prompt) > 100 else prompt
        log.debug(f"Ollama request prompt snippet: {prompt_snippet}")

        response_http = None
        try:
            response_http = await self.client.post(api_endpoint, json=payload)
            log.debug(f"Ollama API response status: {response_http.status_code}")
            response_http.raise_for_status()
            response_data = response_http.json()

            if "response" not in response_data:
                log.error(f"Ollama response missing 'response' field. Status: {response_http.status_code}. Data: {response_data}")
                raise OllamaServiceError(
                    "Ollama response did not contain 'response' field.",
                    status_code=response_http.status_code
                )

            generated_text = response_data["response"]
            processed_text = re.sub(r"<think>.*?</think>", "", generated_text, flags=re.DOTALL)
            processed_text = processed_text.strip('\n\r')

            text_snippet = (processed_text[:100] + '...') if len(processed_text) > 100 else processed_text
            log.info(f"Successfully received and processed response from Ollama model '{current_model}'.")
            log.debug(f"Processed Ollama response text snippet: {text_snippet}")
            return processed_text

        except httpx.TimeoutException as e:
            log.error(f"Request to Ollama timed out ({self.client.timeout}s): {e}")
            raise OllamaServiceError(f"Request to Ollama timed out after {self.client.timeout} seconds.")
        except httpx.ConnectError as e:
            log.error(f"Could not connect to Ollama server at {self.base_url}{api_endpoint}: {e}")
            raise OllamaServiceError(f"Could not connect to Ollama server at {self.base_url}{api_endpoint}.")
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            try:
                error_json = e.response.json()
                if "error" in error_json:
                    error_detail = error_json["error"]
            except Exception:
                pass
            log.error(f"Ollama API request failed: Status={e.response.status_code}, Detail='{error_detail}'")
            raise OllamaServiceError(
                 f"Ollama API request failed with status {e.response.status_code}: {error_detail}",
                status_code=e.response.status_code
            )
        except json.JSONDecodeError as e:
            status_code_for_error = response_http.status_code if response_http else None
            log.error(f"Failed to decode JSON response from Ollama. Status: {status_code_for_error}. Response text: {response_http.text[:500] if response_http else 'N/A'}...")
            raise OllamaServiceError(f"Failed to decode JSON response from Ollama: {e}. Response text: '{response_http.text[:100] if response_http else 'N/A'}...'", status_code=status_code_for_error)
        except Exception as e:
            log.exception(f"An unexpected error occurred while communicating with Ollama: {e}")
            status_code = getattr(e, 'response', None) and getattr(e.response, 'status_code', None)
            raise OllamaServiceError(f"An unexpected error occurred while communicating with Ollama: {str(e)}", status_code=status_code)

    async def generate_stream(
        self,
        prompt: str,
        options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """
        Sends a generation request to the Ollama /api/generate endpoint and streams the response.
        Uses OLLAMA_MODEL and OLLAMA_TEMPERATURE from application settings.
        Yields raw text chunks from the LLM. <think> tags are NOT removed during streaming.
        """
        api_endpoint = "/api/generate"
        current_model = settings.OLLAMA_MODEL
        current_temperature = settings.OLLAMA_TEMPERATURE

        payload: Dict[str, Any] = {
            "model": current_model,
            "prompt": prompt,
            "stream": True, # Explicitly set to True for streaming
        }

        payload_options = options.copy() if options else {}
        if current_temperature is not None:
             payload_options["temperature"] = current_temperature

        if payload_options:
            payload["options"] = payload_options

        log.info(f"Sending streaming request to Ollama {api_endpoint} with model '{current_model}'.")
        log.debug(f"Ollama streaming request effective options: {payload.get('options', {})}")
        prompt_snippet = (prompt[:100] + '...') if len(prompt) > 100 else prompt
        log.debug(f"Ollama streaming request prompt snippet: {prompt_snippet}")

        try:
            async with self.client.stream("POST", api_endpoint, json=payload) as response:
                log.debug(f"Ollama API stream response status: {response.status_code}")
                response.raise_for_status() # Check for HTTP errors before starting to stream

                async for line in response.aiter_lines():
                    if line:
                        try:
                            chunk_data = json.loads(line)
                            if "response" in chunk_data and chunk_data.get("done") is not True:
                                yield chunk_data["response"]
                            elif chunk_data.get("done") is True:
                                log.info(f"Ollama stream finished for model '{current_model}'.")
                                # Optionally yield a final status or metrics if needed, though not raw text.
                                # For now, just stop yielding.
                                break
                        except json.JSONDecodeError:
                            log.warning(f"Could not decode JSON line from Ollama stream: {line[:100]}...")
                            # Decide if to yield raw line or ignore

        except httpx.TimeoutException as e:
            log.error(f"Request to Ollama (stream) timed out ({self.client.timeout}s): {e}")
            raise OllamaServiceError(f"Request to Ollama (stream) timed out after {self.client.timeout} seconds.")
        except httpx.ConnectError as e:
            log.error(f"Could not connect to Ollama server (stream) at {self.base_url}{api_endpoint}: {e}")
            raise OllamaServiceError(f"Could not connect to Ollama server (stream) at {self.base_url}{api_endpoint}.")
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            try:
                error_json = e.response.json()
                if "error" in error_json: error_detail = error_json["error"]
            except Exception: pass
            log.error(f"Ollama API stream request failed: Status={e.response.status_code}, Detail='{error_detail}'")
            raise OllamaServiceError(
                 f"Ollama API stream request failed with status {e.response.status_code}: {error_detail}",
                status_code=e.response.status_code
            )
        except Exception as e:
            log.exception(f"An unexpected error occurred while streaming from Ollama: {e}")
            status_code = getattr(e, 'response', None) and getattr(e.response, 'status_code', None)
            raise OllamaServiceError(f"An unexpected error occurred while streaming from Ollama: {str(e)}", status_code=status_code)


ollama_service_instance = OllamaService()
