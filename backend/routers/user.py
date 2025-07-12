from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from pydantic import BaseModel
from repositories.repository_factory import get_repository_factory
from repositories.user_repository import UserRepository
from models.user import CreateUserRequest, UserResponse
from models.database import KeyBuilder
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_user_repository() -> UserRepository:
    """ユーザーリポジトリを取得"""
    factory = get_repository_factory()
    return factory.get_user_repository()

@router.post("/signup", response_model=UserResponse)
async def signup(
    request: CreateUserRequest,
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserResponse:
    """
    新規会員登録

    Args:
        request: ユーザー作成リクエスト
        user_repo: ユーザーリポジトリ

    Returns:
        UserResponse: 作成されたユーザー情報
    """
    try:
        # ユーザーIDを生成
        user_id = KeyBuilder.generate_uuid()

        # ユーザーを作成
        user_response = await user_repo.create_user(user_id, request)

        if not user_response:
            logger.error(f"ユーザー作成失敗: {request.email}")
            raise HTTPException(
                status_code=500,
                detail="ユーザー作成に失敗しました"
            )

        logger.info(f"新規会員登録成功: {request.email}")
        return user_response

    except Exception as e:
        logger.error(f"新規会員登録エラー: {request.email}, {e}")
        raise HTTPException(
            status_code=500,
            detail=f"新規会員登録中にエラーが発生しました: {str(e)}"
        )

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(
    request: LoginRequest,
    user_repo: UserRepository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """
    ログイン

    Args:
        request: ログインリクエスト
        user_repo: ユーザーリポジトリ

    Returns:
        Dict[str, Any]: ログイン結果
    """
    try:
        # TODO: パスワード認証の実装
        # 現在は簡単な実装

        # メールアドレスでユーザーを検索
        user_response = await user_repo.get_user_by_email(request.email)

        if not user_response:
            raise HTTPException(
                status_code=401,
                detail="メールアドレスまたはパスワードが間違っています"
            )

        # 最終ログイン時刻を更新
        await user_repo.update_last_login(user_response.profile.userId)

        # JWTトークンを生成（簡単な実装）
        # TODO: 実際のJWT実装に置き換える
        token = f"token-{user_response.profile.userId}"

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user_response.model_dump()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ログインエラー: {request.email}, {e}")
        raise HTTPException(
            status_code=500,
            detail=f"ログイン中にエラーが発生しました: {str(e)}"
        )

@router.get("/profile/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: str,
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserResponse:
    """
    ユーザープロフィール取得

    Args:
        user_id: ユーザーID
        user_repo: ユーザーリポジトリ

    Returns:
        UserResponse: ユーザー情報
    """
    try:
        user_response = await user_repo.get_user_by_id(user_id)

        if not user_response:
            raise HTTPException(
                status_code=404,
                detail="ユーザーが見つかりません"
            )

        return user_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ユーザープロフィール取得エラー: {user_id}, {e}")
        raise HTTPException(
            status_code=500,
            detail=f"ユーザープロフィール取得中にエラーが発生しました: {str(e)}"
        )
