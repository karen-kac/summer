import os
import re
import json
import boto3
from dotenv import load_dotenv
from fastapi import HTTPException
from typing import Union

# .envファイルの読み込み
load_dotenv(".env")


class BedrockClient:
    """
    AWS BedrockのClaude APIとのデータ送受信を専門に担当するクラス
    """

    def __init__(self):
        try:
            # AWS認証情報の確認
            aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
            aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
            bedrock_region = os.environ.get("BEDROCK_REGION", "us-east-1")

            if not aws_access_key or not aws_secret_key:
                raise ValueError("AWS認証情報が設定されていません。")

            # Bedrockクライアントの初期化
            self.client = boto3.client(
                "bedrock-runtime",
                region_name=bedrock_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
            self.model_id = os.environ.get("BEDROCK_MODEL_ID")

            if not self.model_id:
                raise ValueError("BedrockモデルIDが設定されていません。")

        except ValueError as e:
            raise RuntimeError(str(e))
        except Exception as e:
            raise RuntimeError(f"Bedrock API初期化中にエラーが発生しました: {e}")

    async def generate_content(self, prompt: str) -> str:
        """
        指定されたプロンプトをBedrock APIに送信し、結果のテキストを返す

        Args:
            prompt (str): Bedrock APIに送信するプロンプト文字列

        Returns:
            str: APIからの応答テキスト

        Raises:
            HTTPException: API通信でエラーが発生した場合
        """
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 8192,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )

            response_body = json.loads(response["body"].read())

            if not response_body.get("content"):
                raise ValueError("Bedrock APIから空の応答が返されました")

            return response_body["content"][0]["text"]

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Bedrock APIとの通信中にエラーが発生しました: {e}"
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
            # Bedrock APIから応答を取得
            raw_response = await self.generate_content(prompt)

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

                # リスト形式の場合はそのまま返す
                if isinstance(result, list):
                    return result
                # 辞書形式の場合の処理
                elif isinstance(result, dict):
                    # テーマ生成の場合：themesキーを探す
                    if 'themes' in result:
                        return result['themes']
                    # 研究計画生成の場合：辞書形式をそのまま返す
                    elif 'steps' in result:
                        return result
                    # その他の単一オブジェクトの場合はリストにラップ
                    else:
                        return [result]
                else:
                    raise ValueError(f"予期しないJSON形式: {type(result)}")

            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"AI応答のJSON解析に失敗しました: {e}\n\n解析対象の一部: {json_string[:100]}..."
                )

        except HTTPException:
            # 既にHTTPExceptionの場合はそのまま再発生
            raise
        except ValueError as e:
            raise HTTPException(
                status_code=500,
                detail=f"AI応答の形式が不正です: {e}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"AI処理中に予期しないエラーが発生しました: {e}"
            )
