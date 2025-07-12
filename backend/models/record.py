from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime, date
from models.database import DynamoDBBaseModel, EntityType, KeyBuilder


class WeatherInfo(BaseModel):
    """天気情報"""
    condition: str  # sunny, cloudy, rainy, snowy
    temperature: float
    humidity: float
    windSpeed: Optional[float] = None
    pressure: Optional[float] = None


class LocationInfo(BaseModel):
    """位置情報"""
    room: Optional[str] = None
    position: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    address: Optional[str] = None


class AIAnalysisResult(BaseModel):
    """AI解析結果"""
    summary: str
    insights: List[str]
    confidence: float
    labels: List[str] = []
    metrics: Dict[str, Any] = {}
    suggestions: List[str] = []


class Record(DynamoDBBaseModel):
    """研究記録"""
    # DynamoDB Keys
    PK: str = Field(..., description="PROJECT#{project_id}")
    SK: str = Field(..., description="RECORD#{date}#{sequence}")
    Type: str = Field(default=EntityType.RECORD)
    GSI1PK: Optional[str] = Field(None, description="USER#{user_id}")
    GSI1SK: Optional[str] = Field(None, description="RECORD#{record_id}")
    GSI3PK: Optional[str] = Field(None, description="DATE#{date}")
    GSI3SK: Optional[str] = Field(None, description="PROJECT#{project_id}")

    # Record Data
    recordId: str
    projectId: str
    userId: str
    stepId: Optional[str] = None
    recordType: Literal["observation", "experiment", "photo", "note", "data", "voice", "video"]
    title: str
    content: str
    recordDate: date
    recordTime: str
    data: Dict[str, Any] = {}
    tags: List[str] = []
    weatherInfo: Optional[WeatherInfo] = None
    locationInfo: Optional[LocationInfo] = None
    mediaIds: List[str] = []
    aiAnalysis: Optional[AIAnalysisResult] = None
    isPublic: bool = False
    parentVisible: bool = True
    createdAt: datetime
    updatedAt: datetime

    @classmethod
    def create(cls, project_id: str, user_id: str, record_date: date, sequence: str, **kwargs) -> "Record":
        """新しい研究記録を作成"""
        record_id = KeyBuilder.generate_date_based_id()
        date_str = record_date.strftime("%Y-%m-%d")
        now = datetime.now()

        return cls(
            PK=KeyBuilder.project_pk(project_id),
            SK=KeyBuilder.record_sk(date_str, sequence),
            recordId=record_id,
            projectId=project_id,
            userId=user_id,
            recordDate=record_date,
            GSI1PK=KeyBuilder.user_pk(user_id),
            GSI1SK=f"RECORD#{record_id}",
            GSI3PK=f"DATE#{date_str}",
            GSI3SK=KeyBuilder.project_pk(project_id),
            createdAt=now,
            updatedAt=now,
            **kwargs
        )


class ExperimentVariable(BaseModel):
    """実験変数"""
    name: str
    type: Literal["independent", "dependent", "controlled"]
    value: Any
    unit: Optional[str] = None
    description: Optional[str] = None


class ExperimentResult(BaseModel):
    """実験結果"""
    measurementId: str
    timestamp: datetime
    variables: List[ExperimentVariable]
    observations: str
    photos: List[str] = []
    notes: Optional[str] = None


class Experiment(DynamoDBBaseModel):
    """実験データ"""
    # DynamoDB Keys
    PK: str = Field(..., description="PROJECT#{project_id}")
    SK: str = Field(..., description="EXPERIMENT#{experiment_id}")
    Type: str = Field(default=EntityType.EXPERIMENT)

    # Experiment Data
    experimentId: str
    projectId: str
    userId: str
    title: str
    hypothesis: str
    method: str
    materials: List[str]
    variables: List[ExperimentVariable]
    results: List[ExperimentResult]
    conclusion: Optional[str] = None
    recordIds: List[str] = []
    mediaIds: List[str] = []
    status: Literal["planned", "in_progress", "completed", "failed"]
    startDate: date
    endDate: Optional[date] = None
    tags: List[str] = []
    createdAt: datetime
    updatedAt: datetime

    @classmethod
    def create(cls, project_id: str, user_id: str, experiment_id: str, **kwargs) -> "Experiment":
        """新しい実験を作成"""
        now = datetime.now()
        return cls(
            PK=KeyBuilder.project_pk(project_id),
            SK=f"EXPERIMENT#{experiment_id}",
            experimentId=experiment_id,
            projectId=project_id,
            userId=user_id,
            createdAt=now,
            updatedAt=now,
            **kwargs
        )


