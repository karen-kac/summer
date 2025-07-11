from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import date
from models.enums import Genre


class ResearchProject(BaseModel):
    id: str
    user_id: str = Field(..., alias="userId")
    theme_id: str = Field(..., alias="themeId")
    title: str
    description: str
    genre: Optional[Genre] = None
    status: Literal["planning", "in_progress", "completed", "paused"]
    start_date: date = Field(..., alias="startDate")
    target_end_date: date = Field(..., alias="targetEndDate")
    actual_end_date: Optional[date] = Field(None, alias="actualEndDate")
    custom_materials: List[str] = Field(..., alias="customMaterials")
    custom_steps: List[str] = Field(..., alias="customSteps")
    progress_percentage: int = Field(..., alias="progressPercentage")
    created_at: date = Field(..., alias="createdAt")
    updated_at: date = Field(..., alias="updatedAt")

    model_config = {
        "populate_by_name": True,
    }


class ProjectsListResponse(BaseModel):
    projects: List[ResearchProject]
