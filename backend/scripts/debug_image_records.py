#!/usr/bin/env python3
"""
画像付き記録を詳しく調査するスクリプト
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

async def debug_image_records():
    """画像付き記録を詳しく調査"""
    try:
        # DynamoDBクライアントを初期化
        db_client = DynamoDBClient()
        record_repo = RecordRepository(db_client)
        
        logger.info("🔍 画像付き記録の調査開始...")
        
        # プロジェクトの記録を取得（最新順）
        project_id = "d3af0d40-74e0-43d5-b003-42564c4b8784"
        result = await record_repo.get_records_by_project(project_id, limit=20)
        
        print(f"\n🔍 プロジェクト {project_id} の記録調査:")
        print(f"総記録件数: {result.total}件")
        print("=" * 100)
        
        image_records = []
        no_image_records = []
        
        for i, record_response in enumerate(result.records, 1):
            record = record_response.record
            
            # 画像データの詳細分析
            has_images = False
            image_details = []
            
            if record.data and 'images' in record.data:
                images = record.data['images']
                if isinstance(images, list) and len(images) > 0:
                    has_images = True
                    for j, img in enumerate(images):
                        if isinstance(img, dict):
                            detail = {
                                'index': j,
                                'keys': list(img.keys()) if img else [],
                                'has_base64Data': 'base64Data' in img if img else False,
                                'has_contentType': 'contentType' in img if img else False,
                                'has_filename': 'filename' in img if img else False,
                                'base64_length': len(img.get('base64Data', '')) if img and 'base64Data' in img else 0,
                                'contentType': img.get('contentType', 'なし') if img else 'なし',
                                'filename': img.get('filename', 'なし') if img else 'なし',
                                'size': img.get('size', 0) if img else 0,
                            }
                            
                            # Base64データの有効性チェック
                            if detail['has_base64Data'] and detail['base64_length'] > 0:
                                base64_data = img['base64Data']
                                detail['base64_starts_with'] = base64_data[:20] if len(base64_data) >= 20 else base64_data
                                detail['base64_valid_chars'] = all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in base64_data)
                            
                            image_details.append(detail)
            
            record_info = {
                'record_id': record.recordId,
                'title': record.title,
                'record_date': str(record.recordDate),
                'record_time': record.recordTime,
                'has_images': has_images,
                'image_count': len(image_details),
                'image_details': image_details,
                'created_at': str(record.createdAt)
            }
            
            if has_images:
                image_records.append(record_info)
                print(f"\n📷 記録 {i} - 画像あり:")
            else:
                no_image_records.append(record_info)
                print(f"\n📝 記録 {i} - 画像なし:")
            
            print(f"  ID: {record.recordId}")
            print(f"  タイトル: {record.title}")
            print(f"  日付: {record.recordDate} {record.recordTime}")
            print(f"  画像数: {len(image_details)}枚")
            
            if has_images:
                for detail in image_details:
                    print(f"    画像 {detail['index'] + 1}:")
                    print(f"      ファイル名: {detail['filename']}")
                    print(f"      コンテンツタイプ: {detail['contentType']}")
                    print(f"      Base64データ長: {detail['base64_length']}")
                    print(f"      Base64有効文字: {detail.get('base64_valid_chars', 'N/A')}")
                    if 'base64_starts_with' in detail:
                        print(f"      Base64開始: {detail['base64_starts_with']}...")
                    print(f"      必須キー: base64Data={detail['has_base64Data']}, contentType={detail['has_contentType']}, filename={detail['has_filename']}")
            
            print("-" * 80)
        
        print(f"\n📊 調査結果サマリー:")
        print(f"画像付き記録: {len(image_records)}件")
        print(f"画像なし記録: {len(no_image_records)}件")
        
        if image_records:
            print(f"\n📷 画像付き記録の詳細:")
            for record in image_records:
                print(f"  {record['record_id']}: {record['title']} - {record['image_count']}枚")
                for detail in record['image_details']:
                    validation_status = "✅" if (detail['has_base64Data'] and detail['has_contentType'] and detail['base64_length'] > 0) else "❌"
                    print(f"    {validation_status} 画像{detail['index'] + 1}: {detail['filename']} ({detail['base64_length']} bytes)")
        
        return len(image_records)
        
    except Exception as e:
        logger.error(f"❌ 調査エラー: {e}")
        import traceback
        logger.error(f"トレースバック: {traceback.format_exc()}")
        return 0

if __name__ == "__main__":
    total = asyncio.run(debug_image_records())
    print(f"\n✅ 完了: {total}件の画像付き記録を調査しました")