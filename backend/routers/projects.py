from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models.user import UserInDB
from models.project import ResearchProject, CreateProjectRequest, ProjectResponse, ProjectWithTheme
from models.theme import ResearchTheme
from repositories.database import db
from dependencies.auth import get_current_active_user
from datetime import datetime, timedelta

router = APIRouter()


@router.post("/create", response_model=ProjectResponse)
async def create_project(
    project_data: CreateProjectRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Create a new research project from a selected theme"""
    # Get the theme details
    theme = db.get_theme_by_id(project_data.theme_id)
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )
    
    # Set default values based on theme if not provided
    title = project_data.title or theme.title
    description = project_data.description or theme.description
    
    # Calculate target end date if not provided (default to theme's estimated days)
    target_end_date = project_data.target_end_date
    if not target_end_date:
        target_end_date = datetime.now() + timedelta(days=theme.estimated_days)
    
    # Create project
    project = ResearchProject(
        user_id=current_user.id,
        theme_id=project_data.theme_id,
        title=title,
        description=description,
        target_end_date=target_end_date,
        custom_materials=project_data.custom_materials or theme.materials,
        custom_steps=project_data.custom_steps or theme.steps,
        status='planning'
    )
    
    # Save to database
    created_project = db.create_project(project)
    
    return ProjectResponse(**created_project.model_dump())


@router.get("/", response_model=List[ProjectWithTheme])
async def get_user_projects(current_user: UserInDB = Depends(get_current_active_user)):
    """Get all projects for the current user"""
    projects = db.get_projects_by_user(current_user.id)
    
    # Add theme details to each project
    projects_with_themes = []
    for project in projects:
        theme = db.get_theme_by_id(project.theme_id)
        project_with_theme = ProjectWithTheme(
            **project.model_dump(),
            theme=theme
        )
        projects_with_themes.append(project_with_theme)
    
    return projects_with_themes


@router.get("/{project_id}", response_model=ProjectWithTheme)
async def get_project(
    project_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get a specific project by ID"""
    project = db.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if project belongs to current user
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    # Get theme details
    theme = db.get_theme_by_id(project.theme_id)
    
    return ProjectWithTheme(
        **project.model_dump(),
        theme=theme
    )


@router.put("/{project_id}/start", response_model=ProjectResponse)
async def start_project(
    project_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Start a project (change status from planning to in_progress)"""
    project = db.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if project belongs to current user
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    # Update project status
    updated_project = db.update_project(
        project_id,
        {
            "status": "in_progress",
            "start_date": datetime.now().isoformat()
        }
    )
    
    return ProjectResponse(**updated_project.model_dump())