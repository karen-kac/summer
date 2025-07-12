# AWS Bedrock API セットアップ手順

## 1. AWSアカウントとIAMユーザーの作成

1. [AWSコンソール](https://console.aws.amazon.com/) にアクセス
2. IAMサービスに移動
3. 新しいユーザーを作成
4. ポリシーで `AmazonBedrockFullAccess` を付与
5. アクセスキーとシークレットキーを取得

## 2. Bedrockモデルアクセスの有効化

1. AWSコンソールでAmazon Bedrockサービスに移動
2. "Model access" をクリック
3. "Manage model access" をクリック
4. Anthropic Claudeモデルを選択
5. "Request model access" でアクセスをリクエスト

## 3. 環境変数の設定

### 方法1: .envファイルを作成（推奨）

```bash
# backend/.env ファイルを作成
cd backend
cp .env.example .env
```

`.env` ファイルに以下を記述:
```
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
```

### 方法2: 環境変数を直接設定

```bash
# Mac/Linux
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_REGION=us-east-1

# Windows (PowerShell)
$env:AWS_ACCESS_KEY_ID="your_access_key_here"
$env:AWS_SECRET_ACCESS_KEY="your_secret_key_here"
$env:AWS_REGION="us-east-1"
```

## 3. サーバーの起動

```bash
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## トラブルシューティング

### エラー: "AWS認証情報が設定されていません"

- `.env` ファイルが `backend/` ディレクトリに存在することを確認
- AWS認証情報が正しく設定されていることを確認
- サーバーを再起動

### エラー: "You don't have access to the model"

- AWSコンソールでBedrockモデルアクセスを有効化
- モデルアクセスの承認に数分かかる場合があります

### API通信エラー

- インターネット接続を確認
- AWS認証情報が有効であることを確認
- 指定したリージョンでBedrockサービスが利用可能か確認

## 注意事項

- AWS認証情報は機密情報です。GitHubなどに公開しないでください
- `.env` ファイルは `.gitignore` に含まれているため、リポジトリにコミットされません
- Bedrockの利用には料金が発生します。AWSコンソールで利用状況を確認してください
