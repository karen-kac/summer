"""
DynamoDBテーブル作成スクリプト
研究アプリケーション用のテーブルを作成します
"""

import boto3
import os
import json
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

def create_dynamodb_table():
    """DynamoDBテーブルを作成"""
    try:
        # DynamoDBクライアントの作成
        dynamodb = boto3.client(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'ap-northeast-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )

        table_name = os.getenv('DYNAMODB_TABLE_NAME', 'ResearchApp')

        # テーブル定義
        table_definition = {
            'TableName': table_name,
            'KeySchema': [
                {
                    'AttributeName': 'PK',
                    'KeyType': 'HASH'  # パーティションキー
                },
                {
                    'AttributeName': 'SK',
                    'KeyType': 'RANGE'  # ソートキー
                }
            ],
            'AttributeDefinitions': [
                {
                    'AttributeName': 'PK',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'SK',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'GSI1PK',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'GSI1SK',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'GSI2PK',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'GSI2SK',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'GSI3PK',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'GSI3SK',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'GSI4PK',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'GSI4SK',
                    'AttributeType': 'S'
                }
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'GSI1',
                    'KeySchema': [
                        {
                            'AttributeName': 'GSI1PK',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'GSI1SK',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'BillingMode': 'PAY_PER_REQUEST'
                },
                {
                    'IndexName': 'GSI2',
                    'KeySchema': [
                        {
                            'AttributeName': 'GSI2PK',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'GSI2SK',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'BillingMode': 'PAY_PER_REQUEST'
                },
                {
                    'IndexName': 'GSI3',
                    'KeySchema': [
                        {
                            'AttributeName': 'GSI3PK',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'GSI3SK',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'BillingMode': 'PAY_PER_REQUEST'
                },
                {
                    'IndexName': 'GSI4',
                    'KeySchema': [
                        {
                            'AttributeName': 'GSI4PK',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'GSI4SK',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'BillingMode': 'PAY_PER_REQUEST'
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST',
            'StreamSpecification': {
                'StreamEnabled': True,
                'StreamViewType': 'NEW_AND_OLD_IMAGES'
            },
            'SSESpecification': {
                'Enabled': True
            },
            'Tags': [
                {
                    'Key': 'Environment',
                    'Value': os.getenv('ENVIRONMENT', 'development')
                },
                {
                    'Key': 'Application',
                    'Value': 'ResearchApp'
                },
                {
                    'Key': 'Purpose',
                    'Value': 'Main data storage'
                }
            ]
        }

        # DynamoDBのバージョンによってはGSIのBillingModeが無効な場合があるので削除
        for gsi in table_definition['GlobalSecondaryIndexes']:
            if 'BillingMode' in gsi:
                del gsi['BillingMode']

        # テーブルの作成
        print(f"DynamoDBテーブル '{table_name}' を作成しています...")
        response = dynamodb.create_table(**table_definition)

        print(f"テーブル作成リクエストが送信されました: {response['TableDescription']['TableStatus']}")

        # テーブルがアクティブになるまで待機
        print("テーブルがアクティブになるまで待機中...")
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name)

        print(f"✅ DynamoDBテーブル '{table_name}' が正常に作成されました！")

        # TTL設定（オプション）
        try:
            dynamodb.update_time_to_live(
                TableName=table_name,
                TimeToLiveSpecification={
                    'AttributeName': 'TTL',
                    'Enabled': True
                }
            )
            print("✅ TTL設定が完了しました")
        except ClientError as e:
            print(f"⚠️ TTL設定でエラーが発生しましたが、テーブルは作成されました: {e}")

        return True

    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠️ テーブル '{table_name}' は既に存在します")
            return True
        else:
            print(f"❌ DynamoDBテーブル作成エラー: {e}")
            return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False


def create_s3_bucket():
    """S3バケットを作成"""
    try:
        s3 = boto3.client(
            's3',
            region_name=os.getenv('AWS_REGION', 'ap-northeast-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )

        bucket_name = os.getenv('S3_BUCKET_NAME', 'research-app-storage')
        region = os.getenv('AWS_REGION', 'ap-northeast-1')

        # バケットの作成
        print(f"S3バケット '{bucket_name}' を作成しています...")

        if region == 'us-east-1':
            # us-east-1では LocationConstraint を指定しない
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )

        # バケットポリシーの設定
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowApplicationAccess",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": f"arn:aws:iam::{get_account_id()}:root"
                    },
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject"
                    ],
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }

        s3.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )

        # CORS設定
        cors_configuration = {
            'CORSRules': [
                {
                    'AllowedHeaders': ['*'],
                    'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
                    'AllowedOrigins': ['*'],
                    'ExposeHeaders': ['ETag'],
                    'MaxAgeSeconds': 3600
                }
            ]
        }

        s3.put_bucket_cors(
            Bucket=bucket_name,
            CORSConfiguration=cors_configuration
        )

        print(f"✅ S3バケット '{bucket_name}' が正常に作成されました！")
        return True

    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyExists':
            print(f"⚠️ バケット '{bucket_name}' は既に存在します")
            return True
        else:
            print(f"❌ S3バケット作成エラー: {e}")
            return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False


def get_account_id():
    """AWSアカウントIDを取得"""
    try:
        sts = boto3.client('sts')
        return sts.get_caller_identity()['Account']
    except Exception:
        return "123456789012"  # デフォルト値


def main():
    """メイン処理"""
    print("🚀 AWS リソース作成スクリプトを実行します")
    print("=" * 50)

    # 環境変数の確認
    required_env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ 必要な環境変数が設定されていません: {missing_vars}")
        print("AWS認証情報を設定してください")
        return False

    print("✅ 環境変数の確認完了")

    # DynamoDBテーブルの作成
    print("\n📊 DynamoDBテーブルの作成")
    print("-" * 30)
    dynamodb_success = create_dynamodb_table()

    # S3バケットの作成
    print("\n🪣 S3バケットの作成")
    print("-" * 30)
    s3_success = create_s3_bucket()

    # 結果の表示
    print("\n" + "=" * 50)
    print("📝 作成結果")
    print(f"DynamoDB: {'✅ 成功' if dynamodb_success else '❌ 失敗'}")
    print(f"S3: {'✅ 成功' if s3_success else '❌ 失敗'}")

    if dynamodb_success and s3_success:
        print("\n🎉 すべてのAWSリソースが正常に作成されました！")
        print("\n📋 次のステップ:")
        print("1. .envファイルに以下の設定を追加してください:")
        print(f"   DYNAMODB_TABLE_NAME={os.getenv('DYNAMODB_TABLE_NAME', 'ResearchApp')}")
        print(f"   S3_BUCKET_NAME={os.getenv('S3_BUCKET_NAME', 'research-app-storage')}")
        print("2. アプリケーションを起動してください")
        return True
    else:
        print("\n❌ 一部のリソース作成に失敗しました")
        return False


if __name__ == "__main__":
    main()
