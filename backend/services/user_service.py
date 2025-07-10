from models.achivement import Achivement, AchivementsListResponse
from repositories.mock_user_repository import MockUserRepository


class UserService:
    def __init__(self, repository=None):
        self.repository = repository if repository else MockUserRepository()

    async def get_achivement(self) -> AchivementsListResponse:
        achivements_data = await self.repository.get_achivement()
        achivements = [Achivement(**data) for data in achivements_data]
        return AchivementsListResponse(achivements=achivements)
