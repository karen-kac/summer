from pydantic import BaseModel
from typing import List


# test用の簡易class
class UserProfileRequest(BaseModel):
    grade: str
    interests: List[str]
    personality: List[str]
    strengths: List[str]
    duration: str

class ThemeRecommendation(BaseModel):
    id: str
    title: str
    description: str
    difficulty: str
    estimated_days: int
    materials: List[str]
    steps: List[str]
    match_score: float
