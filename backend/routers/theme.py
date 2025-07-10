from fastapi import APIRouter
from models.theme import UserProfile, ResearchTheme, ThemeListResponse, SaveThemeRequest, SaveThemeResponse
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
