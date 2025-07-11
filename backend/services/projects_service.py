from models.project import ResearchProject, ProjectsListResponse
from repositories.mock_projects_repository import MockProjectRepository


class ProjectService:
    def __init__(self, repository=None):
        self.repository = repository if repository else MockProjectRepository()
