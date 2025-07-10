from fastapi import APIRouter, Depends, HTTPException, status
from models.user import UserInDB, UserResponse, UserProfileUpdate
from models.project import DashboardData, UserStats, ProjectWithTheme
from repositories.database import db
from dependencies.auth import get_current_active_user

router = APIRouter()


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data(current_user: UserInDB = Depends(get_current_active_user)):
    """Get dashboard data for the current user"""
    # Get user projects
    projects = db.get_projects_by_user(current_user.id)
    
    # Separate active and past projects
    active_projects = []
    past_projects = []
    
    for project in projects:
        # Get theme details
        theme = db.get_theme_by_id(project.theme_id)
        project_with_theme = ProjectWithTheme(
            **project.model_dump(),
            theme=theme
        )
        
        if project.status in ['planning', 'in_progress']:
            active_projects.append(project_with_theme)
        else:
            past_projects.append(project_with_theme)
    
    # Calculate user stats
    completed_projects = len([p for p in projects if p.status == 'completed'])
    user_stats = UserStats(
        total_points=completed_projects * 100,  # Simple point system
        level=min(completed_projects // 2 + 1, 10),  # Level up every 2 completed projects
        completed_projects=completed_projects,
        current_streak=0,  # TODO: Implement streak calculation
        total_records=0,   # TODO: Implement when records are added
        total_photos=0,    # TODO: Implement when photos are added
        total_experiments=len(projects)  # Count all projects as experiments for now
    )
    
    # Create user response
    user_response = UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        profile=current_user.profile,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )
    
    return DashboardData(
        user=user_response.model_dump(),  # Convert to dict to avoid circular import
        active_projects=active_projects,
        past_projects=past_projects,
        user_stats=user_stats
    )


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Update user profile"""
    # Update profile in database
    updated_user = db.update_user(
        current_user.id,
        {"profile": profile_update.profile.model_dump()}
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=updated_user.id,
        email=updated_user.email,
        name=updated_user.name,
        profile=updated_user.profile,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at
    )