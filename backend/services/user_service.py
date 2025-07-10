from models.achivement import Achivement, AchivementsListResponse
from models.project import ResearchProject, ProjectsListResponse
from repositories.mock_user_repository import MockUserRepository


class UserService:
    def __init__(self, repository=None):
        self.repository = repository if repository else MockUserRepository()

    async def get_achivement(self) -> AchivementsListResponse:
        achivements_data = await self.repository.get_achivement()
        achivements = [Achivement(**data) for data in achivements_data]
        return AchivementsListResponse(achivements=achivements)

    async def get_active_projects(self) -> ProjectsListResponse:
        projects_data = await self.repository.get_active_projects()
        projects = [ResearchProject(**data) for data in projects_data]
        return ProjectsListResponse(projects=projects)

    async def get_past_projects(self) -> ProjectsListResponse:
        projects_data = await self.repository.get_past_projects()
        projects = [ResearchProject(**data) for data in projects_data]
        return ProjectsListResponse(projects=projects)
