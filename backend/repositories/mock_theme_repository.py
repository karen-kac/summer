from utils.mock_themes import MOCK_DEFAULT_THEMES


class MockThemeRepository:
    def __init__(self):
        pass

    async def get_default_themes(self):
        result = MOCK_DEFAULT_THEMES.copy()
        return result
