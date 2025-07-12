from fastapi import APIRouter, HTTPException
from models.theme import UserProfile, ResearchTheme, ThemeListResponse, SaveThemeRequest, SaveThemeResponse, GeneratePlanRequest, GeneratePlanResponse, GetSavedThemeResponse, GetResearchPlanResponse
from services.theme_service import ThemeService
from repositories import ThemeRepository, BedrockClient
from utils import PromptBuilder

router = APIRouter()

# 実際のBedrock APIを使用するサービス
prompt_builder = PromptBuilder()
bedrock_client = BedrockClient()
theme_repository = ThemeRepository(prompt_builder, bedrock_client)
theme_service = ThemeService(theme_repository)


@router.post("/generate", response_model=ThemeListResponse)
async def generate_theme(profile: UserProfile):
    """
    Bedrock AIを使用してテーマを生成する
    """
    themes = await theme_service.generate_themes(profile=profile)
    return themes


@router.post("/save", response_model=SaveThemeResponse)
async def save_theme(request: SaveThemeRequest):
    """
    選択されたテーマを保存する
    """
    response = await theme_service.save_theme(request)
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
