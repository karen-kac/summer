from models.achievement import Achievement, AchievementsListResponse
from models.project import ResearchProject, ProjectsListResponse
from repositories.mock_user_repository import MockUserRepository


class UserService:
    def __init__(self, repository=None):
        self.repository = repository if repository else MockUserRepository()

    async def get_achievement(self) -> AchievementsListResponse:
        achievements_data = await self.repository.get_achievement()
        achievements = [Achievement(**data) for data in achievements_data]
        return AchievementsListResponse(achievements=achievements)

    async def get_active_projects(self) -> ProjectsListResponse:
        projects_data = await self.repository.get_active_projects()
        projects = [ResearchProject(**data) for data in projects_data]
        return ProjectsListResponse(projects=projects)

    async def get_past_projects(self) -> ProjectsListResponse:
        projects_data = await self.repository.get_past_projects()
        projects = [ResearchProject(**data) for data in projects_data]
        return ProjectsListResponse(projects=projects)
