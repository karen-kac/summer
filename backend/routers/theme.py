from fastapi import APIRouter, HTTPException
from models.theme import UserProfile, ResearchTheme, ThemeListResponse, SaveThemeRequest, SaveThemeResponse, GeneratePlanRequest, GeneratePlanResponse, GetSavedThemeResponse, GetResearchPlanResponse
from services.theme_service import ThemeService
from repositories import ThemeRepository, GeminiClient
from utils import PromptBuilder

router = APIRouter()

# 実際のGemini APIを使用するサービス
prompt_builder = PromptBuilder()
gemini_client = GeminiClient()
theme_repository = ThemeRepository(prompt_builder, gemini_client)
theme_service = ThemeService(theme_repository)


@router.post("/generate", response_model=ThemeListResponse)
async def generate_theme(profile: UserProfile):
    """
    Gemini AIを使用してテーマを生成する
    """
    print("=" * 50)
    print("🎯 フロントエンドからテーマ生成リクエストを受信")
    print(f"👤 学年: {profile.grade}")
    print(f"❤️ 興味: {profile.interests}")
    print(f"😊 性格: {profile.personality}")
    print(f"💪 得意: {profile.strengths}")
    print(f"⏰ 期間: {profile.duration}")
    if profile.additional_info:
        print(f"📝 追加情報: {profile.additional_info}")
    print("=" * 50)

    themes = await theme_service.generate_themes(profile=profile)

    print("✅ テーマ生成完了！生成されたテーマ:")
    for i, theme in enumerate(themes.themes, 1):
        print(f"  {i}. {theme.title} ({theme.genre}, {theme.estimated_days}日)")
    print("=" * 50)

    return themes


@router.post("/save", response_model=SaveThemeResponse)
async def save_theme(request: SaveThemeRequest):
    """
    選択されたテーマを保存する
    """
    print("=" * 50)
    print("💾 フロントエンドからテーマ保存リクエストを受信")
    print(f"📚 テーマ: {request.theme.title}")
    print(f"🆔 テーマID: {request.theme.id}")
    print("=" * 50)

    response = await theme_service.save_theme(request)

    if response.success:
        print("✅ テーマ保存完了！")
    else:
        print(f"❌ テーマ保存失敗: {response.message}")
    print("=" * 50)

    return response


@router.get("/saved/{theme_id}", response_model=GetSavedThemeResponse)
async def get_saved_theme(theme_id: str):
    """
    保存されたテーマを取得する
    """
    print("=" * 50)
    print("📖 フロントエンドから保存テーマ取得リクエストを受信")
    print(f"🆔 テーマID: {theme_id}")
    print("=" * 50)

    response = await theme_service.get_saved_theme(theme_id)

    if response.success:
        print("✅ 保存テーマ取得完了！")
        print(f"📚 テーマ: {response.theme.title}")
    else:
        print(f"❌ 保存テーマ取得失敗: {response.message}")
    print("=" * 50)

    return response


@router.get("/plan/{theme_id}", response_model=GetResearchPlanResponse)
async def get_research_plan(theme_id: str):
    """
    保存された研究計画を取得する
    """
    print("=" * 50)
    print("📋 フロントエンドから研究計画取得リクエストを受信")
    print(f"🆔 テーマID: {theme_id}")
    print("=" * 50)

    response = await theme_service.get_saved_research_plan(theme_id)

    if response.success:
        print("✅ 研究計画取得完了！")
        print(f"📚 テーマ: {response.plan.theme_title}")
        print(f"📝 ステップ数: {len(response.plan.steps)}")
        print(f"🗄️ キャッシュ: {'使用' if response.is_cached else '新規'}")
    else:
        print(f"❌ 研究計画取得失敗: {response.message}")
    print("=" * 50)

    return response


@router.post("/generate-plan", response_model=GeneratePlanResponse)
async def generate_research_plan(request: GeneratePlanRequest):
    """
    保存されたテーマを基に研究計画を生成する（初回のみ、2回目以降は保存されたものを返す）
    """
    print("=" * 50)
    print("🗓️ フロントエンドから研究計画生成リクエストを受信")
    print(f"🆔 テーマID: {request.theme_id}")
    print("=" * 50)

    response = await theme_service.generate_research_plan(request)

    if response.success:
        print("✅ 研究計画生成完了！")
        print(f"📚 テーマ: {response.plan.theme_title}")
        print(f"📝 ステップ数: {len(response.plan.steps)}")
    else:
        print(f"❌ 研究計画生成失敗: {response.message}")
    print("=" * 50)

    return response
