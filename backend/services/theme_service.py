from models.theme import UserProfile, ResearchTheme, ThemeListResponse
from repositories.mock_theme_repository import MockThemeRepository


class ThemeService:
    def __init__(self, repository=None):
        self.repository = repository if repository else MockThemeRepository()

    async def generate_themes(self, profile: UserProfile) -> ThemeListResponse:
        themes_data = await self.repository.get_default_themes()
        themes = [ResearchTheme(**data) for data in themes_data]
        return ThemeListResponse(themes=themes)
