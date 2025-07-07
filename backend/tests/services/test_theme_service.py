import pytest
from services.theme_service import ThemeService
from models.theme import UserProfile, ThemeListResponse, ResearchTheme
from models.enums import Grade, Interest, Personality, Strength, Duration


@pytest.mark.asyncio
async def test_generate_themes():
    # Create a sample user profile
    profile = UserProfile(
        grade=Grade.elementary1,
        interests=[Interest.science, Interest.nature],
        personality=[Personality.curious, Personality.patient],
        strengths=[Strength.observation, Strength.writing],
        duration=Duration.one_week,
    )

    # Instantiate the service
    service = ThemeService()

    # Call the method
    response = await service.generate_themes(profile)

    # Assert the response
    assert isinstance(response, ThemeListResponse)
    assert isinstance(response.themes, list)
    for theme in response.themes:
        assert isinstance(theme, ResearchTheme)
