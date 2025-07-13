#!/usr/bin/env python3
"""
S3ベースの画像データをrecord.dataに移行するスクリプト
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.client.dynamodb_client import DynamoDBClient
from repositories.client.s3_client import S3Client
from repositories.record_repository import RecordRepository
import logging
from datetime import datetime, date
import base64

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate_s3_images():
    """S3ベースの画像データをrecord.dataに移行"""
    try:
        # クライアントを初期化
        db_client = DynamoDBClient()
        s3_client = S3Client()
        record_repo = RecordRepository(db_client, s3_client)
        
        logger.info("🔄 S3画像データ移行開始...")
        
        # プロジェクトの記録を取得
        project_id = "d3af0d40-74e0-43d5-b003-42564c4b8784"
        result = await record_repo.get_records_by_project(project_id, limit=50)
        
        logger.info(f"📊 対象記録数: {result.total}件")
        
        migrated_count = 0
        error_count = 0
        
        for i, record_response in enumerate(result.records, 1):
            record = record_response.record
            
            try:
                # S3ベースの画像がある記録を特定
                has_s3_media = record.mediaIds and len(record.mediaIds) > 0
                has_data_images = record.data and 'images' in record.data and len(record.data['images']) > 0
                
                if has_s3_media and not has_data_images:
                    logger.info(f"🔄 記録 {i}/{result.total}: {record.recordId} - S3画像を移行中...")
                    logger.info(f"  📷 MediaIDs: {record.mediaIds}")
                    
                    # S3から画像データを取得
                    media_list = await record_repo._get_media_with_urls(record.mediaIds)
                    
                    if media_list:
                        # record.dataに移行
                        migrated_images = []
                        for j, media in enumerate(media_list):
                            if 'base64Data' in media and media['base64Data']:
                                migrated_image = {
                                    'filename': media.get('filename', f'migrated_image_{j+1}.jpg'),
                                    'contentType': media.get('contentType', 'image/jpeg'),
                                    'size': media.get('size', len(media['base64Data'])),
                                    'base64Data': media['base64Data']
                                }
                                migrated_images.append(migrated_image)
                                logger.info(f"    ✅ 画像{j+1}: {migrated_image['filename']} ({len(media['base64Data'])} chars)")
                        
                        if migrated_images:
                            # record.dataを更新
                            if not record.data:
                                record.data = {}
                            record.data['images'] = migrated_images
                            
                            # mediaIDsをクリア（データは保持するが、参照は削除）
                            record.mediaIds = []
                            
                            # データベースを更新
                            success = await db_client.put_item(record.to_dynamo_item())
                            
                            if success:
                                migrated_count += 1
                                logger.info(f"  ✅ 移行完了: {len(migrated_images)}枚の画像")
                            else:
                                error_count += 1
                                logger.error(f"  ❌ データベース更新失敗")
                        else:
                            logger.warning(f"  ⚠️ 移行できる画像がありませんでした")
                    else:
                        logger.warning(f"  ⚠️ S3からメディアを取得できませんでした")
                        
                elif has_data_images:
                    logger.info(f"✅ 記録 {i}/{result.total}: {record.recordId} - 既にrecord.dataに画像あり ({len(record.data['images'])}枚)")
                else:
                    logger.info(f"📝 記録 {i}/{result.total}: {record.recordId} - 画像なし")
                    
            except Exception as e:
                error_count += 1
                logger.error(f"❌ 記録 {record.recordId} の移行でエラー: {e}")
                continue
        
        logger.info(f"\n📊 移行結果:")
        logger.info(f"  ✅ 移行完了: {migrated_count}件")
        logger.info(f"  ❌ エラー: {error_count}件")
        
        return migrated_count
        
    except Exception as e:
        logger.error(f"❌ 移行エラー: {e}")
        import traceback
        logger.error(f"トレースバック: {traceback.format_exc()}")
        return 0

if __name__ == "__main__":
    migrated = asyncio.run(migrate_s3_images())
    print(f"\n✅ 移行完了: {migrated}件の記録を移行しました")