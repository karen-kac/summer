from fastapi.testclient import TestClient
from main import app
from models.theme import ResearchTheme, ThemeListResponse, UserProfile
from services.theme_service import ThemeService
from models.enums import Grade, Interest, Personality, Strength, Duration
import pytest

client = TestClient(app)


def test_sample_theme():
    response = client.get("/theme/sample")
    assert response.status_code == 200
    assert response.json() == {"message": "Sample of Theme API"}


@pytest.fixture
def mock_theme_service(mocker):
    mock_service = mocker.patch.object(ThemeService, "generate_themes")
    mock_service.return_value = ThemeListResponse(
        themes=[
            ResearchTheme(
                id="1",
                title="Mock Theme 1",
                description="Mock Description 1",
                materials=["material1", "material2"],
                steps=["step1", "step2"],
                estimated_days=7,
                difficulty="easy",
            ),
            ResearchTheme(
                id="2",
                title="Mock Theme 2",
                description="Mock Description 2",
                materials=["material3", "material4"],
                steps=["step3", "step4"],
                estimated_days=14,
                difficulty="medium",
            ),
        ]
    )
    return mock_service


def test_generate_theme(mock_theme_service):
    profile_data = {
        "grade": "elementary1",
        "interests": ["science", "nature"],
        "personality": ["social", "analytical"],
        "strengths": ["reading", "craft"],
        "duration": "2weeks",
    }
    response = client.post("/theme/generate", json=profile_data)

    assert response.status_code == 200
    response_data = response.json()
    assert "themes" in response_data
    assert len(response_data["themes"]) == 2
    assert response_data["themes"][0]["title"] == "Mock Theme 1"
    assert response_data["themes"][1]["estimatedDays"] == 14
