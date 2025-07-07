from pydantic import BaseModel, Field
from typing import List
import uuid

# フロントエンドから受け取るclass
class UserProfileRequest(BaseModel):
    grade: str
    interests: List[str]
    personality: List[str]
    strengths: List[str]
    duration: str

# フロントエンドへ送るclass
class ThemeRecommendation(BaseModel):
    id: str = Field(default_factory=lambda: "theme_" + str(uuid.uuid4()))
    title: str
    description: str
    difficulty: str
    estimatedDays: int # estimated_days: int
    materials: List[str]
    steps: List[str]
    match_score: float = Field(default=0.0)
