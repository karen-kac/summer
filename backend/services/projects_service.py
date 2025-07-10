from models.project import ResearchProject, ProjectsListResponse
from repositories.mock_projects_repository import MockProjectRepository


class ProjectService:
    def __init__(self, repository=None):
        self.repository = repository if repository else MockProjectRepository()

    async def get_active_projects(self) -> ProjectsListResponse:
        projects_data = await self.repository.get_active_projects()
        projects = [ResearchProject(**data) for data in projects_data]
        return ProjectsListResponse(projects=projects)

    async def get_past_projects(self) -> ProjectsListResponse:
        projects_data = await self.repository.get_past_projects()
        projects = [ResearchProject(**data) for data in projects_data]
        return ProjectsListResponse(projects=projects)
