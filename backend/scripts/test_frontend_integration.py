#!/usr/bin/env python3
"""
フロントエンド統合テスト用スクリプト
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

async def test_frontend_integration():
    """フロントエンド統合テスト"""
    try:
        # DynamoDBクライアントを初期化
        db_client = DynamoDBClient()
        record_repo = RecordRepository(db_client)
        
        user_id = "test-user-123"
        project_id = "d3af0d40-74e0-43d5-b003-42564c4b8784"
        
        print("🧪 フロントエンド統合テスト開始")
        print("=" * 60)
        
        # 1. 現在の記録数を確認
        print("\n📊 ステップ1: 現在の記録数を確認")
        current_records = await record_repo.get_records_by_user(user_id, limit=50)
        print(f"現在の記録数: {current_records.total}件")
        
        # 2. 新しい記録を作成（フロントエンドと同じ形式）
        print("\n📝 ステップ2: 新しい記録を作成")
        now = datetime.now()
        local_date = now.strftime("%Y-%m-%d")
        local_time = now.strftime("%H:%M")
        
        test_request = CreateRecordRequest(
            projectId=project_id,
            recordDate=date.today(),
            recordTime=local_time,
            stepId="step-1",
            recordType="note",
            title="フロントエンド統合テスト記録",
            content="この記録はフロントエンド統合テストで作成されました。",
            tags=["テスト", "統合テスト", "フロントエンド"],
            data={
                "stepIndex": 0,
                "stepName": "準備",
                "projectGenre": "experiment",
                "testType": "frontend_integration"
            }
        )
        
        result = await record_repo.create_record(user_id, test_request)
        
        if result:
            print(f"✅ 記録作成成功: {result.record.recordId}")
            print(f"   タイトル: {result.record.title}")
            print(f"   日付: {result.record.recordDate}")
            print(f"   時刻: {result.record.recordTime}")
        else:
            print("❌ 記録作成失敗")
            return False
        
        # 3. 記録が正しく保存されたか確認
        print("\n🔍 ステップ3: 記録が正しく保存されたか確認")
        updated_records = await record_repo.get_records_by_user(user_id, limit=50)
        print(f"更新後の記録数: {updated_records.total}件")
        print(f"記録数の増加: {updated_records.total - current_records.total}件")
        
        # 4. 今日の記録を確認
        print("\n📅 ステップ4: 今日の記録を確認")
        today_records = await record_repo.get_records_by_date(date.today(), limit=20)
        print(f"今日の記録数: {today_records.total}件")
        
        if today_records.total > 0:
            print("今日の記録一覧:")
            for i, record_response in enumerate(today_records.records[:5], 1):
                record = record_response.record
                print(f"  {i}. {record.title} ({record.recordTime})")
        
        # 5. プロジェクトの記録を確認
        print("\n📋 ステップ5: プロジェクトの記録を確認")
        project_records = await record_repo.get_records_by_project(project_id, limit=10)
        print(f"プロジェクトの記録数: {project_records.total}件")
        
        if project_records.total > 0:
            print("最新の記録:")
            latest_record = project_records.records[0].record
            print(f"  タイトル: {latest_record.title}")
            print(f"  日付: {latest_record.recordDate}")
            print(f"  時刻: {latest_record.recordTime}")
            print(f"  作成日時: {latest_record.createdAt}")
        
        print("\n✅ フロントエンド統合テスト完了")
        return True
        
    except Exception as e:
        logger.error(f"❌ 統合テストエラー: {e}")
        import traceback
        logger.error(f"トレースバック: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_frontend_integration())
    if success:
        print("\n🎉 統合テスト成功")
    else:
        print("\n💥 統合テスト失敗")