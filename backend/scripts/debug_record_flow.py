#!/usr/bin/env python3
"""
記録作成の流れをデバッグするスクリプト
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.client.dynamodb_client import DynamoDBClient
from repositories.record_repository import RecordRepository
import logging
from datetime import datetime, timedelta

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_record_flow():
    """記録作成の流れをデバッグ"""
    try:
        db_client = DynamoDBClient()
        record_repo = RecordRepository(db_client)
        
        print("🔍 記録作成フローのデバッグ開始")
        print("=" * 60)
        
        # 1. 最近5分以内の記録を確認
        print("\n📊 ステップ1: 最近5分以内の記録を確認")
        now = datetime.now()
        five_minutes_ago = now - timedelta(minutes=5)
        
        # 全記録を取得して時刻でフィルタ
        result = await db_client.scan_items(
            filter_expression="begins_with(SK, :record_prefix)",
            expression_attribute_values={':record_prefix': 'RECORD#'}
        )
        
        recent_records = []
        for item in result['items']:
            created_at_str = item.get('createdAt')
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    if created_at >= five_minutes_ago:
                        recent_records.append(item)
                except:
                    pass
        
        print(f"最近5分以内の記録: {len(recent_records)}件")
        
        for i, record in enumerate(recent_records, 1):
            print(f"  {i}. 「{record.get('title')}」 - {record.get('createdAt')}")
            print(f"     ユーザーID: {record.get('userId')}")
            print(f"     プロジェクトID: {record.get('projectId')}")
        
        # 2. 今日の記録数の変化を確認
        print(f"\n📅 ステップ2: 今日の記録数確認")
        today_result = await db_client.scan_items(
            filter_expression="begins_with(GSI3PK, :date_prefix)",
            expression_attribute_values={':date_prefix': f'DATE#{now.strftime("%Y-%m-%d")}'}
        )
        
        print(f"今日の記録総数: {today_result['count']}件")
        
        # 3. 特定ユーザーの記録を確認
        print(f"\n👤 ステップ3: 各ユーザーの記録数確認")
        user_ids = ["test-user-123", "user-456", "user-789"]
        
        for user_id in user_ids:
            try:
                user_records = await record_repo.get_records_by_user(user_id, limit=10)
                print(f"  {user_id}: {user_records.total}件")
                
                if user_records.total > 0:
                    latest = user_records.records[0].record
                    print(f"    最新: 「{latest.title}」 ({latest.createdAt})")
            except Exception as e:
                print(f"  {user_id}: エラー - {e}")
        
        # 4. APIエンドポイントの確認
        print(f"\n🌐 ステップ4: APIエンドポイント確認")
        import requests
        
        try:
            # ヘルスチェック
            response = requests.get("http://127.0.0.1:8000/", timeout=5)
            print(f"  サーバー状態: {response.status_code}")
        except Exception as e:
            print(f"  ❌ サーバー接続エラー: {e}")
            print(f"  💡 バックエンドサーバーが起動していない可能性があります")
        
        # 5. 記録作成エンドポイントのテスト
        print(f"\n🧪 ステップ5: 記録作成エンドポイントテスト")
        try:
            test_data = {
                "projectId": "d3af0d40-74e0-43d5-b003-42564c4b8784",
                "recordType": "note",
                "title": "デバッグテスト記録",
                "content": "これはデバッグ用のテスト記録です",
                "recordDate": now.strftime("%Y-%m-%d"),
                "recordTime": now.strftime("%H:%M"),
                "stepId": "step-1",
                "data": {"test": True},
                "tags": ["デバッグ"]
            }
            
            response = requests.post(
                "http://127.0.0.1:8000/record/create?user_id=test-user-123",
                json=test_data,
                timeout=10
            )
            
            print(f"  記録作成API: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ 記録作成成功")
                result_data = response.json()
                print(f"  記録ID: {result_data.get('record', {}).get('recordId')}")
            else:
                print(f"  ❌ 記録作成失敗: {response.text}")
                
        except Exception as e:
            print(f"  ❌ 記録作成APIエラー: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ デバッグエラー: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_record_flow())
    if success:
        print("\n✅ デバッグ完了")
    else:
        print("\n❌ デバッグ失敗")