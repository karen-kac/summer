from utils.mock_themes import MOCK_DEFAULT_THEMES


class MockThemeRepository:
    def __init__(self):
        pass

    async def generate_themes(self, profile) -> list:
        result = MOCK_DEFAULT_THEMES.copy()
        return result
