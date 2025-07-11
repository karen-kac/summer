from utils.prompt_builder import PromptBuilder
from repositories import GeminiClient
from models.theme import ResearchTheme, UserProfile


class ThemeRepository:
    def __init__(self, prompt_builder: PromptBuilder, client: GeminiClient):
        self.builder = prompt_builder
        self.client = client

    async def generate_themes(self, profile) -> list:
        prompt = self.builder.build_suggest_themes_prompt(profile)
        themes_data = await self.client.post_prompt(prompt)
        return themes_data

    async def generate_research_plan(self, theme: ResearchTheme, user_profile: UserProfile = None) -> dict:
        """
        保存されたテーマを基に研究計画を生成する
        """
        prompt = self.builder.build_research_plan_prompt(theme, user_profile)
        plan_data = await self.client.post_prompt(prompt)
        return plan_data
