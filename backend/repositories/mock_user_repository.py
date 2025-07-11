from utils.mock_achievements import MOCK_RECENT_ACHIEVEMENTS
from utils.mock_projects import MOCK_ACTIVE_PROJECTS, MOCK_PAST_PROJECTS


class MockUserRepository:
    def __init__(self):
        pass

    async def get_achievement(self):
        result = MOCK_RECENT_ACHIEVEMENTS.copy()
        return result

    async def get_active_projects(self):
        result = MOCK_ACTIVE_PROJECTS.copy()
        return result

    async def get_past_projects(self):
        result = MOCK_PAST_PROJECTS.copy()
        return result
