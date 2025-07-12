from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import date
from repositories.repository_factory import get_repository_factory
from repositories.user_repository import UserRepository
from repositories.project_repository import ProjectRepository
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
    active_projects: List[ResearchProject]
    past_projects: List[ResearchProject]
    user_stats: Dict[str, Any]

@router.get("/dashboard/{user_id}")
async def get_dashboard_data(
    user_id: str,
    user_repo: UserRepository = Depends(get_user_repository),
    project_repo: ProjectRepository = Depends(get_project_repository)
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
        active_projects = await project_repo.get_active_projects_by_user(user_id)

        # 完了したプロジェクトを取得
        completed_projects_response = await project_repo.get_projects_by_user(
            user_id=user_id,
            status="completed",
            limit=10
        )
        past_projects = [p.project for p in completed_projects_response.projects]

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

        return DashboardDataResponse(
            active_projects=active_projects,
            past_projects=past_projects,
            user_stats=user_stats
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
    project_repo: ProjectRepository = Depends(get_project_repository)
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
        return {
            "success": True,
            "project": project_response.project.model_dump(),
            "message": "プロジェクトが正常に作成されました",
            "previous_projects_saved": len(active_projects) if active_projects else 0
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
    project_repo: ProjectRepository = Depends(get_project_repository)
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

        logger.info(f"プロジェクト進捗更新成功: {project_id} - ステップ{request.current_step_index} ({request.progress_percentage}%)")
        return {
            "success": True,
            "message": "プロジェクト進捗が正常に更新されました",
            "current_step_index": request.current_step_index,
            "progress_percentage": request.progress_percentage
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"プロジェクト進捗更新エラー: {project_id}, {e}")
        raise HTTPException(
            status_code=500,
            detail=f"プロジェクト進捗更新中にエラーが発生しました: {str(e)}"
        )
