from typing import Optional, List
from datetime import datetime
from repositories.client.dynamodb_client import DynamoDBClient
from models.user import (
    UserProfile, UserSettings, UserStats, LineConnection,
    CreateUserRequest, UpdateUserProfileRequest, UpdateUserSettingsRequest,
    UserResponse
)
from models.database import KeyBuilder
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    """ユーザーデータリポジトリ"""

    def __init__(self, db_client: DynamoDBClient):
        self.db = db_client

    async def create_user(self, user_id: str, request: CreateUserRequest) -> Optional[UserResponse]:
        """
        新しいユーザーを作成

        Args:
            user_id: ユーザーID
            request: ユーザー作成リクエスト

        Returns:
            UserResponse: 作成されたユーザー情報
        """
        try:
            # ユーザープロフィールを作成
            profile = UserProfile.create(
                user_id=user_id,
                email=request.email,
                displayName=request.displayName,
                grade=request.grade,
                interests=request.interests,
                personality=request.personality,
                strengths=request.strengths,
                preferredDuration=request.preferredDuration,
                parentEmail=request.parentEmail
            )

            # デフォルト設定を作成
            settings = UserSettings.create(user_id)

            # 初期統計を作成
            stats = UserStats.create(user_id)

            # 一括で保存
            success = await self.db.batch_write_items([
                profile.to_dynamo_item(),
                settings.to_dynamo_item(),
                stats.to_dynamo_item()
            ])

            if success:
                logger.info(f"ユーザー作成成功: {user_id}")
                return UserResponse(
                    profile=profile,
                    settings=settings,
                    stats=stats
                )
            else:
                logger.error(f"ユーザー作成失敗: {user_id}")
                return None

        except Exception as e:
            logger.error(f"ユーザー作成エラー: {user_id}, {e}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """
        ユーザーIDでユーザー情報を取得

        Args:
            user_id: ユーザーID

        Returns:
            UserResponse: ユーザー情報
        """
        try:
            # プロフィール、設定、統計、LINE連携を並行取得
            keys = [
                {'PK': KeyBuilder.user_pk(user_id), 'SK': 'PROFILE'},
                {'PK': KeyBuilder.user_pk(user_id), 'SK': 'SETTINGS'},
                {'PK': KeyBuilder.user_pk(user_id), 'SK': 'STATS'},
                {'PK': KeyBuilder.user_pk(user_id), 'SK': 'LINE_CONNECTION'}
            ]

            items = await self.db.batch_get_items(keys)

            if not items:
                return None

            # 取得したデータを分類
            profile_data = None
            settings_data = None
            stats_data = None
            line_connection_data = None

            for item in items:
                if item.get('SK') == 'PROFILE':
                    profile_data = item
                elif item.get('SK') == 'SETTINGS':
                    settings_data = item
                elif item.get('SK') == 'STATS':
                    stats_data = item
                elif item.get('SK') == 'LINE_CONNECTION':
                    line_connection_data = item

            if not profile_data:
                logger.warning(f"ユーザープロフィールが見つかりません: {user_id}")
                return None

            # オブジェクトに変換
            profile = UserProfile(**profile_data)
            settings = UserSettings(**settings_data) if settings_data else None
            stats = UserStats(**stats_data) if stats_data else None
            line_connection = LineConnection(**line_connection_data) if line_connection_data else None

            return UserResponse(
                profile=profile,
                settings=settings,
                stats=stats,
                lineConnection=line_connection
            )

        except Exception as e:
            logger.error(f"ユーザー取得エラー: {user_id}, {e}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """
        メールアドレスでユーザー情報を取得

        Args:
            email: メールアドレス

        Returns:
            UserResponse: ユーザー情報
        """
        try:
            # 一時的にスキャンを使用してemailでユーザーを検索
            # 本番環境では、emailをGSIに追加することを推奨

            logger.warning("email検索は現在スキャンを使用します。本番環境では最適化が必要です。")

            # DynamoDBのスキャン機能を使用してemailで検索
            response = await self.db.scan_items(
                filter_expression="email = :email AND SK = :sk",
                expression_attribute_values={
                    ':email': email,
                    ':sk': 'PROFILE'
                }
            )

            if not response['items']:
                logger.info(f"ユーザーが見つかりません: {email}")
                return None

            # 最初に見つかったユーザーを使用
            profile_data = response['items'][0]
            user_id = profile_data['userId']

            # 完全なユーザー情報を取得
            return await self.get_user_by_id(user_id)

        except Exception as e:
            logger.error(f"ユーザー取得エラー（email）: {email}, {e}")
            return None

    async def update_user_profile(self, user_id: str, request: UpdateUserProfileRequest) -> bool:
        """
        ユーザープロフィールを更新

        Args:
            user_id: ユーザーID
            request: 更新リクエスト

        Returns:
            bool: 更新成功時True
        """
        try:
            # 更新式の構築
            update_expression = "SET updatedAt = :updatedAt"
            expression_values = {':updatedAt': datetime.now()}

            # 更新フィールドを追加
            if request.displayName is not None:
                update_expression += ", displayName = :displayName"
                expression_values[':displayName'] = request.displayName

            if request.grade is not None:
                update_expression += ", grade = :grade"
                expression_values[':grade'] = request.grade

            if request.interests is not None:
                update_expression += ", interests = :interests"
                expression_values[':interests'] = request.interests

            if request.personality is not None:
                update_expression += ", personality = :personality"
                expression_values[':personality'] = request.personality

            if request.strengths is not None:
                update_expression += ", strengths = :strengths"
                expression_values[':strengths'] = request.strengths

            if request.preferredDuration is not None:
                update_expression += ", preferredDuration = :preferredDuration"
                expression_values[':preferredDuration'] = request.preferredDuration

            if request.parentEmail is not None:
                update_expression += ", parentEmail = :parentEmail"
                expression_values[':parentEmail'] = request.parentEmail

            if request.bio is not None:
                update_expression += ", bio = :bio"
                expression_values[':bio'] = request.bio

            success = await self.db.update_item(
                pk=KeyBuilder.user_pk(user_id),
                sk="PROFILE",
                update_expression=update_expression,
                expression_attribute_values=expression_values
            )

            if success:
                logger.info(f"ユーザープロフィール更新成功: {user_id}")
            else:
                logger.error(f"ユーザープロフィール更新失敗: {user_id}")

            return success

        except Exception as e:
            logger.error(f"ユーザープロフィール更新エラー: {user_id}, {e}")
            return False

    async def update_user_settings(self, user_id: str, request: UpdateUserSettingsRequest) -> bool:
        """
        ユーザー設定を更新

        Args:
            user_id: ユーザーID
            request: 設定更新リクエスト

        Returns:
            bool: 更新成功時True
        """
        try:
            update_expression = "SET updatedAt = :updatedAt"
            expression_values = {':updatedAt': datetime.now()}

            if request.notificationSettings is not None:
                update_expression += ", notificationSettings = :notificationSettings"
                expression_values[':notificationSettings'] = request.notificationSettings.model_dump()

            if request.privacySettings is not None:
                update_expression += ", privacySettings = :privacySettings"
                expression_values[':privacySettings'] = request.privacySettings.model_dump()

            if request.displaySettings is not None:
                update_expression += ", displaySettings = :displaySettings"
                expression_values[':displaySettings'] = request.displaySettings.model_dump()

            success = await self.db.update_item(
                pk=KeyBuilder.user_pk(user_id),
                sk="SETTINGS",
                update_expression=update_expression,
                expression_attribute_values=expression_values
            )

            if success:
                logger.info(f"ユーザー設定更新成功: {user_id}")
            else:
                logger.error(f"ユーザー設定更新失敗: {user_id}")

            return success

        except Exception as e:
            logger.error(f"ユーザー設定更新エラー: {user_id}, {e}")
            return False

    async def update_user_stats(self, user_id: str, **kwargs) -> bool:
        """
        ユーザー統計を更新

        Args:
            user_id: ユーザーID
            **kwargs: 更新する統計値

        Returns:
            bool: 更新成功時True
        """
        try:
            update_expression = "SET updatedAt = :updatedAt"
            expression_values = {':updatedAt': datetime.now()}

            # 統計値を更新
            for key, value in kwargs.items():
                if value is not None:
                    update_expression += f", {key} = :{key}"
                    expression_values[f":{key}"] = value

            success = await self.db.update_item(
                pk=KeyBuilder.user_pk(user_id),
                sk="STATS",
                update_expression=update_expression,
                expression_attribute_values=expression_values
            )

            if success:
                logger.info(f"ユーザー統計更新成功: {user_id}")
            else:
                logger.error(f"ユーザー統計更新失敗: {user_id}")

            return success

        except Exception as e:
            logger.error(f"ユーザー統計更新エラー: {user_id}, {e}")
            return False

    async def create_line_connection(self, user_id: str, line_user_id: str, **kwargs) -> bool:
        """
        LINE連携を作成

        Args:
            user_id: ユーザーID
            line_user_id: LINE ユーザーID
            **kwargs: 追加の連携情報

        Returns:
            bool: 作成成功時True
        """
        try:
            line_connection = LineConnection.create(
                user_id=user_id,
                line_user_id=line_user_id,
                **kwargs
            )

            success = await self.db.put_item(line_connection.to_dynamo_item())

            if success:
                logger.info(f"LINE連携作成成功: {user_id} - {line_user_id}")
            else:
                logger.error(f"LINE連携作成失敗: {user_id} - {line_user_id}")

            return success

        except Exception as e:
            logger.error(f"LINE連携作成エラー: {user_id} - {line_user_id}, {e}")
            return False

    async def delete_user(self, user_id: str) -> bool:
        """
        ユーザーを削除（論理削除）

        Args:
            user_id: ユーザーID

        Returns:
            bool: 削除成功時True
        """
        try:
            # 論理削除（isActiveをFalseに設定）
            success = await self.db.update_item(
                pk=KeyBuilder.user_pk(user_id),
                sk="PROFILE",
                update_expression="SET isActive = :isActive, updatedAt = :updatedAt",
                expression_attribute_values={
                    ':isActive': False,
                    ':updatedAt': datetime.now()
                }
            )

            if success:
                logger.info(f"ユーザー削除成功: {user_id}")
            else:
                logger.error(f"ユーザー削除失敗: {user_id}")

            return success

        except Exception as e:
            logger.error(f"ユーザー削除エラー: {user_id}, {e}")
            return False

    async def update_last_login(self, user_id: str) -> bool:
        """
        最終ログイン時刻を更新

        Args:
            user_id: ユーザーID

        Returns:
            bool: 更新成功時True
        """
        try:
            now = datetime.now()
            success = await self.db.update_item(
                pk=KeyBuilder.user_pk(user_id),
                sk="PROFILE",
                update_expression="SET lastLoginAt = :lastLoginAt, updatedAt = :updatedAt",
                expression_attribute_values={
                    ':lastLoginAt': now,
                    ':updatedAt': now
                }
            )

            if success:
                logger.info(f"最終ログイン時刻更新成功: {user_id}")

            return success

        except Exception as e:
            logger.error(f"最終ログイン時刻更新エラー: {user_id}, {e}")
            return False

    async def health_check(self) -> bool:
        """
        リポジトリのヘルスチェック

        Returns:
            bool: 正常時True
        """
        return await self.db.health_check()
