"""
Simple in-memory database for development purposes.
In production, this would be replaced with DynamoDB or RDS.
"""
from typing import Dict, List, Optional
from models.user import User, UserInDB
from models.project import ResearchProject
from models.theme import ResearchTheme
import json
import os
from datetime import datetime


class SimpleDB:
    def __init__(self, data_file: str = "data.json"):
        self.data_file = data_file
        self.data = {
            "users": {},
            "projects": {},
            "themes": {}
        }
        self.load_data()
    
    def load_data(self):
        """Load data from file if it exists"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                # If file is corrupted or doesn't exist, start fresh
                pass
    
    def save_data(self):
        """Save data to file"""
        try:
            # Convert datetime objects to strings for JSON serialization
            serializable_data = {}
            for key, value in self.data.items():
                serializable_data[key] = {}
                for item_id, item_data in value.items():
                    if isinstance(item_data, dict):
                        serializable_item = {}
                        for k, v in item_data.items():
                            if isinstance(v, datetime):
                                serializable_item[k] = v.isoformat()
                            else:
                                serializable_item[k] = v
                        serializable_data[key][item_id] = serializable_item
                    else:
                        serializable_data[key][item_id] = item_data
            
            with open(self.data_file, 'w') as f:
                json.dump(serializable_data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    # User operations
    def create_user(self, user: UserInDB) -> UserInDB:
        """Create a new user"""
        user_dict = user.model_dump()
        self.data["users"][user.id] = user_dict
        self.save_data()
        return user
    
    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        for user_data in self.data["users"].values():
            if user_data.get("email") == email:
                # Convert datetime strings back to datetime objects
                if isinstance(user_data.get("created_at"), str):
                    user_data["created_at"] = datetime.fromisoformat(user_data["created_at"])
                if isinstance(user_data.get("updated_at"), str):
                    user_data["updated_at"] = datetime.fromisoformat(user_data["updated_at"])
                return UserInDB(**user_data)
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID"""
        user_data = self.data["users"].get(user_id)
        if user_data:
            # Convert datetime strings back to datetime objects
            if isinstance(user_data.get("created_at"), str):
                user_data["created_at"] = datetime.fromisoformat(user_data["created_at"])
            if isinstance(user_data.get("updated_at"), str):
                user_data["updated_at"] = datetime.fromisoformat(user_data["updated_at"])
            return UserInDB(**user_data)
        return None
    
    def update_user(self, user_id: str, update_data: dict) -> Optional[UserInDB]:
        """Update user data"""
        if user_id in self.data["users"]:
            self.data["users"][user_id].update(update_data)
            self.data["users"][user_id]["updated_at"] = datetime.now().isoformat()
            self.save_data()
            return self.get_user_by_id(user_id)
        return None
    
    # Project operations
    def create_project(self, project: ResearchProject) -> ResearchProject:
        """Create a new project"""
        project_dict = project.model_dump()
        self.data["projects"][project.id] = project_dict
        self.save_data()
        return project
    
    def get_projects_by_user(self, user_id: str) -> List[ResearchProject]:
        """Get all projects for a user"""
        projects = []
        for project_data in self.data["projects"].values():
            if project_data.get("user_id") == user_id:
                # Convert datetime strings back to datetime objects
                for date_field in ["start_date", "target_end_date", "actual_end_date", "created_at", "updated_at"]:
                    if isinstance(project_data.get(date_field), str):
                        project_data[date_field] = datetime.fromisoformat(project_data[date_field])
                projects.append(ResearchProject(**project_data))
        return projects
    
    def get_project_by_id(self, project_id: str) -> Optional[ResearchProject]:
        """Get project by ID"""
        project_data = self.data["projects"].get(project_id)
        if project_data:
            # Convert datetime strings back to datetime objects
            for date_field in ["start_date", "target_end_date", "actual_end_date", "created_at", "updated_at"]:
                if isinstance(project_data.get(date_field), str):
                    project_data[date_field] = datetime.fromisoformat(project_data[date_field])
            return ResearchProject(**project_data)
        return None
    
    def update_project(self, project_id: str, update_data: dict) -> Optional[ResearchProject]:
        """Update project data"""
        if project_id in self.data["projects"]:
            self.data["projects"][project_id].update(update_data)
            self.data["projects"][project_id]["updated_at"] = datetime.now().isoformat()
            self.save_data()
            return self.get_project_by_id(project_id)
        return None
    
    # Theme operations (for storing generated themes)
    def store_theme(self, theme: ResearchTheme) -> ResearchTheme:
        """Store a generated theme"""
        theme_dict = theme.model_dump()
        self.data["themes"][theme.id] = theme_dict
        self.save_data()
        return theme
    
    def get_theme_by_id(self, theme_id: str) -> Optional[ResearchTheme]:
        """Get theme by ID"""
        theme_data = self.data["themes"].get(theme_id)
        if theme_data:
            return ResearchTheme(**theme_data)
        return None


# Global database instance
db = SimpleDB()