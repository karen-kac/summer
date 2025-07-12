#!/usr/bin/env python3
"""
記録作成APIのテストスクリプト
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.client.dynamodb_client import DynamoDBClient
from repositories.record_repository import RecordRepository
from models.record import CreateRecordRequest
from datetime import date, datetime
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_record_creation():
    """記録作成のテスト"""
    try:
        # DynamoDBクライアントを初期化
        db_client = DynamoDBClient()
        record_repo = RecordRepository(db_client)
        
        # テスト用の記録データ
        test_request = CreateRecordRequest(
            projectId="d3af0d40-74e0-43d5-b003-42564c4b8784",
            recordDate=date.today(),
            recordTime="15:30",
            stepId="step-1",
            recordType="note",
            title="テスト記録",
            content="これはテスト用の記録です。",
            tags=["テスト", "API"],
            data={
                "stepIndex": 0,
                "stepName": "準備",
                "projectGenre": "experiment"
            }
        )
        
        logger.info(f"📝 記録作成テスト開始")
        logger.info(f"プロジェクトID: {test_request.projectId}")
        logger.info(f"記録日付: {test_request.recordDate}")
        logger.info(f"記録時刻: {test_request.recordTime}")
        
        # 記録を作成
        result = await record_repo.create_record("test-user-123", test_request)
        
        if result:
            logger.info(f"✅ 記録作成成功: {result.record.recordId}")
            logger.info(f"作成日時: {result.record.createdAt}")
            
            # 作成した記録を取得して確認
            # SKからsequenceを抽出
            sk_parts = result.record.SK.split('#')
            sequence = sk_parts[-1] if len(sk_parts) > 2 else ''
            
            retrieved = await record_repo.get_record_by_id(
                test_request.projectId,
                test_request.recordDate,
                sequence
            )
            
            if retrieved:
                logger.info(f"✅ 記録取得成功: {retrieved.record.title}")
                return True
            else:
                logger.error(f"❌ 記録取得失敗")
                return False
        else:
            logger.error(f"❌ 記録作成失敗")
            return False
        
    except Exception as e:
        logger.error(f"❌ テストエラー: {e}")
        import traceback
        logger.error(f"トレースバック: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_record_creation())
    if success:
        print("\n✅ 記録作成APIテスト成功")
    else:
        print("\n❌ 記録作成APIテスト失敗")