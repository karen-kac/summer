from fastapi import APIRouter
from models.achievement import Achievement, AchievementsListResponse
from models.project import ResearchProject, ProjectsListResponse
from services.user_service import UserService

router = APIRouter()
user_service = UserService()


@router.get("/achievement", response_model=AchievementsListResponse)
async def get_achievement():
    achievements = await user_service.get_achievement()
    return achievements


@router.get("/project/active", response_model=ProjectsListResponse)
async def get_active_projects():
    projects = await user_service.get_active_projects()
    return projects


@router.get("/project/past", response_model=ProjectsListResponse)
async def get_past_projects():
    projects = await user_service.get_past_projects()
    return projects
