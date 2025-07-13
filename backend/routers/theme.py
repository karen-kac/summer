from fastapi import APIRouter, HTTPException
from models.theme import UserProfile, ResearchTheme, ThemeListResponse, SaveThemeRequest, SaveThemeResponse, GeneratePlanRequest, GeneratePlanResponse, GetSavedThemeResponse, GetResearchPlanResponse
from services.theme_service import ThemeService
from repositories import get_theme_repository
from repositories.repository_factory import get_repository_factory
from datetime import datetime

router = APIRouter()

# ファクトリーパターンを使用してサービスを取得
theme_repository = get_theme_repository()
theme_service = ThemeService(theme_repository)


@router.post("/generate", response_model=ThemeListResponse)
async def generate_theme(profile: UserProfile):
    """
    Bedrock AIを使用してテーマを生成する
    """
    themes = await theme_service.generate_themes(profile=profile)
    return themes


@router.post("/save", response_model=SaveThemeResponse)
async def save_theme(request: SaveThemeRequest, user_id: str = None):
    """
    選択されたテーマを保存する
    """
    response = await theme_service.save_theme(request)

    # ユーザーIDが提供されている場合、ユーザーとテーマの関連付けを保存
    if response.success and user_id:
        try:
            factory = get_repository_factory()
            project_repo = factory.get_project_repository()

            # ユーザーの保存テーマとして記録
            await project_repo.save_theme(
                user_id=user_id,
                theme_id=response.saved_theme_id,
                notes=f"テーマ決定日: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            response.message += " (ユーザーとの関連付けも保存済み)"

        except Exception as e:
            # エラーが発生してもテーマ保存は成功しているので、警告メッセージを追加
            response.message += f" (警告: ユーザーとの関連付け保存に失敗: {str(e)})"

    return response


@router.get("/saved/{theme_id}", response_model=GetSavedThemeResponse)
async def get_saved_theme(theme_id: str):
    """
    保存されたテーマを取得する
    """
    response = await theme_service.get_saved_theme(theme_id)
    return response


@router.get("/plan/{theme_id}", response_model=GetResearchPlanResponse)
async def get_research_plan(theme_id: str):
    """
    保存された研究計画を取得する
    """
    response = await theme_service.get_saved_research_plan(theme_id)
    return response


@router.post("/generate-plan", response_model=GeneratePlanResponse)
async def generate_research_plan(request: GeneratePlanRequest):
    """
    保存されたテーマを基に研究計画を生成する（初回のみ、2回目以降は保存されたものを返す）
    """
    response = await theme_service.generate_research_plan(request)
    return response
