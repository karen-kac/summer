# データベース操作の実装

このドキュメントでは、研究アプリケーション用のDynamoDBとS3を使用したデータベース操作の実装について説明します。

## 🚀 実装概要

### 実装された機能

1. **DynamoDBへの実際のデータ保存・取得**
   - 完全な CRUD 操作
   - 効率的なクエリとインデックス活用
   - バッチ処理のサポート

2. **ユーザー情報の永続化**
   - ユーザープロフィール管理
   - ユーザー設定保存
   - ユーザー統計データ
   - LINE連携情報

3. **プロジェクト・記録データの管理**
   - プロジェクト作成・更新・削除
   - 研究記録の保存・取得
   - 実験データの管理
   - スケジュール管理

4. **研究テーマ・計画の保存**
   - テーマの保存・検索
   - 研究計画の管理
   - ユーザーカスタマイズ対応

5. **メディアファイル管理**
   - S3を使用したファイル管理
   - Presigned URLによる安全なアップロード/ダウンロード
   - サムネイル生成サポート

## 📁 実装されたリポジトリ

```
backend/repositories/
├── client/
│   ├── dynamodb_client.py     # DynamoDB操作クライアント
│   ├── s3_client.py           # S3操作クライアント
│   └── bedrock_client.py      # AI機能用クライアント
├── user_repository.py         # ユーザー情報管理
├── project_repository.py      # プロジェクト管理
├── record_repository.py       # 記録データ管理
├── media_repository.py        # メディアファイル管理
├── theme_repository.py        # テーマ・計画管理
└── repository_factory.py      # リポジトリファクトリー
```

## 🔧 セットアップ手順

### 1. AWS認証情報の設定

`.env`ファイルを作成し、AWS認証情報を設定します：

```env
# AWS認証情報
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=ap-northeast-1

# DynamoDB設定
DYNAMODB_TABLE_NAME=ResearchApp

# S3設定
S3_BUCKET_NAME=research-app-storage

# その他の設定
ENVIRONMENT=development
```

### 2. AWSリソースの作成

DynamoDBテーブルとS3バケットを作成します：

```bash
cd backend
python scripts/setup_dynamodb_table.py
```

### 3. 依存関係のインストール

```bash
pip install boto3 python-dotenv pydantic
```

## 💻 使用方法

### 基本的な使用例

```python
from repositories.repository_factory import get_repository_factory
from models.user import CreateUserRequest
from models.project import CreateProjectRequest
from models.record import CreateRecordRequest
from datetime import date

# リポジトリファクトリーの取得
factory = get_repository_factory()

# ユーザー作成
user_repo = factory.get_user_repository()
user_request = CreateUserRequest(
    email="user@example.com",
    displayName="研究太郎",
    grade="middle_school_1",
    interests=["science", "experiment"],
    personality=["curious", "careful"],
    strengths=["observation", "analysis"],
    preferredDuration="short"
)
user_response = await user_repo.create_user("user123", user_request)

# プロジェクト作成
project_repo = factory.get_project_repository()
project_request = CreateProjectRequest(
    themeId="theme123",
    title="植物の成長実験",
    description="光の条件が植物の成長に与える影響を調べる",
    startDate=date.today(),
    targetEndDate=date.today() + timedelta(days=30),
    customGoals=["毎日観察する", "データを記録する"]
)
project_response = await project_repo.create_project("user123", project_request)

# 記録作成
record_repo = factory.get_record_repository()
record_request = CreateRecordRequest(
    projectId=project_response.project.projectId,
    recordType="observation",
    title="1日目の観察",
    content="種を植えました。土の状態は良好です。",
    recordDate=date.today(),
    recordTime="09:00",
    tags=["植物", "観察"]
)
record_response = await record_repo.create_record("user123", record_request)
```

### データ取得例

```python
# ユーザー情報取得
user = await user_repo.get_user_by_id("user123")
print(f"ユーザー: {user.profile.displayName}")

# プロジェクト一覧取得
projects = await project_repo.get_projects_by_user("user123")
print(f"プロジェクト数: {len(projects.projects)}")

# 記録一覧取得
records = await record_repo.get_records_by_project(project_id)
print(f"記録数: {len(records.records)}")
```

### メディアファイル操作例

