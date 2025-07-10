from models.theme import UserProfile, ResearchTheme, ThemeListResponse, SaveThemeRequest, SaveThemeResponse
import json
import os
from datetime import datetime


class ThemeService:
    def __init__(self, repository=None):
        if repository is None:
            raise ValueError("ThemeService requires a repository instance")
        self.repository = repository
        self.saved_themes_file = "saved_themes.json"

    async def generate_themes(self, profile: UserProfile) -> ThemeListResponse:
        themes_data = await self.repository.generate_themes(profile)
        themes = [ResearchTheme(**data) for data in themes_data]
        return ThemeListResponse(themes=themes)

    async def save_theme(self, request: SaveThemeRequest) -> SaveThemeResponse:
        """
        選択されたテーマを保存する
        """
        try:
            # 保存データを作成
            saved_data = {
                "theme": request.theme.model_dump(),
                "user_profile": request.user_profile.model_dump() if request.user_profile else None,
                "saved_at": datetime.now().isoformat(),
                "theme_id": request.theme.id
            }

            # 既存の保存データを読み込み
            saved_themes = []
            if os.path.exists(self.saved_themes_file):
                with open(self.saved_themes_file, 'r', encoding='utf-8') as f:
                    saved_themes = json.load(f)

            # 新しいテーマを追加
            saved_themes.append(saved_data)

            # ファイルに保存
            with open(self.saved_themes_file, 'w', encoding='utf-8') as f:
                json.dump(saved_themes, f, ensure_ascii=False, indent=2)

            return SaveThemeResponse(
                success=True,
                message="テーマが正常に保存されました",
                saved_theme_id=request.theme.id
            )

        except Exception as e:
            return SaveThemeResponse(
                success=False,
                message=f"テーマの保存に失敗しました: {str(e)}",
                saved_theme_id=""
            )
