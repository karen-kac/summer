from utils.mock_themes import MOCK_DEFAULT_THEMES


class MockThemeRepository:
    def __init__(self):
        pass

    def get_default_themes(self):
        return MOCK_DEFAULT_THEMES.copy()

#a
