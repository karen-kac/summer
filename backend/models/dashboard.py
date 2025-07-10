from pydantic import BaseModel, Field
from typing import List
from models.theme import UserProfile


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
    active_projects: List[str] = Field(..., alias="activeProjects")
    past_projects: List[str] = Field(..., alias="pastProjects")
    user_stats: UserStats = Field(..., alias="userStats")
    recent_achievements: List[str] = Field(..., alias="recentAchievements")
    todays_tasks: List[TaskItem] = Field(..., alias="todaysTasks")

    model_config = {
        "populate_by_name": True,
    }
