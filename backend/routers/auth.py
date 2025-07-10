from fastapi import APIRouter, HTTPException
from backend.models.user import UserCreate, UserLogin
from backend.services.user_service import create_user, authenticate_user

router = APIRouter()

@router.post("/register")
def register(user: UserCreate):
    success = create_user(user)
    if not success:
        raise HTTPException(status_code=400, detail="メールアドレスはすでに登録されています。")
    return {"message": "登録成功"}

@router.post("/login")
def login(user: UserLogin):
    result = authenticate_user(user.email, user.password)
    if not result:
        raise HTTPException(status_code=401, detail="メールアドレスまたはパスワードが間違っています。")
    return {"first_name": result.first_name}
