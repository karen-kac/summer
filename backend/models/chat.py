from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"

class ChatMessage(BaseModel):
    id: Optional[str] = None
    user_id: str
    project_id: str
    message: str
    message_type: MessageType = MessageType.TEXT
    media_url: Optional[str] = None
    is_ai_response: bool = False
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    user_id: str
    project_id: str
    message: str
    message_type: MessageType = MessageType.TEXT
    media_url: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    suggestions: Optional[List[str]] = None
    media_analysis: Optional[str] = None