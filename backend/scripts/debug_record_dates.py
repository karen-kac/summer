#!/usr/bin/env python3
"""
記録の日付形式を詳しく調査するスクリプト
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.client.dynamodb_client import DynamoDBClient
from repositories.record_repository import RecordRepository
import logging
from datetime import datetime, date
import json

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_record_dates():
    """記録の日付形式を詳しく調査"""
    try:
        # DynamoDBクライアントを初期化
        db_client = DynamoDBClient()
        record_repo = RecordRepository(db_client)
        
        logger.info("📅 記録の日付形式調査開始...")
        
        # プロジェクトの記録を取得（最新順）
        project_id = "d3af0d40-74e0-43d5-b003-42564c4b8784"
        result = await record_repo.get_records_by_project(project_id, limit=10)
        
        print(f"\n📅 プロジェクト {project_id} の日付形式調査:")
        print(f"総記録件数: {result.total}件")
        print("=" * 120)
        
        for i, record_response in enumerate(result.records, 1):
            record = record_response.record
            
            # 画像の有無
            has_images = bool(record.data and 'images' in record.data and 
                            isinstance(record.data['images'], list) and 
                            len(record.data['images']) > 0)
            
            # 日付の詳細分析
            record_date_str = str(record.recordDate)
            record_date_obj = record.recordDate
            
            # 日付文字列の生成（フロントエンドで使用される形式）
            local_date_str = f"{record_date_obj.year}-{str(record_date_obj.month).zfill(2)}-{str(record_date_obj.day).zfill(2)}"
            
            print(f"\n📝 記録 {i} {'📷' if has_images else ''}:")
            print(f"  ID: {record.recordId}")
            print(f"  タイトル: {record.title}")
            print(f"  recordDate (raw): {record_date_obj} (type: {type(record_date_obj)})")
            print(f"  recordDate (str): {record_date_str}")
            print(f"  recordTime: {record.recordTime}")
            print(f"  local_date_str: {local_date_str}")
            print(f"  画像あり: {has_images}")
            print(f"  createdAt: {record.createdAt}")
            
            # 今日の日付と比較
            today = date.today()
            today_str = today.strftime("%Y-%m-%d")
            is_today = local_date_str == today_str
            
            print(f"  今日 ({today_str}) の記録: {is_today}")
            
            # 2025-07-13の記録か確認
            is_target_date = local_date_str == "2025-07-13"
            print(f"  2025-07-13の記録: {is_target_date}")
            
            print("-" * 80)
        
        # 今日の記録を特別に確認
        today = date.today()
        today_records = await record_repo.get_records_by_date(today, limit=20)
        
        print(f"\n📅 今日 ({today}) の記録詳細:")
        print(f"件数: {today_records.total}件")
        
        for i, record_response in enumerate(today_records.records, 1):
            record = record_response.record
            has_images = bool(record.data and 'images' in record.data and 
                            isinstance(record.data['images'], list) and 
                            len(record.data['images']) > 0)
            
            print(f"  {i}. {record.title} {'📷' if has_images else ''} ({record.recordTime}) - ID: {record.recordId}")
        
        return result.total
        
    except Exception as e:
        logger.error(f"❌ 調査エラー: {e}")
        import traceback
        logger.error(f"トレースバック: {traceback.format_exc()}")
        return 0

if __name__ == "__main__":
    total = asyncio.run(debug_record_dates())
    print(f"\n✅ 完了: {total}件の記録の日付を調査しました")