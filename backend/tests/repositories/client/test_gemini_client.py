import pytest
import os
import json
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from repositories.client.gemini_client import GeminiClient


@pytest.fixture(autouse=True)
def cleanup_env_vars():
    # 各テストの前に環境変数をクリア
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
    yield
    # 各テストの後に環境変数をクリア
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]


def test_gemini_client_init_with_api_key():
    os.environ["GEMINI_API_KEY"] = "test_api_key"
    client = GeminiClient()
    assert client.model is not None


def test_gemini_client_init_without_api_key():
    with pytest.raises(RuntimeError, match="GEMINI_API_KEYが設定されていません。"):
        GeminiClient()


@pytest.mark.asyncio
async def test_generate_content_success():
    os.environ["GEMINI_API_KEY"] = "test_api_key"
    client = GeminiClient()

    mock_response = AsyncMock()
    mock_response.text = "Mocked response text"

    with patch(
        "google.generativeai.GenerativeModel.generate_content_async",
        return_value=mock_response,
    ) as mock_generate_content:
        result = await client.generate_content("test prompt")
        mock_generate_content.assert_called_once_with("test prompt")
        assert result == "Mocked response text"


@pytest.mark.asyncio
async def test_generate_content_exception():
    os.environ["GEMINI_API_KEY"] = "test_api_key"
    client = GeminiClient()

    with patch(
        "google.generativeai.GenerativeModel.generate_content_async",
        side_effect=Exception("API Error"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await client.generate_content("test prompt")
        assert exc_info.value.status_code == 500
        assert (
            "LLM APIとの通信中にエラーが発生しました: API Error"
            in exc_info.value.detail
        )


@pytest.mark.asyncio
async def test_post_prompt_valid_json():
    os.environ["GEMINI_API_KEY"] = "test_api_key"
    client = GeminiClient()

    mock_generate_content_response = AsyncMock()
    mock_generate_content_response.text = '{"key": "value"}'

    with patch(
        "repositories.client.gemini_client.GeminiClient.generate_content",
        return_value=mock_generate_content_response.text,
    ) as mock_generate_content:
        result = await client.post_prompt("test prompt")
        mock_generate_content.assert_called_once_with("test prompt")
        assert result == {"key": "value"}


@pytest.mark.asyncio
async def test_post_prompt_invalid_json():
    os.environ["GEMINI_API_KEY"] = "test_api_key"
    client = GeminiClient()

    mock_generate_content_response = AsyncMock()
    mock_generate_content_response.text = "invalid json"

    with patch(
        "repositories.client.gemini_client.GeminiClient.generate_content",
        return_value=mock_generate_content_response.text,
    ):
        with pytest.raises(json.JSONDecodeError):
            await client.post_prompt("test prompt")
