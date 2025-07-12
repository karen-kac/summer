from utils.prompt_builder import PromptBuilder
from repositories.client.bedrock_client import BedrockClient
from models.theme import ResearchTheme, UserProfile


class ThemeRepository:
    def __init__(self, prompt_builder: PromptBuilder, client: BedrockClient):
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
    
    async def process_chat_message(self, message: str, project_context: dict, media_analysis: str = None) -> str:
        """
        チャットメッセージを処理してAI応答を生成
        """
        prompt = self.builder.build_chat_prompt(message, project_context, media_analysis)
        response = await self.client.generate_chat_response(prompt)
        return response
