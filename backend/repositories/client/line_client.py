import os
import logging
from typing import List, Optional, Dict, Any
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage,
    QuickReply, QuickReplyButton, MessageAction, PostbackAction
)
import httpx
from datetime import datetime

from models.line_models import (
    LineUserProfile, LineMessage, LineTextMessage, LineFlexMessage,
    ResearchProgressNotification
)

logger = logging.getLogger(__name__)


class LineApiClient:
    """LINE Messaging API クライアント"""

    def __init__(self):
        self.channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        self.channel_secret = os.getenv('LINE_CHANNEL_SECRET')

        if not self.channel_access_token or not self.channel_secret:
            logger.warning("LINE API credentials not found. LINE functionality will be disabled.")
            self.line_bot_api = None
            self.handler = None
        else:
            self.line_bot_api = LineBotApi(self.channel_access_token)
            self.handler = WebhookHandler(self.channel_secret)

    def is_configured(self) -> bool:
        """LINE APIが設定されているかチェック"""
        return self.line_bot_api is not None and self.handler is not None

    async def get_user_profile(self, user_id: str) -> Optional[LineUserProfile]:
        """LINEユーザープロフィールを取得"""
        if not self.is_configured():
            logger.warning("LINE API not configured")
            return None

        try:
            profile = self.line_bot_api.get_profile(user_id)
            return LineUserProfile(
                user_id=user_id,
                display_name=profile.display_name,
                picture_url=profile.picture_url,
                status_message=profile.status_message
            )
        except LineBotApiError as e:
            logger.error(f"Failed to get LINE user profile: {e}")
            return None

    async def send_text_message(self, user_id: str, text: str) -> bool:
        """テキストメッセージを送信"""
        if not self.is_configured():
            logger.warning("LINE API not configured")
            return False

        try:
            message = TextSendMessage(text=text)
            self.line_bot_api.push_message(user_id, message)
            logger.info(f"Text message sent to {user_id}: {text[:50]}...")
            return True
        except LineBotApiError as e:
            logger.error(f"Failed to send text message: {e}")
            return False

    async def send_flex_message(self, user_id: str, alt_text: str, contents: Dict[str, Any]) -> bool:
        """Flexメッセージを送信"""
        if not self.is_configured():
            logger.warning("LINE API not configured")
            return False

        try:
            flex_message = FlexSendMessage(alt_text=alt_text, contents=contents)
            self.line_bot_api.push_message(user_id, flex_message)
            logger.info(f"Flex message sent to {user_id}: {alt_text}")
            return True
        except LineBotApiError as e:
            logger.error(f"Failed to send flex message: {e}")
            return False

    async def reply_message(self, reply_token: str, messages: List[Any]) -> bool:
        """メッセージを返信"""
        if not self.is_configured():
            logger.warning("LINE API not configured")
            return False

        try:
            self.line_bot_api.reply_message(reply_token, messages)
            logger.info(f"Reply message sent with token: {reply_token}")
            return True
        except LineBotApiError as e:
            logger.error(f"Failed to reply message: {e}")
            return False

    async def send_research_progress_notification(self, notification: ResearchProgressNotification) -> bool:
        """研究進捗通知を送信"""
        if not self.is_configured():
            logger.warning("LINE API not configured")
            return False

        # 進捗バーのFlexメッセージを作成
        progress_flex = self._create_progress_flex_message(notification)

        try:
            # まず励ましメッセージを送信
            await self.send_text_message(notification.line_user_id, notification.encouragement_message)

            # 進捗カードを送信
            await self.send_flex_message(
                notification.line_user_id,
                f"研究進捗: {notification.research_title}",
                progress_flex
            )

            # 次のタスクがある場合は送信
            if notification.next_task:
                next_task_message = f"📋 次のタスク:\n{notification.next_task}"
                await self.send_text_message(notification.line_user_id, next_task_message)

            return True
        except Exception as e:
            logger.error(f"Failed to send progress notification: {e}")
            return False

    def _create_progress_flex_message(self, notification: ResearchProgressNotification) -> Dict[str, Any]:
        """進捗表示用のFlexメッセージを作成"""
        progress_percentage = notification.progress_percentage
        completed_tasks = notification.completed_tasks
        total_tasks = notification.total_tasks

        # 進捗バーの表示を計算
        progress_bar_filled = "■" * (progress_percentage // 10)
        progress_bar_empty = "□" * (10 - (progress_percentage // 10))

        return {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "🔬 研究進捗レポート",
                        "weight": "bold",
                        "color": "#4CAF50",
                        "size": "lg"
                    }
                ],
                "backgroundColor": "#E8F5E8",
                "paddingAll": "md"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": notification.research_title,
                        "weight": "bold",
                        "size": "md",
                        "wrap": True,
                        "color": "#2E7D32"
                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"進捗: {progress_percentage}%",
                                "size": "sm",
                                "color": "#666666"
                            },
                            {
                                "type": "text",
                                "text": f"{progress_bar_filled}{progress_bar_empty}",
                                "size": "lg",
                                "weight": "bold",
                                "color": "#4CAF50",
                                "margin": "xs"
                            },
                            {
                                "type": "text",
                                "text": f"完了: {completed_tasks}/{total_tasks} タスク",
                                "size": "sm",
                                "color": "#666666",
                                "margin": "xs"
                            }
                        ]
                    }
                ],
                "paddingAll": "md"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "研究を続ける",
                            "uri": "https://your-app-domain.com/dashboard"
                        },
                        "style": "primary",
                        "color": "#4CAF50"
                    }
                ],
                "paddingAll": "md"
            }
        }

    def create_quick_reply_buttons(self, options: List[Dict[str, str]]) -> QuickReply:
        """クイックリプライボタンを作成"""
        items = []
        for option in options[:13]:  # LINEクイックリプライは最大13個
            action = MessageAction(label=option["label"], text=option["text"])
            items.append(QuickReplyButton(action=action))

        return QuickReply(items=items)

    def verify_signature(self, body: str, signature: str) -> bool:
        """署名を検証"""
        if not self.is_configured():
            return False

        try:
            self.handler.handle(body, signature)
            return True
        except InvalidSignatureError:
            logger.warning("Invalid LINE signature")
            return False
