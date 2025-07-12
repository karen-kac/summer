from pydantic import BaseModel, EmailStr
from typing import Optional

# フロントエンド互換の型定義
class User(BaseModel):
    id: str
    email: str
    name: str
    profile: Optional[dict] = None
    createdAt: str
    updatedAt: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class FrontendAuthResponse(BaseModel):
    success: bool
    message: str
    user: User
    token: str
    refreshToken: Optional[str] = None

# 内部処理用（フロントエンド形式に統一）
class SignUpRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class SignUpResponse(BaseModel):
    success: bool
    user_sub: Optional[str] = None
    confirmation_required: Optional[bool] = None
    error: Optional[str] = None
    message: Optional[str] = None

class ConfirmSignUpRequest(BaseModel):
    name: str
    confirmation_code: str

class SignInRequest(BaseModel):
    name: str
    password: str

class SignInResponse(BaseModel):
    success: bool
    access_token: Optional[str] = None
    id_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    challenge_required: Optional[bool] = None
    challenge_name: Optional[str] = None
    session: Optional[str] = None
    error: Optional[str] = None
    message: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str
    name: str

class RefreshTokenResponse(BaseModel):
    success: bool
    access_token: Optional[str] = None
    id_token: Optional[str] = None
    expires_in: Optional[int] = None
    error: Optional[str] = None
    message: Optional[str] = None

class UserInfoResponse(BaseModel):
    success: bool
    name: Optional[str] = None
    attributes: Optional[dict] = None
    error: Optional[str] = None
    message: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    name: str

class ConfirmForgotPasswordRequest(BaseModel):
    name: str
    confirmation_code: str
    new_password: str

class AuthResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    message: Optional[str] = None

# フロントエンド互換のエラーレスポンス
class ApiResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    message: Optional[str] = None
