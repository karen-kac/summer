import pytest
import os
import json
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from repositories.client.bedrock_client import BedrockClient


@pytest.fixture(autouse=True)
def cleanup_env_vars():
    # 各テストの前に環境変数をクリア
    for key in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION"]:
        if key in os.environ:
            del os.environ[key]
    yield
    # 各テストの後に環境変数をクリア
    for key in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION"]:
        if key in os.environ:
            del os.environ[key]


def test_bedrock_client_init_with_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "test_access_key"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test_secret_key"
    os.environ["BEDROCK_REGION"] = "us-east-1"
    
    with patch('boto3.client') as mock_boto3:
        client = BedrockClient()
        assert client.client is not None
        mock_boto3.assert_called_once()


def test_bedrock_client_init_without_credentials():
    with pytest.raises(RuntimeError, match="AWS認証情報が設定されていません。"):
        BedrockClient()


@pytest.mark.asyncio
async def test_generate_content_success():
    os.environ["AWS_ACCESS_KEY_ID"] = "test_access_key"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test_secret_key"
    os.environ["BEDROCK_REGION"] = "us-east-1"
    
    mock_response = {
        "body": MagicMock()
    }
    mock_response["body"].read.return_value = json.dumps({
        "completion": "Mocked response text"
    })

    with patch('boto3.client') as mock_boto3:
        mock_client = MagicMock()
        mock_client.invoke_model.return_value = mock_response
        mock_boto3.return_value = mock_client
        
        client = BedrockClient()
        result = await client.generate_content("test prompt")
        assert result == "Mocked response text"


@pytest.mark.asyncio
async def test_generate_content_exception():
    os.environ["AWS_ACCESS_KEY_ID"] = "test_access_key"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test_secret_key"
    os.environ["BEDROCK_REGION"] = "us-east-1"
    
    with patch('boto3.client') as mock_boto3:
        mock_client = MagicMock()
        mock_client.invoke_model.side_effect = Exception("API Error")
        mock_boto3.return_value = mock_client
        
        client = BedrockClient()
        with pytest.raises(HTTPException) as exc_info:
            await client.generate_content("test prompt")
        assert exc_info.value.status_code == 500
        assert "Bedrock APIとの通信中にエラーが発生しました: API Error" in exc_info.value.detail


@pytest.mark.asyncio
async def test_post_prompt_valid_json():
    os.environ["AWS_ACCESS_KEY_ID"] = "test_access_key"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test_secret_key"
    os.environ["BEDROCK_REGION"] = "us-east-1"
    
    with patch('boto3.client') as mock_boto3:
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        
        client = BedrockClient()
        
        # generate_contentメソッドをモック
        mock_response_text = '```json\n{"key": "value"}\n```'
        with patch.object(client, 'generate_content', return_value=mock_response_text) as mock_generate_content:
            result = await client.post_prompt("test prompt")
            mock_generate_content.assert_called_once_with("test prompt")
            assert result == {"key": "value"}


@pytest.mark.asyncio
async def test_post_prompt_invalid_json_format():
    os.environ["AWS_ACCESS_KEY_ID"] = "test_access_key"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test_secret_key"
    os.environ["BEDROCK_REGION"] = "us-east-1"
    
    with patch('boto3.client') as mock_boto3:
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        
        client = BedrockClient()
        
        # generate_contentメソッドをモック（無効なJSON）
        with patch.object(client, 'generate_content', return_value="invalid json"):
            with pytest.raises(HTTPException) as exc_info:
                await client.post_prompt("test prompt")
            assert exc_info.value.status_code == 500
            assert "AI応答の形式が不正です" in exc_info.value.detail