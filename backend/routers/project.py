from fastapi import APIRouter
from models.project import ResearchProject, ProjectsListResponse
from services.projects_service import ProjectService

router = APIRouter()
project_service = ProjectService()


@router.get("/test")
def sample():
    return {"message": "hello"}
