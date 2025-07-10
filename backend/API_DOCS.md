# Backend API Documentation

## Authentication Endpoints

### POST /auth/signup
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "User Name"
}
```

**Response:**
```json
{
  "id": "user_uuid",
  "email": "user@example.com",
  "name": "User Name",
  "profile": null,
  "created_at": "2025-07-10T11:16:38.808408",
  "updated_at": "2025-07-10T11:16:38.808412"
}
```

### POST /auth/login
Login and receive access token.

**Request (form-data):**
```
username=user@example.com
password=password123
```

**Response:**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

### GET /auth/me
Get current user profile (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

## User Management Endpoints

### GET /users/dashboard
Get dashboard data for the current user.

**Response:**
```json
{
  "user": {
    "id": "user_uuid",
    "email": "user@example.com",
    "name": "User Name",
    "profile": {
      "grade": "elementary4",
      "interests": ["science", "nature"],
      "personality": ["curious", "creative"],
      "strengths": ["observation", "experiment"],
      "duration": "2weeks"
    }
  },
  "active_projects": [/* active projects */],
  "past_projects": [/* completed projects */],
  "user_stats": {
    "total_points": 0,
    "level": 1,
    "completed_projects": 0,
    "current_streak": 0,
    "total_records": 0,
    "total_photos": 0,
    "total_experiments": 1
  }
}
```

### PUT /users/profile
Update user profile.

**Request:**
```json
{
  "profile": {
    "grade": "elementary4",
    "interests": ["science", "nature"],
    "personality": ["curious", "creative"],
    "strengths": ["observation", "experiment"],
    "duration": "2weeks"
  }
}
```

## Theme Endpoints

### POST /theme/generate
Generate research themes based on user profile (requires authentication).

**Request:**
```json
{
  "grade": "elementary4",
  "interests": ["science", "nature"],
  "personality": ["curious", "creative"],
  "strengths": ["observation", "experiment"],
  "duration": "2weeks"
}
```

**Response:**
```json
{
  "themes": [
    {
      "id": "theme_uuid",
      "title": "Theme Title",
      "description": "Theme description",
      "materials": ["material1", "material2"],
      "steps": ["step1", "step2"],
      "estimatedDays": 5,
      "difficulty": "medium"
    }
  ]
}
```

### GET /theme/{theme_id}
Get a specific theme by ID.

## Project Endpoints

### POST /projects/create
Create a new research project from a selected theme.

**Request:**
```json
{
  "theme_id": "theme_uuid",
  "title": "Optional custom title",
  "description": "Optional custom description",
  "custom_materials": ["optional custom materials"],
  "custom_steps": ["optional custom steps"],
  "target_end_date": "2025-07-15T11:17:14.101028"
}
```

### GET /projects/
Get all projects for the current user.

### GET /projects/{project_id}
Get a specific project by ID.

### PUT /projects/{project_id}/start
Start a project (change status from planning to in_progress).

## Authentication Requirements

All endpoints except `/auth/signup` and `/auth/login` require authentication using a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Development Database

The application currently uses a simple file-based database (`data.json`) for development. In production, this should be replaced with DynamoDB or RDS as specified in the requirements.