#!/usr/bin/env python3
"""
新しい記録作成をテストするスクリプト
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.client.dynamodb_client import DynamoDBClient
from repositories.record_repository import RecordRepository
from models.record import CreateRecordRequest
import logging
from datetime import datetime, date
import base64

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 小さなテスト画像のBase64データ（1x1ピクセルの赤いPNG）
TEST_IMAGE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGhGZ3KwwAAAABJRU5ErkJggg=="

async def test_record_creation():
    """新しい記録作成をテスト"""
    try:
        # DynamoDBクライアントを初期化
        db_client = DynamoDBClient()
        record_repo = RecordRepository(db_client)
        
        logger.info("🧪 新しい記録作成テスト開始...")
        
        # テスト用の記録リクエストを作成
        test_request = CreateRecordRequest(
            projectId="d3af0d40-74e0-43d5-b003-42564c4b8784",
            recordType="photo",
            title="画像統一テスト記録",
            content="record.data方式で画像保存のテストです。",
            recordDate=date.today(),
            recordTime=datetime.now().strftime("%H:%M"),
            data={
                "images": [
                    {
                        "filename": "test_image_1.png",
                        "contentType": "image/png",
                        "size": len(TEST_IMAGE_BASE64),
                        "base64Data": TEST_IMAGE_BASE64
                    },
                    {
                        "filename": "test_image_2.png", 
                        "contentType": "image/png",
                        "size": len(TEST_IMAGE_BASE64),
                        "base64Data": TEST_IMAGE_BASE64
                    }
                ]
            },
            tags=["テスト", "画像統一"]
        )
        
        logger.info(f"📋 テスト記録リクエスト作成: 画像{len(test_request.data['images'])}枚")
        
        # 記録を作成
        user_id = "test-user-12345"  # テスト用ユーザーID
        result = await record_repo.create_record(user_id, test_request)
        
        if result:
            logger.info(f"✅ 記録作成成功: {result.record.recordId}")
            logger.info(f"📷 画像データ保存状況:")
            logger.info(f"  - record.data.images: {len(result.record.data.get('images', [])) if result.record.data else 0}件")
            logger.info(f"  - record.mediaIds: {len(result.record.mediaIds)}件")
            logger.info(f"  - response.media: {len(result.media)}件")
            
            # 画像データの詳細確認
            if result.record.data and 'images' in result.record.data:
                for i, img in enumerate(result.record.data['images']):
                    logger.info(f"  画像{i+1}: {img.get('filename', 'N/A')} ({len(img.get('base64Data', ''))} chars)")
            
            return result.record.recordId
        else:
            logger.error("❌ 記録作成失敗")
            return None
        
    except Exception as e:
        logger.error(f"❌ テストエラー: {e}")
        import traceback
        logger.error(f"トレースバック: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    record_id = asyncio.run(test_record_creation())
    if record_id:
        print(f"\n✅ テスト完了: 記録ID {record_id} が作成されました")
    else:
        print(f"\n❌ テスト失敗: 記録を作成できませんでした")