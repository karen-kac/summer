from fastapi import APIRouter

router = APIRouter()


@router.get("/user_info")
def get_user_info():
    pass
