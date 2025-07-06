import os
import google.generativeai as genai # 本番は不使用(pip install google-generativeai==0.8.5)
from dotenv import load_dotenv
from fastapi import HTTPException

# .envファイルの読み込み
load_dotenv(".env")

class LLMApiRepository:
    """
    LLM APIとのデータ送受信を専門に担当するクラス
    事前開発ではgoogleのGemini APIを使用
    """
    def __init__(self):
        try:
            # APIキーの設定
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise KeyError()
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        except KeyError:
            # .envファイルにキーがない場合
            raise RuntimeError("GEMINI_API_KEYが設定されていません。")
        except Exception as e:
            # その他の初期化エラー
            raise RuntimeError(f"LLMモデルの初期化中にエラーが発生しました: {e}")

    async def generate_content(self, prompt: str) -> str:
        """
        指定されたプロンプトをLLM APIに送信し、結果のテキストを返す
        
        Args:
            prompt (str): LLMに送信するプロンプト文字列
        
        Returns:
            str: APIからの応答テキスト
        
        Raises:
            HTTPException: API通信でエラーが発生した場合
        """
        print(f"🚀 LLM APIへプロンプトを送信:\n---\n{prompt}\n---")
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            # API呼び出し中のエラーをハンドル
            raise HTTPException(
                status_code=500, 
                detail=f"LLM APIとの通信中にエラーが発生しました: {e}"
            )

if __name__ == "__main__":
    # テスト用の簡易実行コード
    import asyncio
    repo = LLMApiRepository()

    async def main_test():
        try:
            result = await repo.generate_content("こんにちは、世界！")
            print(f"APIからの応答: {result}")
        except Exception as e:
            print(f"エラー: {e}")
    asyncio.run(main_test())