from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid


class DynamoDBBaseModel(BaseModel):
    """DynamoDB共通基底クラス"""
    PK: str = Field(..., description="パーティションキー")
    SK: str = Field(..., description="ソートキー")
    Type: str = Field(..., description="エンティティタイプ")
    GSI1PK: Optional[str] = Field(None, description="GSI1パーティションキー")
    GSI1SK: Optional[str] = Field(None, description="GSI1ソートキー")
    GSI2PK: Optional[str] = Field(None, description="GSI2パーティションキー")
    GSI2SK: Optional[str] = Field(None, description="GSI2ソートキー")
    GSI3PK: Optional[str] = Field(None, description="GSI3パーティションキー")
    GSI3SK: Optional[str] = Field(None, description="GSI3ソートキー")
    GSI4PK: Optional[str] = Field(None, description="GSI4パーティションキー")
    GSI4SK: Optional[str] = Field(None, description="GSI4ソートキー")
    TTL: Optional[int] = Field(None, description="Time To Live")

    def to_dynamo_item(self) -> Dict[str, Any]:
        """DynamoDB形式のアイテムに変換"""
        return {k: v for k, v in self.model_dump().items() if v is not None}


class EntityType(str, Enum):
    """エンティティタイプ列挙"""
    USER_PROFILE = "UserProfile"
    USER_SETTINGS = "UserSettings"
    USER_STATS = "UserStats"
    RESEARCH_THEME = "ResearchTheme"
    SAVED_THEME = "SavedTheme"
    RESEARCH_PLAN = "ResearchPlan"
    USER_PLAN = "UserPlan"
    RESEARCH_PROJECT = "ResearchProject"
    PROJECT_SETTINGS = "ProjectSettings"
    SCHEDULE = "Schedule"
    CALENDAR_CONFIG = "CalendarConfig"
    RECORD = "Record"
    EXPERIMENT = "Experiment"
    MEDIA = "Media"
    NOTIFICATION = "Notification"
    LINE_CONNECTION = "LineConnection"
    REPORT = "Report"
    AI_ANALYSIS = "AIAnalysis"
    ACHIEVEMENT = "Achievement"
    USER_ACHIEVEMENT = "UserAchievement"


class KeyBuilder:
    """DynamoDBキー生成ユーティリティ"""

    @staticmethod
    def user_pk(user_id: str) -> str:
        return f"USER#{user_id}"

    @staticmethod
    def theme_pk(theme_id: str) -> str:
        return f"THEME#{theme_id}"

    @staticmethod
    def plan_pk(plan_id: str) -> str:
        return f"PLAN#{plan_id}"

    @staticmethod
    def project_pk(project_id: str) -> str:
        return f"PROJECT#{project_id}"

    @staticmethod
    def media_pk(media_id: str) -> str:
        return f"MEDIA#{media_id}"

    @staticmethod
    def record_sk(date: str, sequence: str) -> str:
        return f"RECORD#{date}#{sequence}"

    @staticmethod
    def schedule_sk(date: str) -> str:
        return f"SCHEDULE#{date}"

    @staticmethod
    def notification_sk(notification_id: str) -> str:
        return f"NOTIFICATION#{notification_id}"

    @staticmethod
    def theme_sk(theme_id: str) -> str:
        return f"THEME#{theme_id}"

    @staticmethod
    def plan_sk(plan_id: str) -> str:
        return f"PLAN#{plan_id}"

    @staticmethod
    def generate_uuid() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def generate_date_based_id() -> str:
        return datetime.now().strftime("%Y%m%d%H%M%S") + "_" + str(uuid.uuid4())[:8]

    @staticmethod
    def achievement_pk(achievement_id: str) -> str:
        return f"ACHIEVEMENT#{achievement_id}"

    @staticmethod
    def achievement_sk(achievement_id: str) -> str:
        return f"ACHIEVEMENT#{achievement_id}"
