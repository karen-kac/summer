"""
研究アプリケーション用リポジトリパッケージ

このパッケージには以下のリポジトリが含まれています：
- UserRepository: ユーザー情報管理
- ProjectRepository: プロジェクト管理
- RecordRepository: 記録データ管理
- MediaRepository: メディアファイル管理
- ThemeRepository: テーマ・計画管理
"""

from .repository_factory import (
    get_repository_factory,
    get_user_repository,
    get_project_repository,
    get_record_repository,
    get_media_repository,
    get_theme_repository
)

# 直接クラスをエクスポート
from .theme_repository import ThemeRepository
from .client.bedrock_client import BedrockClient
from .client.dynamodb_client import DynamoDBClient
from .client.s3_client import S3Client

__all__ = [
    'get_repository_factory',
    'get_user_repository',
    'get_project_repository',
    'get_record_repository',
    'get_media_repository',
    'get_theme_repository',
    'ThemeRepository',
    'BedrockClient',
    'DynamoDBClient',
    'S3Client'
]
