from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from models.enums import Grade, Interest, Personality, Strength, Duration, Genre
import uuid


class UserProfile(BaseModel):
    grade: Grade
    interests: List[Interest]
    personality: List[Personality]
    strengths: List[Strength]
    duration: Duration
    additional_info: Optional[str] = None


class ResearchTheme(BaseModel):
    id: str = Field(default_factory=lambda: "theme_" + str(uuid.uuid4()))  # fixme?
    title: str
    description: str
    genre: Genre
    materials: List[str]
    steps: List[str]
    estimated_days: int = Field(..., alias="estimatedDays")
    difficulty: Literal["easy", "medium", "hard"]

    model_config = {
        "populate_by_name": True,
    }


class ThemeListResponse(BaseModel):
    themes: List[ResearchTheme]


class SaveThemeRequest(BaseModel):
    theme: ResearchTheme
    user_profile: Optional[UserProfile] = None


class SaveThemeResponse(BaseModel):
    success: bool
    message: str
    saved_theme_id: str


class ResearchStep(BaseModel):
    title: str
    description: str
    tips: List[str]
    duration: str
    order: int


class ResearchPlan(BaseModel):
    theme_id: str
    theme_title: str
    steps: List[ResearchStep]
    total_estimated_days: int
    difficulty: Literal["easy", "medium", "hard"]
    genre: Genre


class GeneratePlanRequest(BaseModel):
    theme_id: str


class GeneratePlanResponse(BaseModel):
    success: bool
    message: str
    plan: Optional[ResearchPlan] = None


class GetSavedThemeResponse(BaseModel):
    success: bool
    message: str
    theme: Optional[ResearchTheme] = None
    user_profile: Optional[UserProfile] = None


class GetResearchPlanResponse(BaseModel):
    success: bool
    message: str
    plan: Optional[ResearchPlan] = None
    is_cached: bool = False
