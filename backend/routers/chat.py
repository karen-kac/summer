from fastapi import APIRouter, HTTPException, UploadFile, File
from models.chat import ChatRequest, ChatResponse, MessageType
from services.chat_service import ChatService
import uuid

router = APIRouter(prefix="/api/chat", tags=["chat"])
chat_service = ChatService()

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """テキストメッセージを送信"""
    try:
        response = await chat_service.process_chat_message(
            user_id=request.user_id,
            project_id=request.project_id,
            message=request.message,
            message_type=request.message_type,
            media_url=request.media_url
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-media", response_model=ChatResponse)
async def upload_media(
    user_id: str,
    project_id: str,
    message: str,
    file: UploadFile = File(...)
):
    """メディアファイル付きメッセージを送信"""
    try:
        # ファイルタイプ判定
        if file.content_type.startswith('image/'):
            message_type = MessageType.IMAGE
        elif file.content_type.startswith('audio/'):
            message_type = MessageType.AUDIO
        else:
            raise HTTPException(status_code=400, detail="サポートされていないファイル形式です")
        
        # ファイル保存（実際はS3に保存）
        file_id = str(uuid.uuid4())
        media_url = f"temp/{file_id}_{file.filename}"
        
        response = await chat_service.process_chat_message(
            user_id=user_id,
            project_id=project_id,
            message=message,
            message_type=message_type,
            media_url=media_url
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))