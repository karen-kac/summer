from typing import Optional, List, Dict, Any
from datetime import datetime
from repositories.client.dynamodb_client import DynamoDBClient
from repositories.client.s3_client import S3Client
from models.record import Media, MediaUploadRequest, MediaUploadResponse
from models.database import KeyBuilder
import logging
import mimetypes
import uuid

logger = logging.getLogger(__name__)


class MediaRepository:
    """メディアファイルリポジトリ"""

    def __init__(self, db_client: DynamoDBClient, s3_client: S3Client):
        self.db = db_client
        self.s3 = s3_client

    async def create_media_upload_url(self, user_id: str, request: MediaUploadRequest) -> Optional[MediaUploadResponse]:
        """
        メディアアップロード用のPresigned URLを生成

        Args:
            user_id: ユーザーID
            request: メディアアップロードリクエスト

        Returns:
            MediaUploadResponse: アップロード情報
        """
        try:
            media_id = str(uuid.uuid4())

            # S3キーを生成
            file_extension = request.fileName.split('.')[-1] if '.' in request.fileName else ''
            s3_key = f"media/{user_id}/{request.projectId}/{media_id}.{file_extension}"

            # Presigned URLを生成
            upload_url = await self.s3.generate_presigned_upload_url(
                s3_key=s3_key,
                content_type=request.mimeType,
                expires_in=3600  # 1時間
            )

            if upload_url:
                # メディアメタデータを作成
                media = Media.create(
                    media_id=media_id,
                    user_id=user_id,
                    project_id=request.projectId,
                    recordId=request.recordId,
                    mediaType=request.mediaType,
                    fileName=request.fileName,
                    s3Key=s3_key,
                    s3Bucket=self.s3.bucket_name,
                    fileSize=request.fileSize,
                    mimeType=request.mimeType,
                    processingStatus="pending"
                )

                # データベースに保存
                success = await self.db.put_item(media.to_dynamo_item())

                if success:
                    logger.info(f"メディアアップロードURL生成成功: {media_id}")
                    return MediaUploadResponse(
                        mediaId=media_id,
                        uploadUrl=upload_url,
                        s3Key=s3_key,
                        expiresIn=3600
                    )
                else:
                    logger.error(f"メディアメタデータ保存失敗: {media_id}")
                    return None
            else:
                logger.error("Presigned URL生成失敗")
                return None

        except Exception as e:
            logger.error(f"メディアアップロードURL生成エラー: {e}")
            return None

    async def get_media_by_id(self, media_id: str) -> Optional[Media]:
        """
        メディアIDでメディア情報を取得

        Args:
            media_id: メディアID

        Returns:
            Media: メディア情報
        """
        try:
            item = await self.db.get_item(
                pk=KeyBuilder.media_pk(media_id),
                sk="METADATA"
            )

            if item:
                return Media(**item)
            else:
                return None

        except Exception as e:
            logger.error(f"メディア取得エラー: {media_id}, {e}")
            return None

    async def get_media_by_project(self, project_id: str, limit: int = 20,
                                 last_evaluated_key: Dict[str, Any] = None) -> List[Media]:
        """
        プロジェクトのメディア一覧を取得

        Args:
            project_id: プロジェクトID
            limit: 取得制限数
            last_evaluated_key: ページネーション用のキー

        Returns:
            List[Media]: メディア一覧
        """
        try:
            # GSI2を使用してプロジェクトのメディアを取得
            result = await self.db.query_gsi(
                gsi_name="2",
                pk=KeyBuilder.project_pk(project_id),
                sk_prefix="MEDIA#",
                limit=limit,
                last_evaluated_key=last_evaluated_key
            )

            # メディアオブジェクトに変換
            media_list = []
            for item in result['items']:
                try:
                    media = Media(**item)
                    media_list.append(media)
                except Exception as e:
                    logger.warning(f"メディアデータの変換でエラー: {e}")
                    continue

            return media_list

        except Exception as e:
            logger.error(f"プロジェクトメディア一覧取得エラー: {project_id}, {e}")
            return []

    async def get_media_by_user(self, user_id: str, limit: int = 20,
                              last_evaluated_key: Dict[str, Any] = None) -> List[Media]:
        """
        ユーザーのメディア一覧を取得

        Args:
            user_id: ユーザーID
            limit: 取得制限数
            last_evaluated_key: ページネーション用のキー

        Returns:
            List[Media]: メディア一覧
        """
        try:
            # GSI1を使用してユーザーのメディアを取得
            result = await self.db.query_gsi(
                gsi_name="1",
                pk=KeyBuilder.user_pk(user_id),
                sk_prefix="MEDIA#",
                limit=limit,
                last_evaluated_key=last_evaluated_key
            )

            # メディアオブジェクトに変換
            media_list = []
            for item in result['items']:
                try:
                    media = Media(**item)
                    media_list.append(media)
                except Exception as e:
                    logger.warning(f"メディアデータの変換でエラー: {e}")
                    continue

            return media_list

        except Exception as e:
            logger.error(f"ユーザーメディア一覧取得エラー: {user_id}, {e}")
            return []

    async def update_media_processing_status(self, media_id: str, status: str,
                                           metadata: Dict[str, Any] = None) -> bool:
        """
        メディアの処理状態を更新

        Args:
            media_id: メディアID
            status: 処理状態
            metadata: 追加メタデータ

        Returns:
            bool: 更新成功時True
        """
        try:
            update_expression = "SET processingStatus = :status, updatedAt = :updatedAt"
            expression_values = {
                ':status': status,
                ':updatedAt': datetime.now()
            }

            # メタデータがある場合は追加
            if metadata:
                update_expression += ", metadata = :metadata"
                expression_values[':metadata'] = metadata

            success = await self.db.update_item(
                pk=KeyBuilder.media_pk(media_id),
                sk="METADATA",
                update_expression=update_expression,
                expression_attribute_values=expression_values
            )

            if success:
                logger.info(f"メディア処理状態更新成功: {media_id} - {status}")
            else:
                logger.error(f"メディア処理状態更新失敗: {media_id} - {status}")

            return success

        except Exception as e:
            logger.error(f"メディア処理状態更新エラー: {media_id}, {e}")
            return False

    async def update_media_dimensions(self, media_id: str, width: int, height: int,
                                    duration: float = None) -> bool:
        """
        メディアの寸法情報を更新

        Args:
            media_id: メディアID
            width: 幅
            height: 高さ
            duration: 再生時間（動画・音声の場合）

        Returns:
            bool: 更新成功時True
        """
        try:
            dimensions = {
                'width': width,
                'height': height
            }

            if duration is not None:
                dimensions['duration'] = duration

            success = await self.db.update_item(
                pk=KeyBuilder.media_pk(media_id),
                sk="METADATA",
                update_expression="SET dimensions = :dimensions, updatedAt = :updatedAt",
                expression_attribute_values={
                    ':dimensions': dimensions,
                    ':updatedAt': datetime.now()
                }
            )

            if success:
                logger.info(f"メディア寸法情報更新成功: {media_id}")
            else:
                logger.error(f"メディア寸法情報更新失敗: {media_id}")

            return success

        except Exception as e:
            logger.error(f"メディア寸法情報更新エラー: {media_id}, {e}")
            return False

    async def create_thumbnail(self, media_id: str, thumbnail_s3_key: str) -> bool:
        """
        メディアのサムネイル情報を更新

        Args:
            media_id: メディアID
            thumbnail_s3_key: サムネイルのS3キー

        Returns:
            bool: 更新成功時True
        """
        try:
            success = await self.db.update_item(
                pk=KeyBuilder.media_pk(media_id),
                sk="METADATA",
                update_expression="SET thumbnailS3Key = :thumbnailS3Key, updatedAt = :updatedAt",
                expression_attribute_values={
                    ':thumbnailS3Key': thumbnail_s3_key,
                    ':updatedAt': datetime.now()
                }
            )

            if success:
                logger.info(f"サムネイル情報更新成功: {media_id}")
            else:
                logger.error(f"サムネイル情報更新失敗: {media_id}")

            return success

        except Exception as e:
            logger.error(f"サムネイル情報更新エラー: {media_id}, {e}")
            return False

    async def get_media_download_url(self, media_id: str, expires_in: int = 3600) -> Optional[str]:
        """
        メディアのダウンロード用Presigned URLを生成

        Args:
            media_id: メディアID
            expires_in: URL有効期限（秒）

        Returns:
            str: ダウンロードURL
        """
        try:
            # メディア情報を取得
            media = await self.get_media_by_id(media_id)
            if not media:
                logger.error(f"メディアが見つかりません: {media_id}")
                return None

            # Presigned URLを生成
            download_url = await self.s3.generate_presigned_download_url(
                s3_key=media.s3Key,
                expires_in=expires_in
            )

            if download_url:
                logger.info(f"メディアダウンロードURL生成成功: {media_id}")
                return download_url
            else:
                logger.error(f"メディアダウンロードURL生成失敗: {media_id}")
                return None

        except Exception as e:
            logger.error(f"メディアダウンロードURL生成エラー: {media_id}, {e}")
            return None

    async def delete_media(self, media_id: str) -> bool:
        """
        メディアを削除（S3とDynamoDBから削除）

        Args:
            media_id: メディアID

        Returns:
            bool: 削除成功時True
        """
        try:
            # メディア情報を取得
            media = await self.get_media_by_id(media_id)
            if not media:
                logger.error(f"メディアが見つかりません: {media_id}")
                return False

            # S3からファイルを削除
            s3_deleted = await self.s3.delete_object(media.s3Key)

            # サムネイルがある場合は削除
            if media.thumbnailS3Key:
                await self.s3.delete_object(media.thumbnailS3Key)

            # DynamoDBから削除
            db_deleted = await self.db.delete_item(
                pk=KeyBuilder.media_pk(media_id),
                sk="METADATA"
            )

            success = s3_deleted and db_deleted

            if success:
                logger.info(f"メディア削除成功: {media_id}")
            else:
                logger.error(f"メディア削除失敗: {media_id}")

            return success

        except Exception as e:
            logger.error(f"メディア削除エラー: {media_id}, {e}")
            return False

    async def get_media_by_type(self, user_id: str, media_type: str, limit: int = 20) -> List[Media]:
        """
        メディアタイプでメディア一覧を取得

        Args:
            user_id: ユーザーID
            media_type: メディアタイプ
            limit: 取得制限数

        Returns:
            List[Media]: メディア一覧
        """
        try:
            # ユーザーのメディアを取得してタイプでフィルタリング
            result = await self.db.query_gsi(
                gsi_name="1",
                pk=KeyBuilder.user_pk(user_id),
                sk_prefix="MEDIA#",
                filter_expression="mediaType = :mediaType",
                expression_attribute_values={':mediaType': media_type},
                limit=limit
            )

            # メディアオブジェクトに変換
            media_list = []
            for item in result['items']:
                try:
                    media = Media(**item)
                    media_list.append(media)
                except Exception as e:
                    logger.warning(f"メディアデータの変換でエラー: {e}")
                    continue

            return media_list

        except Exception as e:
            logger.error(f"メディアタイプ別取得エラー: {user_id} - {media_type}, {e}")
            return []

    async def get_media_storage_usage(self, user_id: str) -> Dict[str, Any]:
        """
        ユーザーのメディアストレージ使用量を取得

        Args:
            user_id: ユーザーID

        Returns:
            Dict[str, Any]: ストレージ使用量情報
        """
        try:
            # ユーザーの全メディアを取得
            result = await self.db.query_gsi(
                gsi_name="1",
                pk=KeyBuilder.user_pk(user_id),
                sk_prefix="MEDIA#"
            )

            # 使用量を集計
            total_files = 0
            total_size = 0
            by_type = {}

            for item in result['items']:
                try:
                    media = Media(**item)
                    total_files += 1
                    total_size += media.fileSize

                    if media.mediaType not in by_type:
                        by_type[media.mediaType] = {'count': 0, 'size': 0}

                    by_type[media.mediaType]['count'] += 1
                    by_type[media.mediaType]['size'] += media.fileSize

                except Exception as e:
                    logger.warning(f"メディアデータの変換でエラー: {e}")
                    continue

            return {
                'totalFiles': total_files,
                'totalSize': total_size,
                'byType': by_type
            }

        except Exception as e:
            logger.error(f"ストレージ使用量取得エラー: {user_id}, {e}")
            return {'totalFiles': 0, 'totalSize': 0, 'byType': {}}

    async def health_check(self) -> bool:
        """
        リポジトリのヘルスチェック

        Returns:
            bool: 正常時True
        """
        db_health = await self.db.health_check()
        s3_health = await self.s3.health_check()
        return db_health and s3_health
