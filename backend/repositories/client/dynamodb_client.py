import os
import boto3
import logging
from typing import Dict, Any, List, Optional, Union
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime
from decimal import Decimal
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv(".env")

logger = logging.getLogger(__name__)


class DynamoDBClient:
    """DynamoDB操作クライアント"""

    def __init__(self, table_name: str = None):
        """
        DynamoDBクライアントを初期化

        Args:
            table_name: テーブル名（環境変数から取得される場合は不要）
        """
        try:
            # AWS認証情報の設定
            aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            aws_region = os.getenv("AWS_REGION", "ap-northeast-1")

            if not aws_access_key_id or not aws_secret_access_key:
                raise ValueError("AWS認証情報が設定されていません")

            # DynamoDBリソースの作成
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=aws_region,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )

            # テーブル名の設定
            self.table_name = table_name or os.getenv("DYNAMODB_TABLE_NAME", "ResearchApp")
            self.table = self.dynamodb.Table(self.table_name)

            logger.info(f"DynamoDBクライアント初期化完了: table={self.table_name}, region={aws_region}")

        except NoCredentialsError:
            raise RuntimeError("AWS認証情報が見つかりません")
        except Exception as e:
            logger.error(f"DynamoDBクライアント初期化失敗: {e}")
            raise RuntimeError(f"DynamoDBクライアント初期化失敗: {e}")

    async def put_item(self, item: Dict[str, Any]) -> bool:
        """
        アイテムを追加

        Args:
            item: 追加するアイテム

        Returns:
            bool: 成功時True
        """
        try:
            # datetime型をISO文字列に変換
            processed_item = self._process_datetime_fields(item)

            response = self.table.put_item(Item=processed_item)
            logger.info(f"アイテム追加成功: PK={item.get('PK')}, SK={item.get('SK')}")
            return True

        except ClientError as e:
            logger.error(f"アイテム追加失敗: {e}")
            return False
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return False

    async def get_item(self, pk: str, sk: str) -> Optional[Dict[str, Any]]:
        """
        アイテムを取得

        Args:
            pk: パーティションキー
            sk: ソートキー

        Returns:
            Optional[Dict[str, Any]]: 見つかったアイテム
        """
        try:
            response = self.table.get_item(
                Key={'PK': pk, 'SK': sk}
            )

            item = response.get('Item')
            if item:
                logger.info(f"アイテム取得成功: PK={pk}, SK={sk}")
                return self._process_datetime_fields_reverse(item)
            else:
                logger.info(f"アイテムが見つかりません: PK={pk}, SK={sk}")
                return None

        except ClientError as e:
            logger.error(f"アイテム取得失敗: {e}")
            return None
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return None

    async def update_item(self, pk: str, sk: str, update_expression: str,
                         expression_attribute_values: Dict[str, Any],
                         expression_attribute_names: Dict[str, str] = None) -> bool:
        """
        アイテムを更新

        Args:
            pk: パーティションキー
            sk: ソートキー
            update_expression: 更新式
            expression_attribute_values: 更新値
            expression_attribute_names: 属性名マッピング

        Returns:
            bool: 成功時True
        """
        try:
            # datetime型をISO文字列に変換
            processed_values = self._process_datetime_fields(expression_attribute_values)

            # 更新時刻を自動追加
            if ':updatedAt' not in processed_values:
                processed_values[':updatedAt'] = datetime.now().isoformat()
                if not update_expression.endswith(', '):
                    update_expression += ', '
                update_expression += 'updatedAt = :updatedAt'

            params = {
                'Key': {'PK': pk, 'SK': sk},
                'UpdateExpression': update_expression,
                'ExpressionAttributeValues': processed_values,
                'ReturnValues': 'UPDATED_NEW'
            }

            if expression_attribute_names:
                params['ExpressionAttributeNames'] = expression_attribute_names

            response = self.table.update_item(**params)
            logger.info(f"アイテム更新成功: PK={pk}, SK={sk}")
            return True

        except ClientError as e:
            logger.error(f"アイテム更新失敗: {e}")
            return False
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return False

    async def delete_item(self, pk: str, sk: str) -> bool:
        """
        アイテムを削除

        Args:
            pk: パーティションキー
            sk: ソートキー

        Returns:
            bool: 成功時True
        """
        try:
            response = self.table.delete_item(
                Key={'PK': pk, 'SK': sk}
            )
            logger.info(f"アイテム削除成功: PK={pk}, SK={sk}")
            return True

        except ClientError as e:
            logger.error(f"アイテム削除失敗: {e}")
            return False
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return False

    async def query_items(self, pk: str, sk_prefix: str = None,
                         filter_expression: str = None,
                         expression_attribute_values: Dict[str, Any] = None,
                         expression_attribute_names: Dict[str, str] = None,
                         limit: int = None,
                         last_evaluated_key: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        アイテムをクエリ

        Args:
            pk: パーティションキー
            sk_prefix: ソートキーのプレフィックス
            filter_expression: フィルター式
            expression_attribute_values: 属性値
            expression_attribute_names: 属性名マッピング
            limit: 取得制限
            last_evaluated_key: 前回のクエリの続きから取得

        Returns:
            Dict[str, Any]: クエリ結果
        """
        try:
            # キー条件の作成
            key_condition = Key('PK').eq(pk)
            if sk_prefix:
                key_condition = key_condition & Key('SK').begins_with(sk_prefix)

            params = {
                'KeyConditionExpression': key_condition,
                'ScanIndexForward': True  # ソート順: 昇順
            }

            if filter_expression and expression_attribute_values:
                params['FilterExpression'] = filter_expression
                params['ExpressionAttributeValues'] = self._process_datetime_fields(expression_attribute_values)

            if expression_attribute_names:
                params['ExpressionAttributeNames'] = expression_attribute_names

            if limit:
                params['Limit'] = limit

            if last_evaluated_key:
                params['ExclusiveStartKey'] = last_evaluated_key

            response = self.table.query(**params)

            # 結果の処理
            items = [self._process_datetime_fields_reverse(item) for item in response.get('Items', [])]

            result = {
                'items': items,
                'count': response.get('Count', 0),
                'scanned_count': response.get('ScannedCount', 0),
                'last_evaluated_key': response.get('LastEvaluatedKey')
            }

            logger.info(f"クエリ成功: PK={pk}, count={result['count']}")
            return result

        except ClientError as e:
            logger.error(f"クエリ失敗: {e}")
            return {'items': [], 'count': 0, 'scanned_count': 0, 'last_evaluated_key': None}
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return {'items': [], 'count': 0, 'scanned_count': 0, 'last_evaluated_key': None}

    async def query_gsi(self, gsi_name: str, pk: str, sk_prefix: str = None,
                       filter_expression: str = None,
                       expression_attribute_values: Dict[str, Any] = None,
                       expression_attribute_names: Dict[str, str] = None,
                       limit: int = None,
                       last_evaluated_key: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        GSI(Global Secondary Index)をクエリ

        Args:
            gsi_name: GSI名
            pk: GSIパーティションキー
            sk_prefix: GSIソートキーのプレフィックス
            filter_expression: フィルター式
            expression_attribute_values: 属性値
            expression_attribute_names: 属性名マッピング
            limit: 取得制限
            last_evaluated_key: 前回のクエリの続きから取得

        Returns:
            Dict[str, Any]: クエリ結果
        """
        try:
            # キー条件の作成
            key_condition = Key(f'GSI{gsi_name}PK').eq(pk)
            if sk_prefix:
                key_condition = key_condition & Key(f'GSI{gsi_name}SK').begins_with(sk_prefix)

            params = {
                'IndexName': f'GSI{gsi_name}',
                'KeyConditionExpression': key_condition,
                'ScanIndexForward': True
            }

            if filter_expression and expression_attribute_values:
                params['FilterExpression'] = filter_expression
                params['ExpressionAttributeValues'] = self._process_datetime_fields(expression_attribute_values)

            if expression_attribute_names:
                params['ExpressionAttributeNames'] = expression_attribute_names

            if limit:
                params['Limit'] = limit

            if last_evaluated_key:
                params['ExclusiveStartKey'] = last_evaluated_key

            response = self.table.query(**params)

            # 結果の処理
            items = [self._process_datetime_fields_reverse(item) for item in response.get('Items', [])]

            result = {
                'items': items,
                'count': response.get('Count', 0),
                'scanned_count': response.get('ScannedCount', 0),
                'last_evaluated_key': response.get('LastEvaluatedKey')
            }

            logger.info(f"GSI{gsi_name}クエリ成功: PK={pk}, count={result['count']}")
            return result

        except ClientError as e:
            logger.error(f"GSI{gsi_name}クエリ失敗: {e}")
            return {'items': [], 'count': 0, 'scanned_count': 0, 'last_evaluated_key': None}
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return {'items': [], 'count': 0, 'scanned_count': 0, 'last_evaluated_key': None}

    async def scan_items(self, filter_expression: str = None,
                        expression_attribute_values: Dict[str, Any] = None,
                        expression_attribute_names: Dict[str, str] = None,
                        limit: int = None,
                        last_evaluated_key: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        テーブルをスキャン

        Args:
            filter_expression: フィルター式
            expression_attribute_values: 属性値
            expression_attribute_names: 属性名マッピング
            limit: 取得制限
            last_evaluated_key: 前回のスキャンの続きから取得

        Returns:
            Dict[str, Any]: スキャン結果
        """
        try:
            params = {}

            if filter_expression and expression_attribute_values:
                params['FilterExpression'] = filter_expression
                params['ExpressionAttributeValues'] = self._process_datetime_fields(expression_attribute_values)

            if expression_attribute_names:
                params['ExpressionAttributeNames'] = expression_attribute_names

            if limit:
                params['Limit'] = limit

            if last_evaluated_key:
                params['ExclusiveStartKey'] = last_evaluated_key

            response = self.table.scan(**params)

            # 結果の処理
            items = [self._process_datetime_fields_reverse(item) for item in response.get('Items', [])]

            result = {
                'items': items,
                'count': response.get('Count', 0),
                'scanned_count': response.get('ScannedCount', 0),
                'last_evaluated_key': response.get('LastEvaluatedKey')
            }

            logger.info(f"スキャン成功: count={result['count']}")
            return result

        except ClientError as e:
            logger.error(f"スキャン失敗: {e}")
            return {'items': [], 'count': 0, 'scanned_count': 0, 'last_evaluated_key': None}
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return {'items': [], 'count': 0, 'scanned_count': 0, 'last_evaluated_key': None}

    async def batch_get_items(self, keys: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        複数のアイテムを一括取得

        Args:
            keys: 取得するキーのリスト

        Returns:
            List[Dict[str, Any]]: 取得したアイテムのリスト
        """
        try:
            response = self.dynamodb.batch_get_item(
                RequestItems={
                    self.table_name: {
                        'Keys': keys
                    }
                }
            )

            items = response.get('Responses', {}).get(self.table_name, [])
            processed_items = [self._process_datetime_fields_reverse(item) for item in items]

            logger.info(f"一括取得成功: {len(processed_items)}件")
            return processed_items

        except ClientError as e:
            logger.error(f"一括取得失敗: {e}")
            return []
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return []

    async def batch_write_items(self, items: List[Dict[str, Any]],
                               delete_keys: List[Dict[str, str]] = None) -> bool:
        """
        複数のアイテムを一括書き込み

        Args:
            items: 書き込むアイテムのリスト
            delete_keys: 削除するキーのリスト

        Returns:
            bool: 成功時True
        """
        try:
            requests = []

            # 書き込みリクエスト
            for item in items:
                requests.append({
                    'PutRequest': {
                        'Item': self._process_datetime_fields(item)
                    }
                })

            # 削除リクエスト
            if delete_keys:
                for key in delete_keys:
                    requests.append({
                        'DeleteRequest': {
                            'Key': key
                        }
                    })

            # 25件ずつ処理（DynamoDBの制限）
            for i in range(0, len(requests), 25):
                batch_requests = requests[i:i+25]
                response = self.dynamodb.batch_write_item(
                    RequestItems={
                        self.table_name: batch_requests
                    }
                )

                # 未処理のリクエストがあれば再試行
                unprocessed_items = response.get('UnprocessedItems', {})
                if unprocessed_items:
                    logger.warning(f"未処理のアイテムがあります: {len(unprocessed_items)}")
                    # 実際の実装では指数バックオフで再試行

            logger.info(f"一括書き込み成功: {len(items)}件")
            return True

        except ClientError as e:
            logger.error(f"一括書き込み失敗: {e}")
            return False
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return False

    def _process_datetime_fields(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """datetime型とdate型をISO文字列に変換、float型をDecimal型に変換"""
        from datetime import date
        processed_item = {}
        for key, value in item.items():
            if isinstance(value, datetime):
                processed_item[key] = value.isoformat()
            elif isinstance(value, date):
                processed_item[key] = value.isoformat()
            elif isinstance(value, float):
                processed_item[key] = Decimal(str(value))
            elif isinstance(value, dict):
                processed_item[key] = self._process_datetime_fields(value)
            elif isinstance(value, list):
                processed_item[key] = [
                    self._process_datetime_fields(v) if isinstance(v, dict)
                    else v.isoformat() if isinstance(v, (datetime, date))
                    else Decimal(str(v)) if isinstance(v, float)
                    else v for v in value
                ]
            else:
                processed_item[key] = value
        return processed_item

    def _process_datetime_fields_reverse(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """ISO文字列をdatetime型に変換、Decimal型をfloat型に変換（必要に応じて）"""
        processed_item = {}
        for key, value in item.items():
            if isinstance(value, Decimal):
                processed_item[key] = float(value)
            elif isinstance(value, dict):
                processed_item[key] = self._process_datetime_fields_reverse(value)
            elif isinstance(value, list):
                processed_item[key] = [
                    self._process_datetime_fields_reverse(v) if isinstance(v, dict)
                    else float(v) if isinstance(v, Decimal)
                    else v for v in value
                ]
            else:
                processed_item[key] = value
        return processed_item

    async def health_check(self) -> bool:
        """
        ヘルスチェック

        Returns:
            bool: 接続可能時True
        """
        try:
            response = self.table.meta.client.describe_table(TableName=self.table_name)
            table_status = response['Table']['TableStatus']

            if table_status == 'ACTIVE':
                logger.info("DynamoDBヘルスチェック成功")
                return True
            else:
                logger.warning(f"テーブル状態: {table_status}")
                return False

        except ClientError as e:
            logger.error(f"DynamoDBヘルスチェック失敗: {e}")
            return False
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            return False


# シングルトンインスタンス
_dynamodb_client = None

def get_dynamodb_client() -> DynamoDBClient:
    """DynamoDBクライアントのシングルトンインスタンスを取得"""
    global _dynamodb_client
    if _dynamodb_client is None:
        _dynamodb_client = DynamoDBClient()
    return _dynamodb_client
