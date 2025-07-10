import pytest
from utils.prompt_builder import PromptBuilder
from models.theme import UserProfile
from models.enums import Grade, Interest, Personality, Strength, Duration


@pytest.fixture
def sample_user_profile():
    return UserProfile(
        grade=Grade.junior1,
        interests=[Interest.science, Interest.technology],
        personality=[Personality.curious, Personality.analytical],
        strengths=[Strength.observation, Strength.calculating],
        duration=Duration.one_month,
    )


def test_build_suggest_themes_prompt_all_fields(sample_user_profile):
    builder = PromptBuilder()
    prompt = builder.build_suggest_themes_prompt(sample_user_profile)

    assert "あなたは自由研究の研究テーマを提案する専門家です。" in prompt
    assert f"学年: {sample_user_profile.grade.label}" in prompt
    assert (
        f"興味: {', '.join([i.label for i in sample_user_profile.interests])}" in prompt
    )
    assert (
        f"性格: {', '.join([p.label for p in sample_user_profile.personality])}"
        in prompt
    )
    assert (
        f"得意なこと: {', '.join([s.label for s in sample_user_profile.strengths])}"
        in prompt
    )
    assert f"研究期間: {sample_user_profile.duration.label}" in prompt
    assert (
        "これらの情報を基に、自由研究の研究テーマを3つ提案し、以下の例のようにjsonファイル形式に変換してください。"
        in prompt
    )


def test_build_suggest_themes_prompt_multiple_interests():
    profile = UserProfile(
        grade=Grade.elementary3,
        interests=[Interest.art, Interest.music, Interest.cooking],
        personality=[Personality.creative],
        strengths=[Strength.drawing],
        duration=Duration.two_weeks,
    )
    builder = PromptBuilder()
    prompt = builder.build_suggest_themes_prompt(profile)
    assert "興味: 美術・工作, 音楽・楽器, 料理・食べ物" in prompt
