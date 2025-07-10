from fastapi import APIRouter
from models.achivement import Achivement, AchivementsListResponse
from models.project import ResearchProject, ProjectsListResponse
from services.user_service import UserService

router = APIRouter()
user_service = UserService()


@router.get("/achivement", response_model=AchivementsListResponse)
async def get_achivement():
    achivements = await user_service.get_achivement()
    return achivements


@router.get("/project/active", response_model=ProjectsListResponse)
async def get_active_projects():
    projects = await user_service.get_active_projects()
    return projects


@router.get("/project/past", response_model=ProjectsListResponse)
async def get_past_projects():
    projects = await user_service.get_past_projects()
    return projects
