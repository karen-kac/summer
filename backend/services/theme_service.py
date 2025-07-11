from models.theme import UserProfile, ResearchTheme, ThemeListResponse, SaveThemeRequest, SaveThemeResponse, GeneratePlanRequest, GeneratePlanResponse, ResearchPlan, ResearchStep, GetSavedThemeResponse, GetResearchPlanResponse
import json
import os
from datetime import datetime


class ThemeService:
    def __init__(self, repository=None):
        if repository is None:
            raise ValueError("ThemeService requires a repository instance")
        self.repository = repository
        self.saved_themes_file = "saved_themes.json"
        self.saved_plans_file = "saved_research_plans.json"

    async def generate_themes(self, profile: UserProfile) -> ThemeListResponse:
        themes_data = await self.repository.generate_themes(profile)
        themes = [ResearchTheme(**data) for data in themes_data]
        return ThemeListResponse(themes=themes)

    async def save_theme(self, request: SaveThemeRequest) -> SaveThemeResponse:
        """
        選択されたテーマを保存する
        """
        try:
            # 保存データを作成（theme_idの重複を削除）
            saved_data = {
                "theme": request.theme.model_dump(),
                "user_profile": request.user_profile.model_dump() if request.user_profile else None,
                "saved_at": datetime.now().isoformat()
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

    async def get_saved_theme(self, theme_id: str) -> GetSavedThemeResponse:
        """
        保存されたテーマを取得する
        """
        try:
            if not os.path.exists(self.saved_themes_file):
                return GetSavedThemeResponse(
                    success=False,
                    message="保存されたテーマが見つかりません",
                    theme=None,
                    user_profile=None
                )

            with open(self.saved_themes_file, 'r', encoding='utf-8') as f:
                saved_themes = json.load(f)

            # 指定されたテーマIDを検索（theme.idで検索）
            for saved_data in saved_themes:
                theme_data = saved_data["theme"]
                if theme_data.get("id") == theme_id:
                    theme = ResearchTheme(**theme_data)

                    user_profile = None
                    if saved_data.get("user_profile"):
                        user_profile = UserProfile(**saved_data["user_profile"])

                    return GetSavedThemeResponse(
                        success=True,
                        message="テーマが正常に取得されました",
                        theme=theme,
                        user_profile=user_profile
                    )

            return GetSavedThemeResponse(
                success=False,
                message="指定されたテーマが見つかりません",
                theme=None,
                user_profile=None
            )

        except Exception as e:
            return GetSavedThemeResponse(
                success=False,
                message=f"テーマの取得に失敗しました: {str(e)}",
                theme=None,
                user_profile=None
            )

    async def get_saved_research_plan(self, theme_id: str) -> GetResearchPlanResponse:
        """
        保存された研究計画を取得する
        """
        try:
            if not os.path.exists(self.saved_plans_file):
                return GetResearchPlanResponse(
                    success=False,
                    message="保存された研究計画が見つかりません",
                    plan=None,
                    is_cached=False
                )

            with open(self.saved_plans_file, 'r', encoding='utf-8') as f:
                saved_plans = json.load(f)

            # 指定されたテーマIDを検索（plan.theme_idで検索）
            for saved_data in saved_plans:
                plan_data = saved_data["plan"]
                if plan_data.get("theme_id") == theme_id:

                    # ResearchStepオブジェクトのリストを作成
                    steps = []
                    for step_data in plan_data.get("steps", []):
                        step = ResearchStep(**step_data)
                        steps.append(step)

                    # ResearchPlanオブジェクトを作成
                    plan = ResearchPlan(
                        theme_id=plan_data["theme_id"],
                        theme_title=plan_data["theme_title"],
                        steps=steps,
                        total_estimated_days=plan_data["total_estimated_days"],
                        difficulty=plan_data["difficulty"],
                        genre=plan_data["genre"]
                    )

                    return GetResearchPlanResponse(
                        success=True,
                        message="研究計画が正常に取得されました",
                        plan=plan,
                        is_cached=True
                    )

            return GetResearchPlanResponse(
                success=False,
                message="指定されたテーマの研究計画が見つかりません",
                plan=None,
                is_cached=False
            )

        except Exception as e:
            return GetResearchPlanResponse(
                success=False,
                message=f"研究計画の取得に失敗しました: {str(e)}",
                plan=None,
                is_cached=False
            )

    async def save_research_plan(self, plan: ResearchPlan) -> bool:
        """
        研究計画を保存する（theme_idの重複を削除）
        """
        try:
            # 保存データを作成（トップレベルのtheme_idを削除）
            saved_data = {
                "plan": plan.model_dump(),
                "created_at": datetime.now().isoformat()
            }

            # 既存の保存データを読み込み
            saved_plans = []
            if os.path.exists(self.saved_plans_file):
                with open(self.saved_plans_file, 'r', encoding='utf-8') as f:
                    saved_plans = json.load(f)

            # 既存の同じテーマの計画があれば削除
            saved_plans = [p for p in saved_plans if p.get("plan", {}).get("theme_id") != plan.theme_id]

            # 新しい計画を追加
            saved_plans.append(saved_data)

            # ファイルに保存
            with open(self.saved_plans_file, 'w', encoding='utf-8') as f:
                json.dump(saved_plans, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            return False

    async def generate_research_plan(self, request: GeneratePlanRequest) -> GeneratePlanResponse:
        """
        保存されたテーマを基に研究計画を生成する（初回のみ）
        """
        try:
            # まず既存の研究計画があるかチェック
            existing_plan_response = await self.get_saved_research_plan(request.theme_id)
            if existing_plan_response.success:
                return GeneratePlanResponse(
                    success=True,
                    message="保存された研究計画が見つかりました",
                    plan=existing_plan_response.plan
                )

            # 保存されたテーマを取得
            saved_theme_response = await self.get_saved_theme(request.theme_id)
            if not saved_theme_response.success:
                return GeneratePlanResponse(
                    success=False,
                    message=saved_theme_response.message,
                    plan=None
                )

            theme = saved_theme_response.theme
            user_profile = saved_theme_response.user_profile

            # AI を使って研究計画を生成
            plan_data = await self.repository.generate_research_plan(theme, user_profile)

            # AIからの応答がリスト形式か辞書形式かを判定
            if isinstance(plan_data, list):
                steps_data = plan_data
            elif isinstance(plan_data, dict):
                steps_data = plan_data.get("steps", [])
            else:
                raise ValueError(f"予期しない応答形式: {type(plan_data)}")

            # ResearchStepオブジェクトのリストを作成
            steps = []
            for i, step_data in enumerate(steps_data):
                if not isinstance(step_data, dict):
                    continue

                if 'order' not in step_data:
                    step_data['order'] = i + 1

                try:
                    step = ResearchStep(**step_data)
                    steps.append(step)
                except Exception:
                    continue

            if not steps:
                raise ValueError("有効なステップが生成されませんでした")

            # ResearchPlanオブジェクトを作成
            plan = ResearchPlan(
                theme_id=theme.id,
                theme_title=theme.title,
                steps=steps,
                total_estimated_days=theme.estimated_days,
                difficulty=theme.difficulty,
                genre=theme.genre
            )

            # 研究計画を保存
            await self.save_research_plan(plan)

            return GeneratePlanResponse(
                success=True,
                message="研究計画が正常に生成されました",
                plan=plan
            )

        except Exception as e:
            return GeneratePlanResponse(
                success=False,
                message=f"研究計画の生成に失敗しました: {str(e)}",
                plan=None
            )
