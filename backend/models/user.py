from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from models.database import DynamoDBBaseModel, EntityType, KeyBuilder
from models.enums import Grade, Interest, Personality, Strength, Duration


class NotificationSettings(BaseModel):
    """通知設定"""
    lineNotifications: bool = True
    emailNotifications: bool = True
    progressReminders: bool = True
    dailyTasks: bool = True
    reminderTime: str = "09:00"


class PrivacySettings(BaseModel):
    """プライバシー設定"""
    shareWithParents: bool = True
    allowDataAnalysis: bool = True
    publicProfile: bool = False


class DisplaySettings(BaseModel):
    """表示設定"""
    theme: str = "light"
    language: str = "ja"
    timezone: str = "Asia/Tokyo"


class UserProfile(DynamoDBBaseModel):
    """ユーザープロフィール"""
    # DynamoDB Keys
    PK: str = Field(..., description="USER#{user_id}")
    SK: str = Field(default="PROFILE", description="PROFILE")
    Type: str = Field(default=EntityType.USER_PROFILE)

    # User Data
    userId: str
    email: str
    displayName: str
    grade: Grade
    interests: List[Interest]
    personality: List[Personality]
    strengths: List[Strength]
    preferredDuration: Duration
    parentEmail: Optional[str] = None
    lineUserId: Optional[str] = None
    avatarUrl: Optional[str] = None
    bio: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    isActive: bool = True
    lastLoginAt: Optional[datetime] = None

    @classmethod
    def create(cls, user_id: str, **kwargs) -> "UserProfile":
        """新しいユーザープロフィールを作成"""
        now = datetime.now()
        return cls(
            PK=KeyBuilder.user_pk(user_id),
            SK="PROFILE",
            userId=user_id,
            createdAt=now,
            updatedAt=now,
            **kwargs
        )


class UserSettings(DynamoDBBaseModel):
    """ユーザー設定"""
    # DynamoDB Keys
    PK: str = Field(..., description="USER#{user_id}")
    SK: str = Field(default="SETTINGS", description="SETTINGS")
    Type: str = Field(default=EntityType.USER_SETTINGS)

    # Settings Data
    userId: str
    notificationSettings: NotificationSettings = NotificationSettings()
    privacySettings: PrivacySettings = PrivacySettings()
    displaySettings: DisplaySettings = DisplaySettings()
    updatedAt: datetime

    @classmethod
    def create(cls, user_id: str) -> "UserSettings":
        """デフォルト設定でユーザー設定を作成"""
        return cls(
            PK=KeyBuilder.user_pk(user_id),
            SK="SETTINGS",
            userId=user_id,
            updatedAt=datetime.now()
        )


class UserStats(DynamoDBBaseModel):
    """ユーザー統計"""
    # DynamoDB Keys
    PK: str = Field(..., description="USER#{user_id}")
    SK: str = Field(default="STATS", description="STATS")
    Type: str = Field(default=EntityType.USER_STATS)

    # Stats Data
    userId: str
    totalPoints: int = 0
    level: int = 1
    completedProjects: int = 0
    currentStreak: int = 0
    totalRecords: int = 0
    totalPhotos: int = 0
    totalExperiments: int = 0
    totalObservations: int = 0
    longestStreak: int = 0
    averageProjectDuration: float = 0.0
    favoriteGenre: Optional[str] = None
    achievements: List[str] = []
    lastActivityAt: Optional[datetime] = None
    updatedAt: datetime

    @classmethod
    def create(cls, user_id: str) -> "UserStats":
        """初期統計でユーザー統計を作成"""
        return cls(
            PK=KeyBuilder.user_pk(user_id),
            SK="STATS",
            userId=user_id,
            updatedAt=datetime.now()
        )


class LineConnection(DynamoDBBaseModel):
    """LINE連携情報"""
    # DynamoDB Keys
    PK: str = Field(..., description="USER#{user_id}")
    SK: str = Field(default="LINE_CONNECTION", description="LINE_CONNECTION")
    Type: str = Field(default=EntityType.LINE_CONNECTION)

    # LINE Data
    userId: str
    lineUserId: str
    displayName: Optional[str] = None
    pictureUrl: Optional[str] = None
    isActive: bool = True
    permissions: Dict[str, bool] = {
        "receiveNotifications": True,
        "receiveProgress": True,
        "allowQA": True
    }
    connectedAt: datetime
    lastInteractionAt: Optional[datetime] = None

    @classmethod
    def create(cls, user_id: str, line_user_id: str, **kwargs) -> "LineConnection":
        """新しいLINE連携を作成"""
        now = datetime.now()
        return cls(
            PK=KeyBuilder.user_pk(user_id),
            SK="LINE_CONNECTION",
            userId=user_id,
            lineUserId=line_user_id,
            connectedAt=now,
            lastInteractionAt=now,
            **kwargs
        )


# Request/Response Models
class CreateUserRequest(BaseModel):
    """ユーザー作成リクエスト"""
    email: str
    displayName: str
    grade: Grade
    interests: List[Interest]
    personality: List[Personality]
    strengths: List[Strength]
    preferredDuration: Duration
    parentEmail: Optional[str] = None


class UpdateUserProfileRequest(BaseModel):
    """ユーザープロフィール更新リクエスト"""
    displayName: Optional[str] = None
    grade: Optional[Grade] = None
    interests: Optional[List[Interest]] = None
    personality: Optional[List[Personality]] = None
    strengths: Optional[List[Strength]] = None
    preferredDuration: Optional[Duration] = None
    parentEmail: Optional[str] = None
    bio: Optional[str] = None


class UpdateUserSettingsRequest(BaseModel):
    """ユーザー設定更新リクエスト"""
    notificationSettings: Optional[NotificationSettings] = None
    privacySettings: Optional[PrivacySettings] = None
    displaySettings: Optional[DisplaySettings] = None


class UserResponse(BaseModel):
    """ユーザー情報レスポンス"""
    profile: UserProfile
    settings: Optional[UserSettings] = None
    stats: Optional[UserStats] = None
    lineConnection: Optional[LineConnection] = None
