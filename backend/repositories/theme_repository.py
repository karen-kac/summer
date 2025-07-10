from utils.prompt_builder import PromptBuilder
from repositories import GeminiClient


class ThemeRepository:
    def __init__(self, prompt_builder: PromptBuilder, client: GeminiClient):
        self.builder = prompt_builder
        self.client = client

    async def generate_themes(self, profile) -> list:
        prompt = self.builder.build_suggest_themes_prompt(profile)
        themes_data = await self.client.post_prompt(prompt)
        return themes_data
