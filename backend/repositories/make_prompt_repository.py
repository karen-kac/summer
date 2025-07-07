import os
import sys
sys.path.append(os.pardir)
from fastapi import HTTPException
from backend.models.theme_models import UserProfileRequest

GRADE_MAP = {
    'elementary1': '小学1年生', 'elementary2': '小学2年生', 'elementary3': '小学3年生',
    'elementary4': '小学4年生', 'elementary5': '小学5年生', 'elementary6': '小学6年生',
    'junior1': '中学1年生', 'junior2': '中学2年生', 'junior3': '中学3年生'
}
INTEREST_MAP = {
    'science': '理科・科学', 'nature': '自然・環境', 'animals': '動物・生物',
    'cooking': '料理・食べ物', 'art': '美術・工作', 'sports': 'スポーツ・運動',
    'music': '音楽・楽器', 'history': '歴史・社会', 'technology': 'プログラミング・技術',
    'math': '数学・計算'
}
PERSONALITY_MAP = {
    'curious': '好奇心旺盛', 'patient': '根気強い', 'creative': '創造的',
    'active': '活動的', 'careful': '丁寧・慎重', 'social': '協調性がある',
    'analytical': '分析的・論理的', 'independent': '自立している'
}
STRENGTH_MAP = {
    'observation': '観察', 'writing': '文章を書く', 'drawing': '絵を描く',
    'crafting': 'ものづくり', 'calculating': '計算・数学', 'reading': '読書・調査',
    'presentation': '発表・説明', 'experiment': '実験・検証'
}
DURATION_MAP = {
    '1week': '1週間', '2weeks': '2週間', '1month': '1ヶ月',
    '2months': '2ヶ月以上', 'flexible': '特に決まっていない'
}



class MakePromptRepository:
    """
    プロントエンドから来た属性をプロンプトに変換するクラス
    """
    def __init__(self, request: UserProfileRequest = None):
        try:
           self.request = request
           if not self.request:
               raise KeyError()
        except KeyError:
            raise RuntimeError("UserProfileRequestが設定されていません。")
        except Exception as e:
            # その他の初期化エラー
            raise RuntimeError(f"初期化中にエラーが発生しました: {e}")

    async def generate_prompt_startproject(self) -> str:
        """
        プロントエンドから来た属性をプロンプトに変換する。
        """
        try:
            grade = GRADE_MAP.get(self.request.grade, "不明な学年")
            interests = [INTEREST_MAP.get(i, i) for i in self.request.interests]
            personality = [PERSONALITY_MAP.get(p, p) for p in self.request.personality]
            strengths = [STRENGTH_MAP.get(s, s) for s in self.request.strengths]
            duration = DURATION_MAP.get(self.request.duration, "不明な期間")

            prompt = (
                f"あなたは自由研究の研究テーマを提案する専門家です。\n"
                f"学年: {grade}\n"
                f"興味: {', '.join(interests)}\n"
                f"性格: {', '.join(personality)}\n"
                f"得意なこと: {', '.join(strengths)}\n"
                f"研究期間: {duration}\n"
                "これらの情報を基に、自由研究の研究テーマを3つ提案し、以下の例のようにjsonファイル形式に変換してください。\n"
                "ただし、difficultyは難易度に応じて'easy','medium','hard'を割り振ってください。\n"
                """
                {
                    title: 'pH指示薬を使った酸性・アルカリ性の研究',
                    description: '身近な食材を使って天然のpH指示薬を作り、様々な液体の酸性・アルカリ性を調べる実験です。',
                    materials: ['紫キャベツ', 'レモン汁', '重曹', 'お酢', '石鹸水', 'コップ', 'スポイト'],
                    steps: ['紫キャベツを煮出して指示薬を作る', '様々な液体のpHを測定', '色の変化を記録', '結果をグラフにまとめる', '考察を書く'],
                    estimatedDays: 5,
                    difficulty: 'easy' | 'medium' | 'hard' as const
                }
                """
            )
            return prompt
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"プロンプト生成中にエラーが発生しました: {e}"
            )

        

if __name__ == "__main__":
    # テスト用の簡易実行コード
    import asyncio
    from backend.repositories.prompt_api_repository import LLMApiRepository
    makeprompt = MakePromptRepository(request=UserProfileRequest(
        grade='junior1',
        interests=['music', 'sports'],
        personality=['curious', 'active'],
        strengths=['presentation', 'experiment'],
        duration='1month'
    ))
    repo = LLMApiRepository()

    async def main_test():
        try:
            result = await repo.generate_content(prompt=await makeprompt.generate_prompt_startproject())
            print(f"APIからの応答: {result}")
        except Exception as e:
            print(f"エラー: {e}")
    asyncio.run(main_test())