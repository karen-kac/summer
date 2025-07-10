from fastapi import APIRouter
from models.achivement import Achivement, AchivementsListResponse
from services.user_service import UserService

router = APIRouter()
user_service = UserService()


@router.get("/get", response_model=AchivementsListResponse)
async def get_achivement():
    achivements = await user_service.get_achivement()
    return achivements
