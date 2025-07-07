from pydantic import BaseModel, Field
from typing import List, Literal
from models.enums import Grade, Interest, Personality, Strength, Duration


class UserProfile(BaseModel):
    grade: Grade
    interests: List[Interest]
    personality: List[Personality]
    strengths: List[Strength]
    duration: Duration


class ResearchTheme(BaseModel):
    id: str
    title: str
    description: str
    materials: List[str]
    steps: List[str]
    estimated_days: int = Field(..., alias="estimatedDays")
    difficulty: Literal["easy", "medium", "hard"]

    model_config = {
        "populate_by_name": True,
    }


class ThemeListResponse(BaseModel):
    themes: List[ResearchTheme]
