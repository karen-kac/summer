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
            # DynamoDBに保存するためのデータを準備
            theme_data = {
                "title": request.theme.title,
                "description": request.theme.description,
                "genre": request.theme.genre,
                "difficulty": request.theme.difficulty,
                "estimatedDays": request.theme.estimated_days,
                "materials": request.theme.materials,
                "defaultSteps": request.theme.steps,
                "targetGrades": ["elementary4"],  # デフォルト値
                "keywords": [],  # デフォルト値
                "isPublic": True,
                "createdBy": request.user_profile.email if request.user_profile else None
            }

            # ThemeRepositoryを使ってDynamoDBに保存
            saved_theme = await self.repository.save_theme(theme_data)

            if saved_theme:
                # TODO: ユーザーとテーマの関連付けも保存
                # 現在のユーザー認証システムが完成したら、ユーザーIDを取得してテーマを保存
                # if user_id:
                #     from repositories.repository_factory import get_repository_factory
                #     factory = get_repository_factory()
                #     project_repo = factory.get_project_repository()
                #
                #     # ユーザーの保存テーマとして記録
                #     await project_repo.save_theme(
                #         user_id=user_id,
                #         theme_id=saved_theme.themeId,
                #         notes=f"テーマ決定日: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                #     )

                # JSONファイルにも保存（後方互換性のため）
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
                    message="テーマが正常に保存されました（AWSとローカルファイルの両方に保存）",
                    saved_theme_id=saved_theme.themeId
                )
            else:
                return SaveThemeResponse(
                    success=False,
                    message="AWSへのテーマ保存に失敗しました",
                    saved_theme_id=""
                )

        except Exception as e:
            return SaveThemeResponse(
                success=False,
                message=f"テーマの保存に失敗しました: {str(e)}",
                saved_theme_id=""
            )

    async def get_saved_theme(self, theme_id: str) -> GetSavedThemeResponse:
        """
        保存されたテーマを取得する（AWSからまず取得、見つからなければJSONファイルから）
        """
        try:
            # まずAWS DynamoDBからテーマを取得
            aws_theme = await self.repository.get_theme_by_id(theme_id)

            if aws_theme:
                # models/project.py の ResearchTheme から models/theme.py の ResearchTheme に変換
                converted_theme = ResearchTheme(
                    id=aws_theme.themeId,
                    title=aws_theme.title,
                    description=aws_theme.description,
                    genre=aws_theme.genre,
                    materials=aws_theme.materials,
                    steps=aws_theme.defaultSteps,
                    estimated_days=aws_theme.estimatedDays,
                    difficulty=aws_theme.difficulty
                )

                print(f"✅ テーマをAWSから取得しました: {converted_theme.title}")
                return GetSavedThemeResponse(
                    success=True,
                    message="テーマが正常に取得されました（AWS）",
                    theme=converted_theme,
                    user_profile=None  # 現在のところ、user_profileは別途管理
                )

            # AWS DynamoDBから見つからない場合、JSONファイルから取得
            print(f"⚠️ AWS DynamoDBにテーマが見つかりませんでした。JSONファイルから取得します: {theme_id}")

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

                    print(f"✅ テーマをJSONファイルから取得しました: {theme.title}")
                    return GetSavedThemeResponse(
                        success=True,
                        message="テーマが正常に取得されました（JSONファイル）",
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
            print(f"❌ テーマの取得でエラーが発生しました: {str(e)}")
            return GetSavedThemeResponse(
                success=False,
                message=f"テーマの取得に失敗しました: {str(e)}",
                theme=None,
                user_profile=None
            )

    async def get_saved_research_plan(self, theme_id: str) -> GetResearchPlanResponse:
        """
        保存された研究計画を取得する（AWSからまず取得、見つからなければJSONファイルから）
        """
        try:
            # まずAWS DynamoDBから研究計画を取得
            aws_plan = await self.repository.get_plan_by_theme_id(theme_id)

            if aws_plan:
                # ResearchStepオブジェクトのリストを作成
                steps = []
                for step_data in aws_plan.steps:
                    if isinstance(step_data, dict):
                        step = ResearchStep(**step_data)
                    else:
                        step = step_data  # 既にResearchStepオブジェクトの場合
                    steps.append(step)

                # ResearchPlanオブジェクトを作成
                plan = ResearchPlan(
                    theme_id=aws_plan.themeId,
                    theme_title=aws_plan.title,
                    steps=steps,
                    total_estimated_days=aws_plan.totalDays,
                    difficulty=aws_plan.difficulty,
                    genre=aws_plan.genre
                )

                print(f"✅ 研究計画をAWSから取得しました: {plan.theme_title}")
                return GetResearchPlanResponse(
                    success=True,
                    message="研究計画が正常に取得されました（AWS）",
                    plan=plan,
                    is_cached=True
                )

            # AWS DynamoDBから見つからない場合、JSONファイルから取得
            print(f"⚠️ AWS DynamoDBに研究計画が見つかりませんでした。JSONファイルから取得します: {theme_id}")

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

                    print(f"✅ 研究計画をJSONファイルから取得しました: {plan.theme_title}")
                    return GetResearchPlanResponse(
                        success=True,
                        message="研究計画が正常に取得されました（JSONファイル）",
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
            print(f"❌ 研究計画の取得でエラーが発生しました: {str(e)}")
            return GetResearchPlanResponse(
                success=False,
                message=f"研究計画の取得に失敗しました: {str(e)}",
                plan=None,
                is_cached=False
            )

    async def save_research_plan(self, plan: ResearchPlan) -> bool:
        """
        研究計画を保存する（AWSとJSONファイルの両方）
        """
        try:
            # AWSに保存する用のデータを準備
            # stepIdとestimatedDurationフィールドを追加
            aws_steps = []
            for i, step in enumerate(plan.steps):
                step_data = step.model_dump()
                step_data['stepId'] = f"step-{i+1}"
                step_data['estimatedDuration'] = step_data.get('duration', '1日')
                aws_steps.append(step_data)

            plan_data = {
                "themeId": plan.theme_id,
                "title": plan.theme_title,
                "description": f"{plan.theme_title}の詳細な研究計画",
                "steps": aws_steps,
                "totalDays": plan.total_estimated_days,
                "difficulty": plan.difficulty,
                "genre": plan.genre
            }

            # AWS DynamoDBに保存
            saved_plan = await self.repository.save_research_plan(plan_data)

            if saved_plan:
                print(f"✅ 研究計画をAWSに保存しました: {plan.theme_title}")
                aws_save_success = True
            else:
                print(f"❌ 研究計画のAWS保存に失敗しました: {plan.theme_title}")
                aws_save_success = False

            # JSONファイルにもバックアップ保存
            try:
                saved_data = {
                    "plan": plan.model_dump(),
                    "created_at": datetime.now().isoformat(),
                    "aws_saved": aws_save_success
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

                print(f"✅ 研究計画をJSONファイルにバックアップしました: {plan.theme_title}")
            except Exception as json_error:
                print(f"⚠️ JSONファイルへのバックアップに失敗しました: {json_error}")

            # AWS保存が成功すれば全体として成功
            return aws_save_success

        except Exception as e:
            print(f"❌ 研究計画の保存でエラーが発生しました: {str(e)}")
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
