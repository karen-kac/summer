from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from models.database import DynamoDBBaseModel, EntityType, KeyBuilder


class Achievement(DynamoDBBaseModel):
    """実績定義"""
    # DynamoDB Keys
    PK: str = Field(..., description="ACHIEVEMENT#{achievement_id}")
    SK: str = Field(default="METADATA", description="METADATA")
    Type: str = Field(default=EntityType.ACHIEVEMENT)

    # Achievement Data
    achievementId: str
    name: str
    description: str
    icon: str
    category: str  # "beginner", "progress", "completion", "special"
    requirements: Dict[str, Any]  # 達成条件
    points: int
    isActive: bool = True
    createdAt: datetime
    updatedAt: datetime

    @classmethod
    def create(cls, achievement_id: str, **kwargs) -> "Achievement":
        """新しい実績を作成"""
        now = datetime.now()
        return cls(
            PK=KeyBuilder.achievement_pk(achievement_id),
            SK="METADATA",
            achievementId=achievement_id,
            createdAt=now,
            updatedAt=now,
            **kwargs
        )


class UserAchievement(DynamoDBBaseModel):
    """ユーザーが獲得した実績"""
    # DynamoDB Keys
    PK: str = Field(..., description="USER#{user_id}")
    SK: str = Field(..., description="ACHIEVEMENT#{achievement_id}")
    Type: str = Field(default=EntityType.USER_ACHIEVEMENT)

    # GSI for achievement queries
    GSI1PK: str = Field(..., description="ACHIEVEMENT#{achievement_id}")
    GSI1SK: str = Field(..., description="USER#{user_id}")

    # Achievement Data
    userId: str
    achievementId: str
    earnedAt: datetime
    earnedData: Dict[str, Any] = {}  # 獲得時の追加データ

    @classmethod
    def create(cls, user_id: str, achievement_id: str, **kwargs) -> "UserAchievement":
        """新しいユーザー実績を作成"""
        return cls(
            PK=KeyBuilder.user_pk(user_id),
            SK=KeyBuilder.achievement_sk(achievement_id),
            GSI1PK=KeyBuilder.achievement_pk(achievement_id),
            GSI1SK=KeyBuilder.user_pk(user_id),
            userId=user_id,
            achievementId=achievement_id,
            earnedAt=datetime.now(),
            **kwargs
        )


# Request/Response Models
class AchievementResponse(BaseModel):
    """実績レスポンス"""
    achievementId: str
    name: str
    description: str
    icon: str
    category: str
    points: int
    earnedAt: Optional[datetime] = None
    earnedData: Dict[str, Any] = {}


class GrantAchievementRequest(BaseModel):
    """実績付与リクエスト"""
    userId: str
    achievementId: str
    earnedData: Dict[str, Any] = {}


class AchievementCheckResult(BaseModel):
    """実績チェック結果"""
    newAchievements: List[AchievementResponse] = []
    totalNewPoints: int = 0
