from pydantic import BaseModel
from typing import List


class UserProfile(BaseModel):
    grade: int
    interest: str
    strength: str


class ResearchTheme(BaseModel):
    title: str
    description: str


class ThemeListResponse(BaseModel):
    themes: List[ResearchTheme]
