from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime, date
from models.database import DynamoDBBaseModel, EntityType, KeyBuilder
from models.enums import Grade, Genre


class ResearchTheme(DynamoDBBaseModel):
    """研究テーマ"""
    # DynamoDB Keys
    PK: str = Field(..., description="THEME#{theme_id}")
    SK: str = Field(default="METADATA", description="METADATA")
    Type: str = Field(default=EntityType.RESEARCH_THEME)
    GSI1PK: Optional[str] = Field(None, description="GENRE#{genre}")
    GSI1SK: Optional[str] = Field(None, description="THEME#{theme_id}")

    # Theme Data
    themeId: str
    title: str
    description: str
    genre: Genre
    difficulty: Literal["easy", "medium", "hard"]
    estimatedDays: int
    materials: List[str]
    defaultSteps: List[str]
    targetGrades: List[Grade]
    keywords: List[str]
    isPublic: bool = True
    createdBy: Optional[str] = None
    createdAt: datetime
    usageCount: int = 0
    rating: float = 0.0
    ratingCount: int = 0

    @classmethod
    def create(cls, theme_id: str, **kwargs) -> "ResearchTheme":
        """新しい研究テーマを作成"""
        return cls(
            PK=KeyBuilder.theme_pk(theme_id),
            SK="METADATA",
            themeId=theme_id,
            GSI1PK=f"GENRE#{kwargs.get('genre', 'experiment')}",
            GSI1SK=KeyBuilder.theme_pk(theme_id),
            createdAt=datetime.now(),
            **kwargs
        )


class SavedTheme(DynamoDBBaseModel):
    """ユーザー保存テーマ"""
    # DynamoDB Keys
    PK: str = Field(..., description="USER#{user_id}")
    SK: str = Field(..., description="THEME#{theme_id}")
    Type: str = Field(default=EntityType.SAVED_THEME)

    # Saved Theme Data
    userId: str
    themeId: str
    customMaterials: List[str] = []
    customSteps: List[str] = []
    savedAt: datetime
    notes: Optional[str] = None

    @classmethod
    def create(cls, user_id: str, theme_id: str, **kwargs) -> "SavedTheme":
        """新しい保存テーマを作成"""
        return cls(
            PK=KeyBuilder.user_pk(user_id),
            SK=KeyBuilder.theme_sk(theme_id),
            userId=user_id,
            themeId=theme_id,
            savedAt=datetime.now(),
            **kwargs
        )


class ResearchStep(BaseModel):
    """研究ステップ"""
    stepId: str
    title: str
    description: str
    tips: List[str]
    estimatedDuration: str
    order: int
    isOptional: bool = False
    prerequisites: List[str] = []


class ResearchPlan(DynamoDBBaseModel):
    """研究計画"""
    # DynamoDB Keys
    PK: str = Field(..., description="PLAN#{plan_id}")
    SK: str = Field(default="METADATA", description="METADATA")
    Type: str = Field(default=EntityType.RESEARCH_PLAN)

    # Plan Data
    planId: str
    themeId: str
    title: str
    description: str
    steps: List[ResearchStep]
    totalDays: int
    difficulty: Literal["easy", "medium", "hard"]
    genre: Genre
    isTemplate: bool = True
    createdBy: Optional[str] = None
    createdAt: datetime
    version: str = "1.0"

    @classmethod
    def create(cls, plan_id: str, **kwargs) -> "ResearchPlan":
        """新しい研究計画を作成"""
        return cls(
            PK=KeyBuilder.plan_pk(plan_id),
            SK="METADATA",
            planId=plan_id,
            createdAt=datetime.now(),
            **kwargs
        )


class UserPlan(DynamoDBBaseModel):
    """ユーザー専用計画"""
    # DynamoDB Keys
    PK: str = Field(..., description="USER#{user_id}")
    SK: str = Field(..., description="PLAN#{plan_id}")
    Type: str = Field(default=EntityType.USER_PLAN)

    # User Plan Data
    userId: str
    planId: str
    customSteps: List[ResearchStep] = []
    modifications: Dict[str, Any] = {}
    createdAt: datetime

    @classmethod
    def create(cls, user_id: str, plan_id: str, **kwargs) -> "UserPlan":
        """新しいユーザー計画を作成"""
        return cls(
            PK=KeyBuilder.user_pk(user_id),
            SK=KeyBuilder.plan_sk(plan_id),
            userId=user_id,
            planId=plan_id,
            createdAt=datetime.now(),
            **kwargs
        )


class NotificationSettings(BaseModel):
    """通知設定"""
    dailyReminders: bool = True
    progressUpdates: bool = True
    parentNotifications: bool = True
    deadlineAlerts: bool = True


class SharingSettings(BaseModel):
    """共有設定"""
    allowParentView: bool = True
    allowTeacherView: bool = False
    allowPublicView: bool = False


