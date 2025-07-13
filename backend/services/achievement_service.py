from typing import List, Dict, Any
import logging
from repositories.achievement_repository import AchievementRepository
from repositories.user_repository import UserRepository
from repositories.project_repository import ProjectRepository
from repositories.record_repository import RecordRepository
from models.achievement import AchievementCheckResult, AchievementResponse
from models.user import UserStats

logger = logging.getLogger(__name__)


class AchievementService:
    """実績サービス"""

    def __init__(
        self,
        achievement_repo: AchievementRepository,
        user_repo: UserRepository,
        project_repo: ProjectRepository,
        record_repo: RecordRepository
    ):
        self.achievement_repo = achievement_repo
        self.user_repo = user_repo
        self.project_repo = project_repo
        self.record_repo = record_repo

    async def check_and_grant_achievements(
        self,
        user_id: str,
        event_type: str,
        event_data: Dict[str, Any] = None
    ) -> AchievementCheckResult:
        """
        イベントに基づいて実績をチェックし、該当する実績を授与

        Args:
            user_id: ユーザーID
            event_type: イベントタイプ ("theme_selected", "step_completed", "record_created", "photo_uploaded")
            event_data: イベントデータ

        Returns:
            AchievementCheckResult: チェック結果
        """
        try:
            logger.info(f"🎯 実績チェック開始: user_id={user_id}, event_type={event_type}, event_data={event_data}")

            event_data = event_data or {}
            new_achievements = []
            total_new_points = 0

            # ユーザー統計を取得
            user_response = await self.user_repo.get_user_by_id(user_id)
            if not user_response:
                logger.warning(f"ユーザーが見つかりません: {user_id}")
                return AchievementCheckResult()

            user_stats = user_response.stats
            logger.info(f"📊 ユーザー統計: totalRecords={user_stats.totalRecords if user_stats else 0}, totalPhotos={user_stats.totalPhotos if user_stats else 0}")

            # イベントタイプに応じて実績をチェック
            if event_type == "theme_selected":
                new_achievements.extend(await self._check_theme_achievements(user_id, user_stats, event_data))
            elif event_type == "step_completed":
                new_achievements.extend(await self._check_step_achievements(user_id, user_stats, event_data))
            elif event_type == "record_created":
                new_achievements.extend(await self._check_record_achievements(user_id, user_stats, event_data))
            elif event_type == "photo_uploaded":
                new_achievements.extend(await self._check_photo_achievements(user_id, user_stats, event_data))

            logger.info(f"🔍 実績チェック結果: {len(new_achievements)}件の新しい実績が見つかりました")

            # 実績を授与
            for achievement_response in new_achievements:
                success = await self.achievement_repo.grant_achievement(
                    user_id=user_id,
                    achievement_id=achievement_response.achievementId,
                    earned_data=event_data
                )
                if success:
                    total_new_points += achievement_response.points
                    logger.info(f"実績授与成功: {user_id} - {achievement_response.name}")
                else:
                    logger.warning(f"実績授与失敗: {user_id} - {achievement_response.name}")

            # ユーザー統計を更新
            if total_new_points > 0:
                await self._update_user_stats(user_id, total_new_points)

            result = AchievementCheckResult(
                newAchievements=new_achievements,
                totalNewPoints=total_new_points
            )
            logger.info(f"✅ 実績チェック完了: {len(new_achievements)}件授与, {total_new_points}ポイント獲得")
            return result

        except Exception as e:
            logger.error(f"実績チェックエラー: {user_id} - {event_type}, {e}")
            return AchievementCheckResult()

    async def _check_theme_achievements(
        self,
        user_id: str,
        user_stats: UserStats,
        event_data: Dict[str, Any]
    ) -> List[AchievementResponse]:
        """テーマ選択関連の実績をチェック"""
        achievements = []

        # 初回テーマ選択の実績
        if not await self.achievement_repo.has_user_achievement(user_id, "first_theme"):
            achievements.append(AchievementResponse(
                achievementId="first_theme",
                name="はじめの一歩",
                description="初めて研究テーマを選択しました",
                icon="🌟",
                category="beginner",
                points=10
            ))

        return achievements

    async def _check_step_achievements(
        self,
        user_id: str,
        user_stats: UserStats,
        event_data: Dict[str, Any]
    ) -> List[AchievementResponse]:
        """ステップ完了関連の実績をチェック"""
        achievements = []

        # 初回ステップ完了の実績
        if not await self.achievement_repo.has_user_achievement(user_id, "first_step"):
            achievements.append(AchievementResponse(
                achievementId="first_step",
                name="研究開始",
                description="初めて研究ステップを完了しました",
                icon="🔬",
                category="beginner",
                points=10
            ))

        # 連続ステップ完了の実績
        completed_projects = user_stats.completedProjects if user_stats else 0
        if completed_projects >= 1 and not await self.achievement_repo.has_user_achievement(user_id, "first_project"):
            achievements.append(AchievementResponse(
                achievementId="first_project",
                name="研究完了者",
                description="初めて研究プロジェクトを完了しました",
                icon="🏆",
                category="completion",
                points=50
            ))

        return achievements

    async def _check_record_achievements(
        self,
        user_id: str,
        user_stats: UserStats,
        event_data: Dict[str, Any]
    ) -> List[AchievementResponse]:
        """記録作成関連の実績をチェック"""
        achievements = []

        # 初回記録作成の実績
        if not await self.achievement_repo.has_user_achievement(user_id, "first_record"):
            achievements.append(AchievementResponse(
                achievementId="first_record",
                name="記録の達人",
                description="初めて研究記録を作成しました",
                icon="📝",
                category="beginner",
                points=10
            ))

        # 記録数に応じた実績
        total_records = user_stats.totalRecords if user_stats else 0
        if total_records >= 10 and not await self.achievement_repo.has_user_achievement(user_id, "record_keeper"):
            achievements.append(AchievementResponse(
                achievementId="record_keeper",
                name="記録係",
                description="10件の記録を作成しました",
                icon="📚",
                category="progress",
                points=25
            ))

        if total_records >= 50 and not await self.achievement_repo.has_user_achievement(user_id, "record_master"):
            achievements.append(AchievementResponse(
                achievementId="record_master",
                name="記録マスター",
                description="50件の記録を作成しました",
                icon="📖",
                category="progress",
                points=100
            ))

        return achievements

    async def _check_photo_achievements(
        self,
        user_id: str,
        user_stats: UserStats,
        event_data: Dict[str, Any]
    ) -> List[AchievementResponse]:
        """写真アップロード関連の実績をチェック"""
        achievements = []

        # 初回写真アップロードの実績
        if not await self.achievement_repo.has_user_achievement(user_id, "first_photo"):
            achievements.append(AchievementResponse(
                achievementId="first_photo",
                name="写真家",
                description="初めて写真を記録しました",
                icon="📸",
                category="beginner",
                points=10
            ))

        # 写真数に応じた実績
        total_photos = user_stats.totalPhotos if user_stats else 0
        if total_photos >= 10 and not await self.achievement_repo.has_user_achievement(user_id, "photo_collector"):
            achievements.append(AchievementResponse(
                achievementId="photo_collector",
                name="写真コレクター",
                description="10枚の写真を記録しました",
                icon="🖼️",
                category="progress",
                points=25
            ))

        return achievements

    async def _update_user_stats(self, user_id: str, points_earned: int):
        """ユーザー統計を更新（ポイントとレベル）"""
        try:
            user_response = await self.user_repo.get_user_by_id(user_id)
            if not user_response or not user_response.stats:
                return

            # ポイントを加算
            new_total_points = user_response.stats.totalPoints + points_earned

            # レベルを計算（100ポイントごとにレベルアップ）
            new_level = max(1, (new_total_points // 100) + 1)

            # 統計を更新
            await self.user_repo.update_user_stats(
                user_id=user_id,
                totalPoints=new_total_points,
                level=new_level
            )

            logger.info(f"ユーザー統計更新: {user_id} - ポイント: +{points_earned}, レベル: {new_level}")

        except Exception as e:
            logger.error(f"ユーザー統計更新エラー: {user_id}, {e}")

    async def get_user_achievements(self, user_id: str) -> List[AchievementResponse]:
        """ユーザーの実績一覧を取得"""
        return await self.achievement_repo.get_user_achievements(user_id)

    async def get_recent_achievements(self, user_id: str, limit: int = 5) -> List[AchievementResponse]:
        """ユーザーの最近の実績を取得"""
        return await self.achievement_repo.get_recent_user_achievements(user_id, limit)
