import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from repositories.client.line_client import LineApiClient
from repositories.line_repository import LineRepository, line_repository
from models.line_models import (
    LineUserConnection, LineUserProfile, LineWebhookEvent,
    ResearchProgressNotification, LineTextMessage
)

logger = logging.getLogger(__name__)


class LineService:
    """LINE連携とメッセージング機能を管理するサービス"""

    def __init__(self, line_client: LineApiClient = None, repository: LineRepository = None):
        self.line_client = line_client or LineApiClient()
        self.repository = repository or line_repository

    async def connect_user_to_line(
        self,
        user_id: str,
        line_user_id: str
    ) -> Optional[LineUserConnection]:
        """ユーザーをLINEアカウントに連携"""
        try:
            # LINEプロフィール情報を取得
            profile = await self.line_client.get_user_profile(line_user_id)

            display_name = profile.display_name if profile else None
            picture_url = profile.picture_url if profile else None

            # 連携を作成
            connection = await self.repository.create_connection(
                user_id=user_id,
                line_user_id=line_user_id,
                display_name=display_name,
                picture_url=picture_url
            )

            # 連携完了メッセージを送信
            welcome_message = self._create_welcome_message(display_name)
            await self.line_client.send_text_message(line_user_id, welcome_message)

            logger.info(f"User connected to LINE: user_id={user_id}, line_user_id={line_user_id}")
            return connection

        except Exception as e:
            logger.error(f"Failed to connect user to LINE: {e}")
            return None

    async def disconnect_user_from_line(self, user_id: str) -> bool:
        """ユーザーのLINE連携を解除"""
        try:
            connection = await self.repository.get_connection_by_user_id(user_id)
            if not connection:
                logger.warning(f"No LINE connection found for user: {user_id}")
                return False

            # お別れメッセージを送信
            farewell_message = "🙋‍♀️ 夏休み自由研究AIとの連携を解除しました。\nまたいつでもお待ちしています！"
            await self.line_client.send_text_message(connection.line_user_id, farewell_message)

            # 連携を無効化
            success = await self.repository.deactivate_connection(connection.id)

            if success:
                logger.info(f"User disconnected from LINE: user_id={user_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to disconnect user from LINE: {e}")
            return False

    async def send_progress_notification(
        self,
        user_id: str,
        research_title: str,
        progress_percentage: int,
        completed_tasks: int,
        total_tasks: int,
        next_task: Optional[str] = None
    ) -> bool:
        """研究進捗通知を送信"""
        try:
            connection = await self.repository.get_connection_by_user_id(user_id)
            if not connection:
                logger.warning(f"No LINE connection found for user: {user_id}")
                return False

            # 励ましメッセージを生成
            encouragement = self._generate_encouragement_message(progress_percentage, completed_tasks)

            notification = ResearchProgressNotification(
                user_id=user_id,
                line_user_id=connection.line_user_id,
                research_title=research_title,
                progress_percentage=progress_percentage,
                completed_tasks=completed_tasks,
                total_tasks=total_tasks,
                next_task=next_task,
                encouragement_message=encouragement
            )

            success = await self.line_client.send_research_progress_notification(notification)

            if success:
                # 最終インタラクション時刻を更新
                await self.repository.update_last_interaction(connection.id)
                logger.info(f"Progress notification sent to user: {user_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to send progress notification: {e}")
            return False

    async def send_daily_reminder(self, user_id: str, research_title: str) -> bool:
        """日次リマインダーを送信"""
        try:
            connection = await self.repository.get_connection_by_user_id(user_id)
            if not connection:
                return False

            reminder_message = f"""🌅 おはよう！今日も研究を頑張ろう！

📚 今日の研究テーマ：{research_title}

今日は何を観察したり、実験したりする予定ですか？
小さな発見でも大きな一歩です！

アプリで記録をつけるのも忘れずに！📝✨"""

            success = await self.line_client.send_text_message(
                connection.line_user_id,
                reminder_message
            )

            if success:
                await self.repository.update_last_interaction(connection.id)
                logger.info(f"Daily reminder sent to user: {user_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to send daily reminder: {e}")
            return False

    async def handle_webhook_message(self, event: LineWebhookEvent) -> bool:
        """Webhookメッセージを処理"""
        try:
            if event.type != "message" or not event.message:
                return True  # メッセージイベント以外は無視

            line_user_id = event.source.get("userId")
            if not line_user_id:
                return True

            # ユーザー連携を確認
            connection = await self.repository.get_connection_by_line_user_id(line_user_id)
            if not connection:
                # 未連携ユーザーに案内メッセージを送信
                guidance_message = """👋 こんにちは！

夏休み自由研究AIをご利用いただき、ありがとうございます。

LINEでの通知を受け取るには、まずアプリでアカウント連携を行ってください。

🔗 アプリ: https://your-app-domain.com
📱 設定 > LINE連携 から設定できます！"""

                if event.reply_token:
                    await self.line_client.reply_message(
                        event.reply_token,
                        [LineTextMessage(text=guidance_message)]
                    )
                return True

            # メッセージ内容に応じて応答
            message_text = event.message.get("text", "").lower()
            reply_message = self._generate_reply_message(message_text, connection)

            if reply_message and event.reply_token:
                await self.line_client.reply_message(
                    event.reply_token,
                    [LineTextMessage(text=reply_message)]
                )

            # 最終インタラクション時刻を更新
            await self.repository.update_last_interaction(connection.id)

            return True

        except Exception as e:
            logger.error(f"Failed to handle webhook message: {e}")
            return False

    async def get_user_connection_status(self, user_id: str) -> Dict[str, Any]:
        """ユーザーのLINE連携状態を取得"""
        try:
            connection = await self.repository.get_connection_by_user_id(user_id)

            if not connection:
                return {
                    "is_connected": False,
                    "connection": None
                }

            return {
                "is_connected": True,
                "connection": {
                    "id": connection.id,
                    "line_user_id": connection.line_user_id,
                    "display_name": connection.display_name,
                    "picture_url": connection.picture_url,
                    "connected_at": connection.connected_at.isoformat(),
                    "last_interaction_at": connection.last_interaction_at.isoformat() if connection.last_interaction_at else None
                }
            }

        except Exception as e:
            logger.error(f"Failed to get connection status: {e}")
            return {"is_connected": False, "connection": None}

    def _create_welcome_message(self, display_name: Optional[str]) -> str:
        """連携完了時のウェルカムメッセージを生成"""
        name = display_name or "あなた"
        return f"""🎉 {name}さん、連携完了です！

夏休み自由研究AIとLINEが繋がりました！

これからは研究の進捗や、頑張った時の応援メッセージをLINEでお届けします📱✨

一緒に素晴らしい自由研究を完成させましょう！🔬🌟"""

    def _generate_encouragement_message(self, progress_percentage: int, completed_tasks: int) -> str:
        """進捗に応じた励ましメッセージを生成"""
        if progress_percentage <= 25:
            return f"🌱 研究スタート！{completed_tasks}個のタスクを完了しました。最初の一歩を踏み出して素晴らしいです！"
        elif progress_percentage <= 50:
            return f"🌿 順調に進んでいますね！{completed_tasks}個のタスクを完了。この調子で頑張りましょう！"
        elif progress_percentage <= 75:
            return f"🌳 もう半分以上完了！{completed_tasks}個のタスクを達成。ゴールが見えてきました！"
        else:
            return f"🏆 素晴らしい！{completed_tasks}個のタスクを完了して、もうすぐ完成ですね！最後まで頑張って！"

    def _generate_reply_message(self, message_text: str, connection: LineUserConnection) -> Optional[str]:
        """受信メッセージに応じた返信メッセージを生成"""
        name = connection.display_name or "あなた"

        if any(word in message_text for word in ["こんにちは", "おはよう", "こんばんは"]):
            return f"😊 {name}さん、こんにちは！今日も研究頑張っていますか？"

        elif any(word in message_text for word in ["進捗", "しんちょく", "どこまで"]):
            return "📊 進捗はアプリのダッシュボードで確認できます！\n何か困ったことがあったら教えてくださいね。"

        elif any(word in message_text for word in ["ありがと", "感謝", "たすかった"]):
            return f"💝 {name}さん、こちらこそありがとうございます！\n研究を楽しんでもらえて嬉しいです！"

        elif any(word in message_text for word in ["難しい", "むずかしい", "わからない"]):
            return "🤔 研究で困ったことがありますね！\n\nアプリの「使い方」ページや、お家の人に相談してみてください。\n一歩ずつ進めていけば大丈夫ですよ！"

        elif any(word in message_text for word in ["完成", "終わった", "できた"]):
            return f"🎉 {name}さん、研究完成おめでとうございます！\n\n素晴らしい研究になったと思います。\n夏休みの良い思い出になりましたね！"

        else:
            return f"📚 {name}さん、メッセージありがとうございます！\n\n研究に関して何かサポートが必要でしたら、アプリをチェックしてみてくださいね！"


# グローバルインスタンス
line_service = LineService()
