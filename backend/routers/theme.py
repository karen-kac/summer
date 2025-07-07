from fastapi import APIRouter
from models.theme import UserProfile, ResearchTheme, ThemeListResponse
from services.theme_service import ThemeService
from repositories import ThemeRepository, GeminiClient
from utils import PromptBuilder

router = APIRouter()
mock_theme_service = ThemeService()

prompt_builder = PromptBuilder()
gemini_client = GeminiClient()
theme_repository = ThemeRepository(prompt_builder, gemini_client)
theme_service = ThemeService(theme_repository)


@router.post("/generate", response_model=ThemeListResponse)
async def generate_theme(profile: UserProfile):
    """
    mockデータ用
    """
    themes = await mock_theme_service.generate_themes(profile=profile)
    return themes


@router.post("/test-prompt", response_model=ThemeListResponse)
async def test_prompt(profile: UserProfile):
    """
    promptのテスト用
    """
    themes = await theme_service.generate_themes(profile=profile)
    return themes
