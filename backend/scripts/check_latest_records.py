#!/usr/bin/env python3
"""
最新の記録を確認するスクリプト
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.client.dynamodb_client import DynamoDBClient
from repositories.record_repository import RecordRepository
import logging
from datetime import datetime, date

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_latest_records():
    """最新の記録を確認"""
    try:
        # DynamoDBクライアントを初期化
        db_client = DynamoDBClient()
        record_repo = RecordRepository(db_client)
        
        logger.info("📊 最新記録を確認中...")
        
        # プロジェクトの記録を取得（最新順）
        project_id = "d3af0d40-74e0-43d5-b003-42564c4b8784"
        result = await record_repo.get_records_by_project(project_id, limit=10)
        
        print(f"\n📊 プロジェクト {project_id} の最新記録:")
        print(f"総記録件数: {result.total}件")
        print("=" * 80)
        
        for i, record_response in enumerate(result.records, 1):
            record = record_response.record
            
            print(f"\n📝 記録 {i} (最新順):")
            print(f"  ID: {record.recordId}")
            print(f"  日付: {record.recordDate}")
            print(f"  時刻: {record.recordTime}")
            print(f"  タイトル: {record.title}")
            print(f"  内容: {record.content[:50]}...")
            print(f"  作成日時: {record.createdAt}")
            print("-" * 40)
        
        # 今日の日付で記録があるかチェック
        today = date.today()
        today_records = await record_repo.get_records_by_date(today, limit=10)
        
        print(f"\n📅 今日 ({today}) の記録:")
        print(f"件数: {today_records.total}件")
        
        if today_records.total > 0:
            for i, record_response in enumerate(today_records.records, 1):
                record = record_response.record
                print(f"  {i}. {record.title} ({record.recordTime})")
        
        return result.total
        
    except Exception as e:
        logger.error(f"❌ 記録確認エラー: {e}")
        return 0

if __name__ == "__main__":
    total = asyncio.run(check_latest_records())
    print(f"\n✅ 完了: {total}件の記録を確認しました")