class ResearchProject(DynamoDBBaseModel):
    """研究プロジェクト"""
    # DynamoDB Keys
    PK: str = Field(..., description="PROJECT#{project_id}")
    SK: str = Field(default="METADATA", description="METADATA")
    Type: str = Field(default=EntityType.RESEARCH_PROJECT)
    GSI1PK: Optional[str] = Field(None, description="USER#{user_id}")
    GSI1SK: Optional[str] = Field(None, description="PROJECT#{project_id}")
    GSI2PK: Optional[str] = Field(None, description="STATUS#{status}")
    GSI2SK: Optional[str] = Field(None, description="PROJECT#{project_id}")

    # Project Data
    projectId: str
    userId: str
    themeId: str
    planId: Optional[str] = None
    title: str
    description: str
    status: Literal["planning", "in_progress", "completed", "paused"]
    genre: Genre
    startDate: date
    targetEndDate: date
    actualEndDate: Optional[date] = None
    currentStepIndex: int = 0
    progressPercentage: float = 0.0
    customGoals: List[str] = []
    achievements: List[str] = []
    tags: List[str] = []
    difficulty: Literal["easy", "medium", "hard"]
    estimatedDays: int
    actualDays: Optional[int] = None
    createdAt: datetime
    updatedAt: datetime

    @classmethod
    def create(cls, project_id: str, user_id: str, **kwargs) -> "ResearchProject":
        """新しい研究プロジェクトを作成"""
        now = datetime.now()
        return cls(
            PK=KeyBuilder.project_pk(project_id),
            SK="METADATA",
            projectId=project_id,
            userId=user_id,
            GSI1PK=KeyBuilder.user_pk(user_id),
            GSI1SK=KeyBuilder.project_pk(project_id),
            GSI2PK=f"STATUS#{kwargs.get('status', 'planning')}",
            GSI2SK=KeyBuilder.project_pk(project_id),
            createdAt=now,
            updatedAt=now,
            **kwargs
        )


class ProjectSettings(DynamoDBBaseModel):
    """プロジェクト設定"""
    # DynamoDB Keys
    PK: str = Field(..., description="PROJECT#{project_id}")
    SK: str = Field(default="SETTINGS", description="SETTINGS")
    Type: str = Field(default=EntityType.PROJECT_SETTINGS)

    # Settings Data
    projectId: str
    notifications: NotificationSettings = NotificationSettings()
    sharing: SharingSettings = SharingSettings()
    updatedAt: datetime

    @classmethod
    def create(cls, project_id: str) -> "ProjectSettings":
        """デフォルト設定でプロジェクト設定を作成"""
        return cls(
            PK=KeyBuilder.project_pk(project_id),
            SK="SETTINGS",
            projectId=project_id,
            updatedAt=datetime.now()
        )


class ScheduleEvent(BaseModel):
    """スケジュールイベント"""
    id: str
    projectId: str
    stepId: Optional[str] = None
    title: str
    description: str
    startTime: str
    endTime: str
    type: Literal["task", "reminder", "milestone", "deadline"]
    status: Literal["pending", "completed", "skipped", "cancelled"]
    priority: Literal["low", "normal", "high", "urgent"]
    tags: List[str] = []


class Schedule(DynamoDBBaseModel):
    """スケジュール"""
    # DynamoDB Keys
    PK: str = Field(..., description="USER#{user_id}")
    SK: str = Field(..., description="SCHEDULE#{date}")
    Type: str = Field(default=EntityType.SCHEDULE)
    GSI3PK: Optional[str] = Field(None, description="DATE#{date}")
    GSI3SK: Optional[str] = Field(None, description="USER#{user_id}")

    # Schedule Data
    userId: str
    date: date
    events: List[ScheduleEvent]
    totalTasks: int = 0
    completedTasks: int = 0
    updatedAt: datetime

    @classmethod
    def create(cls, user_id: str, schedule_date: date, **kwargs) -> "Schedule":
        """新しいスケジュールを作成"""
        date_str = schedule_date.strftime("%Y-%m-%d")
        return cls(
            PK=KeyBuilder.user_pk(user_id),
            SK=KeyBuilder.schedule_sk(date_str),
            userId=user_id,
            date=schedule_date,
            GSI3PK=f"DATE#{date_str}",
            GSI3SK=KeyBuilder.user_pk(user_id),
            updatedAt=datetime.now(),
            **kwargs
        )


class CalendarConfig(DynamoDBBaseModel):
    """カレンダー設定"""
    # DynamoDB Keys
    PK: str = Field(..., description="USER#{user_id}")
    SK: str = Field(default="CALENDAR_CONFIG", description="CALENDAR_CONFIG")
    Type: str = Field(default=EntityType.CALENDAR_CONFIG)

    # Config Data
    userId: str
    timezone: str = "Asia/Tokyo"
    weekStartDay: Literal["monday", "sunday"] = "monday"
    defaultReminderTime: str = "09:00"
    autoScheduling: bool = True
    workingDays: List[str] = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    workingHours: Dict[str, str] = {"start": "09:00", "end": "21:00"}
    notifications: Dict[str, int] = {
        "beforeTask": 30,  # 30分前
        "afterDeadline": 60  # 1時間後
    }
    updatedAt: datetime

    @classmethod
    def create(cls, user_id: str, **kwargs) -> "CalendarConfig":
        """デフォルト設定でカレンダー設定を作成"""
        return cls(
            PK=KeyBuilder.user_pk(user_id),
            SK="CALENDAR_CONFIG",
            userId=user_id,
            updatedAt=datetime.now(),
            **kwargs
        )


# Request/Response Models
class CreateProjectRequest(BaseModel):
    """プロジェクト作成リクエスト"""
    themeId: str
    title: str
    description: str
    startDate: date
    targetEndDate: date
    customGoals: List[str] = []
    planId: Optional[str] = None


class UpdateProjectRequest(BaseModel):
    """プロジェクト更新リクエスト"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Literal["planning", "in_progress", "completed", "paused"]] = None
    targetEndDate: Optional[date] = None
    currentStepIndex: Optional[int] = None
    progressPercentage: Optional[float] = None
    customGoals: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class ProjectResponse(BaseModel):
    """プロジェクト情報レスポンス"""
    project: ResearchProject
    settings: Optional[ProjectSettings] = None
    theme: Optional[ResearchTheme] = None
    plan: Optional[ResearchPlan] = None
    schedule: Optional[Schedule] = None


class ProjectListResponse(BaseModel):
    """プロジェクト一覧レスポンス"""
    projects: List[ProjectResponse]
    total: int
    hasMore: bool
