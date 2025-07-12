from fastapi import APIRouter, HTTPException, Request, Header, Depends
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import json
import logging

from services.line_service import LineService, line_service
from models.line_models import LineWebhookEvent

logger = logging.getLogger(__name__)

router = APIRouter()


# 依存性注入（本来はDIコンテナで管理）
def get_line_service() -> LineService:
    return line_service


@router.post("/webhook")
async def line_webhook(
    request: Request,
    x_line_signature: Optional[str] = Header(None),
    service: LineService = Depends(get_line_service)
):
    """LINE Webhookエンドポイント"""
    try:
        # リクエストボディを取得
        body = await request.body()
        body_str = body.decode('utf-8')

        # 署名を検証
        if x_line_signature:
            is_valid = service.line_client.verify_signature(body_str, x_line_signature)
            if not is_valid:
                logger.warning("Invalid LINE webhook signature")
                raise HTTPException(status_code=400, detail="Invalid signature")

        # JSON をパース
        try:
            webhook_data = json.loads(body_str)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in webhook payload")
            raise HTTPException(status_code=400, detail="Invalid JSON")

        # イベントを処理
        events = webhook_data.get("events", [])
        for event_data in events:
            try:
                event = LineWebhookEvent(**event_data)
                await service.handle_webhook_message(event)
            except Exception as e:
                logger.error(f"Failed to process webhook event: {e}")
                # 個別イベントの失敗は無視して続行
                continue

        return JSONResponse(content={"status": "ok"})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/connect")
async def connect_line_account(
    request_data: Dict[str, str],
    service: LineService = Depends(get_line_service)
):
    """ユーザーのLINEアカウント連携"""
    try:
        user_id = request_data.get("user_id")
        line_user_id = request_data.get("line_user_id")

        if not user_id or not line_user_id:
            raise HTTPException(
                status_code=400,
                detail="user_id and line_user_id are required"
            )

        connection = await service.connect_user_to_line(user_id, line_user_id)

        if not connection:
            raise HTTPException(
                status_code=500,
                detail="Failed to connect LINE account"
            )

        return {
            "status": "success",
            "connection": {
                "id": connection.id,
                "line_user_id": connection.line_user_id,
                "display_name": connection.display_name,
                "connected_at": connection.connected_at.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LINE connection failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/disconnect/{user_id}")
async def disconnect_line_account(
    user_id: str,
    service: LineService = Depends(get_line_service)
):
    """ユーザーのLINEアカウント連携解除"""
    try:
        success = await service.disconnect_user_from_line(user_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail="LINE connection not found or already disconnected"
            )

        return {"status": "success", "message": "LINE account disconnected"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LINE disconnection failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/status/{user_id}")
async def get_line_connection_status(
    user_id: str,
    service: LineService = Depends(get_line_service)
):
    """ユーザーのLINE連携状態を取得"""
    try:
        status = await service.get_user_connection_status(user_id)
        return status

    except Exception as e:
        logger.error(f"Failed to get LINE connection status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/send-progress-notification")
async def send_progress_notification(
    request_data: Dict[str, Any],
    service: LineService = Depends(get_line_service)
):
    """研究進捗通知を送信（管理者またはシステム用）"""
    try:
        user_id = request_data.get("user_id")
        research_title = request_data.get("research_title")
        progress_percentage = request_data.get("progress_percentage")
        completed_tasks = request_data.get("completed_tasks")
        total_tasks = request_data.get("total_tasks")
        next_task = request_data.get("next_task")

        if not all([user_id, research_title, progress_percentage is not None,
                   completed_tasks is not None, total_tasks is not None]):
            raise HTTPException(
                status_code=400,
                detail="Required fields: user_id, research_title, progress_percentage, completed_tasks, total_tasks"
            )

        success = await service.send_progress_notification(
            user_id=user_id,
            research_title=research_title,
            progress_percentage=progress_percentage,
            completed_tasks=completed_tasks,
            total_tasks=total_tasks,
            next_task=next_task
        )

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to send progress notification"
            )

        return {"status": "success", "message": "Progress notification sent"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send progress notification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/send-daily-reminder")
async def send_daily_reminder(
    request_data: Dict[str, str],
    service: LineService = Depends(get_line_service)
):
    """日次リマインダーを送信（管理者またはシステム用）"""
    try:
        user_id = request_data.get("user_id")
        research_title = request_data.get("research_title")

        if not user_id or not research_title:
            raise HTTPException(
                status_code=400,
                detail="user_id and research_title are required"
            )

        success = await service.send_daily_reminder(user_id, research_title)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to send daily reminder"
            )

        return {"status": "success", "message": "Daily reminder sent"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send daily reminder: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def line_health_check(service: LineService = Depends(get_line_service)):
    """LINE API の設定状態をチェック"""
    try:
        is_configured = service.line_client.is_configured()

        return {
            "status": "ok" if is_configured else "warning",
            "line_api_configured": is_configured,
            "message": "LINE API is ready" if is_configured else "LINE API credentials not configured"
        }

    except Exception as e:
        logger.error(f"LINE health check failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
