from fastapi import APIRouter
from routers.user import get_achievement, get_active_projects, get_past_projects
from models.dashboard import DashboardResponse

router = APIRouter()


@router.get("/get", response_model=DashboardResponse)
async def get_dashboard_data():
    active_projects = await get_active_projects()
    past_projects = await get_past_projects()
    recent_achievements = await get_achievement()
    data = {
        "active_projects": active_projects,
        "past_projects": past_projects,
        "recent_achievements": recent_achievements,
    }
    dashboard_data = DashboardResponse(**data)
    return dashboard_data
