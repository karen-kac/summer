"""
AWS接続テストスクリプト
リソースの作成権限がない場合でも、既存リソースへの接続を確認できます
"""

import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

def test_aws_credentials():
    """AWS認証情報のテスト"""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print("✅ AWS認証成功")
        print(f"   ユーザーARN: {identity.get('Arn')}")
        print(f"   アカウントID: {identity.get('Account')}")
        return True
    except NoCredentialsError:
        print("❌ AWS認証情報が見つかりません")
        return False
    except ClientError as e:
        print(f"❌ AWS認証エラー: {e}")
        return False

def test_dynamodb_connection():
    """DynamoDB接続テスト"""
    try:
        dynamodb = boto3.client(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'ap-northeast-1')
        )

        table_name = os.getenv('DYNAMODB_TABLE_NAME', 'ResearchApp')

        # テーブルの存在確認
        try:
            response = dynamodb.describe_table(TableName=table_name)
            table_status = response['Table']['TableStatus']
            print(f"✅ DynamoDBテーブル '{table_name}' 接続成功")
            print(f"   テーブル状態: {table_status}")

            # GSIの確認
            gsi_count = len(response['Table'].get('GlobalSecondaryIndexes', []))
            print(f"   GSI数: {gsi_count}")

            return True

        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"⚠️ DynamoDBテーブル '{table_name}' が存在しません")
                print("   手動でテーブルを作成するか、権限を追加してスクリプトを実行してください")
            else:
                print(f"❌ DynamoDBアクセスエラー: {e}")
            return False

    except Exception as e:
        print(f"❌ DynamoDB接続エラー: {e}")
        return False

def test_s3_connection():
    """S3接続テスト"""
    try:
        s3 = boto3.client(
            's3',
            region_name=os.getenv('AWS_REGION', 'ap-northeast-1')
        )

        bucket_name = os.getenv('S3_BUCKET_NAME', 'research-app-storage')

        # バケットの存在確認
        try:
            response = s3.head_bucket(Bucket=bucket_name)
            print(f"✅ S3バケット '{bucket_name}' 接続成功")

            # CORS設定の確認
            try:
                cors = s3.get_bucket_cors(Bucket=bucket_name)
                print("   CORS設定: 有効")
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchCORSConfiguration':
                    print("   CORS設定: 未設定（設定を追加してください）")
                else:
                    print(f"   CORS設定確認エラー: {e}")

            return True

        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                print(f"⚠️ S3バケット '{bucket_name}' が存在しません")
                print("   手動でバケットを作成するか、権限を追加してスクリプトを実行してください")
            elif e.response['Error']['Code'] == 'Forbidden':
                print(f"❌ S3バケット '{bucket_name}' へのアクセスが拒否されました")
                print("   バケットの権限設定を確認してください")
            else:
                print(f"❌ S3アクセスエラー: {e}")
            return False

    except Exception as e:
        print(f"❌ S3接続エラー: {e}")
        return False

def test_repository_connections():
    """リポジトリ接続テスト"""
    try:
        import sys
        import os

        # 現在のディレクトリをPythonパスに追加
        current_dir = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        from repositories.repository_factory import get_repository_factory

        print("\n📊 リポジトリ接続テスト")
        print("-" * 30)

        factory = get_repository_factory()

        # 各リポジトリのヘルスチェック
        health_results = {}

        try:
            user_repo = factory.get_user_repository()
            health_results['user'] = True
            print("✅ UserRepository: 初期化成功")
        except Exception as e:
            health_results['user'] = False
            print(f"❌ UserRepository: 初期化失敗 - {e}")

        try:
            project_repo = factory.get_project_repository()
            health_results['project'] = True
            print("✅ ProjectRepository: 初期化成功")
        except Exception as e:
            health_results['project'] = False
            print(f"❌ ProjectRepository: 初期化失敗 - {e}")

        try:
            record_repo = factory.get_record_repository()
            health_results['record'] = True
            print("✅ RecordRepository: 初期化成功")
        except Exception as e:
            health_results['record'] = False
            print(f"❌ RecordRepository: 初期化失敗 - {e}")

        try:
            media_repo = factory.get_media_repository()
            health_results['media'] = True
            print("✅ MediaRepository: 初期化成功")
        except Exception as e:
            health_results['media'] = False
            print(f"❌ MediaRepository: 初期化失敗 - {e}")

        try:
            theme_repo = factory.get_theme_repository()
            health_results['theme'] = True
            print("✅ ThemeRepository: 初期化成功")
        except Exception as e:
            health_results['theme'] = False
            print(f"❌ ThemeRepository: 初期化失敗 - {e}")

        all_healthy = all(health_results.values())
        return all_healthy

    except ImportError as e:
        print(f"❌ リポジトリインポートエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ リポジトリテストエラー: {e}")
        return False

def main():
    """メインテスト処理"""
    print("🔍 AWS接続テストを開始します")
    print("=" * 50)

    # 環境変数の確認
    print("📋 環境変数の確認")
    print("-" * 20)

    required_vars = {
        'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'AWS_REGION': os.getenv('AWS_REGION', 'ap-northeast-1'),
        'DYNAMODB_TABLE_NAME': os.getenv('DYNAMODB_TABLE_NAME', 'ResearchApp'),
        'S3_BUCKET_NAME': os.getenv('S3_BUCKET_NAME', 'research-app-storage')
    }

    for var, value in required_vars.items():
        if var in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']:
            # セキュリティのため、認証情報は一部のみ表示
            display_value = f"{value[:4]}****" if value else "未設定"
        else:
            display_value = value if value else "未設定"

        status = "✅" if value else "❌"
        print(f"{status} {var}: {display_value}")

    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        print(f"\n❌ 未設定の環境変数: {missing_vars}")
        print("まず .env ファイルを正しく設定してください")
        return False

    print("\n🔐 AWS認証テスト")
    print("-" * 20)
    auth_success = test_aws_credentials()

    print("\n📊 DynamoDB接続テスト")
    print("-" * 25)
    dynamo_success = test_dynamodb_connection()

    print("\n🪣 S3接続テスト")
    print("-" * 15)
    s3_success = test_s3_connection()

    # リポジトリテスト
    repo_success = test_repository_connections()

    # 結果サマリー
    print("\n" + "=" * 50)
    print("📝 テスト結果サマリー")
    print(f"AWS認証: {'✅' if auth_success else '❌'}")
    print(f"DynamoDB: {'✅' if dynamo_success else '❌'}")
    print(f"S3: {'✅' if s3_success else '❌'}")
    print(f"リポジトリ: {'✅' if repo_success else '❌'}")

    if all([auth_success, dynamo_success, s3_success, repo_success]):
        print("\n🎉 すべてのテストが成功しました！")
        print("データベース操作の実装を使用できます。")
        return True
    else:
        print("\n⚠️ 一部のテストが失敗しました")
        print("\n📋 次のステップ:")

        if not dynamo_success:
            print("- DynamoDBテーブルを作成してください")
            print("  → backend/aws-setup/manual-setup-guide.md を参照")

        if not s3_success:
            print("- S3バケットを作成してください")
            print("  → backend/aws-setup/manual-setup-guide.md を参照")

        if not (dynamo_success and s3_success):
            print("- または、IAM権限を追加してスクリプトを実行してください")
            print("  → backend/aws-setup/iam-policy.json を参照")

        return False

if __name__ == "__main__":
    main()
