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
                raise ValueError("GEMINI_API_KEYが設定されていません。")

            # ダミーキーの場合はエラー
            if api_key == "dummy_key_for_testing":
                raise ValueError("実際のGEMINI_API_KEYを設定してください。ダミーキーでは実際のAI生成はできません。")

            # Gemini APIの設定
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                "gemini-1.5-flash",
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
            )

            print(f"✅ Gemini API初期化成功: gemini-1.5-flash")

        except ValueError as e:
            raise RuntimeError(str(e))
        except Exception as e:
            # その他の初期化エラー
            raise RuntimeError(f"Gemini API初期化中にエラーが発生しました: {e}")

    async def generate_content(self, prompt: str) -> str:
        """
        指定されたプロンプトをGemini APIに送信し、結果のテキストを返す

        Args:
            prompt (str): Gemini APIに送信するプロンプト文字列

        Returns:
            str: APIからの応答テキスト

        Raises:
            HTTPException: API通信でエラーが発生した場合
        """
        print(f"🚀 Gemini APIへプロンプトを送信中...")
        print(f"📝 プロンプト概要: {prompt[:100]}...")

        try:
            response = await self.model.generate_content_async(prompt)

            if not response.text:
                raise ValueError("Gemini APIから空の応答が返されました")

            print(f"✅ Gemini API応答受信: {len(response.text)}文字")
            return response.text

        except Exception as e:
            print(f"❌ Gemini API呼び出しエラー: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Gemini APIとの通信中にエラーが発生しました: {e}"
            )

    async def post_prompt(self, prompt: str) -> Union[dict, list]:
        """
        プロンプトを送信してJSON形式の応答を取得

        Args:
            prompt (str): 送信するプロンプト

        Returns:
            Union[dict, list]: 解析されたJSON応答

        Raises:
            HTTPException: API通信やJSON解析でエラーが発生した場合
        """
        try:
            # Gemini APIから応答を取得
            raw_response = await self.generate_content(prompt)
            print(f"🤖 Gemini AI生成結果:\n---\n{raw_response}\n---")

            # JSONブロックを抽出（```json ... ``` の部分）
            json_pattern = r'```json\s*([\s\S]*?)\s*```'
            match = re.search(json_pattern, raw_response)

            if not match:
                # JSONブロックが見つからない場合、別のパターンを試す
                json_pattern_alt = r'\[[\s\S]*\]'
                match_alt = re.search(json_pattern_alt, raw_response)

                if match_alt:
                    json_string = match_alt.group(0).strip()
                else:
                    raise ValueError(
                        f"AI応答にJSONブロックが見つかりませんでした。\n"
                        f"応答: {raw_response[:500]}..."
                    )
            else:
                json_string = match.group(1).strip()

            # JSONを解析
            try:
                result = json.loads(json_string)
                print(f"✅ JSON解析成功: {type(result)}, 件数: {len(result) if isinstance(result, list) else 'N/A'}")

                # リスト形式の場合はそのまま返す
                if isinstance(result, list):
                    return result
                # 辞書形式の場合、テーマのリストが含まれているかチェック
                elif isinstance(result, dict):
                    if 'themes' in result:
                        return result['themes']
                    else:
                        return [result]  # 単一のテーマオブジェクトとして扱う
                else:
                    raise ValueError(f"予期しないJSON形式: {type(result)}")

            except json.JSONDecodeError as e:
                print(f"❌ JSON解析エラー:")
                print(f"エラー詳細: {e}")
                print(f"解析対象: {json_string[:200]}...")
                raise HTTPException(
                    status_code=500,
                    detail=f"AI応答のJSON解析に失敗しました: {e}\n\n解析対象の一部: {json_string[:100]}..."
                )

        except HTTPException:
            # 既にHTTPExceptionの場合はそのまま再発生
            raise
        except ValueError as e:
            print(f"❌ 応答形式エラー: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"AI応答の形式が不正です: {e}"
            )
        except Exception as e:
            print(f"❌ 予期しないエラー: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"AI処理中に予期しないエラーが発生しました: {e}"
            )
