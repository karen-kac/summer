import os
import boto3
import logging
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime, timedelta
from dotenv import load_dotenv
import mimetypes
import uuid

# .envファイルの読み込み
load_dotenv(".env")

logger = logging.getLogger(__name__)


class S3Client:
    """S3操作クライアント"""

    def __init__(self, bucket_name: str = None):
        """
        S3クライアントを初期化

        Args:
            bucket_name: バケット名（環境変数から取得される場合は不要）
        """
        try:
            # AWS認証情報の設定
            aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            aws_region = os.getenv("AWS_REGION", "ap-northeast-1")

            if not aws_access_key_id or not aws_secret_access_key:
                raise ValueError("AWS認証情報が設定されていません")

            # S3クライアントの作成
            self.s3_client = boto3.client(
                's3',
                region_name=aws_region,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )

            # バケット名の設定
            self.bucket_name = bucket_name or os.getenv("S3_BUCKET_NAME", "research-app-storage")
            self.region = aws_region

            logger.info(f"S3クライアント初期化完了: bucket={self.bucket_name}, region={aws_region}")

        except NoCredentialsError:
            raise RuntimeError("AWS認証情報が見つかりません")
        except Exception as e:
            logger.error(f"S3クライアント初期化失敗: {e}")
            raise RuntimeError(f"S3クライアント初期化失敗: {e}")

    def generate_upload_url(self, s3_key: str, content_type: str = None,
                           expires_in: int = 3600) -> Dict[str, Any]:
        """
        署名付きアップロードURLを生成

        Args:
            s3_key: S3オブジェクトキー
            content_type: コンテンツタイプ
            expires_in: 有効期限（秒）

        Returns:
            Dict[str, Any]: 署名付きURLと関連情報
        """
        try:
            # コンテンツタイプの推定
            if not content_type:
                content_type, _ = mimetypes.guess_type(s3_key)
                if not content_type:
                    content_type = 'application/octet-stream'

            # 署名付きURLの生成
            presigned_url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key,
                    'ContentType': content_type
                },
                ExpiresIn=expires_in
            )

            result = {
                'upload_url': presigned_url,
                's3_key': s3_key,
                'bucket': self.bucket_name,
                'content_type': content_type,
                'expires_in': expires_in,
                'expires_at': (datetime.now() + timedelta(seconds=expires_in)).isoformat()
            }

            logger.info(f"署名付きアップロードURL生成成功: {s3_key}")
            return result

        except ClientError as e:
            logger.error(f"署名付きアップロードURL生成失敗: {e}")
            raise Exception(f"署名付きURL生成失敗: {e}")
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            raise Exception(f"予期しないエラー: {e}")

    def generate_download_url(self, s3_key: str, expires_in: int = 3600) -> str:
        """
        署名付きダウンロードURLを生成

        Args:
            s3_key: S3オブジェクトキー
            expires_in: 有効期限（秒）

        Returns:
            str: 署名付きダウンロードURL
        """
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expires_in
            )

            logger.info(f"署名付きダウンロードURL生成成功: {s3_key}")
            return presigned_url

        except ClientError as e:
            logger.error(f"署名付きダウンロードURL生成失敗: {e}")
            raise Exception(f"署名付きURL生成失敗: {e}")
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            raise Exception(f"予期しないエラー: {e}")

    async def upload_file(self, file_path: str, s3_key: str,
                         content_type: str = None, metadata: Dict[str, str] = None) -> bool:
        """
        ファイルをS3にアップロード

        Args:
            file_path: ローカルファイルパス
            s3_key: S3オブジェクトキー
            content_type: コンテンツタイプ
            metadata: メタデータ

        Returns:
            bool: 成功時True
        """
        try:
            # コンテンツタイプの推定
            if not content_type:
                content_type, _ = mimetypes.guess_type(file_path)
                if not content_type:
                    content_type = 'application/octet-stream'

            # アップロード用パラメータ
            upload_params = {
                'Filename': file_path,
                'Bucket': self.bucket_name,
                'Key': s3_key,
                'ExtraArgs': {
                    'ContentType': content_type
                }
            }

            if metadata:
                upload_params['ExtraArgs']['Metadata'] = metadata

            # アップロード実行
            self.s3_client.upload_file(**upload_params)

            logger.info(f"ファイルアップロード成功: {s3_key}")
            return True

        except ClientError as e:
            logger.error(f"ファイルアップロード失敗: {e}")
            return False
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return False

    async def upload_object(self, data: bytes, s3_key: str,
                           content_type: str = None, metadata: Dict[str, str] = None) -> bool:
        """
        バイナリデータをS3にアップロード

        Args:
            data: バイナリデータ
            s3_key: S3オブジェクトキー
            content_type: コンテンツタイプ
            metadata: メタデータ

        Returns:
            bool: 成功時True
        """
        try:
            # アップロード用パラメータ
            upload_params = {
                'Body': data,
                'Bucket': self.bucket_name,
                'Key': s3_key
            }

            if content_type:
                upload_params['ContentType'] = content_type

            if metadata:
                upload_params['Metadata'] = metadata

            # アップロード実行
            self.s3_client.put_object(**upload_params)

            logger.info(f"オブジェクトアップロード成功: {s3_key}")
            return True

        except ClientError as e:
            logger.error(f"オブジェクトアップロード失敗: {e}")
            return False
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return False

    async def download_file(self, s3_key: str, local_path: str) -> bool:
        """
        S3からファイルをダウンロード

        Args:
            s3_key: S3オブジェクトキー
            local_path: ローカル保存パス

        Returns:
            bool: 成功時True
        """
        try:
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            logger.info(f"ファイルダウンロード成功: {s3_key}")
            return True

        except ClientError as e:
            logger.error(f"ファイルダウンロード失敗: {e}")
            return False
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return False

    async def get_object(self, s3_key: str) -> Optional[bytes]:
        """
        S3からオブジェクトを取得

        Args:
            s3_key: S3オブジェクトキー

        Returns:
            Optional[bytes]: オブジェクトデータ
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            data = response['Body'].read()

            logger.info(f"オブジェクト取得成功: {s3_key}")
            return data

        except ClientError as e:
            logger.error(f"オブジェクト取得失敗: {e}")
            return None
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return None

    async def delete_object(self, s3_key: str) -> bool:
        """
        S3からオブジェクトを削除

        Args:
            s3_key: S3オブジェクトキー

        Returns:
            bool: 成功時True
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"オブジェクト削除成功: {s3_key}")
            return True

        except ClientError as e:
            logger.error(f"オブジェクト削除失敗: {e}")
            return False
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return False

    async def delete_objects(self, s3_keys: List[str]) -> bool:
        """
        複数のオブジェクトを一括削除

        Args:
            s3_keys: S3オブジェクトキーのリスト

        Returns:
            bool: 成功時True
        """
        try:
            if not s3_keys:
                return True

            delete_objects = [{'Key': key} for key in s3_keys]

            response = self.s3_client.delete_objects(
                Bucket=self.bucket_name,
                Delete={
                    'Objects': delete_objects,
                    'Quiet': True
                }
            )

            # 削除失敗があるかチェック
            errors = response.get('Errors', [])
            if errors:
                logger.warning(f"一部のオブジェクト削除に失敗: {errors}")
                return False

            logger.info(f"オブジェクト一括削除成功: {len(s3_keys)}件")
            return True

        except ClientError as e:
            logger.error(f"オブジェクト一括削除失敗: {e}")
            return False
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return False

    async def list_objects(self, prefix: str = "", max_keys: int = 1000) -> List[Dict[str, Any]]:
        """
        オブジェクト一覧を取得

        Args:
            prefix: プレフィックス
            max_keys: 最大取得数

        Returns:
            List[Dict[str, Any]]: オブジェクト一覧
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )

            objects = []
            for obj in response.get('Contents', []):
                objects.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'etag': obj['ETag'].strip('"')
                })

            logger.info(f"オブジェクト一覧取得成功: {len(objects)}件")
            return objects

        except ClientError as e:
            logger.error(f"オブジェクト一覧取得失敗: {e}")
            return []
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return []

    async def object_exists(self, s3_key: str) -> bool:
        """
        オブジェクトの存在確認

        Args:
            s3_key: S3オブジェクトキー

        Returns:
            bool: 存在時True
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True

        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.error(f"オブジェクト存在確認失敗: {e}")
                return False
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return False

    async def get_object_metadata(self, s3_key: str) -> Optional[Dict[str, Any]]:
        """
        オブジェクトのメタデータを取得

        Args:
            s3_key: S3オブジェクトキー

        Returns:
            Optional[Dict[str, Any]]: メタデータ
        """
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)

            metadata = {
                'content_type': response.get('ContentType'),
                'content_length': response.get('ContentLength'),
                'last_modified': response.get('LastModified').isoformat() if response.get('LastModified') else None,
                'etag': response.get('ETag', '').strip('"'),
                'metadata': response.get('Metadata', {})
            }

            logger.info(f"オブジェクトメタデータ取得成功: {s3_key}")
            return metadata

        except ClientError as e:
            logger.error(f"オブジェクトメタデータ取得失敗: {e}")
            return None
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return None

    def generate_s3_key(self, user_id: str, project_id: str, file_type: str,
                       file_name: str, subfolder: str = None) -> str:
        """
        S3キーを生成

        Args:
            user_id: ユーザーID
            project_id: プロジェクトID
            file_type: ファイルタイプ（images, videos, documents, etc.）
            file_name: ファイル名
            subfolder: サブフォルダ（オプション）

        Returns:
            str: S3キー
        """
        # ファイル名にUUIDを追加してユニークにする
        file_ext = os.path.splitext(file_name)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"

        # S3キーの構築
        key_parts = ["users", user_id, "projects", project_id, file_type]

        if subfolder:
            key_parts.append(subfolder)

        key_parts.append(unique_filename)

        return "/".join(key_parts)

    def generate_thumbnail_key(self, original_s3_key: str) -> str:
        """
        サムネイル用のS3キーを生成

        Args:
            original_s3_key: 元のS3キー

        Returns:
            str: サムネイル用S3キー
        """
        # パスを分割
        path_parts = original_s3_key.split('/')
        filename = path_parts[-1]

        # サムネイル用のファイル名を生成
        name, ext = os.path.splitext(filename)
        thumbnail_filename = f"{name}_thumb{ext}"

        # サムネイル用のパスを構築
        path_parts[-1] = thumbnail_filename
        path_parts.insert(-1, "thumbnails")

        return "/".join(path_parts)

    async def health_check(self) -> bool:
        """
        ヘルスチェック

        Returns:
            bool: 接続可能時True
        """
        try:
            # バケットの存在確認
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info("S3ヘルスチェック成功")
            return True

        except ClientError as e:
            logger.error(f"S3ヘルスチェック失敗: {e}")
            return False
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return False


# シングルトンインスタンス
_s3_client = None

def get_s3_client() -> S3Client:
    """S3クライアントのシングルトンインスタンスを取得"""
    global _s3_client
    if _s3_client is None:
        _s3_client = S3Client()
    return _s3_client
