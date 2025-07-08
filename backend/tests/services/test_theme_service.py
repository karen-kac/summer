import pytest
from unittest.mock import AsyncMock
from services.theme_service import ThemeService
from models.theme import UserProfile, ResearchTheme, ThemeListResponse
from models.enums import Grade, Interest, Personality, Strength, Duration
from pydantic import ValidationError


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
async def test_generate_themes_success(sample_user_profile):
    mock_repository = AsyncMock()
    mock_repository.generate_themes.return_value = [
        {
            "title": "テーマ1",
            "description": "説明1",
            "materials": ["材料1"],
            "steps": ["手順1"],
            "estimatedDays": 5,
            "difficulty": "easy",
        },
        {
            "title": "テーマ2",
            "description": "説明2",
            "materials": ["材料2"],
            "steps": ["手順2"],
            "estimatedDays": 10,
            "difficulty": "medium",
        },
    ]

    service = ThemeService(repository=mock_repository)
    response = await service.generate_themes(sample_user_profile)

    mock_repository.generate_themes.assert_called_once_with(sample_user_profile)
    assert isinstance(response, ThemeListResponse)
    assert len(response.themes) == 2
    assert isinstance(response.themes[0], ResearchTheme)
    assert response.themes[0].title == "テーマ1"
    assert response.themes[1].title == "テーマ2"


@pytest.mark.asyncio
async def test_generate_themes_empty_list(sample_user_profile):
    mock_repository = AsyncMock()
    mock_repository.generate_themes.return_value = []

    service = ThemeService(repository=mock_repository)
    response = await service.generate_themes(sample_user_profile)

    mock_repository.generate_themes.assert_called_once_with(sample_user_profile)
    assert isinstance(response, ThemeListResponse)
    assert len(response.themes) == 0


@pytest.mark.asyncio
async def test_generate_themes_invalid_data(sample_user_profile):
    mock_repository = AsyncMock()
    mock_repository.generate_themes.return_value = [
        {
            "title": "テーマ1",
            "description": "説明1",
            "materials": ["材料1"],
            "steps": ["手順1"],
            "difficulty": "easy",  # estimatedDaysが不足
        }
    ]

    service = ThemeService(repository=mock_repository)
    with pytest.raises(ValidationError):
        await service.generate_themes(sample_user_profile)
