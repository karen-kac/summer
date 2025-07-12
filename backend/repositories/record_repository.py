from typing import Optional, List, Dict, Any
from datetime import datetime, date
from repositories.client.dynamodb_client import DynamoDBClient
from repositories.client.s3_client import S3Client
from models.record import (
    Record, Experiment, Notification, Report, AIAnalysis, Media,
    CreateRecordRequest, UpdateRecordRequest, RecordResponse, RecordListResponse
)
from models.database import KeyBuilder
import logging
import base64
import uuid
import io

logger = logging.getLogger(__name__)


class RecordRepository:
    """研究記録データリポジトリ"""

    def __init__(self, db_client: DynamoDBClient, s3_client: S3Client = None):
        self.db = db_client
        self.s3 = s3_client

    async def create_record(self, user_id: str, request: CreateRecordRequest) -> Optional[RecordResponse]:
        """
        新しい研究記録を作成

        Args:
            user_id: ユーザーID
            request: 記録作成リクエスト

        Returns:
            RecordResponse: 作成された記録情報
        """
        try:
            logger.info(f"📋 記録作成開始: ユーザー={user_id}, プロジェクト={request.projectId}")

            # リクエストデータのログ
            logger.info(f"📋 リクエストデータ: {request.data}")
            if request.data and 'images' in request.data:
                images = request.data['images']
                logger.info(f"📷 画像データ検出: {len(images) if isinstance(images, list) else 0}件")
                if isinstance(images, list):
                    for i, img in enumerate(images):
                        logger.info(f"📷 画像{i+1}: {img.keys() if isinstance(img, dict) else type(img)}")
                        if isinstance(img, dict) and 'base64Data' in img:
                            logger.info(f"📷 画像{i+1} Base64データ長: {len(img['base64Data'])}")

            # S3クライアントの確認
            logger.info(f"🔧 S3クライアント: {self.s3 is not None}")

            # シーケンス番号を生成（同じ日付内での連番）
            sequence = datetime.now().strftime("%H%M%S")

            # 記録を作成
            record = Record.create(
                project_id=request.projectId,
                user_id=user_id,
                record_date=request.recordDate,
                sequence=sequence,
                stepId=request.stepId,
                recordType=request.recordType,
                title=request.title,
                content=request.content,
                recordTime=request.recordTime,
                data=request.data,
                tags=request.tags,
                weatherInfo=request.weatherInfo,
                locationInfo=request.locationInfo
            )

            logger.info(f"📋 記録オブジェクト作成: {record.recordId}")

            # 画像データを処理
            media_list = []
            if request.data and 'images' in request.data and self.s3:
                images = request.data['images']
                logger.info(f"📷 画像処理開始: {images}")

                if isinstance(images, list) and len(images) > 0:
                    logger.info(f"📷 画像データを処理中: {len(images)}件")

                    for i, image_data in enumerate(images):
                        logger.info(f"📷 画像{i+1}処理開始: {image_data}")
                        try:
                            # Base64画像データをS3に保存
                            media = await self._save_image_to_s3(
                                user_id=user_id,
                                project_id=request.projectId,
                                record_id=record.recordId,
                                image_data=image_data,
                                sequence=i + 1
                            )

                            if media:
                                media_list.append(media)
                                # 記録にメディアIDを追加
                                record.mediaIds.append(media.mediaId)
                                logger.info(f"📷 画像保存成功: {media.mediaId}")
                            else:
                                logger.error(f"📷 画像保存失敗: インデックス {i}")
                        except Exception as e:
                            logger.error(f"📷 画像処理エラー (インデックス {i}): {e}")
                            logger.error(f"📷 画像データ: {image_data}")
                            continue
                else:
                    logger.warning(f"📷 画像データが無効: {type(images)}, {images}")
            elif not self.s3:
                logger.error("📷 S3クライアントが設定されていません")
            else:
                logger.info("📷 画像データなし")

            logger.info(f"📋 画像処理完了: {len(media_list)}件のメディア作成")

            # 記録をDynamoDBに保存
            logger.info(f"📋 記録をDynamoDBに保存中...")
            success = await self.db.put_item(record.to_dynamo_item())

            if success:
                logger.info(f"📋 記録作成成功: {record.recordId}, メディア: {len(media_list)}件")
                response = RecordResponse(record=record, media=media_list)
                logger.info(f"📋 レスポンス: record={response.record.recordId}, media_count={len(response.media)}")
                return response
            else:
                logger.error(f"📋 記録作成失敗: {record.recordId}")
                return None

        except Exception as e:
            logger.error(f"📋 記録作成エラー: {e}")
            logger.error(f"📋 エラー詳細: {str(e)}")
            import traceback
            logger.error(f"📋 トレースバック: {traceback.format_exc()}")
            return None

    async def _save_image_to_s3(self, user_id: str, project_id: str, record_id: str,
                               image_data: Dict[str, Any], sequence: int) -> Optional[Media]:
        """
        画像データをS3に保存してMediaオブジェクトを作成

        Args:
            user_id: ユーザーID
            project_id: プロジェクトID
            record_id: 記録ID
            image_data: 画像データ（Base64とメタデータ）
            sequence: 画像のシーケンス番号

        Returns:
            Media: 作成されたメディアオブジェクト
        """
        try:
            logger.info(f"📷 S3保存開始: ユーザー={user_id}, プロジェクト={project_id}, 記録={record_id}, シーケンス={sequence}")

            # 画像データの検証
            if not image_data or 'base64Data' not in image_data:
                logger.error(f"📷 画像データが無効です: {image_data}")
                return None

            base64_data = image_data['base64Data']
            filename = image_data.get('filename', f'image_{sequence}.jpg')
            content_type = image_data.get('contentType', 'image/jpeg')
            file_size = image_data.get('size', 0)

            logger.info(f"📷 画像メタデータ: filename={filename}, contentType={content_type}, size={file_size}")

            # Base64データをデコード
            try:
                image_bytes = base64.b64decode(base64_data)
                logger.info(f"📷 Base64デコード成功: {len(image_bytes)} バイト")
            except Exception as e:
                logger.error(f"📷 Base64デコードエラー: {e}")
                return None

            # S3キーを生成
            media_id = str(uuid.uuid4())
            file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
            s3_key = f"media/{user_id}/{project_id}/{record_id}/{media_id}.{file_extension}"

            logger.info(f"📷 S3キー生成: {s3_key}, メディアID={media_id}")

            # S3にアップロード
            logger.info(f"📷 S3アップロード開始: {len(image_bytes)} バイト")
            upload_success = await self.s3.upload_object(
                data=image_bytes,
                s3_key=s3_key,
                content_type=content_type,
                metadata={
                    'user_id': user_id,
                    'project_id': project_id,
                    'record_id': record_id,
                    'original_filename': filename
                }
            )

            logger.info(f"📷 S3アップロード結果: {upload_success}")

            if not upload_success:
                logger.error(f"📷 S3アップロード失敗: {s3_key}")
                return None

            # Mediaオブジェクトを作成
            logger.info(f"📷 Mediaオブジェクト作成中...")
            media = Media.create(
                media_id=media_id,
                user_id=user_id,
                project_id=project_id,
                recordId=record_id,
                mediaType='image',
                fileName=filename,
                s3Key=s3_key,
                s3Bucket=self.s3.bucket_name,
                fileSize=file_size or len(image_bytes),
                mimeType=content_type,
                processingStatus='completed'
            )

            logger.info(f"📷 Mediaオブジェクト作成成功: {media.mediaId}")

            # DynamoDBに保存
            logger.info(f"📷 MediaをDynamoDBに保存中...")
            db_success = await self.db.put_item(media.to_dynamo_item())

            logger.info(f"📷 MediaのDynamoDB保存結果: {db_success}")

            if db_success:
                logger.info(f"📷 メディア作成成功: {media_id}")
                return media
            else:
                logger.error(f"📷 メディアDB保存失敗: {media_id}")
                # S3からファイルを削除
                logger.info(f"📷 S3からファイルを削除中: {s3_key}")
                await self.s3.delete_object(s3_key)
                return None

        except Exception as e:
            logger.error(f"📷 画像保存エラー: {e}")
            logger.error(f"📷 エラー詳細: {str(e)}")
            import traceback
            logger.error(f"📷 トレースバック: {traceback.format_exc()}")
            return None

    async def _get_media_with_urls(self, media_ids: List[str]) -> List[Media]:
        """
        メディアIDリストから署名付きURLを持つメディアオブジェクトを取得

        Args:
            media_ids: メディアIDのリスト

        Returns:
            List[Media]: 署名付きURLを持つメディアオブジェクトのリスト
        """
        media_list = []
        for media_id in media_ids:
            try:
                media_item = await self.db.get_item(
                    pk=KeyBuilder.media_pk(media_id),
                    sk="METADATA"
                )
                if media_item:
                    media = Media(**media_item)

                    # 署名付きダウンロードURLを生成
                    if self.s3:
                        download_url = await self.s3.generate_presigned_download_url(
                            s3_key=media.s3Key,
                            expires_in=3600  # 1時間有効
                        )
                        # メディアオブジェクトに一時的にURLを追加
                        media_dict = media.model_dump()
                        media_dict['downloadUrl'] = download_url
                        media_list.append(media_dict)
                    else:
                        media_list.append(media)
            except Exception as e:
                logger.warning(f"メディア取得エラー (ID: {media_id}): {e}")
                continue

        return media_list

    async def get_record_by_id(self, project_id: str, record_date: date, sequence: str) -> Optional[RecordResponse]:
        """
        記録IDで記録を取得

        Args:
            project_id: プロジェクトID
            record_date: 記録日付
            sequence: シーケンス番号

        Returns:
            RecordResponse: 記録情報
        """
        try:
            date_str = record_date.strftime("%Y-%m-%d")
            item = await self.db.get_item(
                pk=KeyBuilder.project_pk(project_id),
                sk=KeyBuilder.record_sk(date_str, sequence)
            )

            if item:
                record = Record(**item)

                # 関連するメディアを取得（署名付きURL付き）
                media_list = []
                if record.mediaIds:
                    media_list = await self._get_media_with_urls(record.mediaIds)

                return RecordResponse(record=record, media=media_list)
            else:
                return None

        except Exception as e:
            logger.error(f"記録取得エラー: {project_id}, {e}")
            return None

    async def get_records_by_project(self, project_id: str, limit: int = 20,
                                   last_evaluated_key: Dict[str, Any] = None) -> RecordListResponse:
        """
        プロジェクトの記録一覧を取得

        Args:
            project_id: プロジェクトID
            limit: 取得制限数
            last_evaluated_key: ページネーション用のキー

        Returns:
            RecordListResponse: 記録一覧
        """
        try:
            result = await self.db.query_items(
                pk=KeyBuilder.project_pk(project_id),
                sk_prefix="RECORD#",
                limit=limit,
                last_evaluated_key=last_evaluated_key
            )

            # 記録オブジェクトに変換
            records = []
            for item in result['items']:
                try:
                    record = Record(**item)

                    # 関連するメディアを取得（署名付きURL付き）
                    media_list = []
                    if record.mediaIds:
                        media_list = await self._get_media_with_urls(record.mediaIds)

                    records.append(RecordResponse(record=record, media=media_list))
                except Exception as e:
                    logger.warning(f"記録データの変換でエラー: {e}")
                    continue

            return RecordListResponse(
                records=records,
                total=result['count'],
                hasMore=result['last_evaluated_key'] is not None,
                nextToken=str(result['last_evaluated_key']) if result['last_evaluated_key'] else None
            )

        except Exception as e:
            logger.error(f"記録一覧取得エラー: {project_id}, {e}")
            return RecordListResponse(records=[], total=0, hasMore=False)

    async def get_records_by_user(self, user_id: str, limit: int = 20,
                                last_evaluated_key: Dict[str, Any] = None) -> RecordListResponse:
        """
        ユーザーの記録一覧を取得

        Args:
            user_id: ユーザーID
            limit: 取得制限数
            last_evaluated_key: ページネーション用のキー

        Returns:
            RecordListResponse: 記録一覧
        """
        try:
            # GSI1を使用してユーザーの記録を取得
            result = await self.db.query_gsi(
                gsi_name="1",
                pk=KeyBuilder.user_pk(user_id),
                sk_prefix="RECORD#",
                limit=limit,
                last_evaluated_key=last_evaluated_key
            )

            # 記録オブジェクトに変換
            records = []
            for item in result['items']:
                try:
                    record = Record(**item)

                    # 関連するメディアを取得（署名付きURL付き）
                    media_list = []
                    if record.mediaIds:
                        media_list = await self._get_media_with_urls(record.mediaIds)

                    records.append(RecordResponse(record=record, media=media_list))
                except Exception as e:
                    logger.warning(f"記録データの変換でエラー: {e}")
                    continue

            return RecordListResponse(
                records=records,
                total=result['count'],
                hasMore=result['last_evaluated_key'] is not None,
                nextToken=str(result['last_evaluated_key']) if result['last_evaluated_key'] else None
            )

        except Exception as e:
            logger.error(f"ユーザー記録一覧取得エラー: {user_id}, {e}")
            return RecordListResponse(records=[], total=0, hasMore=False)

    async def get_records_by_date(self, record_date: date, limit: int = 20,
                                last_evaluated_key: Dict[str, Any] = None) -> RecordListResponse:
        """
        日付で記録一覧を取得

        Args:
            record_date: 記録日付
            limit: 取得制限数
            last_evaluated_key: ページネーション用のキー

        Returns:
            RecordListResponse: 記録一覧
        """
        try:
            date_str = record_date.strftime("%Y-%m-%d")

            # GSI3を使用して日付の記録を取得
            result = await self.db.query_gsi(
                gsi_name="3",
                pk=f"DATE#{date_str}",
                limit=limit,
                last_evaluated_key=last_evaluated_key
            )

            # 記録オブジェクトに変換
            records = []
            for item in result['items']:
                try:
                    record = Record(**item)

                    # 関連するメディアを取得（署名付きURL付き）
                    media_list = []
                    if record.mediaIds:
                        media_list = await self._get_media_with_urls(record.mediaIds)

                    records.append(RecordResponse(record=record, media=media_list))
                except Exception as e:
                    logger.warning(f"記録データの変換でエラー: {e}")
                    continue

            return RecordListResponse(
                records=records,
                total=result['count'],
                hasMore=result['last_evaluated_key'] is not None,
                nextToken=str(result['last_evaluated_key']) if result['last_evaluated_key'] else None
            )

        except Exception as e:
            logger.error(f"日付記録一覧取得エラー: {record_date}, {e}")
            return RecordListResponse(records=[], total=0, hasMore=False)

    async def update_record(self, project_id: str, record_date: date, sequence: str,
                          request: UpdateRecordRequest) -> bool:
        """
        記録を更新

        Args:
            project_id: プロジェクトID
            record_date: 記録日付
            sequence: シーケンス番号
            request: 更新リクエスト

        Returns:
            bool: 更新成功時True
        """
        try:
            date_str = record_date.strftime("%Y-%m-%d")

            # 更新式の構築
            update_expression = "SET updatedAt = :updatedAt"
            expression_values = {':updatedAt': datetime.now()}

            # 更新フィールドを追加
            if request.title is not None:
                update_expression += ", title = :title"
                expression_values[':title'] = request.title

            if request.content is not None:
                update_expression += ", content = :content"
                expression_values[':content'] = request.content

            if request.data is not None:
                update_expression += ", #data = :data"
                expression_values[':data'] = request.data

            if request.tags is not None:
                update_expression += ", tags = :tags"
                expression_values[':tags'] = request.tags

            if request.weatherInfo is not None:
                update_expression += ", weatherInfo = :weatherInfo"
                expression_values[':weatherInfo'] = request.weatherInfo.model_dump()

            if request.locationInfo is not None:
                update_expression += ", locationInfo = :locationInfo"
                expression_values[':locationInfo'] = request.locationInfo.model_dump()

            success = await self.db.update_item(
                pk=KeyBuilder.project_pk(project_id),
                sk=KeyBuilder.record_sk(date_str, sequence),
                update_expression=update_expression,
                expression_attribute_values=expression_values,
                expression_attribute_names={'#data': 'data'} if request.data is not None else None
            )

            if success:
                logger.info(f"記録更新成功: {project_id} - {date_str} - {sequence}")
            else:
                logger.error(f"記録更新失敗: {project_id} - {date_str} - {sequence}")

            return success

        except Exception as e:
            logger.error(f"記録更新エラー: {project_id}, {e}")
            return False

    async def delete_record(self, project_id: str, record_date: date, sequence: str) -> bool:
        """
        記録を削除

        Args:
            project_id: プロジェクトID
            record_date: 記録日付
            sequence: シーケンス番号

        Returns:
            bool: 削除成功時True
        """
        try:
            date_str = record_date.strftime("%Y-%m-%d")

            success = await self.db.delete_item(
                pk=KeyBuilder.project_pk(project_id),
                sk=KeyBuilder.record_sk(date_str, sequence)
            )

            if success:
                logger.info(f"記録削除成功: {project_id} - {date_str} - {sequence}")
            else:
                logger.error(f"記録削除失敗: {project_id} - {date_str} - {sequence}")

            return success

        except Exception as e:
            logger.error(f"記録削除エラー: {project_id}, {e}")
            return False

    async def create_experiment(self, project_id: str, user_id: str, experiment_data: Dict[str, Any]) -> Optional[Experiment]:
        """
        実験データを作成

        Args:
            project_id: プロジェクトID
            user_id: ユーザーID
            experiment_data: 実験データ

        Returns:
            Experiment: 作成された実験データ
        """
        try:
            experiment_id = KeyBuilder.generate_uuid()

            experiment = Experiment.create(
                project_id=project_id,
                user_id=user_id,
                experiment_id=experiment_id,
                **experiment_data
            )

            success = await self.db.put_item(experiment.to_dynamo_item())

            if success:
                logger.info(f"実験データ作成成功: {experiment_id}")
                return experiment
            else:
                logger.error(f"実験データ作成失敗: {experiment_id}")
                return None

        except Exception as e:
            logger.error(f"実験データ作成エラー: {e}")
            return None

    async def get_experiments_by_project(self, project_id: str) -> List[Experiment]:
        """
        プロジェクトの実験データ一覧を取得

        Args:
            project_id: プロジェクトID

        Returns:
            List[Experiment]: 実験データ一覧
        """
        try:
            result = await self.db.query_items(
                pk=KeyBuilder.project_pk(project_id),
                sk_prefix="EXPERIMENT#"
            )

            # 実験データオブジェクトに変換
            experiments = []
            for item in result['items']:
                try:
                    experiment = Experiment(**item)
                    experiments.append(experiment)
                except Exception as e:
                    logger.warning(f"実験データの変換でエラー: {e}")
                    continue

            return experiments

        except Exception as e:
            logger.error(f"実験データ一覧取得エラー: {project_id}, {e}")
            return []

    async def create_notification(self, user_id: str, notification_data: Dict[str, Any]) -> Optional[Notification]:
        """
        通知を作成

        Args:
            user_id: ユーザーID
            notification_data: 通知データ

        Returns:
            Notification: 作成された通知
        """
        try:
            notification_id = KeyBuilder.generate_uuid()

            notification = Notification.create(
                user_id=user_id,
                notification_id=notification_id,
                **notification_data
            )

            success = await self.db.put_item(notification.to_dynamo_item())

            if success:
                logger.info(f"通知作成成功: {notification_id}")
                return notification
            else:
                logger.error(f"通知作成失敗: {notification_id}")
                return None

        except Exception as e:
            logger.error(f"通知作成エラー: {e}")
            return None

    async def get_notifications_by_user(self, user_id: str, status: str = None,
                                      limit: int = 20) -> List[Notification]:
        """
        ユーザーの通知一覧を取得

        Args:
            user_id: ユーザーID
            status: 通知状態でのフィルタリング
            limit: 取得制限数

        Returns:
            List[Notification]: 通知一覧
        """
        try:
            if status:
                # GSI1を使用して状態でフィルタリング
                result = await self.db.query_gsi(
                    gsi_name="1",
                    pk=f"STATUS#{status}",
                    filter_expression="userId = :userId",
                    expression_attribute_values={':userId': user_id},
                    limit=limit
                )
            else:
                # ユーザーの全通知を取得
                result = await self.db.query_items(
                    pk=KeyBuilder.user_pk(user_id),
                    sk_prefix="NOTIFICATION#",
                    limit=limit
                )

            # 通知オブジェクトに変換
            notifications = []
            for item in result['items']:
                try:
                    notification = Notification(**item)
                    notifications.append(notification)
                except Exception as e:
                    logger.warning(f"通知データの変換でエラー: {e}")
                    continue

            return notifications

        except Exception as e:
            logger.error(f"通知一覧取得エラー: {user_id}, {e}")
            return []

    async def update_notification_status(self, user_id: str, notification_id: str, status: str) -> bool:
        """
        通知状態を更新

        Args:
            user_id: ユーザーID
            notification_id: 通知ID
            status: 新しい状態

        Returns:
            bool: 更新成功時True
        """
        try:
            now = datetime.now()
            update_expression = "SET #status = :status, updatedAt = :updatedAt"
            expression_values = {
                ':status': status,
                ':updatedAt': now
            }
            expression_names = {'#status': 'status'}

            # 状態に応じて時刻を設定
            if status == "read":
                update_expression += ", readAt = :readAt"
                expression_values[':readAt'] = now
            elif status == "dismissed":
                update_expression += ", dismissedAt = :dismissedAt"
                expression_values[':dismissedAt'] = now

            success = await self.db.update_item(
                pk=KeyBuilder.user_pk(user_id),
                sk=KeyBuilder.notification_sk(notification_id),
                update_expression=update_expression,
                expression_attribute_values=expression_values,
                expression_attribute_names=expression_names
            )

            if success:
                logger.info(f"通知状態更新成功: {notification_id} - {status}")
            else:
                logger.error(f"通知状態更新失敗: {notification_id} - {status}")

            return success

        except Exception as e:
            logger.error(f"通知状態更新エラー: {notification_id}, {e}")
            return False

    async def create_report(self, project_id: str, user_id: str, report_data: Dict[str, Any]) -> Optional[Report]:
        """
        レポートを作成

        Args:
            project_id: プロジェクトID
            user_id: ユーザーID
            report_data: レポートデータ

        Returns:
            Report: 作成されたレポート
        """
        try:
            report = Report.create(
                project_id=project_id,
                user_id=user_id,
                report_type=report_data.get('reportType', 'summary'),
                **report_data
            )

            success = await self.db.put_item(report.to_dynamo_item())

            if success:
                logger.info(f"レポート作成成功: {report.reportId}")
                return report
            else:
                logger.error(f"レポート作成失敗: {report.reportId}")
                return None

        except Exception as e:
            logger.error(f"レポート作成エラー: {e}")
            return None

    async def get_reports_by_project(self, project_id: str) -> List[Report]:
        """
        プロジェクトのレポート一覧を取得

        Args:
            project_id: プロジェクトID

        Returns:
            List[Report]: レポート一覧
        """
        try:
            result = await self.db.query_items(
                pk=KeyBuilder.project_pk(project_id),
                sk_prefix="REPORT#"
            )

            # レポートオブジェクトに変換
            reports = []
            for item in result['items']:
                try:
                    report = Report(**item)
                    reports.append(report)
                except Exception as e:
                    logger.warning(f"レポートデータの変換でエラー: {e}")
                    continue

            return reports

        except Exception as e:
            logger.error(f"レポート一覧取得エラー: {project_id}, {e}")
            return []

    async def health_check(self) -> bool:
        """
        リポジトリのヘルスチェック

        Returns:
            bool: 正常時True
        """
        return await self.db.health_check()
