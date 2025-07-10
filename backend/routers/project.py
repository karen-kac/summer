from fastapi import APIRouter
from models.project import ResearchProject, ProjectsListResponse
from services.projects_service import ProjectService

router = APIRouter()
project_service = ProjectService()


@router.get("/get_active", response_model=ProjectsListResponse)
async def get_active_projects():
    projects = await project_service.get_active_projects()
    return projects


@router.get("/get_past", response_model=ProjectsListResponse)
async def get_past_projects():
    projects = await project_service.get_past_projects()
    return projects
