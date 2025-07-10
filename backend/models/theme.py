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
