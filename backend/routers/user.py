from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import date
from repositories.repository_factory import get_repository_factory
from repositories.user_repository import UserRepository
from repositories.project_repository import ProjectRepository
from repositories.achievement_repository import AchievementRepository
from services.achievement_service import AchievementService
from models.user import CreateUserRequest, UserResponse
from models.project import ResearchProject, CreateProjectRequest
from models.database import KeyBuilder
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_user_repository() -> UserRepository:
    """ユーザーリポジトリを取得"""
    factory = get_repository_factory()
    return factory.get_user_repository()

def get_project_repository() -> ProjectRepository:
    """プロジェクトリポジトリを取得"""
    factory = get_repository_factory()
    return factory.get_project_repository()

def get_achievement_service() -> AchievementService:
    """実績サービスを取得"""
    factory = get_repository_factory()
    return AchievementService(
        achievement_repo=factory.get_achievement_repository(),
        user_repo=factory.get_user_repository(),
        project_repo=factory.get_project_repository(),
        record_repo=factory.get_record_repository()
    )

@router.post("/signup", response_model=UserResponse)
async def signup(
    request: CreateUserRequest,
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserResponse:
    """
    新規会員登録

    Args:
        request: ユーザー作成リクエスト
        user_repo: ユーザーリポジトリ

    Returns:
        UserResponse: 作成されたユーザー情報
    """
    try:
        # ユーザーIDを生成
        user_id = KeyBuilder.generate_uuid()

        # ユーザーを作成
        user_response = await user_repo.create_user(user_id, request)

        if not user_response:
            logger.error(f"ユーザー作成失敗: {request.email}")
            raise HTTPException(
                status_code=500,
                detail="ユーザー作成に失敗しました"
            )

        logger.info(f"新規会員登録成功: {request.email}")
        return user_response

    except Exception as e:
        logger.error(f"新規会員登録エラー: {request.email}, {e}")
        raise HTTPException(
            status_code=500,
            detail=f"新規会員登録中にエラーが発生しました: {str(e)}"
        )

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(
    request: LoginRequest,
    user_repo: UserRepository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """
    ログイン

    Args:
        request: ログインリクエスト
        user_repo: ユーザーリポジトリ

    Returns:
        Dict[str, Any]: ログイン結果
    """
    try:
        # TODO: パスワード認証の実装
        # 現在は簡単な実装

        # メールアドレスでユーザーを検索
        user_response = await user_repo.get_user_by_email(request.email)

        if not user_response:
            raise HTTPException(
                status_code=401,
                detail="メールアドレスまたはパスワードが間違っています"
            )

        # 最終ログイン時刻を更新
        await user_repo.update_last_login(user_response.profile.userId)

        # JWTトークンを生成（簡単な実装）
        # TODO: 実際のJWT実装に置き換える
        token = f"token-{user_response.profile.userId}"

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user_response.model_dump()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ログインエラー: {request.email}, {e}")
        raise HTTPException(
            status_code=500,
            detail=f"ログイン中にエラーが発生しました: {str(e)}"
        )

@router.get("/profile/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: str,
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserResponse:
    """
    ユーザープロフィール取得

    Args:
        user_id: ユーザーID
        user_repo: ユーザーリポジトリ

    Returns:
        UserResponse: ユーザー情報
    """
    try:
        user_response = await user_repo.get_user_by_id(user_id)

        if not user_response:
            raise HTTPException(
                status_code=404,
                detail="ユーザーが見つかりません"
            )

        return user_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ユーザープロフィール取得エラー: {user_id}, {e}")
        raise HTTPException(
            status_code=500,
            detail=f"ユーザープロフィール取得中にエラーが発生しました: {str(e)}"
        )

# ダッシュボードデータのレスポンス型
class DashboardDataResponse(BaseModel):
    active_projects: List[Dict[str, Any]]
    past_projects: List[Dict[str, Any]]
    user_stats: Dict[str, Any]
    recent_achievements: List[Dict[str, Any]]

@router.get("/dashboard/{user_id}")
async def get_dashboard_data(
    user_id: str,
    user_repo: UserRepository = Depends(get_user_repository),
    project_repo: ProjectRepository = Depends(get_project_repository),
    achievement_service: AchievementService = Depends(get_achievement_service)
) -> DashboardDataResponse:
    """
    ダッシュボード用のユーザーデータを取得

    Args:
        user_id: ユーザーID
        user_repo: ユーザーリポジトリ
        project_repo: プロジェクトリポジトリ

    Returns:
        DashboardDataResponse: ダッシュボードデータ
    """
    try:
        # ユーザー情報を取得
        user_response = await user_repo.get_user_by_id(user_id)
        if not user_response:
            raise HTTPException(
                status_code=404,
                detail="ユーザーが見つかりません"
            )

        # アクティブなプロジェクトを取得
        active_projects_raw = await project_repo.get_active_projects_by_user(user_id)

        # フロントエンド用にフィールド名を変換
        active_projects = []
        for project in active_projects_raw:
            project_dict = project.model_dump()
            # PKからプロジェクトIDを抽出して id フィールドに設定
            pk = project_dict.get('PK', '')
            if pk.startswith('PROJECT#'):
                project_id = pk[8:]  # 'PROJECT#' を除去
                project_dict['id'] = project_id
            else:
                # フォールバック: projectId フィールドがある場合
                project_dict['id'] = project_dict.get('projectId', project_dict.get('PK', ''))

            # 不要なDynamoDBフィールドを除去
            for key in ['PK', 'SK', 'Type', 'GSI1PK', 'GSI1SK', 'GSI2PK', 'GSI2SK']:
                project_dict.pop(key, None)
            project_dict.pop('projectId', None)  # 古いprojectIdフィールドも削除

            active_projects.append(project_dict)

        # 完了したプロジェクトを取得
        completed_projects_response = await project_repo.get_projects_by_user(
            user_id=user_id,
            status="completed",
            limit=10
        )
        past_projects_raw = [p.project for p in completed_projects_response.projects]

        # フロントエンド用にフィールド名を変換
        past_projects = []
        for project in past_projects_raw:
            project_dict = project.model_dump()
            # PKからプロジェクトIDを抽出して id フィールドに設定
            pk = project_dict.get('PK', '')
            if pk.startswith('PROJECT#'):
                project_id = pk[8:]  # 'PROJECT#' を除去
                project_dict['id'] = project_id
            else:
                # フォールバック: projectId フィールドがある場合
                project_dict['id'] = project_dict.get('projectId', project_dict.get('PK', ''))

            # 不要なDynamoDBフィールドを除去
            for key in ['PK', 'SK', 'Type', 'GSI1PK', 'GSI1SK', 'GSI2PK', 'GSI2SK']:
                project_dict.pop(key, None)
            project_dict.pop('projectId', None)  # 古いprojectIdフィールドも削除

            past_projects.append(project_dict)

        # ユーザー統計を構築
        user_stats = {
            "totalPoints": user_response.stats.totalPoints if user_response.stats else 0,
            "level": user_response.stats.level if user_response.stats else 1,
            "completedProjects": user_response.stats.completedProjects if user_response.stats else 0,
            "currentStreak": user_response.stats.currentStreak if user_response.stats else 0,
            "totalRecords": user_response.stats.totalRecords if user_response.stats else 0,
            "totalPhotos": user_response.stats.totalPhotos if user_response.stats else 0,
            "totalExperiments": user_response.stats.totalExperiments if user_response.stats else 0,
        }

        # 最近の実績を取得
        recent_achievements_response = await achievement_service.get_recent_achievements(user_id, limit=5)
        recent_achievements = []
        for achievement in recent_achievements_response:
            achievement_dict = {
                "id": achievement.achievementId,
                "name": achievement.name,
                "description": achievement.description,
                "icon": achievement.icon,
                "category": achievement.category,
                "points": achievement.points,
                "earnedAt": achievement.earnedAt.isoformat() if achievement.earnedAt else None
            }
            recent_achievements.append(achievement_dict)

        return DashboardDataResponse(
            active_projects=active_projects,
            past_projects=past_projects,
            user_stats=user_stats,
            recent_achievements=recent_achievements
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ダッシュボードデータ取得エラー: {user_id}, {e}")
        raise HTTPException(
            status_code=500,
            detail=f"ダッシュボードデータ取得中にエラーが発生しました: {str(e)}"
        )

# フロントエンド用のプロジェクト作成リクエスト型
class CreateProjectFromThemeRequest(BaseModel):
    theme_id: str
    title: str
    description: str
    genre: str
    estimated_days: int
    materials: List[str]
    steps: List[str]
    target_end_date: str  # ISO date string

# プロジェクト進捗更新用のリクエスト型
class UpdateProjectProgressRequest(BaseModel):
    current_step_index: int
    progress_percentage: float
    status: str = "in_progress"

@router.post("/projects")
async def create_project_from_theme(
    user_id: str,
    request: CreateProjectFromThemeRequest,
    project_repo: ProjectRepository = Depends(get_project_repository),
    achievement_service: AchievementService = Depends(get_achievement_service)
) -> Dict[str, Any]:
    """
    テーマからプロジェクトを作成

    Args:
        user_id: ユーザーID
        request: プロジェクト作成リクエスト
        project_repo: プロジェクトリポジトリ

    Returns:
        Dict[str, Any]: 作成されたプロジェクト情報
    """
    try:
        # 既存のアクティブなプロジェクトを取得
        active_projects = await project_repo.get_active_projects_by_user(user_id)

        # 既存のアクティブなプロジェクトがある場合は、それらを過去の研究として保存
        if active_projects:
            from models.project import UpdateProjectRequest

            for active_project in active_projects:
                # アクティブなプロジェクトを完了状態に変更
                update_request = UpdateProjectRequest(
                    status="completed",
                    progressPercentage=100.0 if active_project.progressPercentage >= 90 else active_project.progressPercentage
                )

                success = await project_repo.update_project(active_project.projectId, update_request)
                if success:
                    logger.info(f"既存のアクティブなプロジェクトを過去の研究として保存: {active_project.projectId}")
                else:
                    logger.warning(f"既存のアクティブなプロジェクトの状態更新に失敗: {active_project.projectId}")

        # フロントエンドからのリクエストをバックエンドの形式に変換
        project_request = CreateProjectRequest(
            themeId=request.theme_id,
            planId=None,
            title=request.title,
            description=request.description,
            startDate=date.today(),
            targetEndDate=date.fromisoformat(request.target_end_date),
            customGoals=[],
            genre=request.genre,
            difficulty="medium",  # デフォルト
            estimatedDays=request.estimated_days
        )

        # プロジェクトを作成
        project_response = await project_repo.create_project(user_id, project_request)

        if not project_response:
            raise HTTPException(
                status_code=500,
                detail="プロジェクト作成に失敗しました"
            )

        logger.info(f"プロジェクト作成成功: {user_id}")

        # 実績チェック - テーマ選択完了
        achievement_result = await achievement_service.check_and_grant_achievements(
            user_id=user_id,
            event_type="theme_selected",
            event_data={
                "theme_id": request.theme_id,
                "project_id": project_response.project.projectId,
                "theme_title": request.title
            }
        )

        # フロントエンド用にフィールド名を変換
        project_dict = project_response.project.model_dump()
        # PKからプロジェクトIDを抽出して id フィールドに設定
        pk = project_dict.get('PK', '')
        if pk.startswith('PROJECT#'):
            project_id = pk[8:]  # 'PROJECT#' を除去
            project_dict['id'] = project_id
        else:
            # フォールバック: projectId フィールドがある場合
            project_dict['id'] = project_dict.get('projectId', project_dict.get('PK', ''))

        # 不要なDynamoDBフィールドを除去
        for key in ['PK', 'SK', 'Type', 'GSI1PK', 'GSI1SK', 'GSI2PK', 'GSI2SK']:
            project_dict.pop(key, None)
        project_dict.pop('projectId', None)  # 古いprojectIdフィールドも削除

        return {
            "success": True,
            "project": project_dict,
            "message": "プロジェクトが正常に作成されました",
            "previous_projects_saved": len(active_projects) if active_projects else 0,
            "new_achievements": [ach.model_dump() for ach in achievement_result.newAchievements] if achievement_result.newAchievements else [],
            "points_earned": achievement_result.totalNewPoints
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"プロジェクト作成エラー: {user_id}, {e}")
        raise HTTPException(
            status_code=500,
            detail=f"プロジェクト作成中にエラーが発生しました: {str(e)}"
        )

@router.put("/projects/{project_id}/progress")
async def update_project_progress(
    project_id: str,
    request: UpdateProjectProgressRequest,
    project_repo: ProjectRepository = Depends(get_project_repository),
    achievement_service: AchievementService = Depends(get_achievement_service)
) -> Dict[str, Any]:
    """
    プロジェクトの進捗を更新

    Args:
        project_id: プロジェクトID
        request: 進捗更新リクエスト
        project_repo: プロジェクトリポジトリ

    Returns:
        Dict[str, Any]: 更新結果
    """
    try:
        # バックエンドの UpdateProjectRequest 形式に変換
        from models.project import UpdateProjectRequest

        update_request = UpdateProjectRequest(
            currentStepIndex=request.current_step_index,
            progressPercentage=request.progress_percentage,
            status=request.status
        )

        # プロジェクトを更新
        success = await project_repo.update_project(project_id, update_request)

        if not success:
            raise HTTPException(
                status_code=500,
                detail="プロジェクト進捗更新に失敗しました"
            )

        # プロジェクト情報を取得してユーザーIDを取得
        project = await project_repo.get_project_by_id(project_id)
        if project:
            # 実績チェック - ステップ完了
            achievement_result = await achievement_service.check_and_grant_achievements(
                user_id=project.project.userId,
                event_type="step_completed",
                event_data={
                    "project_id": project_id,
                    "step_index": request.current_step_index,
                    "progress_percentage": request.progress_percentage,
                    "project_title": project.project.title
                }
            )
        else:
            achievement_result = None

        logger.info(f"プロジェクト進捗更新成功: {project_id} - ステップ{request.current_step_index} ({request.progress_percentage}%)")
        return {
            "success": True,
            "message": "プロジェクト進捗が正常に更新されました",
            "current_step_index": request.current_step_index,
            "progress_percentage": request.progress_percentage,
            "new_achievements": [ach.model_dump() for ach in achievement_result.newAchievements] if achievement_result and achievement_result.newAchievements else [],
            "points_earned": achievement_result.totalNewPoints if achievement_result else 0
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"プロジェクト進捗更新エラー: {project_id}, {e}")
        raise HTTPException(
            status_code=500,
            detail=f"プロジェクト進捗更新中にエラーが発生しました: {str(e)}"
        )
