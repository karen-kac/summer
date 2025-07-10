from pydantic import BaseModel, Field
from typing import List, Optional, Literal, TYPE_CHECKING
from datetime import datetime
from models.theme import ResearchTheme
import uuid

if TYPE_CHECKING:
    from models.user import UserResponse


class ResearchProject(BaseModel):
    id: str = Field(default_factory=lambda: "project_" + str(uuid.uuid4()))
    user_id: str
    theme_id: str
    title: str
    description: str
    status: Literal['planning', 'in_progress', 'completed', 'paused'] = 'planning'
    start_date: datetime = Field(default_factory=datetime.now)
    target_end_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    custom_materials: List[str] = Field(default_factory=list)
    custom_steps: List[str] = Field(default_factory=list)
    progress_percentage: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CreateProjectRequest(BaseModel):
    """Request model for creating a new project"""
    theme_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    custom_materials: Optional[List[str]] = None
    custom_steps: Optional[List[str]] = None
    target_end_date: Optional[datetime] = None


class ProjectResponse(BaseModel):
    """Response model for project data"""
    id: str
    user_id: str
    theme_id: str
    title: str
    description: str
    status: str
    start_date: datetime
    target_end_date: Optional[datetime]
    actual_end_date: Optional[datetime]
    custom_materials: List[str]
    custom_steps: List[str]
    progress_percentage: int
    created_at: datetime
    updated_at: datetime


class ProjectWithTheme(ProjectResponse):
    """Project response with theme details"""
    theme: Optional[ResearchTheme] = None


class UserStats(BaseModel):
    """User statistics for dashboard"""
    total_points: int = 0
    level: int = 1
    completed_projects: int = 0
    current_streak: int = 0
    total_records: int = 0
    total_photos: int = 0
    total_experiments: int = 0


class DashboardData(BaseModel):
    """Dashboard data aggregation"""
    user: dict  # Will be UserResponse, but avoiding circular import
    active_projects: List[ProjectWithTheme]
    past_projects: List[ProjectWithTheme]
    user_stats: UserStats