from fastapi import APIRouter, Depends, HTTPException, status
from models.theme import UserProfile, ResearchTheme, ThemeListResponse
from models.user import UserInDB
from services.theme_service import ThemeService
from repositories import ThemeRepository, GeminiClient
from repositories.database import db
from dependencies.auth import get_current_active_user
from utils import PromptBuilder

router = APIRouter()
mock_theme_service = ThemeService()

# Initialize services - they may fail if API keys are not available
try:
    prompt_builder = PromptBuilder()
    gemini_client = GeminiClient()
    theme_repository = ThemeRepository(prompt_builder, gemini_client)
    theme_service = ThemeService(theme_repository)
except Exception as e:
    print(f"Warning: Could not initialize Gemini services: {e}")
    theme_service = None


@router.post("/generate", response_model=ThemeListResponse)
async def generate_theme(
    profile: UserProfile,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Generate themes for authenticated user and update their profile
    """
    # Update user profile if provided
    if profile:
        db.update_user(current_user.id, {"profile": profile.model_dump()})
    
    # Generate themes using mock data for now
    themes_response = await mock_theme_service.generate_themes(profile=profile)
    
    # Store generated themes in database for later retrieval
    for theme in themes_response.themes:
        db.store_theme(theme)
    
    return themes_response


@router.post("/test-prompt", response_model=ThemeListResponse)
async def test_prompt(
    profile: UserProfile,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Test prompt generation with Gemini API (requires API key)
    """
    if theme_service is None:
        # Fall back to mock data if Gemini service is not available
        themes_response = await mock_theme_service.generate_themes(profile=profile)
    else:
        try:
            themes_response = await theme_service.generate_themes(profile=profile)
        except Exception as e:
            # Fall back to mock data if Gemini API fails
            themes_response = await mock_theme_service.generate_themes(profile=profile)
    
    # Store generated themes in database
    for theme in themes_response.themes:
        db.store_theme(theme)
    
    return themes_response


@router.get("/{theme_id}", response_model=ResearchTheme)
async def get_theme(
    theme_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Get a specific theme by ID
    """
    theme = db.get_theme_by_id(theme_id)
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )
    return theme
