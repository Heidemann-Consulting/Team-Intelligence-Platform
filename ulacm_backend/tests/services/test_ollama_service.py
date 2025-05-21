# File: ulacm_backend/tests/services/test_ollama_service.py
# Purpose: Unit tests for the OllamaService class.
# No changes needed in this file based on the latest error log,
# but including full file for consistency.

import pytest
import httpx
import json
from unittest.mock import patch, AsyncMock, MagicMock

# Import the service and exception to test
from app.services.ollama_service import OllamaService, OllamaServiceError
from app.core.config import settings # To get default URL or mock it


MOCK_BASE_URL = "http://test-ollama:11434"
MOCK_API_ENDPOINT = "/api/generate"

@pytest.fixture
def ollama_service() -> OllamaService:
    """Fixture to create an instance of OllamaService for testing."""
    # Patch httpx.AsyncClient before initializing the service instance
    with patch('httpx.AsyncClient', new_callable=MagicMock) as MockAsyncClient:
        service = OllamaService(base_url=MOCK_BASE_URL)
        service.client = MockAsyncClient() # Assign the mock client instance
        yield service
        # No explicit close needed for mock usually, but good practice if testing close itself

@pytest.fixture
def mock_httpx_response():
    """Factory fixture to create mock httpx.Response objects."""
    def _create_mock_response(status_code=200, json_data=None, text_data=None, raise_for_status_effect=None):
        response = AsyncMock(spec=httpx.Response)
        response.status_code = status_code
        response.headers = httpx.Headers({'content-type': 'application/json'})

        if json_data is not None:
            response.json = MagicMock(return_value=json_data)
            response.text = json.dumps(json_data)
        elif text_data is not None:
            response.text = text_data
            response.json = MagicMock(side_effect=json.JSONDecodeError("Mock decode error", "", 0))
        else:
            response.text = ""
            response.json = MagicMock(return_value={}) # Default empty dict

        # Configure raise_for_status mock
        if raise_for_status_effect:
            response.raise_for_status = MagicMock(side_effect=raise_for_status_effect)
        else:
            response.raise_for_status = MagicMock()

        return response
    return _create_mock_response

# --- Test Cases ---

def test_ollama_service_init():
    """Test service initialization."""
    test_url = "http://custom-ollama:1234/"
    with patch('httpx.AsyncClient') as MockAsyncClient:
        service = OllamaService(base_url=test_url)
        assert service.base_url == test_url.rstrip('/')
        MockAsyncClient.assert_called_once_with(base_url=test_url.rstrip('/'), timeout=120.0)

@pytest.mark.asyncio
async def test_generate_success(ollama_service, mock_httpx_response):
    """Test successful call to Ollama generate endpoint."""
    model_name = "test-model"
    prompt_text = "Generate something creative."
    expected_response_text = "Here is something creative."
    mock_response_json = {"response": expected_response_text, "other_field": "value"}

    ollama_service.client.post = AsyncMock(return_value=mock_httpx_response(status_code=200, json_data=mock_response_json))

    result = await ollama_service.generate(model=model_name, prompt=prompt_text)

    assert result == expected_response_text
    ollama_service.client.post.assert_awaited_once_with(
        MOCK_API_ENDPOINT,
        json={
            "model": model_name,
            "prompt": prompt_text,
            "stream": False
        }
    )
    ollama_service.client.post.return_value.raise_for_status.assert_called_once()

@pytest.mark.asyncio
async def test_generate_with_options_and_temp(ollama_service, mock_httpx_response):
    """Test passing temperature and options to generate."""
    model_name = "test-options"
    prompt_text = "Test options."
    temp = 0.5
    options = {"top_k": 40, "top_p": 0.9}
    expected_response_text = "Options processed."
    mock_response_json = {"response": expected_response_text}

    ollama_service.client.post = AsyncMock(return_value=mock_httpx_response(status_code=200, json_data=mock_response_json))

    result = await ollama_service.generate(
        model=model_name,
        prompt=prompt_text,
        temperature=temp,
        options=options
    )

    assert result == expected_response_text
    ollama_service.client.post.assert_awaited_once_with(
        MOCK_API_ENDPOINT,
        json={
            "model": model_name,
            "prompt": prompt_text,
            "stream": False,
            "options": {
                "temperature": temp,
                "top_k": options["top_k"],
                "top_p": options["top_p"],
            }
        }
    )

