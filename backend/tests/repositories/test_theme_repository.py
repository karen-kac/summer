import pytest
from unittest.mock import AsyncMock, MagicMock
from repositories.theme_repository import ThemeRepository
from models.theme import UserProfile
from models.enums import Grade, Interest, Personality, Strength, Duration


@pytest.fixture
def sample_user_profile():
    return UserProfile(
        grade=Grade.junior1,
        interests=[Interest.science],
        personality=[Personality.curious],
        strengths=[Strength.observation],
        duration=Duration.one_month,
    )


@pytest.mark.asyncio
async def test_generate_themes_calls_dependencies_correctly(sample_user_profile):
    mock_prompt_builder = MagicMock()
    mock_bedrock_client = AsyncMock()

    # build_suggest_themes_promptの戻り値を設定
    mock_prompt_builder.build_suggest_themes_prompt.return_value = (
        "mocked prompt string"
    )

    # post_promptの戻り値を設定
    mock_bedrock_client.post_prompt.return_value = [{"title": "Mock Theme"}]

    repository = ThemeRepository(
        prompt_builder=mock_prompt_builder, client=mock_bedrock_client
    )

    result = await repository.generate_themes(sample_user_profile)

    # PromptBuilder.build_suggest_themes_promptが正しい引数で呼び出されたことを確認
    mock_prompt_builder.build_suggest_themes_prompt.assert_called_once_with(
        sample_user_profile
    )

    # BedrockClient.post_promptが正しい引数で呼び出されたことを確認
    mock_bedrock_client.post_prompt.assert_called_once_with("mocked prompt string")

    # post_promptの戻り値がそのまま返されたことを確認
    assert result == [{"title": "Mock Theme"}]