```python
# メディアリポジトリの取得
media_repo = factory.get_media_repository()

# アップロード用URL生成
upload_request = MediaUploadRequest(
    projectId="project123",
    mediaType="image",
    fileName="experiment_photo.jpg",
    fileSize=1024000,
    mimeType="image/jpeg"
)
upload_response = await media_repo.create_media_upload_url("user123", upload_request)
print(f"アップロードURL: {upload_response.uploadUrl}")

# ダウンロード用URL生成
download_url = await media_repo.get_media_download_url("media123")
print(f"ダウンロードURL: {download_url}")
```

## 📊 データベース設計

### DynamoDBテーブル構造

メインテーブル `ResearchApp` を使用し、以下のアクセスパターンをサポートします：

#### 主要キー構造
- **PK (パーティションキー)**: エンティティタイプ + ID
- **SK (ソートキー)**: エンティティのサブタイプ + 詳細情報

#### グローバルセカンダリインデックス (GSI)
- **GSI1**: ユーザーベースの検索
- **GSI2**: プロジェクトベースの検索
- **GSI3**: 日付ベースの検索
- **GSI4**: 追加のクエリパターン

### データアクセスパターン

| アクセスパターン | 使用するキー | 説明 |
|---|---|---|
| ユーザー情報取得 | PK=USER#{user_id}, SK=PROFILE | ユーザープロフィール |
| ユーザーのプロジェクト一覧 | GSI1: PK=USER#{user_id}, SK=PROJECT#{project_id} | ユーザーのプロジェクト |
| プロジェクトの記録一覧 | PK=PROJECT#{project_id}, SK=RECORD#{date}#{seq} | プロジェクトの記録 |
| 日付別記録一覧 | GSI3: PK=DATE#{date}, SK=PROJECT#{project_id} | 特定日の記録 |

## 🔒 セキュリティ考慮事項

### 認証・認可
- AWS IAMロールベースのアクセス制御
- アプリケーションレベルでのユーザー認証
- リソースアクセス権限の適切な設定

### データ保護
- DynamoDB暗号化の有効化
- S3バケットの適切なアクセス制御
- Presigned URLによる安全なファイルアクセス

### プライバシー
- 個人情報の適切な管理
- 親権者への情報共有設定
- データの論理削除対応

## 🎯 パフォーマンス最適化

### DynamoDB最適化
- 適切なパーティション設計
- GSIを活用した効率的なクエリ
- バッチ処理の活用

### S3最適化
- 適切なフォルダ構造
- CloudFrontとの連携（推奨）
- 画像リサイズ処理の最適化

## 🧪 テスト

### ユニットテスト
```bash
# テストの実行
cd backend
python -m pytest tests/repositories/
```

### 統合テスト
```bash
# 統合テストの実行
python -m pytest tests/integration/
```

### ヘルスチェック
```python
# 全リポジトリのヘルスチェック
factory = get_repository_factory()
health_status = await factory.health_check()
print(f"全体の健全性: {health_status['overall']}")
```

## 🚨 トラブルシューティング

### よくある問題

1. **AWS認証エラー**
   - 環境変数の設定確認
   - IAM権限の確認
   - リージョン設定の確認

2. **DynamoDB接続エラー**
   - テーブル存在確認
   - ネットワーク接続確認
   - 権限設定確認

3. **S3アクセスエラー**
   - バケット存在確認
   - CORS設定確認
   - 権限設定確認

### ログ確認
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## 📈 監視とメトリクス

### CloudWatch メトリクス
- DynamoDB読み取り/書き込み容量
- S3 API呼び出し数
- エラー率の監視

### アプリケーションメトリクス
- データベース操作の成功率
- レスポンス時間
- リソース使用量

## 🔄 今後の拡張計画

### 機能拡張
- 検索機能の強化（ElasticSearch導入）
- リアルタイム通知（DynamoDB Streams）
- データ分析機能の追加

### スケーラビリティ
- 読み取り専用レプリカの活用
- キャッシュ戦略の実装
- 分散データベース設計

---

このデータベース操作の実装により、研究アプリケーションに必要なすべてのデータ管理機能が提供されています。各リポジトリは独立してテスト可能で、拡張性を考慮した設計となっています。
