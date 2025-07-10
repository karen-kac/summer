from utils.mock_achivements import MOCK_RECENT_ACHIVEMENTS


class MockUserRepository:
    def __init__(self):
        pass

    async def get_achivement(self):
        result = MOCK_RECENT_ACHIVEMENTS.copy()
        return result
