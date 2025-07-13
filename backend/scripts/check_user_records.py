#!/usr/bin/env python3
"""
実際のユーザーIDと記録の紐付けを確認するスクリプト
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.client.dynamodb_client import DynamoDBClient
from repositories.record_repository import RecordRepository
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_user_records():
    """実際のユーザーIDと記録の紐付けを確認"""
    try:
        db_client = DynamoDBClient()
        record_repo = RecordRepository(db_client)
        
        print("🔍 ユーザーIDと記録の紐付け確認")
        print("=" * 60)
        
        # 1. 全記録からユーザーIDを抽出
        result = await db_client.scan_items(
            filter_expression="begins_with(SK, :record_prefix)",
            expression_attribute_values={':record_prefix': 'RECORD#'}
        )
        
        user_ids = set()
        for item in result['items']:
            user_id = item.get('userId')
            if user_id:
                user_ids.add(user_id)
        
        print(f"📊 発見されたユーザーID: {len(user_ids)}個")
        for user_id in sorted(user_ids):
            print(f"  - {user_id}")
        
        # 2. 各ユーザーIDの記録数を確認
        print(f"\n👥 各ユーザーの記録数:")
        for user_id in sorted(user_ids):
            try:
                user_records = await record_repo.get_records_by_user(user_id, limit=100)
                print(f"  {user_id}: {user_records.total}件")
                
                if user_records.total > 0:
                    print(f"    最新記録:")
                    for i, record_response in enumerate(user_records.records[:3], 1):
                        record = record_response.record
                        print(f"      {i}. 「{record.title}」 ({record.recordDate} {record.recordTime})")
                        
            except Exception as e:
                print(f"  {user_id}: エラー - {e}")
        
        # 3. 特定のユーザーID（フロントエンドで使用されている可能性）の確認
        print(f"\n🎯 特定ユーザーIDの詳細確認:")
        target_user_id = "d8f5c258-2bf9-4801-8e65-865a2e5c33e5"  # 新しい記録で見つかったユーザーID
        
        try:
            target_records = await record_repo.get_records_by_user(target_user_id, limit=100)
            print(f"  ユーザー {target_user_id}: {target_records.total}件")
            
            if target_records.total > 0:
                print(f"    全記録:")
                for i, record_response in enumerate(target_records.records, 1):
                    record = record_response.record
                    print(f"      {i}. 「{record.title}」")
                    print(f"         日時: {record.recordDate} {record.recordTime}")
                    print(f"         タイプ: {record.recordType}")
                    print(f"         プロジェクト: {record.projectId}")
                    print(f"         作成日時: {record.createdAt}")
                    print()
                    
        except Exception as e:
            print(f"  エラー: {e}")
        
        return len(user_ids)
        
    except Exception as e:
        logger.error(f"❌ 確認エラー: {e}")
        return 0

if __name__ == "__main__":
    count = asyncio.run(check_user_records())
    print(f"\n✅ 確認完了: {count}個のユーザーIDを発見")