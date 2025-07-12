from typing import List, Optional
from datetime import datetime
import logging
from repositories.client.dynamodb_client import DynamoDBClient
from models.achievement import Achievement, UserAchievement, AchievementResponse
from models.database import KeyBuilder

logger = logging.getLogger(__name__)


class AchievementRepository:
    """実績リポジトリ"""

    def __init__(self, client: DynamoDBClient):
        self.client = client

    async def create_achievement(self, achievement: Achievement) -> bool:
        """実績定義を作成"""
        try:
            success = await self.client.put_item(achievement.to_dynamo_item())
            if success:
                logger.info(f"実績定義作成成功: {achievement.achievementId}")
            else:
                logger.error(f"実績定義作成失敗: {achievement.achievementId}")
            return success
        except Exception as e:
            logger.error(f"実績定義作成エラー: {achievement.achievementId}, {e}")
            return False

    async def get_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """実績定義を取得"""
        try:
            pk = KeyBuilder.achievement_pk(achievement_id)
            sk = "METADATA"

            item = await self.client.get_item(pk, sk)
            if item:
                return Achievement(**item)
            return None
        except Exception as e:
            logger.error(f"実績定義取得エラー: {achievement_id}, {e}")
            return None

    async def get_all_achievements(self) -> List[Achievement]:
        """全ての実績定義を取得"""
        try:
            response = await self.client.scan_items(
                filter_expression="#type = :type",
                expression_attribute_names={"#type": "Type"},
                expression_attribute_values={":type": "Achievement"}
            )
            achievements = []
            for item in response.get('items', []):
                achievements.append(Achievement(**item))

            logger.info(f"実績定義取得成功: {len(achievements)}件")
            return achievements
        except Exception as e:
            logger.error(f"実績定義一覧取得エラー: {e}")
            return []

    async def grant_achievement(self, user_id: str, achievement_id: str, earned_data: dict = None) -> bool:
        """ユーザーに実績を付与"""
        try:
            # 既に獲得済みかチェック
            existing = await self.get_user_achievement(user_id, achievement_id)
            if existing:
                logger.info(f"実績は既に獲得済み: {user_id} - {achievement_id}")
                return False

            # 新しいユーザー実績を作成
            user_achievement = UserAchievement.create(
                user_id=user_id,
                achievement_id=achievement_id,
                earnedData=earned_data or {}
            )

            success = await self.client.put_item(user_achievement.to_dynamo_item())
            if success:
                logger.info(f"実績付与成功: {user_id} - {achievement_id}")
            else:
                logger.error(f"実績付与失敗: {user_id} - {achievement_id}")
            return success
        except Exception as e:
            logger.error(f"実績付与エラー: {user_id} - {achievement_id}, {e}")
            return False

    async def get_user_achievement(self, user_id: str, achievement_id: str) -> Optional[UserAchievement]:
        """ユーザーの特定実績を取得"""
        try:
            pk = KeyBuilder.user_pk(user_id)
            sk = KeyBuilder.achievement_sk(achievement_id)

            item = await self.client.get_item(pk, sk)
            if item:
                return UserAchievement(**item)
            return None
        except Exception as e:
            logger.error(f"ユーザー実績取得エラー: {user_id} - {achievement_id}, {e}")
            return None

    async def get_user_achievements(self, user_id: str, limit: int = 50) -> List[AchievementResponse]:
        """ユーザーの獲得実績一覧を取得"""
        try:
            pk = KeyBuilder.user_pk(user_id)

            # ユーザーの実績を取得
            response = await self.client.query_items(pk, "ACHIEVEMENT#", limit=limit)
            user_achievements = []
            for item in response.get('items', []):
                user_achievements.append(UserAchievement(**item))

            # 実績詳細情報を取得
            achievement_responses = []
            for user_ach in user_achievements:
                achievement = await self.get_achievement(user_ach.achievementId)
                if achievement:
                    achievement_responses.append(AchievementResponse(
                        achievementId=achievement.achievementId,
                        name=achievement.name,
                        description=achievement.description,
                        icon=achievement.icon,
                        category=achievement.category,
                        points=achievement.points,
                        earnedAt=user_ach.earnedAt,
                        earnedData=user_ach.earnedData
                    ))

            # 獲得日時の降順でソート
            achievement_responses.sort(key=lambda x: x.earnedAt or datetime.min, reverse=True)

            logger.info(f"ユーザー実績取得成功: {user_id} - {len(achievement_responses)}件")
            return achievement_responses
        except Exception as e:
            logger.error(f"ユーザー実績一覧取得エラー: {user_id}, {e}")
            return []

    async def get_recent_user_achievements(self, user_id: str, limit: int = 10) -> List[AchievementResponse]:
        """ユーザーの最近の実績を取得"""
        try:
            all_achievements = await self.get_user_achievements(user_id, limit=limit)
            return all_achievements[:limit]
        except Exception as e:
            logger.error(f"最近の実績取得エラー: {user_id}, {e}")
            return []

    async def has_user_achievement(self, user_id: str, achievement_id: str) -> bool:
        """ユーザーが特定の実績を獲得しているかチェック"""
        try:
            user_achievement = await self.get_user_achievement(user_id, achievement_id)
            return user_achievement is not None
        except Exception as e:
            logger.error(f"実績獲得チェックエラー: {user_id} - {achievement_id}, {e}")
            return False

    async def count_user_achievements(self, user_id: str) -> int:
        """ユーザーの実績獲得数をカウント"""
        try:
            pk = KeyBuilder.user_pk(user_id)
            response = await self.client.query_items(pk, "ACHIEVEMENT#")
            return response.get('count', 0)
        except Exception as e:
            logger.error(f"実績カウントエラー: {user_id}, {e}")
            return 0
