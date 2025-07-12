from typing import Optional, List, Dict, Any
from datetime import datetime
from utils.prompt_builder import PromptBuilder
from repositories.client.bedrock_client import BedrockClient
from repositories.client.dynamodb_client import DynamoDBClient
from models.project import ResearchTheme, ResearchPlan, UserPlan
from models.user import UserProfile
from models.database import KeyBuilder
import logging

logger = logging.getLogger(__name__)


class ThemeRepository:
    def __init__(self, prompt_builder: PromptBuilder, bedrock_client: BedrockClient,
                 db_client: DynamoDBClient = None):
        self.builder = prompt_builder
        self.bedrock_client = bedrock_client
        self.db = db_client

    async def generate_themes(self, profile) -> list:
        """AIを使用してテーマを生成"""
        prompt = self.builder.build_suggest_themes_prompt(profile)
        themes_data = await self.bedrock_client.post_prompt(prompt)
        return themes_data

    async def generate_research_plan(self, theme: ResearchTheme, user_profile: UserProfile = None) -> dict:
        """
        保存されたテーマを基に研究計画を生成する
        """
        prompt = self.builder.build_research_plan_prompt(theme, user_profile)
        plan_data = await self.bedrock_client.post_prompt(prompt)
        return plan_data

    async def save_theme(self, theme_data: Dict[str, Any]) -> Optional[ResearchTheme]:
        """
        研究テーマをDynamoDBに保存

        Args:
            theme_data: テーマデータ

        Returns:
            ResearchTheme: 保存されたテーマ
        """
        if not self.db:
            logger.error("DynamoDBクライアントが設定されていません")
            return None

        try:
            theme_id = KeyBuilder.generate_uuid()

            theme = ResearchTheme.create(
                theme_id=theme_id,
                **theme_data
            )

            success = await self.db.put_item(theme.to_dynamo_item())

            if success:
                logger.info(f"研究テーマ保存成功: {theme_id}")
                return theme
            else:
                logger.error(f"研究テーマ保存失敗: {theme_id}")
                return None

        except Exception as e:
            logger.error(f"研究テーマ保存エラー: {e}")
            return None

    async def get_theme_by_id(self, theme_id: str) -> Optional[ResearchTheme]:
        """
        テーマIDで研究テーマを取得

        Args:
            theme_id: テーマID

        Returns:
            ResearchTheme: 研究テーマ
        """
        if not self.db:
            logger.error("DynamoDBクライアントが設定されていません")
            return None

        try:
            item = await self.db.get_item(
                pk=KeyBuilder.theme_pk(theme_id),
                sk="METADATA"
            )

            if item:
                return ResearchTheme(**item)
            else:
                return None

        except Exception as e:
            logger.error(f"研究テーマ取得エラー: {theme_id}, {e}")
            return None

    async def get_themes_by_genre(self, genre: str, limit: int = 20) -> List[ResearchTheme]:
        """
        ジャンルで研究テーマ一覧を取得

        Args:
            genre: ジャンル
            limit: 取得制限数

        Returns:
            List[ResearchTheme]: 研究テーマ一覧
        """
        if not self.db:
            logger.error("DynamoDBクライアントが設定されていません")
            return []

        try:
            # GSI1を使用してジャンル別にクエリ
            result = await self.db.query_gsi(
                gsi_name="1",
                pk=f"GENRE#{genre}",
                sk_prefix="THEME#",
                limit=limit
            )

            # テーマオブジェクトに変換
            themes = []
            for item in result['items']:
                try:
                    theme = ResearchTheme(**item)
                    themes.append(theme)
                except Exception as e:
                    logger.warning(f"テーマデータの変換でエラー: {e}")
                    continue

            return themes

        except Exception as e:
            logger.error(f"ジャンル別テーマ取得エラー: {genre}, {e}")
            return []

    async def search_themes(self, keywords: List[str], limit: int = 20) -> List[ResearchTheme]:
        """
        キーワードで研究テーマを検索

        Args:
            keywords: 検索キーワード
            limit: 取得制限数

        Returns:
            List[ResearchTheme]: 検索結果
        """
        if not self.db:
            logger.error("DynamoDBクライアントが設定されていません")
            return []

        try:
            # DynamoDBのスキャンを使用してキーワード検索
            # 実際の実装では、ElasticSearchやOpenSearchを使用することを推奨
            logger.warning("キーワード検索は現在基本的な実装です。本番環境では検索エンジンの使用を推奨します。")

            # 全テーマを取得してキーワードでフィルタリング（非効率）
            # 本番環境では改善が必要
            return []

        except Exception as e:
            logger.error(f"テーマ検索エラー: {keywords}, {e}")
            return []

    async def save_research_plan(self, plan_data: Dict[str, Any]) -> Optional[ResearchPlan]:
        """
        研究計画をDynamoDBに保存

        Args:
            plan_data: 計画データ

        Returns:
            ResearchPlan: 保存された計画
        """
        if not self.db:
            logger.error("DynamoDBクライアントが設定されていません")
            return None

        try:
            plan_id = KeyBuilder.generate_uuid()

            plan = ResearchPlan.create(
                plan_id=plan_id,
                **plan_data
            )

            success = await self.db.put_item(plan.to_dynamo_item())

            if success:
                logger.info(f"研究計画保存成功: {plan_id}")
                return plan
            else:
                logger.error(f"研究計画保存失敗: {plan_id}")
                return None

        except Exception as e:
            logger.error(f"研究計画保存エラー: {e}")
            return None

    async def get_plan_by_id(self, plan_id: str) -> Optional[ResearchPlan]:
        """
        計画IDで研究計画を取得

        Args:
            plan_id: 計画ID

        Returns:
            ResearchPlan: 研究計画
        """
        if not self.db:
            logger.error("DynamoDBクライアントが設定されていません")
            return None

        try:
            item = await self.db.get_item(
                pk=KeyBuilder.plan_pk(plan_id),
                sk="METADATA"
            )

            if item:
                return ResearchPlan(**item)
            else:
                return None

        except Exception as e:
            logger.error(f"研究計画取得エラー: {plan_id}, {e}")
            return None

    async def create_user_plan(self, user_id: str, plan_id: str,
                             modifications: Dict[str, Any] = None) -> Optional[UserPlan]:
        """
        ユーザー専用の研究計画を作成

        Args:
            user_id: ユーザーID
            plan_id: 元の計画ID
            modifications: カスタマイズ内容

        Returns:
            UserPlan: ユーザー専用計画
        """
        if not self.db:
            logger.error("DynamoDBクライアントが設定されていません")
            return None

        try:
            user_plan = UserPlan.create(
                user_id=user_id,
                plan_id=plan_id,
                modifications=modifications or {}
            )

            success = await self.db.put_item(user_plan.to_dynamo_item())

            if success:
                logger.info(f"ユーザー計画作成成功: {user_id} - {plan_id}")
                return user_plan
            else:
                logger.error(f"ユーザー計画作成失敗: {user_id} - {plan_id}")
                return None

        except Exception as e:
            logger.error(f"ユーザー計画作成エラー: {user_id} - {plan_id}, {e}")
            return None

    async def get_user_plans(self, user_id: str) -> List[UserPlan]:
        """
        ユーザーの研究計画一覧を取得

        Args:
            user_id: ユーザーID

        Returns:
            List[UserPlan]: ユーザー計画一覧
        """
        if not self.db:
            logger.error("DynamoDBクライアントが設定されていません")
            return []

        try:
            result = await self.db.query_items(
                pk=KeyBuilder.user_pk(user_id),
                sk_prefix="PLAN#"
            )

            # ユーザー計画オブジェクトに変換
            user_plans = []
            for item in result['items']:
                try:
                    user_plan = UserPlan(**item)
                    user_plans.append(user_plan)
                except Exception as e:
                    logger.warning(f"ユーザー計画データの変換でエラー: {e}")
                    continue

            return user_plans

        except Exception as e:
            logger.error(f"ユーザー計画一覧取得エラー: {user_id}, {e}")
            return []

    async def update_theme_usage(self, theme_id: str) -> bool:
        """
        テーマの使用回数を更新

        Args:
            theme_id: テーマID

        Returns:
            bool: 更新成功時True
        """
        if not self.db:
            logger.error("DynamoDBクライアントが設定されていません")
            return False

        try:
            success = await self.db.update_item(
                pk=KeyBuilder.theme_pk(theme_id),
                sk="METADATA",
                update_expression="SET usageCount = usageCount + :inc",
                expression_attribute_values={':inc': 1}
            )

            if success:
                logger.info(f"テーマ使用回数更新成功: {theme_id}")
            else:
                logger.error(f"テーマ使用回数更新失敗: {theme_id}")

            return success

        except Exception as e:
            logger.error(f"テーマ使用回数更新エラー: {theme_id}, {e}")
            return False

    async def rate_theme(self, theme_id: str, rating: float) -> bool:
        """
        テーマの評価を更新

        Args:
            theme_id: テーマID
            rating: 評価値（1.0-5.0）

        Returns:
            bool: 更新成功時True
        """
        if not self.db:
            logger.error("DynamoDBクライアントが設定されていません")
            return False

        try:
            # 現在の評価を取得
            current_theme = await self.get_theme_by_id(theme_id)
            if not current_theme:
                logger.error(f"テーマが見つかりません: {theme_id}")
                return False

            # 新しい評価を計算
            current_rating = current_theme.rating
            current_count = current_theme.ratingCount

            new_count = current_count + 1
            new_rating = ((current_rating * current_count) + rating) / new_count

            success = await self.db.update_item(
                pk=KeyBuilder.theme_pk(theme_id),
                sk="METADATA",
                update_expression="SET rating = :rating, ratingCount = :count",
                expression_attribute_values={
                    ':rating': new_rating,
                    ':count': new_count
                }
            )

            if success:
                logger.info(f"テーマ評価更新成功: {theme_id} - {rating}")
            else:
                logger.error(f"テーマ評価更新失敗: {theme_id} - {rating}")

            return success

        except Exception as e:
            logger.error(f"テーマ評価更新エラー: {theme_id}, {e}")
            return False

    async def health_check(self) -> bool:
        """
        リポジトリのヘルスチェック

        Returns:
            bool: 正常時True
        """
        if self.db:
            return await self.db.health_check()
        return True  # DynamoDBクライアントが設定されていない場合はTrue