class MediaMetadata(BaseModel):
    """メディアメタデータ"""
    camera: Optional[str] = None
    location: Optional[LocationInfo] = None
    timestamp: Optional[datetime] = None
    settings: Dict[str, Any] = {}
    exif: Dict[str, Any] = {}


class MediaDimensions(BaseModel):
    """メディア寸法"""
    width: int
    height: int
    duration: Optional[float] = None  # 動画・音声の場合


class Media(DynamoDBBaseModel):
    """メディアファイル"""
    # DynamoDB Keys
    PK: str = Field(..., description="MEDIA#{media_id}")
    SK: str = Field(default="METADATA", description="METADATA")
    Type: str = Field(default=EntityType.MEDIA)
    GSI1PK: Optional[str] = Field(None, description="USER#{user_id}")
    GSI1SK: Optional[str] = Field(None, description="MEDIA#{media_id}")
    GSI2PK: Optional[str] = Field(None, description="PROJECT#{project_id}")
    GSI2SK: Optional[str] = Field(None, description="MEDIA#{media_id}")

    # Media Data
    mediaId: str
    userId: str
    projectId: str
    recordId: Optional[str] = None
    mediaType: Literal["image", "video", "audio", "document"]
    fileName: str
    s3Key: str
    s3Bucket: str
    thumbnailS3Key: Optional[str] = None
    fileSize: int
    mimeType: str
    dimensions: Optional[MediaDimensions] = None
    metadata: Optional[MediaMetadata] = None
    aiAnalysis: Optional[AIAnalysisResult] = None
    isPublic: bool = False
    parentVisible: bool = True
    processingStatus: Literal["pending", "processing", "completed", "failed"] = "pending"
    createdAt: datetime
    updatedAt: datetime

    @classmethod
    def create(cls, media_id: str, user_id: str, project_id: str, **kwargs) -> "Media":
        """新しいメディアファイルを作成"""
        now = datetime.now()
        return cls(
            PK=KeyBuilder.media_pk(media_id),
            SK="METADATA",
            mediaId=media_id,
            userId=user_id,
            projectId=project_id,
            GSI1PK=KeyBuilder.user_pk(user_id),
            GSI1SK=KeyBuilder.media_pk(media_id),
            GSI2PK=KeyBuilder.project_pk(project_id),
            GSI2SK=KeyBuilder.media_pk(media_id),
            createdAt=now,
            updatedAt=now,
            **kwargs
        )


class NotificationData(BaseModel):
    """通知データ"""
    projectId: Optional[str] = None
    stepId: Optional[str] = None
    reminderType: Optional[str] = None
    actionUrl: Optional[str] = None
    customData: Dict[str, Any] = {}


class Notification(DynamoDBBaseModel):
    """通知"""
    # DynamoDB Keys
    PK: str = Field(..., description="USER#{user_id}")
    SK: str = Field(..., description="NOTIFICATION#{notification_id}")
    Type: str = Field(default=EntityType.NOTIFICATION)
    GSI1PK: Optional[str] = Field(None, description="STATUS#{status}")
    GSI1SK: Optional[str] = Field(None, description="NOTIFICATION#{notification_id}")

    # Notification Data
    notificationId: str
    userId: str
    type: Literal["progress_reminder", "achievement", "deadline", "system", "parent_update"]
    title: str
    message: str
    priority: Literal["low", "normal", "high", "urgent"]
    status: Literal["unread", "read", "dismissed"]
    channels: List[Literal["app", "line", "email"]]
    data: Optional[NotificationData] = None
    scheduledAt: Optional[datetime] = None
    sentAt: Optional[datetime] = None
    readAt: Optional[datetime] = None
    dismissedAt: Optional[datetime] = None
    createdAt: datetime

    @classmethod
    def create(cls, user_id: str, notification_id: str, **kwargs) -> "Notification":
        """新しい通知を作成"""
        now = datetime.now()
        return cls(
            PK=KeyBuilder.user_pk(user_id),
            SK=KeyBuilder.notification_sk(notification_id),
            notificationId=notification_id,
            userId=user_id,
            GSI1PK=f"STATUS#{kwargs.get('status', 'unread')}",
            GSI1SK=KeyBuilder.notification_sk(notification_id),
            createdAt=now,
            **kwargs
        )


class ReportSection(BaseModel):
    """レポートセクション"""
    title: str
    content: str
    order: int
    type: Literal["text", "image", "chart", "table", "graph"]
    mediaIds: List[str] = []
    data: Dict[str, Any] = {}