@pytest.mark.asyncio
async def test_generate_http_error(ollama_service, mock_httpx_response):
    """Test handling of HTTP 4xx/5xx errors from Ollama."""
    status_code = 404
    error_detail = "Model not found"
    mock_response_json = {"error": error_detail}

    mock_error = httpx.HTTPStatusError(
        message=f"{status_code} Client Error: Not Found for url...",
        request=MagicMock(spec=httpx.Request),
        response=mock_httpx_response(status_code=status_code, json_data=mock_response_json)
    )
    mock_error.response.raise_for_status = MagicMock(side_effect=mock_error)

    ollama_service.client.post = AsyncMock(return_value=mock_error.response)

    with pytest.raises(OllamaServiceError) as excinfo:
        await ollama_service.generate(model="unknown-model", prompt="test")

    assert excinfo.value.status_code == status_code
    assert error_detail in str(excinfo.value)
    assert f"{status_code}" in str(excinfo.value)

@pytest.mark.asyncio
async def test_generate_connection_error(ollama_service):
    """Test handling of connection errors."""
    ollama_service.client.post = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))

    with pytest.raises(OllamaServiceError) as excinfo:
        await ollama_service.generate(model="any-model", prompt="test")

    assert "Could not connect" in str(excinfo.value)
    assert MOCK_BASE_URL in str(excinfo.value)
    assert excinfo.value.status_code is None

@pytest.mark.asyncio
async def test_generate_timeout_error(ollama_service):
    """Test handling of timeout errors."""
    ollama_service.client.post = AsyncMock(side_effect=httpx.TimeoutException("Read timeout"))

    with pytest.raises(OllamaServiceError) as excinfo:
        await ollama_service.generate(model="any-model", prompt="test")

    assert "timed out" in str(excinfo.value)
    assert str(ollama_service.client.timeout) in str(excinfo.value)
    assert excinfo.value.status_code is None

@pytest.mark.asyncio
async def test_generate_missing_response_field(ollama_service, mock_httpx_response):
    """Test handling response JSON that lacks the 'response' field."""
    mock_response_json = {"some_other_data": "value"}
    ollama_service.client.post = AsyncMock(return_value=mock_httpx_response(status_code=200, json_data=mock_response_json))

    with pytest.raises(OllamaServiceError) as excinfo:
        await ollama_service.generate(model="any-model", prompt="test")

    assert "ollama response did not contain 'response' field" in str(excinfo.value).lower()
    # This assertion should now pass because the status_code is passed to the exception
    assert excinfo.value.status_code == 200

@pytest.mark.asyncio
async def test_generate_invalid_json_response_text(ollama_service, mock_httpx_response):
    """Test handling response that is not valid JSON."""
    invalid_json_text = "<html><body>Error</body></html>"
    mock_response = mock_httpx_response(status_code=200, text_data=invalid_json_text)
    # Ensure .json() raises the correct error
    mock_response.json = MagicMock(side_effect=json.JSONDecodeError("Mock decode error", "", 0))
    ollama_service.client.post = AsyncMock(return_value=mock_response)

    with pytest.raises(OllamaServiceError) as excinfo:
        await ollama_service.generate(model="any-model", prompt="test")

    # Check if the JSON decode error message is part of the raised exception
    assert "failed to decode json response from ollama" in str(excinfo.value).lower()
    assert "mock decode error" in str(excinfo.value).lower()
    # The status code should be included now
    assert excinfo.value.status_code == 200

@pytest.mark.asyncio
async def test_close(ollama_service):
    """Test the close method calls client.aclose."""
    ollama_service.client.aclose = AsyncMock() # Ensure the mock client has aclose
    await ollama_service.close()
    ollama_service.client.aclose.assert_awaited_once()
