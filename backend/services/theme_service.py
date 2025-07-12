from models.theme import UserProfile, ResearchTheme, ThemeListResponse, SaveThemeRequest, SaveThemeResponse, GeneratePlanRequest, GeneratePlanResponse, ResearchPlan, ResearchStep, GetSavedThemeResponse, GetResearchPlanResponse
from datetime import datetime


class ThemeService:
    def __init__(self, repository=None):
        if repository is None:
            raise ValueError("ThemeService requires a repository instance")
        self.repository = repository

    async def generate_themes(self, profile: UserProfile) -> ThemeListResponse:
        themes_data = await self.repository.generate_themes(profile)
        themes = [ResearchTheme(**data) for data in themes_data]
        return ThemeListResponse(themes=themes)

    async def save_theme(self, request: SaveThemeRequest) -> SaveThemeResponse:
        """
        選択されたテーマを保存する（AWSのみ）
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

                return SaveThemeResponse(
                    success=True,
                    message="テーマが正常に保存されました（AWS）",
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
        保存されたテーマを取得する（AWSのみ）
        """
        try:
            # AWS DynamoDBからテーマを取得
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
            else:
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
        保存された研究計画を取得する（AWSのみ）
        """
        try:
            # AWS DynamoDBから研究計画を取得
            aws_plan = await self.repository.get_plan_by_theme_id(theme_id)

            if aws_plan:
                # ResearchStepオブジェクトのリストを作成
                # project.py の ResearchStep から theme.py の ResearchStep に変換
                steps = []
                for step_data in aws_plan.steps:
                    if isinstance(step_data, dict):
                        # 辞書の場合はtheme.pyのResearchStepに変換
                        theme_step = ResearchStep(
                            title=step_data.get('title', ''),
                            description=step_data.get('description', ''),
                            tips=step_data.get('tips', []),
                            duration=step_data.get('estimatedDuration', step_data.get('duration', '1日')),
                            order=step_data.get('order', 1)
                        )
                    else:
                        # project.py の ResearchStep オブジェクトの場合
                        theme_step = ResearchStep(
                            title=step_data.title,
                            description=step_data.description,
                            tips=step_data.tips,
                            duration=step_data.estimatedDuration,
                            order=step_data.order
                        )
                    steps.append(theme_step)

                # models/theme.py の ResearchPlan オブジェクトを作成
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
            else:
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
        研究計画を保存する（AWSのみ）
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
                return True
            else:
                print(f"❌ 研究計画のAWS保存に失敗しました: {plan.theme_title}")
                return False

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
