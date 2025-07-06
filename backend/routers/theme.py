from fastapi import APIRouter
from models.theme import UserProfile, ResearchTheme, ThemeListResponse
from services.theme_service import ThemeService

router = APIRouter()
theme_service = ThemeService()


@router.post("/generate", response_model=ThemeListResponse)
async def generate_theme(profile: UserProfile):
    themes = await theme_service.generate_themes(profile=profile)
    return themes
