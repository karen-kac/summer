from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import date


class Achivement(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    category: str
    requirements: Optional[Dict[str, Any]] = {}
    points: int
    is_active: bool = Field(..., alias="isActive")
    created_at: date = Field(..., alias="createdAt")

    model_config = {
        "populate_by_name": True,
    }


class AchivementsListResponse(BaseModel):
    achivements: List[Achivement]
