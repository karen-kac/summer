from typing import Optional, List, Dict, Any
from datetime import datetime, date
from repositories.client.dynamodb_client import DynamoDBClient
from models.project import (
    ResearchProject, ProjectSettings, Schedule, CalendarConfig,
    ResearchTheme, ResearchPlan, SavedTheme, UserPlan,
    CreateProjectRequest, UpdateProjectRequest, ProjectResponse, ProjectListResponse
)
from models.database import KeyBuilder
import logging

logger = logging.getLogger(__name__)


class ProjectRepository:
    """プロジェクトデータリポジトリ"""

    def __init__(self, db_client: DynamoDBClient):
        self.db = db_client

    async def create_project(self, user_id: str, request: CreateProjectRequest) -> Optional[ProjectResponse]:
        """
        新しいプロジェクトを作成

        Args:
            user_id: ユーザーID
            request: プロジェクト作成リクエスト

        Returns:
            ProjectResponse: 作成されたプロジェクト情報
        """
        try:
            project_id = KeyBuilder.generate_uuid()

            # 推定日数を計算
            estimated_days = (request.targetEndDate - request.startDate).days

            # estimatedDaysが指定されていない場合は計算値を使用
            final_estimated_days = request.estimatedDays if request.estimatedDays is not None else estimated_days

            # プロジェクトを作成
            project = ResearchProject.create(
                project_id=project_id,
                user_id=user_id,
                themeId=request.themeId,
                planId=request.planId,
                title=request.title,
                description=request.description,
                startDate=request.startDate,
                targetEndDate=request.targetEndDate,
                customGoals=request.customGoals,
                status="planning",
                genre=request.genre,
                difficulty=request.difficulty,
                estimatedDays=final_estimated_days
            )

            # プロジェクト設定を作成
            settings = ProjectSettings.create(project_id)

            # 一括で保存
            success = await self.db.batch_write_items([
                project.to_dynamo_item(),
                settings.to_dynamo_item()
            ])

            if success:
                logger.info(f"プロジェクト作成成功: {project_id}")
                return ProjectResponse(
                    project=project,
                    settings=settings
                )
            else:
                logger.error(f"プロジェクト作成失敗: {project_id}")
                return None

        except Exception as e:
            logger.error(f"プロジェクト作成エラー: {e}")
            return None

    async def get_project_by_id(self, project_id: str) -> Optional[ProjectResponse]:
        """
        プロジェクトIDでプロジェクト情報を取得

        Args:
            project_id: プロジェクトID

        Returns:
            ProjectResponse: プロジェクト情報
        """
        try:
            # プロジェクトとプロジェクト設定を並行取得
            keys = [
                {'PK': KeyBuilder.project_pk(project_id), 'SK': 'METADATA'},
                {'PK': KeyBuilder.project_pk(project_id), 'SK': 'SETTINGS'}
            ]

            items = await self.db.batch_get_items(keys)

            if not items:
                return None

            # 取得したデータを分類
            project_data = None
            settings_data = None

            for item in items:
                if item.get('SK') == 'METADATA':
                    project_data = item
                elif item.get('SK') == 'SETTINGS':
                    settings_data = item

            if not project_data:
                logger.warning(f"プロジェクトが見つかりません: {project_id}")
                return None

            # オブジェクトに変換
            project = ResearchProject(**project_data)
            settings = ProjectSettings(**settings_data) if settings_data else None

            return ProjectResponse(
                project=project,
                settings=settings
            )

        except Exception as e:
            logger.error(f"プロジェクト取得エラー: {project_id}, {e}")
            return None

    async def get_projects_by_user(self, user_id: str, status: str = None,
                                 limit: int = 20, last_evaluated_key: Dict[str, Any] = None) -> ProjectListResponse:
        """
        ユーザーのプロジェクト一覧を取得

        Args:
            user_id: ユーザーID
            status: プロジェクト状態でのフィルタリング
            limit: 取得制限数
            last_evaluated_key: ページネーション用のキー

        Returns:
            ProjectListResponse: プロジェクト一覧
        """
        try:
            # GSI1を使用してユーザーのプロジェクト一覧を取得
            if status:
                # 状態でフィルタリング
                result = await self.db.query_gsi(
                    gsi_name="1",
                    pk=KeyBuilder.user_pk(user_id),
                    sk_prefix="PROJECT#",
                    filter_expression="attribute_exists(#status) AND #status = :status",
                    expression_attribute_values={':status': status},
                    limit=limit,
                    last_evaluated_key=last_evaluated_key
                )
            else:
                # 全プロジェクト取得
                result = await self.db.query_gsi(
                    gsi_name="1",
                    pk=KeyBuilder.user_pk(user_id),
                    sk_prefix="PROJECT#",
                    limit=limit,
                    last_evaluated_key=last_evaluated_key
                )

            # プロジェクトオブジェクトに変換
            projects = []
            for item in result['items']:
                try:
                    project = ResearchProject(**item)
                    projects.append(ProjectResponse(project=project))
                except Exception as e:
                    logger.warning(f"プロジェクトデータの変換でエラー: {e}")
                    continue

            return ProjectListResponse(
                projects=projects,
                total=result['count'],
                hasMore=result['last_evaluated_key'] is not None
            )

        except Exception as e:
            logger.error(f"プロジェクト一覧取得エラー: {user_id}, {e}")
            return ProjectListResponse(projects=[], total=0, hasMore=False)

    async def update_project(self, project_id: str, request: UpdateProjectRequest) -> bool:
        """
        プロジェクトを更新

        Args:
            project_id: プロジェクトID
            request: 更新リクエスト

        Returns:
            bool: 更新成功時True
        """
        try:
            # 更新式の構築
            update_expression = "SET updatedAt = :updatedAt"
            expression_values = {':updatedAt': datetime.now()}
            expression_names = {}

            # 更新フィールドを追加
            if request.title is not None:
                update_expression += ", title = :title"
                expression_values[':title'] = request.title

            if request.description is not None:
                update_expression += ", description = :description"
                expression_values[':description'] = request.description

            if request.status is not None:
                update_expression += ", #status = :status"
                expression_values[':status'] = request.status
                expression_names['#status'] = 'status'

            if request.targetEndDate is not None:
                update_expression += ", targetEndDate = :targetEndDate"
                expression_values[':targetEndDate'] = request.targetEndDate

            if request.currentStepIndex is not None:
                update_expression += ", currentStepIndex = :currentStepIndex"
                expression_values[':currentStepIndex'] = request.currentStepIndex

            if request.progressPercentage is not None:
                update_expression += ", progressPercentage = :progressPercentage"
                expression_values[':progressPercentage'] = request.progressPercentage

            if request.customGoals is not None:
                update_expression += ", customGoals = :customGoals"
                expression_values[':customGoals'] = request.customGoals

            if request.achievements is not None:
                update_expression += ", achievements = :achievements"
                expression_values[':achievements'] = request.achievements

            if request.tags is not None:
                update_expression += ", tags = :tags"
                expression_values[':tags'] = request.tags

            # 完了時は完了日を設定
            if request.status == "completed":
                update_expression += ", actualEndDate = :actualEndDate"
                expression_values[':actualEndDate'] = date.today()

            success = await self.db.update_item(
                pk=KeyBuilder.project_pk(project_id),
                sk="METADATA",
                update_expression=update_expression,
                expression_attribute_values=expression_values,
                expression_attribute_names=expression_names if expression_names else None
            )

            if success:
                logger.info(f"プロジェクト更新成功: {project_id}")
            else:
                logger.error(f"プロジェクト更新失敗: {project_id}")

            return success

        except Exception as e:
            logger.error(f"プロジェクト更新エラー: {project_id}, {e}")
            return False

    async def delete_project(self, project_id: str) -> bool:
        """
        プロジェクトを削除

        Args:
            project_id: プロジェクトID

        Returns:
            bool: 削除成功時True
        """
        try:
            # プロジェクトとプロジェクト設定を削除
            delete_keys = [
                {'PK': KeyBuilder.project_pk(project_id), 'SK': 'METADATA'},
                {'PK': KeyBuilder.project_pk(project_id), 'SK': 'SETTINGS'}
            ]

            success = await self.db.batch_write_items([], delete_keys)

            if success:
                logger.info(f"プロジェクト削除成功: {project_id}")
            else:
                logger.error(f"プロジェクト削除失敗: {project_id}")

            return success

        except Exception as e:
            logger.error(f"プロジェクト削除エラー: {project_id}, {e}")
            return False

    async def get_active_projects_by_user(self, user_id: str) -> List[ResearchProject]:
        """
        ユーザーのアクティブなプロジェクト一覧を取得

        Args:
            user_id: ユーザーID

        Returns:
            List[ResearchProject]: アクティブなプロジェクト一覧
        """
        try:
            # GSI1を使用してユーザーのアクティブなプロジェクトを取得
            result = await self.db.query_gsi(
                gsi_name="1",
                pk=KeyBuilder.user_pk(user_id),
                sk_prefix="PROJECT#",
                filter_expression="attribute_exists(#status) AND #status IN (:planning, :in_progress)",
                expression_attribute_values={
                    ':planning': 'planning',
                    ':in_progress': 'in_progress'
                }
            )

            # プロジェクトオブジェクトに変換
            projects = []
            for item in result['items']:
                try:
                    project = ResearchProject(**item)
                    projects.append(project)
                except Exception as e:
                    logger.warning(f"プロジェクトデータの変換でエラー: {e}")
                    continue

            return projects

        except Exception as e:
            logger.error(f"アクティブプロジェクト取得エラー: {user_id}, {e}")
            return []

    async def save_theme(self, user_id: str, theme_id: str, custom_materials: List[str] = None,
                        custom_steps: List[str] = None, notes: str = None) -> bool:
        """
        テーマを保存

        Args:
            user_id: ユーザーID
            theme_id: テーマID
            custom_materials: カスタマイズした材料
            custom_steps: カスタマイズした手順
            notes: メモ

        Returns:
            bool: 保存成功時True
        """
        try:
            saved_theme = SavedTheme.create(
                user_id=user_id,
                theme_id=theme_id,
                customMaterials=custom_materials or [],
                customSteps=custom_steps or [],
                notes=notes
            )

            success = await self.db.put_item(saved_theme.to_dynamo_item())

            if success:
                logger.info(f"テーマ保存成功: {user_id} - {theme_id}")
            else:
                logger.error(f"テーマ保存失敗: {user_id} - {theme_id}")

            return success

        except Exception as e:
            logger.error(f"テーマ保存エラー: {user_id} - {theme_id}, {e}")
            return False

    async def get_saved_themes(self, user_id: str) -> List[SavedTheme]:
        """
        ユーザーの保存済みテーマを取得

        Args:
            user_id: ユーザーID

        Returns:
            List[SavedTheme]: 保存済みテーマ一覧
        """
        try:
            result = await self.db.query_items(
                pk=KeyBuilder.user_pk(user_id),
                sk_prefix="THEME#"
            )

            # 保存テーマオブジェクトに変換
            saved_themes = []
            for item in result['items']:
                try:
                    saved_theme = SavedTheme(**item)
                    saved_themes.append(saved_theme)
                except Exception as e:
                    logger.warning(f"保存テーマデータの変換でエラー: {e}")
                    continue

            return saved_themes

        except Exception as e:
            logger.error(f"保存済みテーマ取得エラー: {user_id}, {e}")
            return []

    async def create_schedule(self, user_id: str, schedule_date: date, events: List[Dict[str, Any]]) -> bool:
        """
        スケジュールを作成

        Args:
            user_id: ユーザーID
            schedule_date: スケジュール日付
            events: イベント一覧

        Returns:
            bool: 作成成功時True
        """
        try:
            schedule = Schedule.create(
                user_id=user_id,
                schedule_date=schedule_date,
                events=events,
                totalTasks=len(events)
            )

            success = await self.db.put_item(schedule.to_dynamo_item())

            if success:
                logger.info(f"スケジュール作成成功: {user_id} - {schedule_date}")
            else:
                logger.error(f"スケジュール作成失敗: {user_id} - {schedule_date}")

            return success

        except Exception as e:
            logger.error(f"スケジュール作成エラー: {user_id} - {schedule_date}, {e}")
            return False

    async def get_schedule(self, user_id: str, schedule_date: date) -> Optional[Schedule]:
        """
        スケジュールを取得

        Args:
            user_id: ユーザーID
            schedule_date: スケジュール日付

        Returns:
            Schedule: スケジュール情報
        """
        try:
            date_str = schedule_date.strftime("%Y-%m-%d")
            item = await self.db.get_item(
                pk=KeyBuilder.user_pk(user_id),
                sk=KeyBuilder.schedule_sk(date_str)
            )

            if item:
                return Schedule(**item)
            else:
                return None

        except Exception as e:
            logger.error(f"スケジュール取得エラー: {user_id} - {schedule_date}, {e}")
            return None

    async def update_calendar_config(self, user_id: str, config: Dict[str, Any]) -> bool:
        """
        カレンダー設定を更新

        Args:
            user_id: ユーザーID
            config: 設定データ

        Returns:
            bool: 更新成功時True
        """
        try:
            # 更新式の構築
            update_expression = "SET updatedAt = :updatedAt"
            expression_values = {':updatedAt': datetime.now()}

            # 設定フィールドを追加
            for key, value in config.items():
                if value is not None:
                    update_expression += f", {key} = :{key}"
                    expression_values[f":{key}"] = value

            success = await self.db.update_item(
                pk=KeyBuilder.user_pk(user_id),
                sk="CALENDAR_CONFIG",
                update_expression=update_expression,
                expression_attribute_values=expression_values
            )

            if success:
                logger.info(f"カレンダー設定更新成功: {user_id}")
            else:
                logger.error(f"カレンダー設定更新失敗: {user_id}")

            return success

        except Exception as e:
            logger.error(f"カレンダー設定更新エラー: {user_id}, {e}")
            return False

    async def get_calendar_config(self, user_id: str) -> Optional[CalendarConfig]:
        """
        カレンダー設定を取得

        Args:
            user_id: ユーザーID

        Returns:
            CalendarConfig: カレンダー設定
        """
        try:
            item = await self.db.get_item(
                pk=KeyBuilder.user_pk(user_id),
                sk="CALENDAR_CONFIG"
            )

            if item:
                return CalendarConfig(**item)
            else:
                # デフォルト設定を作成
                default_config = CalendarConfig.create(user_id)
                await self.db.put_item(default_config.to_dynamo_item())
                return default_config

        except Exception as e:
            logger.error(f"カレンダー設定取得エラー: {user_id}, {e}")
            return None

    async def health_check(self) -> bool:
        """
        リポジトリのヘルスチェック

        Returns:
            bool: 正常時True
        """
        return await self.db.health_check()
