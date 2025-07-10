import os
import re
import json
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import HTTPException
from typing import Union

# .envファイルの読み込み
load_dotenv(".env")


class GeminiClient:
    """
    GoogleのGemini APIとのデータ送受信を専門に担当するクラス
    """

    def __init__(self):
        try:
            # APIキーの設定
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise KeyError()
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
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
                status_code=500, detail=f"LLM APIとの通信中にエラーが発生しました: {e}"
            )

    async def post_prompt(self, prompt: str) -> Union[dict, list]:
        res = await self.generate_content(prompt)
        match = re.search(r'```json\s*([\s\S]*?)\s*```', res)
        json_string = match.group(1).strip()
        result = json.loads(json_string)
        return result
