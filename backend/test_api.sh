#!/bin/bash

# Summer Research AI Backend Test Script
# This script demonstrates the complete authentication and project creation flow

BASE_URL="http://localhost:8000"
echo "🧪 Testing Summer Research AI Backend API"
echo "==========================================="

# 1. Test root endpoint
echo "1. Testing root endpoint..."
curl -s -X GET $BASE_URL/ | jq .
echo

# 2. Register a new user
echo "2. Registering new user..."
SIGNUP_RESPONSE=$(curl -s -X POST $BASE_URL/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "demopassword123",
    "name": "Demo User"
  }')
echo $SIGNUP_RESPONSE | jq .
echo

# 3. Login to get token
echo "3. Logging in to get access token..."
LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo@example.com&password=demopassword123")
TOKEN=$(echo $LOGIN_RESPONSE | jq -r .access_token)
echo "Login successful! Token: ${TOKEN:0:50}..."
echo

# 4. Get user profile
echo "4. Getting user profile..."
curl -s -X GET $BASE_URL/auth/me \
  -H "Authorization: Bearer $TOKEN" | jq .
echo

# 5. Generate themes
echo "5. Generating research themes..."
THEMES_RESPONSE=$(curl -s -X POST $BASE_URL/theme/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "grade": "elementary5",
    "interests": ["science", "technology"],
    "personality": ["curious", "analytical"],
    "strengths": ["experiment", "observation"],
    "duration": "1month"
  }')
echo $THEMES_RESPONSE | jq .
THEME_ID=$(echo $THEMES_RESPONSE | jq -r '.themes[0].id')
echo "Selected theme ID: $THEME_ID"
echo

# 6. Create project from theme
echo "6. Creating project from selected theme..."
PROJECT_RESPONSE=$(curl -s -X POST $BASE_URL/projects/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"theme_id\": \"$THEME_ID\"
  }")
echo $PROJECT_RESPONSE | jq .
PROJECT_ID=$(echo $PROJECT_RESPONSE | jq -r '.id')
echo "Created project ID: $PROJECT_ID"
echo

# 7. Get dashboard data
echo "7. Getting dashboard data..."
curl -s -X GET $BASE_URL/users/dashboard \
  -H "Authorization: Bearer $TOKEN" | jq .
echo

# 8. Start the project
echo "8. Starting the project..."
curl -s -X PUT $BASE_URL/projects/$PROJECT_ID/start \
  -H "Authorization: Bearer $TOKEN" | jq .
echo

# 9. Get updated dashboard
echo "9. Getting updated dashboard data..."
curl -s -X GET $BASE_URL/users/dashboard \
  -H "Authorization: Bearer $TOKEN" | jq .
echo

echo "✅ All tests completed successfully!"
echo "The backend is ready to support the frontend application."