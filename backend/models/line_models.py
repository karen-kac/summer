from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class LineMessageType(str, Enum):
    """LINEメッセージタイプ"""
    TEXT = "text"
    IMAGE = "image"
    STICKER = "sticker"
    TEMPLATE = "template"
    FLEX = "flex"


class LineUserProfile(BaseModel):
    """LINE ユーザープロフィール情報"""
    user_id: str
    display_name: Optional[str] = None
    picture_url: Optional[str] = None
    status_message: Optional[str] = None


class LineUserConnection(BaseModel):
    """ユーザーとLINEアカウントの連携情報"""
    id: str
    user_id: str  # 内部ユーザーID
    line_user_id: str  # LINE ユーザーID
    display_name: Optional[str] = None
    picture_url: Optional[str] = None
    is_active: bool = True
    connected_at: datetime
    last_interaction_at: Optional[datetime] = None


class LineMessage(BaseModel):
    """LINEメッセージモデル"""
    type: LineMessageType
    text: Optional[str] = None
    alt_text: Optional[str] = None  # Flexメッセージ用
    contents: Optional[Dict[str, Any]] = None  # Flexメッセージ用


class LineTextMessage(LineMessage):
    """LINEテキストメッセージ"""
    type: LineMessageType = LineMessageType.TEXT
    text: str


class LineFlexMessage(LineMessage):
    """LINE Flexメッセージ"""
    type: LineMessageType = LineMessageType.FLEX
    alt_text: str
    contents: Dict[str, Any]


class LineWebhookEvent(BaseModel):
    """LINE Webhook イベントモデル"""
    type: str
    timestamp: int
    source: Dict[str, Any]
    reply_token: Optional[str] = None
    message: Optional[Dict[str, Any]] = None


class LineQuickReply(BaseModel):
    """LINE クイックリプライ"""
    type: str = "action"
    action: Dict[str, Any]


class ResearchProgressNotification(BaseModel):
    """研究進捗通知モデル"""
    user_id: str
    line_user_id: str
    research_title: str
    progress_percentage: int
    completed_tasks: int
    total_tasks: int
    next_task: Optional[str] = None
    encouragement_message: str
