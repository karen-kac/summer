from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models.user import User, UserCreate, UserLogin, Token, UserResponse, UserInDB
from repositories.database import db
from utils.auth import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from dependencies.auth import get_current_active_user

router = APIRouter()


@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.get_user_by_email(email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user_data.password)
    user = UserInDB(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password
    )
    
    # Save to database
    created_user = db.create_user(user)
    
    # Return user response (without password)
    return UserResponse(
        id=created_user.id,
        email=created_user.email,
        name=created_user.name,
        profile=created_user.profile,
        created_at=created_user.created_at,
        updated_at=created_user.updated_at
    )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user and return access token"""
    user = db.get_user_by_email(email=form_data.username)  # OAuth2PasswordRequestForm uses 'username' field for email
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: UserInDB = Depends(get_current_active_user)):
    """Get current user profile"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        profile=current_user.profile,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )