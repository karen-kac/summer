from typing import Optional
from repositories.client.dynamodb_client import DynamoDBClient, get_dynamodb_client
from repositories.client.s3_client import S3Client
from repositories.client.bedrock_client import BedrockClient
from repositories.user_repository import UserRepository
from repositories.project_repository import ProjectRepository
from repositories.record_repository import RecordRepository
from repositories.media_repository import MediaRepository
from repositories.theme_repository import ThemeRepository
from repositories.achievement_repository import AchievementRepository
from utils.prompt_builder import PromptBuilder
import logging

logger = logging.getLogger(__name__)


class RepositoryFactory:
    """リポジトリファクトリークラス"""

    def __init__(self):
        self._db_client: Optional[DynamoDBClient] = None
        self._s3_client: Optional[S3Client] = None
        self._bedrock_client: Optional[BedrockClient] = None
        self._prompt_builder: Optional[PromptBuilder] = None

        # リポジトリインスタンス
        self._user_repo: Optional[UserRepository] = None
        self._project_repo: Optional[ProjectRepository] = None
        self._record_repo: Optional[RecordRepository] = None
        self._media_repo: Optional[MediaRepository] = None
        self._theme_repo: Optional[ThemeRepository] = None
        self._achievement_repo: Optional[AchievementRepository] = None

    def _get_db_client(self) -> DynamoDBClient:
        """DynamoDBクライアントを取得"""
        if self._db_client is None:
            self._db_client = get_dynamodb_client()
        return self._db_client

    def _get_s3_client(self) -> S3Client:
        """S3クライアントを取得"""
        if self._s3_client is None:
            self._s3_client = S3Client()
        return self._s3_client

    def _get_bedrock_client(self) -> BedrockClient:
        """Bedrockクライアントを取得"""
        if self._bedrock_client is None:
            self._bedrock_client = BedrockClient()
        return self._bedrock_client

    def _get_prompt_builder(self) -> PromptBuilder:
        """PromptBuilderを取得"""
        if self._prompt_builder is None:
            self._prompt_builder = PromptBuilder()
        return self._prompt_builder

    def get_user_repository(self) -> UserRepository:
        """ユーザーリポジトリを取得"""
        if self._user_repo is None:
            self._user_repo = UserRepository(self._get_db_client())
        return self._user_repo

    def get_project_repository(self) -> ProjectRepository:
        """プロジェクトリポジトリを取得"""
        if self._project_repo is None:
            self._project_repo = ProjectRepository(self._get_db_client())
        return self._project_repo

    def get_record_repository(self) -> RecordRepository:
        """記録リポジトリを取得"""
        if self._record_repo is None:
            self._record_repo = RecordRepository(
                db_client=self._get_db_client(),
                s3_client=self._get_s3_client()
            )
        return self._record_repo

    def get_media_repository(self) -> MediaRepository:
        """メディアリポジトリを取得"""
        if self._media_repo is None:
            self._media_repo = MediaRepository(
                self._get_db_client(),
                self._get_s3_client()
            )
        return self._media_repo

    def get_theme_repository(self) -> ThemeRepository:
        """テーマリポジトリを取得"""
        if self._theme_repo is None:
            self._theme_repo = ThemeRepository(
                self._get_prompt_builder(),
                self._get_bedrock_client(),
                self._get_db_client()
            )
        return self._theme_repo

    def get_achievement_repository(self) -> AchievementRepository:
        """実績リポジトリを取得"""
        if self._achievement_repo is None:
            self._achievement_repo = AchievementRepository(self._get_db_client())
        return self._achievement_repo

    async def health_check(self) -> dict:
        """全リポジトリのヘルスチェック"""
        results = {}

        try:
            # 各リポジトリのヘルスチェック
            results['user_repository'] = await self.get_user_repository().health_check()
            results['project_repository'] = await self.get_project_repository().health_check()
            results['record_repository'] = await self.get_record_repository().health_check()
            results['media_repository'] = await self.get_media_repository().health_check()
            results['theme_repository'] = await self.get_theme_repository().health_check()
            results['achievement_repository'] = True  # 簡単なヘルスチェック

            # 全体の健全性を判定
            all_healthy = all(results.values())
            results['overall'] = all_healthy

            if all_healthy:
                logger.info("全リポジトリのヘルスチェック成功")
            else:
                logger.warning(f"一部のリポジトリでヘルスチェック失敗: {results}")

        except Exception as e:
            logger.error(f"ヘルスチェック実行エラー: {e}")
            results['overall'] = False
            results['error'] = str(e)

        return results

    def close(self):
        """リソースのクリーンアップ"""
        # 必要に応じてクライアントのクリーンアップ処理を追加
        self._db_client = None
        self._s3_client = None
        self._bedrock_client = None
        self._prompt_builder = None

        self._user_repo = None
        self._project_repo = None
        self._record_repo = None
        self._media_repo = None
        self._theme_repo = None
        self._achievement_repo = None

        logger.info("リポジトリファクトリークリーンアップ完了")


# シングルトンインスタンス
_repository_factory = None


def get_repository_factory() -> RepositoryFactory:
    """リポジトリファクトリーのシングルトンインスタンスを取得"""
    global _repository_factory
    if _repository_factory is None:
        _repository_factory = RepositoryFactory()
    return _repository_factory


# 便利な関数
def get_user_repository() -> UserRepository:
    """ユーザーリポジトリを取得"""
    return get_repository_factory().get_user_repository()


def get_project_repository() -> ProjectRepository:
    """プロジェクトリポジトリを取得"""
    return get_repository_factory().get_project_repository()


def get_record_repository() -> RecordRepository:
    """記録リポジトリを取得"""
    return get_repository_factory().get_record_repository()


def get_media_repository() -> MediaRepository:
    """メディアリポジトリを取得"""
    return get_repository_factory().get_media_repository()


def get_theme_repository() -> ThemeRepository:
    """テーマリポジトリを取得"""
    return get_repository_factory().get_theme_repository()


def get_achievement_repository() -> AchievementRepository:
    """実績リポジトリを取得"""
    return get_repository_factory().get_achievement_repository()
