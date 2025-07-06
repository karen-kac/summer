from pydantic import BaseModel
from typing import List
from models.enums import Grade, Interest, Personality, Strength, Duration


class UserProfile(BaseModel):
    grade: Grade
    interest: List[Interest]
    personality: List[Personality]
    strength: List[Strength]
    duration: Duration


class ResearchTheme(BaseModel):
    title: str
    description: str


class ThemeListResponse(BaseModel):
    themes: List[ResearchTheme]
