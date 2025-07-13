from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict
import logging
from datetime import datetime

from services.auth_factory import AuthServiceFactory
from models.auth import (
    LoginRequest, SignupRequest, FrontendAuthResponse, User, ApiResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["frontend-auth"])
security = HTTPBearer()

def get_auth_service():
    """認証サービスの依存性注入（本番用）"""
    return AuthServiceFactory.get_production_service()

def get_test_auth_service():
    """認証サービスの依存性注入（テスト用）"""
    return AuthServiceFactory.get_test_service()

def get_auth_service():
    """認証サービスの依存性注入（本番用Cognito）"""
    return AuthServiceFactory.get_production_service()

@router.post("/login", response_model=FrontendAuthResponse)
async def login(request: LoginRequest, auth_service = Depends(get_auth_service)):
    """フロントエンド互換のログイン"""
    try:
        # Email alias設定により、emailでログイン可能
        result = auth_service.authenticate_user(
            username=request.email,  # emailでログイン（Email alias対応）
            password=request.password
        )

        if not result['success']:
            raise HTTPException(
                status_code=401,
                detail=result.get('message', 'Authentication failed')
            )

        # フロントエンド互換のレスポンスを作成
        user_info = auth_service.get_user_profile(result['access_token'])

        user = User(
            id=user_info.get('username', 'user-1'),
            email=user_info.get('attributes', {}).get('email', request.email),
            name=user_info.get('attributes', {}).get('name', 'User'),
            profile={
                'grade': user_info.get('attributes', {}).get('custom:grade')
            } if user_info.get('attributes', {}).get('custom:grade') else None,
            createdAt=datetime.now().isoformat(),
            updatedAt=datetime.now().isoformat()
        )

        return FrontendAuthResponse(
            success=True,
            message="Login successful",
            user=user,
            token=result['access_token'],
            refreshToken=result.get('refresh_token')
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/signup", response_model=FrontendAuthResponse)
async def signup(request: SignupRequest, auth_service = Depends(get_auth_service)):
    """フロントエンド互換のサインアップ"""
    try:
        # name, email, passwordの形式でユーザー登録
        signup_result = auth_service.register_user(
            name=request.name,
            email=request.email,
            password=request.password
        )

        if not signup_result['success']:
            raise HTTPException(
                status_code=400,
                detail=signup_result.get('message', 'Registration failed')
            )

        # 自動確認（メール検証スキップ）
        confirm_result = auth_service.confirm_registration(
            username=request.name,  # nameをusernameとして使用
            confirmation_code="123456"
        )

        if not confirm_result['success']:
            raise HTTPException(
                status_code=400,
                detail="Account confirmation failed"
            )

        # 自動ログイン
        login_result = auth_service.authenticate_user(
            username=request.name,  # nameをusernameとして使用
            password=request.password
        )

        if not login_result['success']:
            raise HTTPException(
                status_code=400,
                detail="Auto-login failed"
            )

        # ユーザー情報取得
        user_info = auth_service.get_user_profile(login_result['access_token'])

        user = User(
            id=user_info.get('username', request.name),
            email=request.email,
            name=request.name,
            profile=request.profile if hasattr(request, 'profile') and request.profile else None,
            createdAt=datetime.now().isoformat(),
            updatedAt=datetime.now().isoformat()
        )

        return FrontendAuthResponse(
            success=True,
            message="Signup successful",
            user=user,
            token=login_result['access_token'],
            refreshToken=login_result.get('refresh_token')
        )

        if not login_result['success']:
            raise HTTPException(
                status_code=500,
                detail="Auto-login failed after registration"
            )

        # フロントエンド互換のレスポンスを作成
        user = User(
            id=signup_result.get('user_sub', 'user-' + str(hash(request.email))),
            email=request.email,
            name=request.name,
            profile=None,
            createdAt=datetime.now().isoformat(),
            updatedAt=datetime.now().isoformat()
        )

        return FrontendAuthResponse(
            user=user,
            token=login_result['access_token'],
            refreshToken=login_result['refresh_token']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/me", response_model=User)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), auth_service = Depends(get_auth_service)):
    """現在のユーザー情報を取得（フロントエンド互換）"""
    try:
        access_token = credentials.credentials
        result = auth_service.get_user_profile(access_token)

        if not result['success']:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )

        user = User(
            id=result.get('username', 'user-1'),
            email=result.get('attributes', {}).get('email', ''),
            name=result.get('attributes', {}).get('name', 'User'),
            profile={
                'grade': result.get('attributes', {}).get('custom:grade')
            } if result.get('attributes', {}).get('custom:grade') else None,
            createdAt=datetime.now().isoformat(),
            updatedAt=datetime.now().isoformat()
        )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/logout", response_model=ApiResponse)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security), auth_service = Depends(get_auth_service)):
    """ログアウト（フロントエンド互換）"""
    try:
        access_token = credentials.credentials
        result = auth_service.logout_user(access_token)

        return ApiResponse(
            success=result['success'],
            message="Logged out successfully" if result['success'] else "Logout failed"
        )

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return ApiResponse(
            success=False,
            error="Internal server error",
            message=str(e)
        )

@router.post("/refresh", response_model=FrontendAuthResponse)
async def refresh_token(refresh_token: str, auth_service = Depends(get_auth_service)):
    """トークンリフレッシュ（フロントエンド互換）"""
    try:
        # リフレッシュトークンからユーザー名を取得（簡易実装）
        # 実際の実装では、トークンをデコードしてユーザー名を取得
        username = "user@example.com"  # プレースホルダー

        result = auth_service.refresh_user_token(
            refresh_token=refresh_token,
            username=username
        )

        if not result['success']:
            raise HTTPException(
                status_code=401,
                detail="Token refresh failed"
            )

        # ユーザー情報を取得
        user_info = auth_service.get_user_profile(result['access_token'])

        user = User(
            id=user_info.get('username', 'user-1'),
            email=user_info.get('attributes', {}).get('email', ''),
            name=user_info.get('attributes', {}).get('name', 'User'),
            profile={
                'grade': user_info.get('attributes', {}).get('custom:grade')
            } if user_info.get('attributes', {}).get('custom:grade') else None,
            createdAt=datetime.now().isoformat(),
            updatedAt=datetime.now().isoformat()
        )

        return FrontendAuthResponse(
            user=user,
            token=result['access_token'],
            refreshToken=refresh_token  # 既存のリフレッシュトークンを返す
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Refresh token error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
