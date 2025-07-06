from pydantic import BaseModel
from typing import List
from models.enums import Grade, Interest, Personality, Strength, Duration


class UserProfile(BaseModel):
    grade: Grade
    interests: List[Interest]
    personality: List[Personality]
    strengths: List[Strength]
    duration: Duration


class ResearchTheme(BaseModel):
    title: str
    description: str


class ThemeListResponse(BaseModel):
    themes: List[ResearchTheme]
