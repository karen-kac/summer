from fastapi import APIRouter
from models.theme import UserProfile, ResearchTheme, ThemeListResponse
from services.theme_service import ThemeService

router = APIRouter()
theme_service = ThemeService()


@router.get("/sample")
def sample_theme():
    return {"message": "Sample of Theme API"}


@router.post("/generate", response_model=ThemeListResponse)
def generate_theme(profile: UserProfile):
    themes = theme_service.generate_themes(profile=profile)
    return themes
