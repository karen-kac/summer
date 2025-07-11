from pydantic import BaseModel, Field
from typing import List
from models.theme import UserProfile
from models.project import ProjectsListResponse
from models.achievement import AchievementsListResponse


class UserStats(BaseModel):
    total_points: int = Field(..., alias="totalPoints")
    level: int
    completed_projects: int = Field(..., alias="completedProjects")
    current_streak: int
    total_records: int = Field(..., alias="totalRecords")
    total_photos: int = Field(..., alias="totalPhotos")
    total_experiments: int = Field(..., alias="totalExperiments")

    model_config = {
        "populate_by_name": True,
    }


class TaskItem(BaseModel):
    icon: str
    task: str
    urgent: bool


class DashboardData(BaseModel):
    user: UserProfile
    active_projects: ProjectsListResponse = Field(..., alias="activeProjects")
    past_projects: ProjectsListResponse = Field(..., alias="pastProjects")
    user_stats: UserStats = Field(..., alias="userStats")
    recent_achievements: AchievementsListResponse = Field(..., alias="recentAchievements")
    todays_tasks: List[TaskItem] = Field(..., alias="todaysTasks")

    model_config = {
        "populate_by_name": True,
    }


class DashboardResponse(BaseModel):
    active_projects: ProjectsListResponse = Field(..., alias="activeProjects")
    past_projects: ProjectsListResponse = Field(..., alias="pastProjects")
    recent_achievements: AchievementsListResponse = Field(..., alias="recentAchievements")

    model_config = {
        "populate_by_name": True,
    }
