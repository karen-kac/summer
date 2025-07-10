from models.theme import UserProfile, ResearchTheme, ThemeListResponse


class ThemeService:
    def __init__(self, repository=None):
        if repository is None:
            raise ValueError("ThemeService requires a repository instance")
        self.repository = repository

    async def generate_themes(self, profile: UserProfile) -> ThemeListResponse:
        themes_data = await self.repository.generate_themes(profile)
        themes = [ResearchTheme(**data) for data in themes_data]
        return ThemeListResponse(themes=themes)
