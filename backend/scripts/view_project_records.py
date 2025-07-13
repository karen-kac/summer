#!/usr/bin/env python3
"""
特定プロジェクトの記録を表示するスクリプト
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.client.dynamodb_client import DynamoDBClient
from repositories.record_repository import RecordRepository
import logging
import json

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def view_project_records(project_id: str):
    """指定プロジェクトの記録を表示"""
    try:
        # DynamoDBクライアントを初期化
        db_client = DynamoDBClient()
        record_repo = RecordRepository(db_client)
        
        logger.info(f"📊 プロジェクト記録を取得中: {project_id}")
        
        # プロジェクトの記録を取得
        result = await record_repo.get_records_by_project(project_id, limit=50)
        
        print(f"\n📊 プロジェクト記録: {project_id}")
        print(f"総記録件数: {result.total}件")
        print("=" * 80)
        
        for i, record_response in enumerate(result.records, 1):
            record = record_response.record
            media = record_response.media
            
            print(f"\n📝 記録 {i}:")
            print(f"  ID: {record.recordId}")
            print(f"  日付: {record.recordDate}")
            print(f"  時刻: {record.recordTime}")
            print(f"  タイトル: {record.title}")
            print(f"  内容: {record.content}")
            print(f"  タイプ: {record.recordType}")
            print(f"  ステップID: {record.stepId}")
            print(f"  タグ: {record.tags}")
            print(f"  作成日時: {record.createdAt}")
            print(f"  更新日時: {record.updatedAt}")
            
            if record.weatherInfo:
                print(f"  天気情報: {record.weatherInfo}")
            
            if record.locationInfo:
                print(f"  位置情報: {record.locationInfo}")
            
            if record.data:
                print(f"  データ: {json.dumps(record.data, ensure_ascii=False, indent=2)}")
            
            if media:
                print(f"  メディア: {len(media)}件")
                for j, m in enumerate(media, 1):
                    if isinstance(m, dict):
                        print(f"    メディア{j}: {m.get('filename', 'unknown')} ({m.get('contentType', 'unknown')})")
            
            print("-" * 40)
        
        return result.total
        
    except Exception as e:
        logger.error(f"❌ 記録取得エラー: {e}")
        return 0

if __name__ == "__main__":
    project_id = "d3af0d40-74e0-43d5-b003-42564c4b8784"
    total = asyncio.run(view_project_records(project_id))
    print(f"\n✅ 完了: {total}件の記録を表示しました")