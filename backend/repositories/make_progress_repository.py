import os
import re
import json
import sys
sys.path.append(os.pardir)
from typing import List
from fastapi import HTTPException
from backend.models.theme_models import UserProfileRequest, ThemeRecommendation

# 未完成
class MakeProgressRepository:
    """
    プロントエンドから来たテーマを進捗に変換するクラス
    """
    def __init__(self, theme: ThemeRecommendation = None):
        try:
           self.theme = theme
           if not self.theme:
               raise KeyError()
        except KeyError:
            raise RuntimeError("テーマが設定されていません。")
        except Exception as e:
            # その他の初期化エラー
            raise RuntimeError(f"初期化中にエラーが発生しました: {e}")

    async def generate_recommend(self):
        """
        テキストからJSON部分を抽出し、ThemeRecommendationのリストを生成する。
        """
        try:
            match = re.search(r'```json\s*([\s\S]*?)\s*```', self.text)
            if not match:
              raise ValueError("テキスト内にJSONブロックが見つかりません。")

            json_string = match.group(1).strip()
            if not json_string:
                 raise ValueError("テキスト内に有効なJSONコンテンツが見つかりません。")
            
            data = json.loads(json_string)
            
            recommendations = [ThemeRecommendation(**item) for item in data]
            
            return recommendations
        except json.JSONDecodeError as e:
             raise HTTPException(
                status_code=500, 
                detail=f"JSONの解析に失敗しました: {e}. 元のテキスト: '{json_string[:100]}...'"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"テキスト変換中にエラーが発生しました: {e}"
            )

        

if __name__ == "__main__":
    # テスト用の簡易実行コード
    import asyncio
    from backend.repositories.prompt_api_repository import LLMApiRepository
    from backend.repositories.make_prompt_repository import MakePromptRepository
    makeprompt = MakePromptRepository(request=UserProfileRequest(
        grade='junior1',
        interests=['music', 'sports'],
        personality=['curious', 'active'],
        strengths=['presentation', 'experiment'],
        duration='1month'
    ))
    repo = LLMApiRepository()

    async def generate_test():
        try:
            result = await repo.generate_content(prompt=await makeprompt.generate_prompt_startproject())
            return result
        except Exception as e:
            print(f"エラー: {e}")
    result = asyncio.run(generate_test())
    progress = MakeProgressRepository(text=result)

    async def main_test():
        try:
            result = await progress.generate_recommend()
            # 結果をJSON形式で出力
            print(json.dumps([item.model_dump() for item in result], ensure_ascii=False, indent=2))
            # もしくは、ThemeRecommendationのリストをそのまま出力
            # これはデバッグ用に便利です
            # print(f"APIからの応答: {result}")
        except Exception as e:
            print(f"エラー: {e}")
    asyncio.run(main_test())