class Report(DynamoDBBaseModel):
    """研究レポート"""
    # DynamoDB Keys
    PK: str = Field(..., description="PROJECT#{project_id}")
    SK: str = Field(..., description="REPORT#{report_type}")
    Type: str = Field(default=EntityType.REPORT)
    GSI1PK: Optional[str] = Field(None, description="USER#{user_id}")
    GSI1SK: Optional[str] = Field(None, description="REPORT#{report_id}")

    # Report Data
    reportId: str
    projectId: str
    userId: str
    title: str
    reportType: Literal["daily", "weekly", "final", "summary"]
    content: str
    sections: List[ReportSection]
    mediaIds: List[str] = []
    s3Key: Optional[str] = None
    pdfS3Key: Optional[str] = None
    status: Literal["draft", "published", "shared"]
    generatedBy: Literal["user", "ai", "hybrid"]
    aiModel: Optional[str] = None
    templateId: Optional[str] = None
    version: str = "1.0"
    isPublic: bool = False
    parentVisible: bool = True
    createdAt: datetime
    publishedAt: Optional[datetime] = None
    updatedAt: datetime

    @classmethod
    def create(cls, project_id: str, user_id: str, report_type: str, **kwargs) -> "Report":
        """新しいレポートを作成"""
        report_id = KeyBuilder.generate_date_based_id()
        now = datetime.now()
        return cls(
            PK=KeyBuilder.project_pk(project_id),
            SK=f"REPORT#{report_type}",
            reportId=report_id,
            projectId=project_id,
            userId=user_id,
            reportType=report_type,
            GSI1PK=KeyBuilder.user_pk(user_id),
            GSI1SK=f"REPORT#{report_id}",
            createdAt=now,
            updatedAt=now,
            **kwargs
        )


class AIAnalysisInput(BaseModel):
    """AI解析入力"""
    type: Literal["image", "text", "data", "audio", "video"]
    s3Key: Optional[str] = None
    content: Optional[str] = None
    data: Dict[str, Any] = {}


class AIAnalysisOutput(BaseModel):
    """AI解析出力"""
    result: Dict[str, Any]
    confidence: float
    labels: List[str] = []
    description: str
    suggestions: List[str] = []
    metrics: Dict[str, Any] = {}


class AIAnalysis(DynamoDBBaseModel):
    """AI解析結果"""
    # DynamoDB Keys
    PK: str = Field(..., description="PROJECT#{project_id}")
    SK: str = Field(..., description="AI_ANALYSIS#{analysis_id}")
    Type: str = Field(default=EntityType.AI_ANALYSIS)

    # Analysis Data
    analysisId: str
    projectId: str
    userId: str
    recordId: Optional[str] = None
    mediaId: Optional[str] = None
    analysisType: Literal["image", "text", "data", "trend", "audio", "video"]
    input: AIAnalysisInput
    output: AIAnalysisOutput
    model: str
    version: str
    processingTime: float
    cost: float
    status: Literal["pending", "processing", "completed", "failed"]
    errorMessage: Optional[str] = None
    createdAt: datetime
    completedAt: Optional[datetime] = None

    @classmethod
    def create(cls, project_id: str, user_id: str, analysis_id: str, **kwargs) -> "AIAnalysis":
        """新しいAI解析を作成"""
        now = datetime.now()
        return cls(
            PK=KeyBuilder.project_pk(project_id),
            SK=f"AI_ANALYSIS#{analysis_id}",
            analysisId=analysis_id,
            projectId=project_id,
            userId=user_id,
            createdAt=now,
            **kwargs
        )


# Request/Response Models
class CreateRecordRequest(BaseModel):
    """記録作成リクエスト"""
    projectId: str
    recordType: Literal["observation", "experiment", "photo", "note", "data", "voice", "video"]
    title: str
    content: str
    recordDate: date
    recordTime: str
    data: Dict[str, Any] = {}
    tags: List[str] = []
    weatherInfo: Optional[WeatherInfo] = None
    locationInfo: Optional[LocationInfo] = None
    stepId: Optional[str] = None


class UpdateRecordRequest(BaseModel):
    """記録更新リクエスト"""
    title: Optional[str] = None
    content: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    weatherInfo: Optional[WeatherInfo] = None
    locationInfo: Optional[LocationInfo] = None


class MediaUploadRequest(BaseModel):
    """メディアアップロードリクエスト"""
    projectId: str
    recordId: Optional[str] = None
    mediaType: Literal["image", "video", "audio", "document"]
    fileName: str
    fileSize: int
    mimeType: str


class MediaUploadResponse(BaseModel):
    """メディアアップロードレスポンス"""
    mediaId: str
    uploadUrl: str
    s3Key: str
    expiresIn: int


class RecordResponse(BaseModel):
    """記録レスポンス"""
    record: Record
    media: List[Media] = []
    aiAnalysis: Optional[AIAnalysis] = None


class RecordListResponse(BaseModel):
    """記録一覧レスポンス"""
    records: List[RecordResponse]
    total: int
    hasMore: bool
    nextToken: Optional[str] = None
