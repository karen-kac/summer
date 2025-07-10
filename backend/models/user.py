from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from models.theme import UserProfile
import uuid


class User(BaseModel):
    id: str = Field(default_factory=lambda: "user_" + str(uuid.uuid4()))
    email: EmailStr
    name: str
    hashed_password: str
    profile: Optional[UserProfile] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True


class UserInDB(User):
    """User model with hashed password for database storage"""
    pass


class UserCreate(BaseModel):
    """Model for user registration"""
    email: EmailStr
    password: str
    name: str


class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Model for user response (without sensitive data)"""
    id: str
    email: EmailStr
    name: str
    profile: Optional[UserProfile] = None
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token payload data"""
    email: Optional[str] = None


class UserProfileUpdate(BaseModel):
    """Model for updating user profile"""
    profile: UserProfile